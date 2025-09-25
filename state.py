# state.py
"""
State management for the Economic Analysis Deep Agent
Includes TODO list, file system, and conversation state
"""

from typing import TypedDict, List, Dict, Optional, Literal, Annotated
from datetime import datetime
from langgraph.graph import add_messages
import operator

# Define TODO item structure
class TodoItem(TypedDict):
    id: int
    task: str
    status: Literal["pending", "in_progress", "completed"]
    created_at: str
    completed_at: Optional[str]
    notes: Optional[str]

def add_todos(left: List[TodoItem], right: List[TodoItem]) -> List[TodoItem]:
    """Reducer function to combine TODO lists"""
    if not left:
        return right
    if not right:
        return left
    # Merge the lists, avoiding duplicates based on task content
    existing_tasks = {todo["task"] for todo in left}
    new_todos = [todo for todo in right if todo["task"] not in existing_tasks]
    return left + new_todos

def update_last_updated(left: str, right: str) -> str:
    """Reducer function for last_updated - use the most recent timestamp"""
    if not left:
        return right
    if not right:
        return left
    # Return the later timestamp
    return max(left, right)

def update_iteration_count(left: int, right: int) -> int:
    """Reducer function for iteration_count - use the maximum"""
    return max(left, right)

def update_should_continue(left: bool, right: bool) -> bool:
    """Reducer function for should_continue - use OR logic"""
    return left or right

def update_next_step(left: Optional[str], right: Optional[str]) -> Optional[str]:
    """Reducer function for next_step - use the rightmost non-None value"""
    if right is not None:
        return right
    return left

# Define File structure for virtual file system
class FileData(TypedDict):
    name: str
    content: str
    created_at: str
    modified_at: str
    size: int

# Define the main agent state
class EconomicAgentState(TypedDict):
    """State for the Economic Analysis Deep Agent"""
    
    # Conversation messages
    messages: Annotated[list, add_messages]
    
    # TODO list for task planning
    todos: Annotated[List[TodoItem], add_todos]
    todo_counter: int
    
    # Virtual file system
    files: Dict[str, FileData]
    
    # Analysis context
    current_analysis: Optional[str]
    analysis_type: Optional[str]  # 'market', 'indicator', 'forecast', 'comparison'
    
    # Data cache for FRED series
    data_cache: Dict[str, any]
    
    # Metadata
    session_id: str
    created_at: str
    last_updated: Annotated[str, update_last_updated]
    
    # Control flow
    next_step: Annotated[Optional[str], update_next_step]
    iteration_count: Annotated[int, update_iteration_count]
    max_iterations: int
    should_continue: Annotated[bool, update_should_continue]
    
    # Sub-agent results
    sub_agent_results: Dict[str, any]

def create_initial_state(session_id: str = None, max_iterations: int = 50) -> EconomicAgentState:
    """Create initial state for the agent"""
    from uuid import uuid4
    
    if not session_id:
        session_id = str(uuid4())
    
    current_time = datetime.now().isoformat()
    
    return {
        "messages": [],
        "todos": [],
        "todo_counter": 0,
        "files": {},
        "current_analysis": None,
        "analysis_type": None,
        "data_cache": {},
        "session_id": session_id,
        "created_at": current_time,
        "last_updated": current_time,
        "next_step": None,
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "should_continue": True,
        "sub_agent_results": {},
    }