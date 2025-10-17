"""
Database Optimization Script.

Creates indexes on frequently-queried fields for optimal performance
with 70,239+ course records.

Run this script to:
1. Add indexes on course search fields
2. Analyze query performance
3. Optimize database structure
4. Verify index effectiveness
"""

import asyncio
import logging
import sqlite3
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path.parent))

try:
    from backend.app.config import settings
except ModuleNotFoundError:
    # Fallback for direct execution
    class Settings:
        DATABASE_URL = "sqlite+aiosqlite:///./nycu_course_platform.db"
    settings = Settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Database optimization utilities."""

    def __init__(self, db_path: str):
        """
        Initialize optimizer.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection."""
        logger.info(f"Connecting to database: {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def create_indexes(self):
        """
        Create optimized indexes for course search operations.

        Indexes are created on:
        - crs_no: For course number lookups
        - name: For course name searches
        - teacher: For instructor searches
        - dept: For department filtering
        - semester_id: For semester filtering
        - credits: For credit filtering
        - day_codes: For schedule filtering
        - Composite indexes for common query patterns
        """
        logger.info("Creating database indexes...")

        indexes = [
            # Single-column indexes
            (
                "idx_courses_crs_no",
                "CREATE INDEX IF NOT EXISTS idx_courses_crs_no ON courses(crs_no)"
            ),
            (
                "idx_courses_name",
                "CREATE INDEX IF NOT EXISTS idx_courses_name ON courses(name)"
            ),
            (
                "idx_courses_teacher",
                "CREATE INDEX IF NOT EXISTS idx_courses_teacher ON courses(teacher)"
            ),
            (
                "idx_courses_dept",
                "CREATE INDEX IF NOT EXISTS idx_courses_dept ON courses(dept)"
            ),
            (
                "idx_courses_semester_id",
                "CREATE INDEX IF NOT EXISTS idx_courses_semester_id ON courses(semester_id)"
            ),
            (
                "idx_courses_credits",
                "CREATE INDEX IF NOT EXISTS idx_courses_credits ON courses(credits)"
            ),
            (
                "idx_courses_day_codes",
                "CREATE INDEX IF NOT EXISTS idx_courses_day_codes ON courses(day_codes)"
            ),

            # Composite indexes for common query patterns
            (
                "idx_courses_semester_dept",
                "CREATE INDEX IF NOT EXISTS idx_courses_semester_dept "
                "ON courses(semester_id, dept)"
            ),
            (
                "idx_courses_dept_credits",
                "CREATE INDEX IF NOT EXISTS idx_courses_dept_credits "
                "ON courses(dept, credits)"
            ),
            (
                "idx_courses_semester_teacher",
                "CREATE INDEX IF NOT EXISTS idx_courses_semester_teacher "
                "ON courses(semester_id, teacher)"
            ),

            # Semesters table indexes
            (
                "idx_semesters_acy_sem",
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_semesters_acy_sem "
                "ON semesters(acy, sem)"
            ),
        ]

        created_count = 0
        for index_name, sql in indexes:
            try:
                start = time.time()
                self.cursor.execute(sql)
                elapsed = (time.time() - start) * 1000
                logger.info(f"Created index: {index_name} ({elapsed:.2f}ms)")
                created_count += 1
            except sqlite3.Error as e:
                logger.error(f"Failed to create index {index_name}: {e}")

        self.conn.commit()
        logger.info(f"Successfully created {created_count}/{len(indexes)} indexes")

    def analyze_database(self):
        """
        Analyze database to update query planner statistics.

        This helps SQLite optimize query execution plans.
        """
        logger.info("Analyzing database...")
        try:
            start = time.time()
            self.cursor.execute("ANALYZE")
            self.conn.commit()
            elapsed = (time.time() - start) * 1000
            logger.info(f"Database analysis completed ({elapsed:.2f}ms)")
        except sqlite3.Error as e:
            logger.error(f"Database analysis failed: {e}")

    def vacuum_database(self):
        """
        Vacuum database to reclaim space and optimize structure.

        This rebuilds the database file, repacking it into a minimal amount of disk space.
        """
        logger.info("Vacuuming database...")
        try:
            start = time.time()
            self.cursor.execute("VACUUM")
            elapsed = (time.time() - start) * 1000
            logger.info(f"Database vacuum completed ({elapsed:.2f}ms)")
        except sqlite3.Error as e:
            logger.error(f"Database vacuum failed: {e}")

    def get_table_info(self):
        """Get information about database tables."""
        logger.info("Retrieving table information...")

        # Get course count
        self.cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = self.cursor.fetchone()[0]

        # Get semester count
        self.cursor.execute("SELECT COUNT(*) FROM semesters")
        semester_count = self.cursor.fetchone()[0]

        # Get database size
        self.cursor.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
        db_size = self.cursor.fetchone()[0]

        logger.info(f"Total courses: {course_count:,}")
        logger.info(f"Total semesters: {semester_count}")
        logger.info(f"Database size: {db_size / (1024*1024):.2f} MB")

        return {
            "course_count": course_count,
            "semester_count": semester_count,
            "db_size_mb": db_size / (1024*1024)
        }

    def list_indexes(self):
        """List all indexes in the database."""
        logger.info("Listing existing indexes...")

        self.cursor.execute("""
            SELECT name, tbl_name, sql
            FROM sqlite_master
            WHERE type = 'index'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY tbl_name, name
        """)

        indexes = self.cursor.fetchall()
        logger.info(f"Found {len(indexes)} indexes:")
        for idx_name, tbl_name, sql in indexes:
            logger.info(f"  - {idx_name} on {tbl_name}")

        return indexes

    def benchmark_queries(self):
        """
        Benchmark common query patterns.

        Tests query performance with different filters.
        """
        logger.info("Benchmarking common queries...")

        queries = [
            (
                "Full course scan",
                "SELECT COUNT(*) FROM courses"
            ),
            (
                "Filter by department",
                "SELECT * FROM courses WHERE dept = 'CS' LIMIT 100"
            ),
            (
                "Filter by teacher",
                "SELECT * FROM courses WHERE teacher LIKE '%Smith%' LIMIT 100"
            ),
            (
                "Filter by credits",
                "SELECT * FROM courses WHERE credits >= 3 AND credits <= 4 LIMIT 100"
            ),
            (
                "Search by name",
                "SELECT * FROM courses WHERE name LIKE '%computer%' LIMIT 100"
            ),
            (
                "Complex filter",
                "SELECT * FROM courses WHERE dept IN ('CS', 'ECE') "
                "AND credits >= 3 AND teacher IS NOT NULL LIMIT 100"
            ),
            (
                "Join with semesters",
                "SELECT c.* FROM courses c JOIN semesters s ON c.semester_id = s.id "
                "WHERE s.acy = 113 AND s.sem = 1 LIMIT 100"
            ),
        ]

        results = []
        for query_name, sql in queries:
            try:
                start = time.time()
                self.cursor.execute(sql)
                self.cursor.fetchall()
                elapsed = (time.time() - start) * 1000
                logger.info(f"  {query_name}: {elapsed:.2f}ms")
                results.append((query_name, elapsed))
            except sqlite3.Error as e:
                logger.error(f"  {query_name}: FAILED - {e}")
                results.append((query_name, -1))

        return results

    def optimize_connection_settings(self):
        """
        Optimize SQLite connection settings for better performance.

        Configures:
        - Page size
        - Cache size
        - Journal mode
        - Synchronous mode
        - Temp store
        """
        logger.info("Optimizing connection settings...")

        settings_queries = [
            # Use WAL mode for better concurrency
            ("journal_mode", "PRAGMA journal_mode=WAL"),

            # Increase cache size (10MB)
            ("cache_size", "PRAGMA cache_size=-10000"),

            # Use memory for temporary tables
            ("temp_store", "PRAGMA temp_store=MEMORY"),

            # Reduce synchronous for better performance (still safe with WAL)
            ("synchronous", "PRAGMA synchronous=NORMAL"),
        ]

        for setting_name, sql in settings_queries:
            try:
                self.cursor.execute(sql)
                result = self.cursor.fetchone()
                logger.info(f"  {setting_name}: {result[0] if result else 'SET'}")
            except sqlite3.Error as e:
                logger.error(f"  {setting_name}: FAILED - {e}")

        self.conn.commit()

    def verify_indexes(self):
        """
        Verify that indexes are being used by the query planner.

        Uses EXPLAIN QUERY PLAN to check index usage.
        """
        logger.info("Verifying index usage...")

        test_queries = [
            ("Dept index", "SELECT * FROM courses WHERE dept = 'CS'"),
            ("Name index", "SELECT * FROM courses WHERE name LIKE '%computer%'"),
            ("Teacher index", "SELECT * FROM courses WHERE teacher LIKE '%Smith%'"),
            ("Credits index", "SELECT * FROM courses WHERE credits >= 3"),
        ]

        for query_name, sql in test_queries:
            self.cursor.execute(f"EXPLAIN QUERY PLAN {sql}")
            plan = self.cursor.fetchall()
            uses_index = any("INDEX" in str(row).upper() for row in plan)
            status = "USING INDEX" if uses_index else "TABLE SCAN"
            logger.info(f"  {query_name}: {status}")
            if uses_index:
                for row in plan:
                    logger.debug(f"    {row}")


def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("Database Optimization Script")
    logger.info("=" * 70)

    # Determine database path
    db_url = settings.DATABASE_URL
    if "sqlite" in db_url:
        # Extract path from SQLite URL
        db_path = db_url.split("///")[-1]
        if not Path(db_path).exists():
            # Try alternate location
            db_path = "/home/thc1006/dev/nycu_course_platform/nycu_course_platform.db"

        logger.info(f"Using database: {db_path}")

        if not Path(db_path).exists():
            logger.error(f"Database file not found: {db_path}")
            logger.info("Please specify the correct database path")
            return 1

        # Create optimizer
        optimizer = DatabaseOptimizer(db_path)

        try:
            # Connect to database
            optimizer.connect()

            # Get current table info
            logger.info("\n" + "=" * 70)
            logger.info("Current Database Status")
            logger.info("=" * 70)
            optimizer.get_table_info()

            # List existing indexes
            logger.info("\n" + "=" * 70)
            logger.info("Existing Indexes")
            logger.info("=" * 70)
            optimizer.list_indexes()

            # Create new indexes
            logger.info("\n" + "=" * 70)
            logger.info("Creating Indexes")
            logger.info("=" * 70)
            optimizer.create_indexes()

            # Optimize connection settings
            logger.info("\n" + "=" * 70)
            logger.info("Optimizing Connection Settings")
            logger.info("=" * 70)
            optimizer.optimize_connection_settings()

            # Analyze database
            logger.info("\n" + "=" * 70)
            logger.info("Analyzing Database")
            logger.info("=" * 70)
            optimizer.analyze_database()

            # Verify index usage
            logger.info("\n" + "=" * 70)
            logger.info("Verifying Index Usage")
            logger.info("=" * 70)
            optimizer.verify_indexes()

            # Benchmark queries
            logger.info("\n" + "=" * 70)
            logger.info("Benchmarking Queries")
            logger.info("=" * 70)
            optimizer.benchmark_queries()

            # Optional: Vacuum (can be slow for large databases)
            logger.info("\n" + "=" * 70)
            logger.info("Database Maintenance")
            logger.info("=" * 70)
            response = input("Run VACUUM to optimize database file? (y/N): ")
            if response.lower() == 'y':
                optimizer.vacuum_database()
            else:
                logger.info("Skipping VACUUM")

            logger.info("\n" + "=" * 70)
            logger.info("Optimization Complete!")
            logger.info("=" * 70)

        except Exception as e:
            logger.error(f"Optimization failed: {e}", exc_info=True)
            return 1
        finally:
            optimizer.close()

    else:
        logger.error("This script only supports SQLite databases")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
