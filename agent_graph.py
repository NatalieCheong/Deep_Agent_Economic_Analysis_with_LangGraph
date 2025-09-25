# agent_graph.py
"""
Simplified agent implementation that works reliably with OpenAI
Using ReAct pattern with proper message handling
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.agents import AgentAction, AgentFinish
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

from config import Config
from prompts import MAIN_SYSTEM_PROMPT, PLANNING_PROMPT
from tools import ECONOMIC_TOOLS
from planning_tools import PLANNING_TOOLS

class EconomicAnalysisAgent:
    """Economic Analysis Agent using LangChain's AgentExecutor"""
    
    def __init__(self):
        self.llm = Config.get_llm()
        self.tools = ECONOMIC_TOOLS + PLANNING_TOOLS
        self.agent_executor = self._create_agent()
        self.state = {
            "todos": [],
            "files": {},
            "data_cache": {},
            "session_data": {}
        }
    
    def _create_agent(self):
        """Create the agent using LangChain's create_openai_tools_agent"""
        
        # Create the prompt template with shorter system prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an Economic Analysis Agent with access to FRED data.
Your task is to analyze economic indicators and provide insights.
Use tools to fetch and analyze data, then provide clear conclusions.
Be concise to avoid context overflow."""),
            ("system", "{additional_context}"),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create the agent executor with reduced iterations
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=8,  # Reduced from 15
            handle_parsing_errors=True,
            return_intermediate_steps=True,
            max_execution_time=60,  # Add timeout
        )
        
        return agent_executor
    
    def _build_context(self) -> str:
        """Build additional context from state"""
        context_parts = []
        
        # Add TODO context
        if self.state["todos"]:
            pending = [t for t in self.state["todos"] if t["status"] != "completed"]
            completed = [t for t in self.state["todos"] if t["status"] == "completed"]
            
            if pending:
                context_parts.append("Pending tasks:")
                for task in pending:
                    context_parts.append(f"- [{task['id']}] {task['task']}")
            
            if completed:
                context_parts.append("\nCompleted tasks:")
                for task in completed:
                    context_parts.append(f"- [✓] {task['task']}")
        
        # Add file context
        if self.state["files"]:
            context_parts.append(f"\nAvailable files: {list(self.state['files'].keys())}")
        
        # Add data cache info
        if self.state["data_cache"]:
            context_parts.append(f"\nCached data series: {list(self.state['data_cache'].keys())}")
        
        return "\n".join(context_parts) if context_parts else "Start by creating a plan using write_todos tool."
    
    def analyze_sync(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run synchronous analysis
        
        Args:
            query: The analysis request
            session_id: Optional session ID
        
        Returns:
            Analysis results
        """
        try:
            # Build context
            additional_context = self._build_context()
            
            # If this is the first query and no todos exist, add planning instruction
            if not self.state["todos"]:
                additional_context = PLANNING_PROMPT + "\n\n" + additional_context
            
            # Run the agent
            result = self.agent_executor.invoke({
                "input": query,
                "additional_context": additional_context,
                "chat_history": []
            })
            
            # Process intermediate steps to update state
            self._process_intermediate_steps(result.get("intermediate_steps", []))
            
            # Format results
            return self._format_results(result, query, session_id)
            
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "query": query
            }
    
    def _process_intermediate_steps(self, intermediate_steps: List):
        """Process intermediate steps to update internal state"""
        todo_counter = len(self.state["todos"])
        
        for action, observation in intermediate_steps:
            if isinstance(action, AgentAction):
                tool_name = action.tool
                tool_input = action.tool_input
                
                # Handle TODO creation
                if tool_name == "write_todos":
                    tasks = tool_input.get("tasks", [])
                    for task in tasks:
                        todo_counter += 1
                        self.state["todos"].append({
                            "id": todo_counter,
                            "task": task,
                            "status": "pending",
                            "created_at": datetime.now().isoformat()
                        })
                
                # Handle TODO updates
                elif tool_name == "update_todo":
                    todo_id = tool_input.get("todo_id")
                    status = tool_input.get("status")
                    for todo in self.state["todos"]:
                        if todo["id"] == todo_id:
                            todo["status"] = status
                            if status == "completed":
                                todo["completed_at"] = datetime.now().isoformat()
                
                # Handle file operations
                elif tool_name == "write_file":
                    filename = tool_input.get("filename")
                    content = tool_input.get("content")
                    self.state["files"][filename] = {
                        "content": content,
                        "created_at": datetime.now().isoformat()
                    }
                
                # Cache FRED data
                elif tool_name in ["fetch_fred_series", "calculate_statistics"]:
                    series_id = tool_input.get("series_id")
                    if series_id and observation:
                        try:
                            self.state["data_cache"][series_id] = json.loads(str(observation))
                        except:
                            pass
    
    def _format_results(self, result: Dict, query: str, session_id: str) -> Dict[str, Any]:
        """Format agent results"""
        # Extract the final output
        output = result.get("output", "")
        
        # Get completed tasks
        completed_tasks = [t for t in self.state["todos"] if t.get("status") == "completed"]
        pending_tasks = [t for t in self.state["todos"] if t.get("status") != "completed"]
        
        # Find any reports in files
        report_content = None
        for filename, file_data in self.state["files"].items():
            if "report" in filename.lower():
                report_content = file_data.get("content", "")
                break
        
        return {
            "success": True,
            "session_id": session_id or "default",
            "query": query,
            "response": output,
            "report": report_content,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "data_sources": list(self.state["data_cache"].keys()),
            "files_created": list(self.state["files"].keys()),
            "total_steps": len(result.get("intermediate_steps", []))
        }
    
    async def analyze(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Async version - just calls sync for now"""
        return self.analyze_sync(query, session_id)

# Create singleton instance
economic_agent = EconomicAnalysisAgent()