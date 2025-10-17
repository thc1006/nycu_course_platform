"""
API Performance Benchmark Tool.

Benchmarks the NYCU Course Platform API for:
- Search query performance
- Filter operation speed
- Pagination efficiency
- Concurrent request handling
- Cache effectiveness

Run this to validate that the API can handle 70,239+ courses efficiently.
"""

import asyncio
import json
import logging
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import httpx

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class APIBenchmark:
    """API performance benchmarking tool."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize benchmark tool.

        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url
        self.results = []

    async def check_health(self) -> bool:
        """
        Check if API is healthy and responsive.

        Returns:
            bool: True if API is healthy
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def benchmark_endpoint(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        iterations: int = 10,
    ) -> Dict[str, Any]:
        """
        Benchmark a single endpoint.

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            data: Request data for POST requests
            iterations: Number of times to run the test

        Returns:
            Dictionary with benchmark results
        """
        logger.info(f"Benchmarking {method} {endpoint} ({iterations} iterations)")

        durations = []
        status_codes = []
        errors = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(iterations):
                try:
                    start = time.time()

                    if method == "GET":
                        response = await client.get(f"{self.base_url}{endpoint}")
                    elif method == "POST":
                        response = await client.post(
                            f"{self.base_url}{endpoint}",
                            json=data
                        )
                    else:
                        raise ValueError(f"Unsupported method: {method}")

                    duration = (time.time() - start) * 1000  # Convert to ms
                    durations.append(duration)
                    status_codes.append(response.status_code)

                    if response.status_code >= 400:
                        logger.warning(
                            f"Request {i+1} failed with status {response.status_code}"
                        )
                        errors += 1

                except Exception as e:
                    logger.error(f"Request {i+1} failed: {e}")
                    errors += 1

                # Small delay between requests
                await asyncio.sleep(0.1)

        # Calculate statistics
        if durations:
            result = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "errors": errors,
                "success_rate": (iterations - errors) / iterations * 100,
                "min_ms": min(durations),
                "max_ms": max(durations),
                "mean_ms": statistics.mean(durations),
                "median_ms": statistics.median(durations),
                "stdev_ms": statistics.stdev(durations) if len(durations) > 1 else 0,
                "p95_ms": sorted(durations)[int(len(durations) * 0.95)] if durations else 0,
                "p99_ms": sorted(durations)[int(len(durations) * 0.99)] if durations else 0,
            }
        else:
            result = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "errors": errors,
                "success_rate": 0,
            }

        self.results.append(result)
        return result

    async def benchmark_search_queries(self):
        """Benchmark various search query patterns."""
        logger.info("\n" + "=" * 70)
        logger.info("Benchmarking Search Queries")
        logger.info("=" * 70)

        # Test cases with different complexities
        test_cases = [
            {
                "name": "Simple text search",
                "data": {"query": "computer", "limit": 50}
            },
            {
                "name": "Department filter",
                "data": {"dept": ["CS"], "limit": 50}
            },
            {
                "name": "Credits range filter",
                "data": {"credits_min": 3, "credits_max": 4, "limit": 50}
            },
            {
                "name": "Multiple filters combined",
                "data": {
                    "query": "science",
                    "dept": ["CS", "ECE"],
                    "credits_min": 3,
                    "limit": 50
                }
            },
            {
                "name": "Semester filter",
                "data": {"acy": [113, 114], "limit": 100}
            },
            {
                "name": "Teacher search",
                "data": {"teacher": "Wang", "limit": 50}
            },
            {
                "name": "Large result set",
                "data": {"dept": ["CS"], "limit": 500}
            },
            {
                "name": "Pagination test (page 1)",
                "data": {"limit": 50, "offset": 0}
            },
            {
                "name": "Pagination test (page 10)",
                "data": {"limit": 50, "offset": 450}
            },
        ]

        results = []
        for test_case in test_cases:
            logger.info(f"\nTest: {test_case['name']}")
            result = await self.benchmark_endpoint(
                method="POST",
                endpoint="/api/courses/search",
                data=test_case["data"],
                iterations=10
            )
            result["test_name"] = test_case["name"]
            results.append(result)

            logger.info(
                f"  Mean: {result.get('mean_ms', 0):.2f}ms, "
                f"P95: {result.get('p95_ms', 0):.2f}ms, "
                f"Success: {result.get('success_rate', 0):.1f}%"
            )

        return results

    async def benchmark_legacy_endpoints(self):
        """Benchmark existing course listing endpoints."""
        logger.info("\n" + "=" * 70)
        logger.info("Benchmarking Legacy Endpoints")
        logger.info("=" * 70)

        endpoints = [
            ("GET", "/api/semesters/"),
            ("GET", "/api/courses/?limit=50"),
            ("GET", "/api/courses/?acy=113&sem=1&limit=100"),
            ("GET", "/api/courses/?dept=CS&limit=50"),
        ]

        results = []
        for method, endpoint in endpoints:
            logger.info(f"\nEndpoint: {endpoint}")
            result = await self.benchmark_endpoint(
                method=method,
                endpoint=endpoint,
                iterations=10
            )
            results.append(result)

            logger.info(
                f"  Mean: {result.get('mean_ms', 0):.2f}ms, "
                f"P95: {result.get('p95_ms', 0):.2f}ms"
            )

        return results

    async def benchmark_concurrent_requests(self, concurrency: int = 10):
        """
        Test concurrent request handling.

        Args:
            concurrency: Number of concurrent requests

        Returns:
            Benchmark results
        """
        logger.info("\n" + "=" * 70)
        logger.info(f"Benchmarking Concurrent Requests ({concurrency} concurrent)")
        logger.info("=" * 70)

        async def make_request():
            async with httpx.AsyncClient(timeout=30.0) as client:
                start = time.time()
                response = await client.post(
                    f"{self.base_url}/api/courses/search",
                    json={"query": "computer", "limit": 50}
                )
                duration = (time.time() - start) * 1000
                return duration, response.status_code

        start_time = time.time()

        # Create concurrent tasks
        tasks = [make_request() for _ in range(concurrency)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_time = (time.time() - start_time) * 1000

        # Process results
        durations = []
        successes = 0
        for result in results:
            if isinstance(result, tuple):
                duration, status_code = result
                durations.append(duration)
                if status_code == 200:
                    successes += 1

        if durations:
            benchmark_result = {
                "test": "concurrent_requests",
                "concurrency": concurrency,
                "total_time_ms": total_time,
                "success_rate": (successes / concurrency) * 100,
                "requests_per_second": concurrency / (total_time / 1000),
                "mean_ms": statistics.mean(durations),
                "median_ms": statistics.median(durations),
                "max_ms": max(durations),
            }

            logger.info(f"Total time: {total_time:.2f}ms")
            logger.info(f"Success rate: {benchmark_result['success_rate']:.1f}%")
            logger.info(f"Requests/sec: {benchmark_result['requests_per_second']:.2f}")
            logger.info(f"Mean latency: {benchmark_result['mean_ms']:.2f}ms")

            return benchmark_result

        return None

    async def benchmark_cache_effectiveness(self):
        """Test cache effectiveness by making repeated requests."""
        logger.info("\n" + "=" * 70)
        logger.info("Benchmarking Cache Effectiveness")
        logger.info("=" * 70)

        test_data = {"query": "algorithms", "dept": ["CS"], "limit": 50}

        # First request (cold cache)
        logger.info("Cold cache request...")
        result1 = await self.benchmark_endpoint(
            method="POST",
            endpoint="/api/courses/search",
            data=test_data,
            iterations=1
        )
        cold_time = result1.get("mean_ms", 0)

        # Wait a bit
        await asyncio.sleep(0.5)

        # Subsequent requests (warm cache)
        logger.info("Warm cache requests...")
        result2 = await self.benchmark_endpoint(
            method="POST",
            endpoint="/api/courses/search",
            data=test_data,
            iterations=5
        )
        warm_time = result2.get("mean_ms", 0)

        speedup = cold_time / warm_time if warm_time > 0 else 0

        cache_result = {
            "test": "cache_effectiveness",
            "cold_cache_ms": cold_time,
            "warm_cache_ms": warm_time,
            "speedup_factor": speedup,
            "improvement_pct": ((cold_time - warm_time) / cold_time * 100) if cold_time > 0 else 0
        }

        logger.info(f"Cold cache: {cold_time:.2f}ms")
        logger.info(f"Warm cache: {warm_time:.2f}ms")
        logger.info(f"Speedup: {speedup:.2f}x")

        return cache_result

    def generate_report(self):
        """Generate a comprehensive benchmark report."""
        logger.info("\n" + "=" * 70)
        logger.info("BENCHMARK SUMMARY")
        logger.info("=" * 70)

        if not self.results:
            logger.info("No benchmark results available")
            return

        # Overall statistics
        all_means = [r.get("mean_ms", 0) for r in self.results if "mean_ms" in r]
        all_success_rates = [r.get("success_rate", 0) for r in self.results if "success_rate" in r]

        logger.info(f"\nTotal tests run: {len(self.results)}")
        if all_means:
            logger.info(f"Average response time: {statistics.mean(all_means):.2f}ms")
            logger.info(f"Fastest response: {min(all_means):.2f}ms")
            logger.info(f"Slowest response: {max(all_means):.2f}ms")
        if all_success_rates:
            logger.info(f"Overall success rate: {statistics.mean(all_success_rates):.1f}%")

        # Performance thresholds
        logger.info("\n" + "=" * 70)
        logger.info("Performance Assessment")
        logger.info("=" * 70)

        excellent_threshold = 100  # ms
        good_threshold = 500  # ms
        acceptable_threshold = 1000  # ms

        for result in self.results:
            mean_ms = result.get("mean_ms", float("inf"))
            endpoint = result.get("endpoint", "unknown")

            if mean_ms < excellent_threshold:
                status = "EXCELLENT"
            elif mean_ms < good_threshold:
                status = "GOOD"
            elif mean_ms < acceptable_threshold:
                status = "ACCEPTABLE"
            else:
                status = "NEEDS OPTIMIZATION"

            logger.info(f"{endpoint}: {mean_ms:.2f}ms - {status}")


async def main():
    """Main benchmark execution."""
    logger.info("=" * 70)
    logger.info("NYCU Course Platform API Benchmark")
    logger.info("70,239+ Course Records Performance Test")
    logger.info("=" * 70)

    # Create benchmark instance
    benchmark = APIBenchmark(base_url="http://localhost:8000")

    # Check if API is available
    logger.info("\nChecking API health...")
    if not await benchmark.check_health():
        logger.error("API is not available. Please start the server first.")
        return 1

    logger.info("API is healthy and responsive")

    try:
        # Run benchmarks
        await benchmark.benchmark_search_queries()
        await benchmark.benchmark_legacy_endpoints()
        await benchmark.benchmark_concurrent_requests(concurrency=10)
        await benchmark.benchmark_concurrent_requests(concurrency=50)
        await benchmark.benchmark_cache_effectiveness()

        # Generate report
        benchmark.generate_report()

        logger.info("\n" + "=" * 70)
        logger.info("Benchmark completed successfully!")
        logger.info("=" * 70)

        return 0

    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
