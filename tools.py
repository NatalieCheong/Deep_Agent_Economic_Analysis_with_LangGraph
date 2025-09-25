# tools.py
"""
Tools for the Economic Analysis Deep Agent
Includes FRED API tools, data analysis tools, and web search capabilities
"""

import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from langchain.tools import tool
from langchain_community.tools import TavilySearchResults
from config import Config

# Initialize Tavily search if API key is available
tavily_search = None
if Config.TAVILY_API_KEY:
    tavily_search = TavilySearchResults(api_key=Config.TAVILY_API_KEY, max_results=5)

@tool
def fetch_fred_series(series_id: str) -> str:
    """
    Fetch economic time series data from FRED (Federal Reserve Economic Data).
    
    Args:
        series_id: FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL', 'DGS10')
    
    Returns:
        JSON string with series summary and recent data only
    """
    try:
        start_date = "2023-01-01"
        end_date = "2025-12-31"
        
        # Construct API URL
        url = f"{Config.FRED_BASE_URL}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": Config.FRED_API_KEY,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date,
            "limit": 100,
        }
        
        # Fetch data
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Get series info
        info_url = f"{Config.FRED_BASE_URL}/series"
        info_params = {
            "series_id": series_id,
            "api_key": Config.FRED_API_KEY,
            "file_type": "json",
        }
        info_response = requests.get(info_url, params=info_params)
        info_data = info_response.json()
        
        # Filter observations
        observations = data.get("observations", [])
        filtered_observations = []
        for obs in observations:
            if obs.get("value") and obs.get("value") != ".":
                filtered_observations.append({
                    "date": obs["date"],
                    "value": obs["value"]
                })
        
        # Limit to last 24 observations
        if len(filtered_observations) > 24:
            filtered_observations = filtered_observations[-24:]
        
        # Create a summary
        result = {
            "series_id": series_id,
            "title": info_data["seriess"][0]["title"] if "seriess" in info_data else series_id,
            "units": info_data["seriess"][0]["units"] if "seriess" in info_data else "Unknown",
            "frequency": info_data["seriess"][0]["frequency"] if "seriess" in info_data else "Unknown",
            "data_points": len(filtered_observations),
            "latest_value": filtered_observations[-1]["value"] if filtered_observations else None,
            "latest_date": filtered_observations[-1]["date"] if filtered_observations else None,
            "first_value": filtered_observations[0]["value"] if filtered_observations else None,
            "first_date": filtered_observations[0]["date"] if filtered_observations else None,
            "recent_data": filtered_observations[-12:] if len(filtered_observations) > 12 else filtered_observations
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch {series_id}: {str(e)}"})

@tool
def search_fred_series(search_text: str) -> str:
    """
    Search for FRED series by keywords.
    
    Args:
        search_text: Keywords to search for (e.g., 'inflation', 'unemployment rate')
    
    Returns:
        JSON string with matching series information
    """
    try:
        limit = 10
        url = f"{Config.FRED_BASE_URL}/series/search"
        params = {
            "search_text": search_text,
            "api_key": Config.FRED_API_KEY,
            "file_type": "json",
            "limit": limit,
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Format results
        results = []
        for series in data.get("seriess", [])[:limit]:
            results.append({
                "id": series["id"],
                "title": series["title"],
                "units": series["units"],
                "frequency": series["frequency"],
                "popularity": series["popularity"],
                "observation_start": series["observation_start"],
                "observation_end": series["observation_end"],
            })
        
        return json.dumps({
            "search_text": search_text,
            "count": len(results),
            "series": results
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"})

@tool
def calculate_statistics(series_id: str) -> str:
    """
    Calculate statistical measures for a FRED series.
    
    Args:
        series_id: FRED series ID
    
    Returns:
        JSON string with statistical analysis
    """
    try:
        start_date = "2023-01-01"
        end_date = "2025-12-31"
        
        # Construct API URL
        url = f"{Config.FRED_BASE_URL}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": Config.FRED_API_KEY,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date,
            "limit": 100,
        }
        
        # Fetch data
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Get series info
        info_url = f"{Config.FRED_BASE_URL}/series"
        info_params = {
            "series_id": series_id,
            "api_key": Config.FRED_API_KEY,
            "file_type": "json",
        }
        info_response = requests.get(info_url, params=info_params)
        info_data = info_response.json()
        
        # Filter observations
        observations = data.get("observations", [])
        values = []
        dates = []
        
        for obs in observations:
            if obs.get("value") and obs.get("value") != ".":
                try:
                    values.append(float(obs["value"]))
                    dates.append(obs["date"])
                except ValueError:
                    continue
        
        if not values:
            return json.dumps({"error": "No valid data points found"})
        
        # Limit to recent data
        if len(values) > 50:
            values = values[-50:]
            dates = dates[-50:]
        
        # Calculate statistics
        stats = {
            "series_id": series_id,
            "title": info_data["seriess"][0]["title"] if "seriess" in info_data else series_id,
            "period": f"{dates[0]} to {dates[-1]}",
            "count": len(values),
            "mean": round(float(np.mean(values)), 2),
            "median": round(float(np.median(values)), 2),
            "std_dev": round(float(np.std(values)), 2),
            "min": round(float(np.min(values)), 2),
            "max": round(float(np.max(values)), 2),
            "latest_value": round(values[-1], 2),
            "latest_date": dates[-1],
        }
        
        # Calculate growth rates
        if len(values) > 1:
            stats["change_from_start"] = round(values[-1] - values[0], 2)
            if values[0] != 0:
                stats["percent_change_from_start"] = round(((values[-1] - values[0]) / values[0]) * 100, 2)
            
            # Year-over-year change if we have enough data
            if len(values) > 12:
                stats["yoy_change"] = round(values[-1] - values[-13], 2)
                if values[-13] != 0:
                    stats["yoy_percent_change"] = round(((values[-1] - values[-13]) / values[-13]) * 100, 2)
        
        return json.dumps(stats, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Failed to calculate statistics: {str(e)}"})

@tool
def compare_series(series_ids: List[str]) -> str:
    """
    Compare multiple FRED series side by side.
    
    Args:
        series_ids: List of FRED series IDs to compare
    
    Returns:
        JSON string with comparative analysis
    """
    try:
        comparison = {
            "series": [],
            "period": "2023-01-01 to 2025-12-31",
        }
        
        # Limit to 5 series max
        for series_id in series_ids[:5]:
            # Get statistics for each series
            stats_json = calculate_statistics.invoke({"series_id": series_id})
            stats = json.loads(stats_json)
            
            if "error" not in stats:
                comparison["series"].append({
                    "id": series_id,
                    "title": stats.get("title", series_id)[:50],
                    "latest_value": stats.get("latest_value"),
                    "mean": stats.get("mean"),
                    "std_dev": stats.get("std_dev"),
                    "percent_change": stats.get("percent_change_from_start"),
                })
        
        return json.dumps(comparison, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Failed to compare series: {str(e)}"})

@tool
def get_economic_indicators() -> str:
    """
    Get key economic indicators dashboard with latest values.
    
    Returns:
        JSON string with major economic indicators
    """
    key_indicators = {
        "GDP": "Gross Domestic Product",
        "UNRATE": "Unemployment Rate",
        "CPIAUCSL": "Consumer Price Index",
        "DGS10": "10-Year Treasury Rate",
        "DEXUSEU": "US/Euro Exchange Rate",
        "DFF": "Federal Funds Rate",
        "HOUST": "Housing Starts",
        "INDPRO": "Industrial Production Index",
        "PAYEMS": "Nonfarm Payrolls",
        "UMCSENT": "Consumer Sentiment",
    }
    
    dashboard = {
        "timestamp": datetime.now().isoformat(),
        "indicators": []
    }
    
    for series_id, name in key_indicators.items():
        try:
            # Fetch data directly
            url = f"{Config.FRED_BASE_URL}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": Config.FRED_API_KEY,
                "file_type": "json",
                "observation_start": "2024-01-01",
                "limit": 1,
                "sort_order": "desc"
            }
            
            response = requests.get(url, params=params)
            
            # Get series info for units
            info_url = f"{Config.FRED_BASE_URL}/series"
            info_params = {
                "series_id": series_id,
                "api_key": Config.FRED_API_KEY,
                "file_type": "json",
            }
            info_response = requests.get(info_url, params=info_params)
            info_data = info_response.json()
            
            if response.status_code == 200:
                data = response.json()
                if data.get("observations"):
                    latest_obs = data["observations"][0]
                    dashboard["indicators"].append({
                        "id": series_id,
                        "name": name,
                        "value": latest_obs.get("value"),
                        "date": latest_obs.get("date"),
                        "units": info_data["seriess"][0]["units"] if "seriess" in info_data else "Unknown",
                    })
        except:
            continue
    
    return json.dumps(dashboard, indent=2)

@tool
def web_search(query: str) -> str:
    """
    Search the web for economic news and analysis.
    
    Args:
        query: Search query
    
    Returns:
        Search results as string
    """
    if not tavily_search:
        return json.dumps({"error": "Web search not available (Tavily API key not configured)"})
    
    try:
        results = tavily_search.invoke(query)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Web search failed: {str(e)}"})

# Export all tools
ECONOMIC_TOOLS = [
    fetch_fred_series,
    search_fred_series,
    calculate_statistics,
    compare_series,
    get_economic_indicators,
    web_search,
]