# main.py
"""
Main entry point for the Economic Analysis Deep Agent System
Run this file to start interactive analysis or execute specific queries
"""

import asyncio
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from config import Config
from agent_graph import economic_agent

class EconomicAnalysisSystem:
    """Main system orchestrator for economic analysis"""
    
    def __init__(self):
        self.agent = economic_agent
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def run_analysis(self, query: str) -> Dict[str, Any]:
        """
        Run synchronous analysis
        
        Args:
            query: Analysis request
        
        Returns:
            Analysis results
        """
        print(f"\n🔍 Starting analysis: {query}")
        print(f"📊 Session ID: {self.session_id}")
        print("-" * 50)
        
        try:
            # Run the analysis
            results = self.agent.analyze_sync(query, self.session_id)
            
            # Display results
            self._display_results(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def run_analysis_async(self, query: str) -> Dict[str, Any]:
        """
        Run asynchronous analysis with progress updates
        
        Args:
            query: Analysis request
        
        Returns:
            Analysis results
        """
        print(f"\n🔍 Starting async analysis: {query}")
        print(f"📊 Session ID: {self.session_id}")
        print("-" * 50)
        
        try:
            # Run the analysis
            results = await self.agent.analyze(query, self.session_id)
            
            # Display results
            self._display_results(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _display_results(self, results: Dict[str, Any]):
        """Display analysis results in a formatted way"""
        if results.get("success"):
            print("\n✅ Analysis Complete!")
            print("=" * 50)
            
            # Display response
            if results.get("response"):
                print("\n📝 Summary:")
                print(results["response"])
            
            # Display completed tasks
            if results.get("completed_tasks"):
                print("\n✔️ Completed Tasks:")
                for task in results["completed_tasks"]:
                    print(f"  - {task['task']}")
            
            # Display data sources
            if results.get("data_sources"):
                print("\n📊 Data Sources Used:")
                for source in results["data_sources"]:
                    print(f"  - {source}")
            
            # Display files created
            if results.get("files_created"):
                print("\n📁 Files Created:")
                for filename in results["files_created"]:
                    print(f"  - {filename}")
            
            # Display report if available
            if results.get("report"):
                print("\n📄 Report Generated:")
                print("-" * 40)
                print(results["report"])
                print("-" * 40)
            
            print(f"\n🔄 Total iterations: {results.get('total_iterations', 0)}")
        else:
            print("\n❌ Analysis failed")
            if results.get("error"):
                print(f"Error: {results['error']}")

def interactive_mode():
    """Run the system in interactive mode"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     Economic Analysis Deep Agent System                   ║
    ║     Powered by LangChain, LangGraph & FRED                ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    print("Available analysis types:")
    print("1. Economic Indicators Analysis")
    print("2. Market Analysis")
    print("3. Comparative Analysis")
    print("4. Economic Forecast")
    print("5. Custom Query")
    print("\nType 'exit' to quit\n")
    
    system = EconomicAnalysisSystem()
    
    while True:
        try:
            user_input = input("\n💬 Enter your analysis request: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Run the analysis
            results = system.run_analysis(user_input)
            
            # Ask if user wants to continue with same session or start new
            continue_choice = input("\n🔄 Continue with same session (y) or new session (n)? [y/n]: ")
            if continue_choice.lower() == 'n':
                system = EconomicAnalysisSystem()  # Create new system with new session
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

def batch_mode(queries: List[str]):
    """Run multiple analyses in batch mode"""
    system = EconomicAnalysisSystem()
    results = []
    
    print(f"\n📦 Running {len(queries)} analyses in batch mode...")
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Processing: {query[:50]}...")
        result = system.run_analysis(query)
        results.append({
            "query": query,
            "result": result
        })
    
    # Save results to file
    output_file = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Batch processing complete! Results saved to {output_file}")
    return results

def example_analyses():
    """Run example analyses to demonstrate capabilities"""
    examples = [
        "Analyze current inflation trends using CPI data from the last 2 years",
        "Compare unemployment rates across different economic cycles",
        "Generate a 6-month economic forecast based on leading indicators",
        "Analyze the relationship between interest rates and stock market performance",
        "Create a comprehensive report on current economic conditions",
    ]
    
    print("\n🎯 Running example analyses...")
    system = EconomicAnalysisSystem()
    
    for example in examples:
        print(f"\n{'='*60}")
        print(f"Example: {example}")
        print('='*60)
        
        results = system.run_analysis(example)
        
        input("\n[Press Enter for next example...]")

# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Economic Analysis Deep Agent System')
    parser.add_argument('--mode', choices=['interactive', 'batch', 'example', 'single'],
                       default='interactive', help='Execution mode')
    parser.add_argument('--query', type=str, help='Single query to analyze')
    parser.add_argument('--file', type=str, help='File with batch queries (one per line)')
    
    args = parser.parse_args()
    
    try:
        # Validate configuration
        Config.validate()
        
        if args.mode == 'interactive':
            interactive_mode()
        elif args.mode == 'example':
            example_analyses()
        elif args.mode == 'single' and args.query:
            system = EconomicAnalysisSystem()
            system.run_analysis(args.query)
        elif args.mode == 'batch' and args.file:
            with open(args.file, 'r') as f:
                queries = [line.strip() for line in f if line.strip()]
            batch_mode(queries)
        else:
            print("❌ Invalid arguments. Use --help for usage information")
            
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)