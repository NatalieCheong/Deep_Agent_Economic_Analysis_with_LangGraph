# sub_agents.py
"""
Specialized sub-agents for focused economic analysis tasks
Each sub-agent handles specific aspects of economic analysis
"""

from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from config import Config
from state import EconomicAgentState
from prompts import (
    DATA_RETRIEVAL_PROMPT,
    STATISTICAL_ANALYSIS_PROMPT,
    REPORT_GENERATION_PROMPT,
    INDICATOR_ANALYSIS_TEMPLATE,
    COMPARISON_ANALYSIS_TEMPLATE,
    FORECAST_ANALYSIS_TEMPLATE
)
from tools import ECONOMIC_TOOLS

class DataRetrievalAgent:
    """Sub-agent specialized in efficient data retrieval from FRED"""
    
    def __init__(self):
        self.llm = Config.get_llm(temperature=0.0)
        self.tools = [t for t in ECONOMIC_TOOLS if "fred" in t.name or "search" in t.name]
        self.prompt = DATA_RETRIEVAL_PROMPT
    
    def run(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute data retrieval task
        
        Args:
            request: What data to retrieve
            context: Additional context (existing data, constraints, etc.)
        
        Returns:
            Retrieved data and metadata
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompt),
            ("system", f"Context: {context}" if context else ""),
            ("human", request)
        ])
        
        llm_with_tools = self.llm.bind_tools(self.tools)
        
        results = {
            "data": {},
            "series_retrieved": [],
            "errors": []
        }
        
        # Execute retrieval with up to 5 iterations
        messages = [prompt.format_messages()[0]]
        for i in range(5):
            response = llm_with_tools.invoke(messages)
            messages.append(response)
            
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    # Execute tool
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    
                    for tool in self.tools:
                        if tool.name == tool_name:
                            try:
                                result = tool.invoke(tool_args)
                                if "fetch_fred_series" in tool_name:
                                    series_id = tool_args.get("series_id")
                                    results["data"][series_id] = result
                                    results["series_retrieved"].append(series_id)
                            except Exception as e:
                                results["errors"].append(f"Error with {tool_name}: {str(e)}")
                            break
            else:
                # No more tool calls, extraction complete
                break
        
        results["message"] = response.content if hasattr(response, 'content') else ""
        return results

class StatisticalAnalysisAgent:
    """Sub-agent specialized in statistical analysis of economic data"""
    
    def __init__(self):
        self.llm = Config.get_llm(temperature=0.0)
        self.tools = [t for t in ECONOMIC_TOOLS if "calculate" in t.name or "compare" in t.name]
        self.prompt = STATISTICAL_ANALYSIS_PROMPT
    
    def run(self, data: Dict[str, Any], analysis_type: str = "general") -> Dict[str, Any]:
        """
        Perform statistical analysis on economic data
        
        Args:
            data: Data to analyze (FRED series data)
            analysis_type: Type of analysis ('trend', 'correlation', 'forecast', etc.)
        
        Returns:
            Statistical analysis results
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompt),
            ("system", f"Analysis type: {analysis_type}"),
            ("system", f"Available data: {list(data.keys())}"),
            ("human", f"Perform {analysis_type} analysis on the provided economic data.")
        ])
        
        llm_with_tools = self.llm.bind_tools(self.tools)
        
        results = {
            "statistics": {},
            "insights": [],
            "visualizations": []
        }
        
        # Execute analysis
        response = llm_with_tools.invoke(prompt.format_messages())
        
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                for tool in self.tools:
                    if tool.name == tool_name:
                        try:
                            result = tool.invoke(tool_args)
                            results["statistics"][tool_name] = result
                        except Exception as e:
                            results["errors"] = results.get("errors", [])
                            results["errors"].append(f"Error in {tool_name}: {str(e)}")
                        break
        
        # Extract insights from response
        results["summary"] = response.content if hasattr(response, 'content') else ""
        
        return results

class MarketAnalysisAgent:
    """Sub-agent specialized in market and sector analysis"""
    
    def __init__(self):
        self.llm = Config.get_llm(temperature=0.1)
        self.tools = ECONOMIC_TOOLS
        self.indicators = {
            "equity_markets": ["SP500", "DJIA", "NASDAQCOM"],
            "bond_markets": ["DGS10", "DGS2", "DGS30", "T10Y2Y"],
            "commodities": ["DCOILWTICO", "GOLDAMGBD228NLBM"],
            "currencies": ["DEXUSEU", "DEXJPUS", "DEXCHUS"],
            "volatility": ["VIXCLS"],
        }
    
    def run(self, market_sector: str, time_period: str = "1Y") -> Dict[str, Any]:
        """
        Analyze specific market sector
        
        Args:
            market_sector: Sector to analyze ('equity', 'bonds', 'commodities', 'fx', 'all')
            time_period: Time period for analysis
        
        Returns:
            Market analysis results
        """
        # Select relevant indicators
        if market_sector == "all":
            series_to_analyze = []
            for indicators in self.indicators.values():
                series_to_analyze.extend(indicators)
        else:
            series_to_analyze = self.indicators.get(f"{market_sector}_markets", [])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a market analysis expert. Analyze market conditions and trends."),
            ("system", f"Focus on {market_sector} markets"),
            ("system", f"Analyze these series: {series_to_analyze}"),
            ("human", f"Provide comprehensive {market_sector} market analysis for {time_period}")
        ])
        
        llm_with_tools = self.llm.bind_tools(self.tools)
        
        results = {
            "sector": market_sector,
            "period": time_period,
            "indicators_analyzed": series_to_analyze,
            "market_conditions": {},
            "trends": [],
            "risks": [],
            "opportunities": []
        }
        
        # Execute market analysis
        response = llm_with_tools.invoke(prompt.format_messages())
        
        # Process response and tool calls
        if response.tool_calls:
            for tool_call in response.tool_calls:
                # Execute tools and collect results
                pass  # Implementation similar to above
        
        results["analysis"] = response.content if hasattr(response, 'content') else ""
        
        return results

class ForecastingAgent:
    """Sub-agent specialized in economic forecasting"""
    
    def __init__(self):
        self.llm = Config.get_llm(temperature=0.2)
        self.tools = ECONOMIC_TOOLS
        self.prompt = FORECAST_ANALYSIS_TEMPLATE
        
        # Leading indicators for forecasting
        self.leading_indicators = [
            "AHETPI",  # Average Hourly Earnings
            "ICSA",    # Initial Claims
            "PERMIT",  # Building Permits
            "UMCSENT", # Consumer Sentiment
            "T10Y2Y",  # Yield Curve
            "NEWORDER", # New Orders
        ]
    
    def run(self, target: str, horizon: str = "3M") -> Dict[str, Any]:
        """
        Generate economic forecast
        
        Args:
            target: What to forecast ('gdp', 'inflation', 'unemployment', 'general')
            horizon: Forecast horizon ('1M', '3M', '6M', '1Y')
        
        Returns:
            Forecast results with scenarios
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompt),
            ("system", f"Forecast target: {target}"),
            ("system", f"Forecast horizon: {horizon}"),
            ("system", f"Use leading indicators: {self.leading_indicators}"),
            ("human", f"Generate {horizon} forecast for {target}")
        ])
        
        llm_with_tools = self.llm.bind_tools(self.tools)
        
        results = {
            "target": target,
            "horizon": horizon,
            "baseline_forecast": {},
            "optimistic_scenario": {},
            "pessimistic_scenario": {},
            "confidence_level": "medium",
            "key_assumptions": [],
            "risk_factors": []
        }
        
        # Execute forecasting analysis
        response = llm_with_tools.invoke(prompt.format_messages())
        
        # Process response
        results["forecast_narrative"] = response.content if hasattr(response, 'content') else ""
        
        return results

class ReportGenerationAgent:
    """Sub-agent specialized in creating professional reports"""
    
    def __init__(self):
        self.llm = Config.get_llm(temperature=0.3)
        self.prompt = REPORT_GENERATION_PROMPT
    
    def run(self, analysis_results: Dict[str, Any], report_type: str = "standard") -> str:
        """
        Generate professional economic report
        
        Args:
            analysis_results: Results from various analyses
            report_type: Type of report ('executive', 'technical', 'standard')
        
        Returns:
            Formatted report in markdown
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompt),
            ("system", f"Report type: {report_type}"),
            ("human", f"Generate {report_type} report from analysis results: {analysis_results}")
        ])
        
        response = self.llm.invoke(prompt.format_messages())
        
        return response.content

# Factory function to create sub-agents
def create_sub_agent(agent_type: str) -> Any:
    """
    Create a specialized sub-agent
    
    Args:
        agent_type: Type of agent ('data', 'stats', 'market', 'forecast', 'report')
    
    Returns:
        Initialized sub-agent
    """
    agents = {
        "data": DataRetrievalAgent,
        "stats": StatisticalAnalysisAgent,
        "market": MarketAnalysisAgent,
        "forecast": ForecastingAgent,
        "report": ReportGenerationAgent,
    }
    
    agent_class = agents.get(agent_type)
    if agent_class:
        return agent_class()
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

# Define sub-agent configurations for main agent
SUB_AGENT_CONFIGS = [
    {
        "name": "data_specialist",
        "description": "Specialized in efficient data retrieval from FRED and other sources",
        "agent": DataRetrievalAgent()
    },
    {
        "name": "statistician",
        "description": "Expert in statistical analysis and quantitative methods",
        "agent": StatisticalAnalysisAgent()
    },
    {
        "name": "market_analyst",
        "description": "Specialized in market analysis and sector trends",
        "agent": MarketAnalysisAgent()
    },
    {
        "name": "forecaster",
        "description": "Expert in economic forecasting and scenario analysis",
        "agent": ForecastingAgent()
    },
    {
        "name": "report_writer",
        "description": "Creates professional economic reports and presentations",
        "agent": ReportGenerationAgent()
    }
]