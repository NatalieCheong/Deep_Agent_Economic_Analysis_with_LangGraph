# Economic Analysis Deep Agent System

A sophisticated AI-powered economic analysis platform that leverages advanced language models and real-time economic data to provide comprehensive economic insights, forecasting, and market analysis using Deep Agents with LangGraph.

## 🌟 Features

- **Real-time Economic Data**: Direct integration with FRED (Federal Reserve Economic Data) API
- **AI-Powered Analysis**: Advanced language models for intelligent economic interpretation
- **Multiple Analysis Types**: 
  - Economic Indicators Analysis
  - Market Analysis
  - Comparative Analysis
  - Economic Forecasting
  - Custom Query Analysis
- **Statistical Analysis**: Comprehensive statistical measures and trend analysis
- **Interactive Workflow**: LangGraph-powered agent orchestration for complex analysis tasks
- **Data Visualization**: Enhanced understanding through trend analysis and correlations

## 🚀 Quick Start

### Prerequisites

- Python 3.11 
- FRED API key (free registration at [FRED API](https://fred.stlouisfed.org/docs/api/api_key.html))
- OpenAI API key

### Installation

1. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   FRED_API_KEY=your_fred_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here  # Optional for web search
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## 📊 Usage

### Available Analysis Types

1. **Economic Indicators Analysis** - Analyze key economic indicators like GDP, unemployment, inflation
2. **Market Analysis** - Comprehensive market trend analysis
3. **Comparative Analysis** - Side-by-side comparison of multiple economic series
4. **Economic Forecast** - AI-powered economic forecasting and predictions
5. **Custom Query** - Ask specific economic questions and get detailed analysis

### Example Usage

```bash
💬 Enter your analysis request: 4  # Economic Forecast
```

The system will automatically:
- Identify relevant economic indicators
- Fetch real-time data from FRED
- Perform statistical analysis
- Generate comprehensive reports
- Provide actionable insights

## 🏗️ Architecture

### Core Components

- **`main.py`** - Application entry point and user interface
- **`agent_graph.py`** - LangGraph workflow orchestration
- **`state.py`** - State management and data structures
- **`tools.py`** - FRED API integration and analysis tools
- **`planning_tools.py`** - Task planning and management utilities
- **`config.py`** - Configuration and API key management

## 📈 Data Sources

- **FRED (Federal Reserve Economic Data)**: Primary economic data source
- **Real-time Indicators**: GDP, unemployment, inflation, interest rates
- **Market Data**: Treasury rates, exchange rates, housing data
- **Employment Data**: Nonfarm payrolls, labor statistics
- **Consumer Data**: Sentiment indices, price indices

## 🔧 Configuration

### API Keys Required

1. **OpenAI API Key**: For language model access
2. **FRED API Key**: For economic data access (free)
3. **Tavily API Key**: For web search capabilities (optional)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. The economic analysis and forecasts provided are not financial advice and should not be used as the sole basis for investment or economic decisions. Users should consult with qualified financial advisors and conduct their own research before making any financial decisions.

The accuracy of economic forecasts and analysis cannot be guaranteed, and past performance does not indicate future results. The developers and contributors are not responsible for any financial losses or decisions made based on this software.

## 🙏 Acknowledgements

This project is built using several open-source libraries and services:

- **OpenAI** - For providing advanced language models and AI capabilities
- **LangChain** - For the comprehensive LLM application framework
- **LangGraph** - For multi-agent workflow orchestration and state management
- **FRED (Federal Reserve Economic Data)** - For providing free access to economic time series data
- **Pandas & NumPy** - For data processing and statistical analysis
- **Python Community** - For the extensive ecosystem of data science libraries

Special thanks to the Federal Reserve Bank of St. Louis for maintaining the FRED database and providing free access to economic data.

---

**Economic Analysis Deep Agent System** 
