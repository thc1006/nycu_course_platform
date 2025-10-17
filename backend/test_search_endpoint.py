"""
Quick test script for the new search endpoint.

Run this after starting the API server to verify functionality.
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"


async def test_health():
    """Test API health."""
    print("=" * 70)
    print("Testing API Health")
    print("=" * 70)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False


async def test_search():
    """Test advanced search endpoint."""
    print("\n" + "=" * 70)
    print("Testing POST /api/courses/search")
    print("=" * 70)

    test_cases = [
        {
            "name": "Simple search",
            "data": {"query": "computer", "limit": 5}
        },
        {
            "name": "Department filter",
            "data": {"dept": ["CS"], "limit": 5}
        },
        {
            "name": "Credits filter",
            "data": {"credits_min": 3, "credits_max": 4, "limit": 5}
        },
        {
            "name": "Multiple filters",
            "data": {
                "query": "science",
                "dept": ["CS"],
                "credits_min": 3,
                "limit": 5
            }
        },
    ]

    async with httpx.AsyncClient(timeout=10.0) as client:
        for test_case in test_cases:
            print(f"\n{test_case['name']}:")
            print(f"Request: {json.dumps(test_case['data'], indent=2)}")

            try:
                response = await client.post(
                    f"{BASE_URL}/api/courses/search",
                    json=test_case['data']
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Success!")
                    print(f"   Results: {len(result['courses'])} courses")
                    print(f"   Total: {result['total']}")
                    print(f"   Query time: {result['query_time_ms']:.2f}ms")

                    if result['courses']:
                        print(f"   First course: {result['courses'][0]['name']}")
                else:
                    print(f"❌ Failed with status {response.status_code}")
                    print(f"   Error: {response.text}")

            except Exception as e:
                print(f"❌ Error: {e}")


async def test_autocomplete():
    """Test autocomplete endpoint."""
    print("\n" + "=" * 70)
    print("Testing GET /api/courses/autocomplete")
    print("=" * 70)

    queries = ["comp", "wang", "cs"]

    async with httpx.AsyncClient(timeout=10.0) as client:
        for query in queries:
            print(f"\nQuery: '{query}'")

            try:
                response = await client.get(
                    f"{BASE_URL}/api/courses/autocomplete",
                    params={"q": query, "limit": 5}
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Success! {len(result['suggestions'])} suggestions")

                    for suggestion in result['suggestions'][:3]:
                        print(f"   - {suggestion['type']}: {suggestion['value']}")
                else:
                    print(f"❌ Failed with status {response.status_code}")

            except Exception as e:
                print(f"❌ Error: {e}")


async def test_popular_departments():
    """Test popular departments endpoint."""
    print("\n" + "=" * 70)
    print("Testing GET /api/courses/popular-departments")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/courses/popular-departments",
                params={"limit": 10}
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success!")
                print(f"   Total departments: {result['total_departments']}")
                print(f"   Total courses: {result['total_courses']}")
                print(f"\n   Top 5 departments:")

                for dept in result['departments'][:5]:
                    print(f"   - {dept['code']}: {dept['count']} courses ({dept['percentage']}%)")
            else:
                print(f"❌ Failed with status {response.status_code}")

        except Exception as e:
            print(f"❌ Error: {e}")


async def test_performance_headers():
    """Test performance middleware headers."""
    print("\n" + "=" * 70)
    print("Testing Performance Headers")
    print("=" * 70)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/courses/search",
                json={"query": "test", "limit": 10}
            )

            print("\nResponse Headers:")
            headers_to_check = [
                "x-process-time",
                "x-ratelimit-limit",
                "x-ratelimit-remaining",
                "cache-control",
                "content-encoding",
            ]

            for header in headers_to_check:
                value = response.headers.get(header, "Not found")
                print(f"   {header}: {value}")

        except Exception as e:
            print(f"❌ Error: {e}")


async def test_pagination():
    """Test pagination functionality."""
    print("\n" + "=" * 70)
    print("Testing Pagination")
    print("=" * 70)

    async with httpx.AsyncClient() as client:
        try:
            # First page
            response1 = await client.post(
                f"{BASE_URL}/api/courses/search",
                json={"dept": ["CS"], "limit": 10, "offset": 0}
            )

            # Second page
            response2 = await client.post(
                f"{BASE_URL}/api/courses/search",
                json={"dept": ["CS"], "limit": 10, "offset": 10}
            )

            if response1.status_code == 200 and response2.status_code == 200:
                result1 = response1.json()
                result2 = response2.json()

                print(f"✅ Pagination working!")
                print(f"   Page 1: {len(result1['courses'])} courses")
                print(f"   Page 2: {len(result2['courses'])} courses")
                print(f"   Total: {result1['total']} courses")
                print(f"   Has next (page 1): {result1['has_next']}")
                print(f"   Has previous (page 2): {result2['has_previous']}")

                # Verify different results
                if result1['courses'][0]['id'] != result2['courses'][0]['id']:
                    print("   ✅ Different courses on each page")
                else:
                    print("   ⚠️ Same courses on both pages")
            else:
                print(f"❌ Failed")

        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Run all tests."""
    print("=" * 70)
    print("NYCU Course Platform - Search Endpoint Test Suite")
    print("=" * 70)

    # Check if API is running
    if not await test_health():
        print("\n❌ API is not running. Please start the server first:")
        print("   cd /home/thc1006/dev/nycu_course_platform/backend")
        print("   python3 -m uvicorn backend.app.main:app --reload")
        return

    print("\n✅ API is healthy!\n")

    # Run tests
    await test_search()
    await test_autocomplete()
    await test_popular_departments()
    await test_performance_headers()
    await test_pagination()

    print("\n" + "=" * 70)
    print("Test Suite Complete!")
    print("=" * 70)
    print("\n📖 For full API documentation, visit: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())
