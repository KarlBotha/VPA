#!/usr/bin/env python3
"""
VPA Advanced LLM Provider Performance Benchmarking Script

This script benchmarks the performance of different LLM providers integrated
in the VPA system, measuring response times, throughput, cost efficiency,
and quality metrics.

Usage:
    python scripts/benchmark_llm_providers.py
    python scripts/benchmark_llm_providers.py --providers openai,anthropic
    python scripts/benchmark_llm_providers.py --iterations 100
    python scripts/benchmark_llm_providers.py --concurrent 10
"""

import asyncio
import json
import logging
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vpa_llm_benchmark.log')
    ]
)
logger = logging.getLogger(__name__)

# Import VPA components
try:
    from src.vpa.core.llm_provider_manager import (
        create_llm_provider_manager,
        LLMProviderConfig,
        LLMProvider,
        LLMModel,
        LLMRequest,
        LLMResponse
    )
    from src.vpa.core.enhanced_llm_integration import (
        create_complete_vpa_system,
        EnhancedLLMRequest,
        EnhancedLLMResponse,
        VPAEnhancedLLMIntegration
    )
    from src.vpa.config.deployment_config import get_config
    
    VPA_IMPORTS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import VPA components: {e}")
    VPA_IMPORTS_AVAILABLE = False


class VPALLMBenchmarker:
    """
    Performance benchmarker for VPA LLM providers.
    """
    
    def __init__(self, providers: Optional[List[str]] = None, iterations: int = 10, concurrent: int = 1):
        """Initialize the benchmarker."""
        self.providers = providers or ["openai", "anthropic", "google", "mock"]
        self.iterations = iterations
        self.concurrent = concurrent
        
        self.results = {
            "benchmark_session": {
                "start_time": datetime.now().isoformat(),
                "benchmark_type": "VPA LLM Provider Performance Benchmark",
                "milestone": "Advanced LLM Provider Expansion",
                "environment": os.getenv("VPA_ENVIRONMENT", "development"),
                "providers": self.providers,
                "iterations": iterations,
                "concurrent": concurrent
            },
            "system_info": {},
            "provider_benchmarks": {},
            "comparison_analysis": {},
            "performance_metrics": {},
            "recommendations": {}
        }
        
        # Benchmark queries with different characteristics
        self.benchmark_queries = [
            {
                "id": "short_factual",
                "query": "What is Python?",
                "expected_tokens": 50,
                "category": "factual"
            },
            {
                "id": "medium_explanation",
                "query": "Explain how machine learning works and its main types.",
                "expected_tokens": 200,
                "category": "explanation"
            },
            {
                "id": "long_comprehensive",
                "query": "Provide a comprehensive overview of artificial intelligence, including its history, current applications, and future prospects.",
                "expected_tokens": 500,
                "category": "comprehensive"
            },
            {
                "id": "technical_detailed",
                "query": "Explain the architecture and working principles of transformer neural networks, including attention mechanisms and their applications in natural language processing.",
                "expected_tokens": 400,
                "category": "technical"
            },
            {
                "id": "creative_generation",
                "query": "Write a creative story about a robot that learns to paint, incorporating themes of artificial intelligence and human creativity.",
                "expected_tokens": 300,
                "category": "creative"
            }
        ]
        
        self.manager = None
        self.llm_integration = None
        self.rag_system = None
        self.vector_db = None
    
    async def setup_benchmark_environment(self) -> bool:
        """Set up the benchmark environment."""
        logger.info("Setting up VPA LLM benchmark environment...")
        
        try:
            # Check VPA imports
            if not VPA_IMPORTS_AVAILABLE:
                logger.error("VPA components not available for benchmarking")
                return False
            
            # Create LLM provider manager
            self.manager = create_llm_provider_manager()
            
            # Create complete VPA system
            self.llm_integration, self.rag_system, self.vector_db = \
                await create_complete_vpa_system()
            
            # Connect providers
            connection_results = await self.manager.connect_all_providers()
            
            # Record system info
            self.results["system_info"] = {
                "python_version": sys.version,
                "vpa_components_available": VPA_IMPORTS_AVAILABLE,
                "providers_connected": len(connection_results),
                "benchmark_queries": len(self.benchmark_queries),
                "system_configuration": {
                    "iterations": self.iterations,
                    "concurrent_requests": self.concurrent,
                    "providers_to_test": self.providers
                }
            }
            
            logger.info("Benchmark environment setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup benchmark environment: {e}")
            self.results["system_info"]["setup_error"] = str(e)
            return False
    
    async def benchmark_provider_performance(self, provider_id: str) -> Dict[str, Any]:
        """Benchmark a specific provider's performance."""
        logger.info(f"Benchmarking provider: {provider_id}")
        
        provider_results = {
            "provider_id": provider_id,
            "benchmark_start": datetime.now().isoformat(),
            "query_results": {},
            "performance_metrics": {},
            "error_analysis": {}
        }
        
        try:
            for query_info in self.benchmark_queries:
                query_id = query_info["id"]
                query_text = query_info["query"]
                
                logger.info(f"Testing query: {query_id}")
                
                query_results = {
                    "query_info": query_info,
                    "iterations": [],
                    "statistics": {},
                    "errors": []
                }
                
                # Run multiple iterations
                for iteration in range(self.iterations):
                    iteration_result = await self.run_single_benchmark_iteration(
                        provider_id, query_text, iteration
                    )
                    
                    if iteration_result.get("success"):
                        query_results["iterations"].append(iteration_result)
                    else:
                        query_results["errors"].append(iteration_result)
                
                # Calculate statistics
                if query_results["iterations"]:
                    query_results["statistics"] = self.calculate_query_statistics(
                        query_results["iterations"]
                    )
                
                provider_results["query_results"][query_id] = query_results
            
            # Calculate overall provider metrics
            provider_results["performance_metrics"] = self.calculate_provider_metrics(
                provider_results["query_results"]
            )
            
            provider_results["benchmark_end"] = datetime.now().isoformat()
            
            self.results["provider_benchmarks"][provider_id] = provider_results
            return provider_results
            
        except Exception as e:
            logger.error(f"Provider benchmark failed for {provider_id}: {e}")
            provider_results["benchmark_error"] = str(e)
            self.results["provider_benchmarks"][provider_id] = provider_results
            return provider_results
    
    async def run_single_benchmark_iteration(self, provider_id: str, query: str, iteration: int) -> Dict[str, Any]:
        """Run a single benchmark iteration."""
        iteration_result = {
            "iteration": iteration,
            "provider_id": provider_id,
            "query": query,
            "success": False,
            "start_time": None,
            "end_time": None,
            "response_time": None,
            "response_length": None,
            "token_count": None,
            "cost_estimate": None,
            "error": None
        }
        
        try:
            # Create request
            request = EnhancedLLMRequest(
                user_query=query,
                user_id=f"benchmark_user_{iteration}",
                provider=provider_id,
                use_rag=False  # Disable RAG for pure provider benchmarking
            )
            
            # Measure response time
            start_time = time.time()
            iteration_result["start_time"] = start_time
            
            # Generate response
            response = await self.llm_integration.generate_enhanced_response(request)
            
            end_time = time.time()
            iteration_result["end_time"] = end_time
            iteration_result["response_time"] = end_time - start_time
            
            # Extract metrics
            iteration_result["success"] = True
            iteration_result["response_length"] = len(response.content)
            
            # Estimate token count (rough approximation)
            iteration_result["token_count"] = len(response.content.split()) * 1.3  # Rough tokens
            
            # Cost estimation (would need actual provider pricing)
            iteration_result["cost_estimate"] = iteration_result["token_count"] * 0.00002  # Rough estimate
            
            return iteration_result
            
        except Exception as e:
            iteration_result["error"] = str(e)
            iteration_result["end_time"] = time.time()
            return iteration_result
    
    def calculate_query_statistics(self, iterations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for a query across iterations."""
        if not iterations:
            return {}
        
        # Extract metrics
        response_times = [it["response_time"] for it in iterations if it["response_time"]]
        response_lengths = [it["response_length"] for it in iterations if it["response_length"]]
        token_counts = [it["token_count"] for it in iterations if it["token_count"]]
        cost_estimates = [it["cost_estimate"] for it in iterations if it["cost_estimate"]]
        
        statistics_result = {
            "successful_iterations": len(iterations),
            "total_iterations": len(iterations),
            "success_rate": 1.0,  # Only successful iterations are included
            "response_time": {},
            "response_length": {},
            "token_count": {},
            "cost_estimate": {}
        }
        
        # Calculate response time statistics
        if response_times:
            statistics_result["response_time"] = {
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "min": min(response_times),
                "max": max(response_times),
                "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "percentile_95": sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0
            }
        
        # Calculate response length statistics
        if response_lengths:
            statistics_result["response_length"] = {
                "mean": statistics.mean(response_lengths),
                "median": statistics.median(response_lengths),
                "min": min(response_lengths),
                "max": max(response_lengths),
                "std_dev": statistics.stdev(response_lengths) if len(response_lengths) > 1 else 0
            }
        
        # Calculate token count statistics
        if token_counts:
            statistics_result["token_count"] = {
                "mean": statistics.mean(token_counts),
                "median": statistics.median(token_counts),
                "min": min(token_counts),
                "max": max(token_counts),
                "std_dev": statistics.stdev(token_counts) if len(token_counts) > 1 else 0
            }
        
        # Calculate cost estimate statistics
        if cost_estimates:
            statistics_result["cost_estimate"] = {
                "mean": statistics.mean(cost_estimates),
                "median": statistics.median(cost_estimates),
                "min": min(cost_estimates),
                "max": max(cost_estimates),
                "total": sum(cost_estimates)
            }
        
        return statistics_result
    
    def calculate_provider_metrics(self, query_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall provider performance metrics."""
        metrics = {
            "overall_performance": {},
            "query_breakdown": {},
            "reliability": {},
            "cost_efficiency": {}
        }
        
        all_response_times = []
        all_token_counts = []
        all_cost_estimates = []
        total_errors = 0
        total_requests = 0
        
        for query_id, query_data in query_results.items():
            if "statistics" in query_data and query_data["statistics"]:
                stats = query_data["statistics"]
                
                # Collect overall metrics
                if "response_time" in stats and "mean" in stats["response_time"]:
                    all_response_times.append(stats["response_time"]["mean"])
                
                if "token_count" in stats and "mean" in stats["token_count"]:
                    all_token_counts.append(stats["token_count"]["mean"])
                
                if "cost_estimate" in stats and "total" in stats["cost_estimate"]:
                    all_cost_estimates.append(stats["cost_estimate"]["total"])
                
                total_requests += stats.get("successful_iterations", 0)
            
            total_errors += len(query_data.get("errors", []))
        
        # Calculate overall performance
        if all_response_times:
            metrics["overall_performance"] = {
                "avg_response_time": statistics.mean(all_response_times),
                "response_time_consistency": 1.0 - (statistics.stdev(all_response_times) / statistics.mean(all_response_times)) if len(all_response_times) > 1 else 1.0,
                "throughput": 1.0 / statistics.mean(all_response_times) if all_response_times else 0
            }
        
        # Calculate reliability metrics
        total_attempts = total_requests + total_errors
        metrics["reliability"] = {
            "success_rate": total_requests / total_attempts if total_attempts > 0 else 0,
            "error_rate": total_errors / total_attempts if total_attempts > 0 else 0,
            "total_requests": total_requests,
            "total_errors": total_errors
        }
        
        # Calculate cost efficiency
        if all_cost_estimates:
            metrics["cost_efficiency"] = {
                "total_cost": sum(all_cost_estimates),
                "avg_cost_per_request": statistics.mean(all_cost_estimates),
                "cost_consistency": 1.0 - (statistics.stdev(all_cost_estimates) / statistics.mean(all_cost_estimates)) if len(all_cost_estimates) > 1 else 1.0
            }
        
        return metrics
    
    async def run_concurrent_benchmark(self, provider_id: str, query: str, concurrent_requests: int) -> Dict[str, Any]:
        """Run concurrent benchmark test."""
        logger.info(f"Running concurrent benchmark for {provider_id} with {concurrent_requests} concurrent requests")
        
        async def single_request():
            request = EnhancedLLMRequest(
                user_query=query,
                user_id=f"concurrent_user_{time.time()}",
                provider=provider_id,
                use_rag=False
            )
            
            start_time = time.time()
            try:
                response = await self.llm_integration.generate_enhanced_response(request)
                return {
                    "success": True,
                    "response_time": time.time() - start_time,
                    "response_length": len(response.content)
                }
            except Exception as e:
                return {
                    "success": False,
                    "response_time": time.time() - start_time,
                    "error": str(e)
                }
        
        # Run concurrent requests
        start_time = time.time()
        tasks = [single_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        concurrent_metrics = {
            "concurrent_requests": concurrent_requests,
            "total_time": total_time,
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(successful_requests) / concurrent_requests,
            "requests_per_second": concurrent_requests / total_time,
            "avg_response_time": statistics.mean([r["response_time"] for r in successful_requests]) if successful_requests else 0
        }
        
        return concurrent_metrics
    
    async def generate_comparison_analysis(self) -> Dict[str, Any]:
        """Generate comparison analysis between providers."""
        logger.info("Generating provider comparison analysis...")
        
        comparison = {
            "provider_ranking": {},
            "performance_comparison": {},
            "cost_comparison": {},
            "reliability_comparison": {}
        }
        
        # Extract provider metrics
        provider_metrics = {}
        for provider_id, provider_data in self.results["provider_benchmarks"].items():
            if "performance_metrics" in provider_data:
                provider_metrics[provider_id] = provider_data["performance_metrics"]
        
        if not provider_metrics:
            return comparison
        
        # Performance comparison
        performance_scores = {}
        for provider_id, metrics in provider_metrics.items():
            overall_perf = metrics.get("overall_performance", {})
            reliability = metrics.get("reliability", {})
            cost_eff = metrics.get("cost_efficiency", {})
            
            # Calculate composite score
            score = 0
            if overall_perf.get("avg_response_time"):
                score += 30 / overall_perf["avg_response_time"]  # Lower is better
            if reliability.get("success_rate"):
                score += 40 * reliability["success_rate"]  # Higher is better
            if cost_eff.get("avg_cost_per_request"):
                score += 30 / cost_eff["avg_cost_per_request"]  # Lower is better
            
            performance_scores[provider_id] = score
        
        # Rank providers
        ranked_providers = sorted(performance_scores.items(), key=lambda x: x[1], reverse=True)
        comparison["provider_ranking"] = {
            "ranking": [{"provider": p[0], "score": p[1]} for p in ranked_providers],
            "best_performer": ranked_providers[0][0] if ranked_providers else None,
            "worst_performer": ranked_providers[-1][0] if ranked_providers else None
        }
        
        # Detailed comparisons
        comparison["performance_comparison"] = {
            provider_id: {
                "avg_response_time": metrics.get("overall_performance", {}).get("avg_response_time", 0),
                "throughput": metrics.get("overall_performance", {}).get("throughput", 0),
                "consistency": metrics.get("overall_performance", {}).get("response_time_consistency", 0)
            }
            for provider_id, metrics in provider_metrics.items()
        }
        
        comparison["reliability_comparison"] = {
            provider_id: {
                "success_rate": metrics.get("reliability", {}).get("success_rate", 0),
                "error_rate": metrics.get("reliability", {}).get("error_rate", 0),
                "total_requests": metrics.get("reliability", {}).get("total_requests", 0)
            }
            for provider_id, metrics in provider_metrics.items()
        }
        
        comparison["cost_comparison"] = {
            provider_id: {
                "avg_cost_per_request": metrics.get("cost_efficiency", {}).get("avg_cost_per_request", 0),
                "total_cost": metrics.get("cost_efficiency", {}).get("total_cost", 0),
                "cost_consistency": metrics.get("cost_efficiency", {}).get("cost_consistency", 0)
            }
            for provider_id, metrics in provider_metrics.items()
        }
        
        self.results["comparison_analysis"] = comparison
        return comparison
    
    def generate_recommendations(self) -> Dict[str, Any]:
        """Generate performance recommendations."""
        logger.info("Generating performance recommendations...")
        
        recommendations = {
            "provider_recommendations": {},
            "optimization_suggestions": [],
            "configuration_recommendations": {},
            "cost_optimization": [],
            "performance_optimization": []
        }
        
        comparison = self.results.get("comparison_analysis", {})
        
        # Provider recommendations
        ranking = comparison.get("provider_ranking", {})
        if ranking.get("best_performer"):
            recommendations["provider_recommendations"]["primary"] = {
                "provider": ranking["best_performer"],
                "reason": "Best overall performance score"
            }
        
        # Performance optimization suggestions
        for provider_id, provider_data in self.results["provider_benchmarks"].items():
            metrics = provider_data.get("performance_metrics", {})
            overall_perf = metrics.get("overall_performance", {})
            
            if overall_perf.get("avg_response_time", 0) > 5.0:
                recommendations["performance_optimization"].append({
                    "provider": provider_id,
                    "issue": "High response time",
                    "suggestion": "Consider using faster models or optimizing request parameters"
                })
            
            if overall_perf.get("response_time_consistency", 1.0) < 0.8:
                recommendations["performance_optimization"].append({
                    "provider": provider_id,
                    "issue": "Inconsistent response times",
                    "suggestion": "Implement caching or load balancing"
                })
        
        # Cost optimization suggestions
        cost_comparison = comparison.get("cost_comparison", {})
        if cost_comparison:
            cheapest_provider = min(cost_comparison.items(), key=lambda x: x[1].get("avg_cost_per_request", float('inf')))
            recommendations["cost_optimization"].append({
                "suggestion": f"Consider using {cheapest_provider[0]} for cost-sensitive workloads",
                "potential_savings": "Up to 50% cost reduction"
            })
        
        # Configuration recommendations
        recommendations["configuration_recommendations"] = {
            "caching": "Enable response caching for frequently asked questions",
            "load_balancing": "Implement load balancing across multiple providers",
            "failover": "Set up automatic failover to backup providers",
            "rate_limiting": "Implement rate limiting to prevent provider overload"
        }
        
        self.results["recommendations"] = recommendations
        return recommendations
    
    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark suite."""
        logger.info("Starting comprehensive VPA LLM provider benchmark...")
        
        # Setup benchmark environment
        setup_success = await self.setup_benchmark_environment()
        if not setup_success:
            logger.error("Failed to setup benchmark environment")
            return self.results
        
        # Benchmark each provider
        for provider_id in self.providers:
            logger.info(f"Benchmarking provider: {provider_id}")
            try:
                await self.benchmark_provider_performance(provider_id)
                logger.info(f"Completed benchmark for provider: {provider_id}")
            except Exception as e:
                logger.error(f"Benchmark failed for provider {provider_id}: {e}")
        
        # Generate comparison analysis
        await self.generate_comparison_analysis()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Save results
        self.save_benchmark_results()
        
        self.results["benchmark_session"]["end_time"] = datetime.now().isoformat()
        logger.info("Comprehensive VPA LLM provider benchmark completed")
        return self.results
    
    def save_benchmark_results(self):
        """Save benchmark results to file."""
        try:
            results_file = "vpa_llm_provider_benchmark_report.json"
            
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            logger.info(f"Benchmark results saved to {results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save benchmark results: {e}")


async def main():
    """Main benchmark execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="VPA LLM Provider Performance Benchmark")
    parser.add_argument("--providers", "-p", type=str, help="Comma-separated list of providers to benchmark")
    parser.add_argument("--iterations", "-i", type=int, default=10, help="Number of iterations per query")
    parser.add_argument("--concurrent", "-c", type=int, default=1, help="Number of concurrent requests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse providers
    providers = args.providers.split(',') if args.providers else None
    
    # Create and run benchmarker
    benchmarker = VPALLMBenchmarker(
        providers=providers,
        iterations=args.iterations,
        concurrent=args.concurrent
    )
    
    print("🚀 VPA LLM Provider Performance Benchmark")
    print("=" * 60)
    print(f"Environment: {os.getenv('VPA_ENVIRONMENT', 'development')}")
    print(f"Providers: {', '.join(benchmarker.providers)}")
    print(f"Iterations: {args.iterations}")
    print(f"Concurrent: {args.concurrent}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Run benchmark
    results = await benchmarker.run_comprehensive_benchmark()
    
    # Print summary
    comparison = results.get("comparison_analysis", {})
    ranking = comparison.get("provider_ranking", {})
    
    print("\n" + "=" * 60)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 60)
    
    if ranking.get("ranking"):
        print("🏆 PROVIDER RANKING:")
        for i, provider_data in enumerate(ranking["ranking"], 1):
            print(f"{i}. {provider_data['provider']} (Score: {provider_data['score']:.2f})")
    
    print("\n📈 PERFORMANCE METRICS:")
    perf_comparison = comparison.get("performance_comparison", {})
    for provider_id, metrics in perf_comparison.items():
        print(f"{provider_id}:")
        print(f"  - Avg Response Time: {metrics.get('avg_response_time', 0):.2f}s")
        print(f"  - Throughput: {metrics.get('throughput', 0):.2f} req/s")
        print(f"  - Consistency: {metrics.get('consistency', 0):.2f}")
    
    print("\n💰 COST ANALYSIS:")
    cost_comparison = comparison.get("cost_comparison", {})
    for provider_id, metrics in cost_comparison.items():
        print(f"{provider_id}:")
        print(f"  - Avg Cost/Request: ${metrics.get('avg_cost_per_request', 0):.4f}")
        print(f"  - Total Cost: ${metrics.get('total_cost', 0):.4f}")
    
    print("\n🔧 RECOMMENDATIONS:")
    recommendations = results.get("recommendations", {})
    for suggestion in recommendations.get("performance_optimization", []):
        print(f"  - {suggestion['provider']}: {suggestion['suggestion']}")
    
    print("\n📁 Results saved to: vpa_llm_provider_benchmark_report.json")
    print("📁 Logs saved to: vpa_llm_benchmark.log")
    
    print("\n✅ Benchmark completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
