# config.py
"""
Configuration file for Economic Analysis Deep Agent System
Sets up environment variables, API keys, and system settings
"""

import os
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Economic Analysis System"""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    FRED_API_KEY: str = os.getenv("FRED_API_KEY", "")
    LANGSMITH_API_KEY: Optional[str] = os.getenv("LANGSMITH_API_KEY")
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    
    # LangSmith Configuration
    LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "economic-analysis-deep-agent")
    
    # Model Configuration
    MODEL_NAME: str = "gpt-4o-mini"
    MODEL_TEMPERATURE: float = 0.0
    MAX_ITERATIONS: int = 50
    
    # FRED API Configuration
    FRED_BASE_URL: str = "https://api.stlouisfed.org/fred"
    
    # File System Settings
    WORKSPACE_DIR: str = "agent_workspace"
    MAX_FILE_SIZE: int = 100000  # Maximum file size in bytes
    
    # Agent Settings
    MAX_RETRIES: int = 3
    TIMEOUT: int = 300  # Timeout in seconds
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        if not cls.FRED_API_KEY:
            raise ValueError("FRED_API_KEY is required")
        
        # Set up LangSmith if configured
        if cls.LANGSMITH_TRACING and cls.LANGSMITH_API_KEY:
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_API_KEY"] = cls.LANGSMITH_API_KEY
            os.environ["LANGSMITH_PROJECT"] = cls.LANGSMITH_PROJECT
            print(f"✅ LangSmith tracing enabled for project: {cls.LANGSMITH_PROJECT}")
        
        return True
    
    @classmethod
    def get_llm(cls, **kwargs) -> ChatOpenAI:
        """Get configured LLM instance"""
        default_kwargs = {
            "model": cls.MODEL_NAME,
            "temperature": cls.MODEL_TEMPERATURE,
            "api_key": cls.OPENAI_API_KEY,
        }
        default_kwargs.update(kwargs)
        return ChatOpenAI(**default_kwargs)

# Validate configuration on import
Config.validate()