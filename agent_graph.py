# agent_graph.py
"""
Economic Analysis Agent using LangGraph's create_react_agent
Based on LangChain's deep agents architecture
"""

from typing import Dict, Any, List, Optional, Sequence
from datetime import datetime
import json
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config import Config
from prompts import MAIN_SYSTEM_PROMPT, PLANNING_PROMPT
from tools import ECONOMIC_TOOLS
from planning_tools import PLANNING_TOOLS

class EconomicAnalysisAgent:
    """Economic Analysis Agent using LangGraph's create_react_agent"""
    
    def __init__(self):
        self.llm = Config.get_llm()
        self.tools = ECONOMIC_TOOLS + PLANNING_TOOLS
        self.memory = MemorySaver()
        self.system_message = MAIN_SYSTEM_PROMPT
        self.agent = self._create_agent()
        self.state = {
            "todos": [],
            "files": {},
            "data_cache": {},
            "session_data": {}
        }
    
    def _create_agent(self):
        """Create the agent using LangGraph's create_react_agent"""
        
        # According to LangGraph docs, create_react_agent takes:
        # model, tools, and optional checkpointer
        # The system message is handled differently
        
        # First, bind the system prompt to the model
        model_with_system = self.llm.bind(
            system=self.system_message
        )
        
        # Create the agent with the bound model and tools
        agent = create_react_agent(
            model_with_system,
            self.tools,
            checkpointer=self.memory
        )
        
        return agent
    
    def _build_context_message(self) -> str:
        """Build context from current state"""
        context_parts = []
        
        if self.state["todos"]:
            pending = [t for t in self.state["todos"] if t.get("status", "") != "completed"]
            completed = [t for t in self.state["todos"] if t.get("status", "") == "completed"]
            
            if pending:
                context_parts.append("Current pending tasks:")
                for task in pending:
                    context_parts.append(f"- [{task.get('id', '')}] {task.get('task', '')}")
            
            if completed:
                context_parts.append("\nCompleted tasks:")
                for task in completed:
                    context_parts.append(f"- [✓] {task.get('task', '')}")
        
        if self.state["files"]:
            context_parts.append(f"\nAvailable files: {list(self.state['files'].keys())}")
        
        if self.state["data_cache"]:
            context_parts.append(f"\nCached data series: {list(self.state['data_cache'].keys())}")
        
        # Add planning instruction if no todos exist
        if not self.state["todos"]:
            context_parts.insert(0, PLANNING_PROMPT + "\n")
        
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
            context = self._build_context_message()
            
            # Create config for the agent
            config = {
                "configurable": {
                    "thread_id": session_id or "default"
                }
            }
            
            # Combine context with query
            full_query = f"{context}\n\nUser request: {query}" if context else query
            
            # Create input
            input_data = {
                "messages": [HumanMessage(content=full_query)]
            }
            
            # Run the agent
            result = self.agent.invoke(input_data, config)
            
            # Process the result
            self._process_result(result)
            
            # Format results
            return self._format_results(result, query, session_id)
            
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "query": query
            }
    
    def _process_result(self, result: Dict[str, Any]):
        """Process agent result to update internal state"""
        messages = result.get("messages", [])
        todo_counter = len(self.state["todos"])
        
        # Look through messages for tool calls
        for message in messages:
            if isinstance(message, AIMessage) and hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.get("name", "")
                    tool_args = tool_call.get("args", {})
                    
                    # Handle TODO creation
                    if tool_name == "write_todos":
                        tasks = tool_args.get("tasks", [])
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
                        todo_id = tool_args.get("todo_id")
                        status = tool_args.get("status")
                        for todo in self.state["todos"]:
                            if todo.get("id") == todo_id:
                                todo["status"] = status
                                if status == "completed":
                                    todo["completed_at"] = datetime.now().isoformat()
                    
                    # Handle file operations
                    elif tool_name == "write_file":
                        filename = tool_args.get("filename")
                        content = tool_args.get("content")
                        if filename and content:
                            self.state["files"][filename] = {
                                "content": content,
                                "created_at": datetime.now().isoformat()
                            }
                    
                    # Cache FRED data
                    elif tool_name in ["fetch_fred_series", "calculate_statistics"]:
                        series_id = tool_args.get("series_id")
                        if series_id:
                            # Find the corresponding tool response
                            msg_index = messages.index(message)
                            # Look for the next ToolMessage
                            for next_msg in messages[msg_index + 1:]:
                                if hasattr(next_msg, 'content'):
                                    try:
                                        data = json.loads(next_msg.content)
                                        if "error" not in data:
                                            self.state["data_cache"][series_id] = data
                                        break
                                    except:
                                        pass
    
    def _format_results(self, result: Dict[str, Any], query: str, session_id: str) -> Dict[str, Any]:
        """Format agent results"""
        messages = result.get("messages", [])
        
        # Get the final response
        final_response = ""
        for message in reversed(messages):
            if isinstance(message, AIMessage) and not (hasattr(message, 'tool_calls') and message.tool_calls):
                final_response = message.content
                break
        
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
            "response": final_response,
            "report": report_content,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "data_sources": list(self.state["data_cache"].keys()),
            "files_created": list(self.state["files"].keys()),
            "total_messages": len(messages)
        }
    
    async def analyze(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run asynchronous analysis
        
        Args:
            query: The analysis request
            session_id: Optional session ID
        
        Returns:
            Analysis results
        """
        try:
            # Build context
            context = self._build_context_message()
            
            # Create config for the agent
            config = {
                "configurable": {
                    "thread_id": session_id or "default"
                }
            }
            
            # Combine context with query
            full_query = f"{context}\n\nUser request: {query}" if context else query
            
            # Create input
            input_data = {
                "messages": [HumanMessage(content=full_query)]
            }
            
            # Stream the agent execution
            final_result = None
            async for chunk in self.agent.astream(input_data, config):
                final_result = chunk
            
            if final_result:
                # Process the result
                self._process_result(final_result)
                
                # Format results
                return self._format_results(final_result, query, session_id)
            else:
                raise Exception("No result from agent")
            
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "query": query
            }

# Create singleton instance
economic_agent = EconomicAnalysisAgent()