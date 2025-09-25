# planning_tools.py
"""
Planning and organization tools for the Economic Analysis Deep Agent
Includes TODO management and virtual file system
"""

from typing import List, Optional, Literal, Dict
from datetime import datetime
from langchain.tools import tool
import json

@tool
def write_todos(tasks: List[str]) -> str:
    """
    Create a TODO list for planning the analysis workflow.
    This is a planning tool that helps organize complex analyses into manageable steps.
    
    Args:
        tasks: List of task descriptions to add to the TODO list
    
    Returns:
        Confirmation message with the created TODO list
    """
    # This is a no-op tool for planning purposes
    # The actual TODO management happens in the agent's state
    todo_list = "\n".join([f"- [ ] {task}" for task in tasks])
    return f"Created TODO list with {len(tasks)} tasks:\n{todo_list}"

@tool
def update_todo(todo_id: int, status: Literal["pending", "in_progress", "completed"], notes: Optional[str] = None) -> str:
    """
    Update the status of a TODO item.
    
    Args:
        todo_id: ID of the TODO item to update
        status: New status ('pending', 'in_progress', or 'completed')
        notes: Optional notes about progress or completion
    
    Returns:
        Confirmation of the update
    """
    return f"Updated TODO #{todo_id} to status: {status}" + (f" with notes: {notes}" if notes else "")

@tool
def list_todos(status_filter: Optional[Literal["pending", "in_progress", "completed"]] = None) -> str:
    """
    List current TODO items.
    
    Args:
        status_filter: Optional filter by status
    
    Returns:
        Formatted list of TODO items
    """
    # This will be implemented in the agent to read from state
    return f"Listing TODOs" + (f" with status: {status_filter}" if status_filter else " (all)")

@tool
def ls(path: str = "/") -> str:
    """
    List files in the virtual file system.
    
    Args:
        path: Directory path (currently only supports root "/")
    
    Returns:
        List of files and their metadata
    """
    # This will be implemented to read from agent state
    return f"Listing files in {path}"

@tool
def write_file(filename: str, content: str) -> str:
    """
    Write content to a file in the virtual file system.
    
    Args:
        filename: Name of the file to write
        content: Content to write to the file
    
    Returns:
        Confirmation message
    """
    return f"Successfully wrote {len(content)} characters to {filename}"

@tool
def read_file(filename: str) -> str:
    """
    Read content from a file in the virtual file system.
    
    Args:
        filename: Name of the file to read
    
    Returns:
        File content
    """
    return f"Reading file: {filename}"

@tool
def edit_file(filename: str, old_content: str, new_content: str) -> str:
    """
    Edit a file by replacing old content with new content.
    
    Args:
        filename: Name of the file to edit
        old_content: Content to find and replace
        new_content: New content to insert
    
    Returns:
        Confirmation message
    """
    return f"Successfully edited {filename}"

@tool
def delete_file(filename: str) -> str:
    """
    Delete a file from the virtual file system.
    
    Args:
        filename: Name of the file to delete
    
    Returns:
        Confirmation message
    """
    return f"Successfully deleted {filename}"

@tool
def create_analysis_report(
    title: str,
    summary: str,
    findings: List[Dict[str, str]],
    recommendations: List[str],
    data_sources: List[str]
) -> str:
    """
    Create a structured analysis report.
    
    Args:
        title: Report title
        summary: Executive summary
        findings: List of key findings with descriptions
        recommendations: List of actionable recommendations
        data_sources: List of FRED series or other data sources used
    
    Returns:
        Formatted report as markdown
    """
    report = f"""# {title}

## Executive Summary
{summary}

## Key Findings
"""
    
    for i, finding in enumerate(findings, 1):
        report += f"\n### {i}. {finding.get('title', 'Finding')}\n{finding.get('description', '')}\n"
    
    report += "\n## Recommendations\n"
    for rec in recommendations:
        report += f"- {rec}\n"
    
    report += "\n## Data Sources\n"
    for source in data_sources:
        report += f"- {source}\n"
    
    report += f"\n---\n*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    
    return report

# Export all planning tools
PLANNING_TOOLS = [
    write_todos,
    update_todo,
    list_todos,
    ls,
    write_file,
    read_file,
    edit_file,
    delete_file,
    create_analysis_report,
]