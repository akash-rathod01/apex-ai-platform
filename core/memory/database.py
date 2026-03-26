"""
SQLite Database Manager for Apex AI Platform
Handles per-app memory storage, test intelligence, and baseline management.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class AppContext:
    """Application context for database operations"""
    app_id: str
    db_path: Path


class DatabaseManager:
    """
    Manages SQLite databases for the Apex AI Platform.
    Each application has its own isolated database.
    
    Storage Layout:
    - core/memory/app1_memory.db
    - core/memory/app2_memory.db
    - core/memory/app3_memory.db
    
    Tables per database:
    - test_results: Historical test execution results
    - baselines: Performance and UI baselines
    - flakiness: Test flakiness tracking
    - risk_scores: Test risk analysis
    - auto_healing: Healing pattern storage
    """
    
    def __init__(self, context: AppContext):
        self.context = context
        self.db_path = context.db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """Create database and tables if they don't exist"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self._connect() as conn:
            self._create_tables(conn)
    
    def _connect(self) -> sqlite3.Connection:
        """Create database connection with JSON support"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Create all required tables"""
        
        # Test Results Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blueprint_id TEXT NOT NULL,
                execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                passed_checks TEXT,
                failed_checks TEXT,
                warnings TEXT,
                evidence TEXT,
                reasoning TEXT,
                confidence REAL,
                execution_time_ms INTEGER,
                UNIQUE(blueprint_id, execution_timestamp)
            )
        """)
        
        # Baselines Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blueprint_id TEXT NOT NULL,
                baseline_type TEXT NOT NULL,
                baseline_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_time_p50 INTEGER,
                response_time_p95 INTEGER,
                dom_snapshot_hash TEXT,
                api_responses TEXT,
                ui_snapshot_path TEXT,
                metadata TEXT,
                UNIQUE(blueprint_id, baseline_type)
            )
        """)
        
        # Flakiness Tracking Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS flakiness (
                blueprint_id TEXT PRIMARY KEY,
                total_runs INTEGER DEFAULT 0,
                pass_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0,
                flakiness_score REAL DEFAULT 0.0,
                consecutive_passes INTEGER DEFAULT 0,
                consecutive_fails INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Risk Scores Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS risk_scores (
                blueprint_id TEXT PRIMARY KEY,
                risk_score REAL DEFAULT 0.0,
                critical_path BOOLEAN DEFAULT 0,
                business_impact TEXT,
                failure_impact_score REAL DEFAULT 0.0,
                last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Auto-Healing Patterns Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS auto_healing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blueprint_id TEXT NOT NULL,
                failure_pattern TEXT NOT NULL,
                healing_action TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                attempt_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
    
    def store_test_result(
        self,
        blueprint_id: str,
        status: str,
        passed_checks: List[str],
        failed_checks: List[str],
        warnings: List[str],
        evidence: Dict[str, Any],
        reasoning: str,
        confidence: float,
        execution_time_ms: int
    ):
        """Store test execution result"""
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO test_results (
                    blueprint_id, status, passed_checks, failed_checks,
                    warnings, evidence, reasoning, confidence, execution_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                blueprint_id,
                status,
                json.dumps(passed_checks),
                json.dumps(failed_checks),
                json.dumps(warnings),
                json.dumps(evidence),
                reasoning,
                confidence,
                execution_time_ms
            ))
            conn.commit()
    
    def get_baseline(self, blueprint_id: str, baseline_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve baseline for a test"""
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT * FROM baselines
                WHERE blueprint_id = ? AND baseline_type = ?
            """, (blueprint_id, baseline_type))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def store_baseline(
        self,
        blueprint_id: str,
        baseline_type: str,
        response_time_p50: Optional[int] = None,
        response_time_p95: Optional[int] = None,
        dom_snapshot_hash: Optional[str] = None,
        api_responses: Optional[Dict] = None,
        ui_snapshot_path: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Store or update baseline"""
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO baselines (
                    blueprint_id, baseline_type, response_time_p50,
                    response_time_p95, dom_snapshot_hash, api_responses,
                    ui_snapshot_path, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                blueprint_id,
                baseline_type,
                response_time_p50,
                response_time_p95,
                dom_snapshot_hash,
                json.dumps(api_responses) if api_responses else None,
                ui_snapshot_path,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
    
    def update_flakiness(self, blueprint_id: str, test_passed: bool):
        """Update flakiness tracking for a test"""
        with self._connect() as conn:
            # Get current flakiness data
            cursor = conn.execute("""
                SELECT * FROM flakiness WHERE blueprint_id = ?
            """, (blueprint_id,))
            
            row = cursor.fetchone()
            
            if row:
                total_runs = row['total_runs'] + 1
                pass_count = row['pass_count'] + (1 if test_passed else 0)
                fail_count = row['fail_count'] + (0 if test_passed else 1)
                consecutive_passes = row['consecutive_passes'] + 1 if test_passed else 0
                consecutive_fails = row['consecutive_fails'] + 1 if not test_passed else 0
            else:
                total_runs = 1
                pass_count = 1 if test_passed else 0
                fail_count = 0 if test_passed else 1
                consecutive_passes = 1 if test_passed else 0
                consecutive_fails = 0 if test_passed else 1
            
            # Calculate flakiness score (0.0 = stable, 1.0 = very flaky)
            # Flakiness is high when there are frequent status changes
            flakiness_score = self._calculate_flakiness_score(
                total_runs, pass_count, fail_count
            )
            
            conn.execute("""
                INSERT OR REPLACE INTO flakiness (
                    blueprint_id, total_runs, pass_count, fail_count,
                    flakiness_score, consecutive_passes, consecutive_fails
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                blueprint_id, total_runs, pass_count, fail_count,
                flakiness_score, consecutive_passes, consecutive_fails
            ))
            conn.commit()
    
    def _calculate_flakiness_score(
        self,
        total_runs: int,
        pass_count: int,
        fail_count: int
    ) -> float:
        """Calculate flakiness score"""
        if total_runs == 0:
            return 0.0
        
        # If all pass or all fail, it's stable (low flakiness)
        if pass_count == total_runs or fail_count == total_runs:
            return 0.0
        
        # Calculate ratio of passes to total runs
        pass_rate = pass_count / total_runs
        
        # Flakiness is highest when pass rate is around 50%
        # Use parabolic function: flakiness = 4 * pass_rate * (1 - pass_rate)
        flakiness = 4 * pass_rate * (1 - pass_rate)
        
        return min(1.0, flakiness)
    
    def get_risk_score(self, blueprint_id: str) -> float:
        """Get risk score for a test"""
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT risk_score FROM risk_scores WHERE blueprint_id = ?
            """, (blueprint_id,))
            
            row = cursor.fetchone()
            return row['risk_score'] if row else 0.0
    
    def close(self):
        """Clean up resources"""
        # SQLite connections are closed automatically via context manager
        pass


# Factory function for creating database managers
def get_database_manager(app_id: str, base_path: Optional[Path] = None) -> DatabaseManager:
    """
    Get database manager for an application.
    
    Args:
        app_id: Application identifier (e.g., "app1", "app2")
        base_path: Base path for memory storage (default: core/memory/)
    
    Returns:
        DatabaseManager instance for the application
    """
    if base_path is None:
        base_path = Path(__file__).parent
    
    db_path = base_path / f"{app_id}_memory.db"
    context = AppContext(app_id=app_id, db_path=db_path)
    
    return DatabaseManager(context)
