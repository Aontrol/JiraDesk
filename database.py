"""
SQLite Database Engine for JiraDesk with live backup, restore, and reset capabilities.
"""
import os
import json
import sqlite3
import shutil
from typing import List, Optional, Dict, Any
from models import Project, Status, Issue, Worklog


class Database:
    def __init__(self, db_path: Optional[str] = None):
        if not db_path:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jira_tracker.db")
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self, seed_samples: bool = True):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Projects Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Statuses Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS statuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                sort_order INTEGER NOT NULL,
                color TEXT DEFAULT '#5f6368',
                bg_color TEXT DEFAULT '#f1f3f4'
            );
            """)

            # Issues Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                issue_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                issue_type TEXT CHECK(issue_type IN ('Task', 'Bug', 'Story', 'Epic')) DEFAULT 'Task',
                priority TEXT CHECK(priority IN ('Low', 'Medium', 'High', 'Urgent')) DEFAULT 'Medium',
                status_id INTEGER NOT NULL REFERENCES statuses(id),
                position INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_id, issue_number)
            );
            """)

            # Worklogs Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS worklogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_id INTEGER NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
                minutes_spent INTEGER NOT NULL,
                notes TEXT DEFAULT '',
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Ensure default statuses exist
            cursor.execute("SELECT COUNT(*) FROM statuses;")
            if cursor.fetchone()[0] == 0:
                default_statuses = [
                    (1, "Backlog", 1, "#5f6368", "#f1f3f4"),
                    (2, "To Do", 2, "#1a73e8", "#e8f0fe"),
                    (3, "In Progress", 3, "#f29900", "#fef7e0"),
                    (4, "In Review", 4, "#a142f4", "#f3e8fd"),
                    (5, "Done", 5, "#1e8e3e", "#e6f4ea"),
                ]
                cursor.executemany(
                    "INSERT INTO statuses (id, name, sort_order, color, bg_color) VALUES (?, ?, ?, ?, ?);",
                    default_statuses
                )

            # Ensure at least one project exists
            cursor.execute("SELECT COUNT(*) FROM projects;")
            if cursor.fetchone()[0] == 0:
                if seed_samples:
                    cursor.execute(
                        "INSERT INTO projects (key, name, description) VALUES (?, ?, ?);",
                        ("DEV", "Personal Workflow", "Main development and personal tracking workspace")
                    )
                    dev_proj_id = cursor.lastrowid
                    
                    starter_issues = [
                        (dev_proj_id, 1, "Review weekly roadmap & goals", "Outline the major milestones for upcoming feature launches and personal deliverables.", "Story", "High", 2, 0),
                        (dev_proj_id, 2, "Implement Google Material theme styling", "Refine buttons, cards, typography, and status chips to match Google design guidelines.", "Task", "Medium", 3, 0),
                        (dev_proj_id, 3, "Test SQLite database backup routine", "Ensure database can be reliably saved, loaded, and migrated across machines.", "Task", "Low", 3, 1),
                        (dev_proj_id, 4, "Automate Windows .exe build pipeline", "Verify Inno Setup and PyInstaller packaging scripts produce clean standalone installer.", "Task", "Urgent", 4, 0),
                        (dev_proj_id, 5, "Setup project repository and structure", "Initial directory scaffold and virtual environment setup.", "Task", "Medium", 5, 0),
                        (dev_proj_id, 6, "Research drag-and-drop enhancements", "Explore potential fractional indexing algorithms for future card reordering.", "Story", "Low", 1, 0),
                    ]
                    cursor.executemany(
                        """INSERT INTO issues 
                        (project_id, issue_number, title, description, issue_type, priority, status_id, position) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                        starter_issues
                    )

                    cursor.execute(
                        "INSERT INTO worklogs (issue_id, minutes_spent, notes) VALUES (?, ?, ?);",
                        (5, 120, "Completed initial project setup and directory scaffold.")
                    )
                    cursor.execute(
                        "INSERT INTO worklogs (issue_id, minutes_spent, notes) VALUES (?, ?, ?);",
                        (2, 90, "Styled navigation bar and primary buttons.")
                    )
                else:
                    # Clean starter workspace
                    cursor.execute(
                        "INSERT INTO projects (key, name, description) VALUES (?, ?, ?);",
                        ("MAIN", "My Workspace", "Fresh default workspace for personal tasks")
                    )

            conn.commit()

    # --- Backup, Restore, Reset & Export ---
    def backup_database(self, target_path: str):
        """Creates an atomic live backup of the SQLite database."""
        target_dir = os.path.dirname(os.path.abspath(target_path))
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
            
        src_conn = self.get_connection()
        try:
            dst_conn = sqlite3.connect(target_path)
            try:
                src_conn.backup(dst_conn)
                dst_conn.commit()
            finally:
                dst_conn.close()
        finally:
            src_conn.close()

    def restore_database(self, source_path: str):
        """Safely restores database from a valid SQLite backup file."""
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Backup file not found: {source_path}")

        # Validate that the source file is a valid JiraDesk database
        test_conn = sqlite3.connect(source_path)
        try:
            cursor = test_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row[0] for row in cursor.fetchall()}
            required_tables = {"projects", "statuses", "issues"}
            if not required_tables.issubset(tables):
                raise ValueError("The selected file is not a valid JiraDesk backup database.")
        finally:
            test_conn.close()

        # Perform atomic restore
        dst_conn = self.get_connection()
        try:
            src_conn = sqlite3.connect(source_path)
            try:
                src_conn.backup(dst_conn)
                dst_conn.commit()
            finally:
                src_conn.close()
        finally:
            dst_conn.close()

    def reset_database(self, seed_samples: bool = False):
        """
        Completely resets the database.
        If seed_samples is False, sets up a clean slate with zero issues.
        If seed_samples is True, resets with default sample project and tasks.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("DELETE FROM worklogs;")
            cursor.execute("DELETE FROM issues;")
            cursor.execute("DELETE FROM projects;")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('worklogs', 'issues', 'projects');")
            cursor.execute("PRAGMA foreign_keys = ON;")
            conn.commit()

        # Re-initialize with or without samples
        self._init_db(seed_samples=seed_samples)

    def export_data_json(self, target_path: str):
        """Exports all workspace projects, issues, statuses, and worklogs to a JSON file."""
        data = {
            "version": "1.0.0",
            "exported_at": str(sqlite3.datetime.datetime.now() if hasattr(sqlite3, "datetime") else ""),
            "projects": [p.__dict__ for p in self.get_projects()],
            "statuses": [s.__dict__ for s in self.get_statuses()],
            "issues": [i.__dict__ for i in self.get_issues()],
        }
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # --- Project Operations ---
    def get_projects(self) -> List[Project]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, key, name, description, created_at FROM projects ORDER BY key ASC;")
            rows = cursor.fetchall()
            return [Project(id=r["id"], key=r["key"], name=r["name"], description=r["description"], created_at=str(r["created_at"])) for r in rows]

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, key, name, description, created_at FROM projects WHERE id = ?;", (project_id,))
            r = cursor.fetchone()
            if r:
                return Project(id=r["id"], key=r["key"], name=r["name"], description=r["description"], created_at=str(r["created_at"]))
            return None

    def get_project_by_key(self, key: str) -> Optional[Project]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, key, name, description, created_at FROM projects WHERE key = ?;", (key.strip().upper(),))
            r = cursor.fetchone()
            if r:
                return Project(id=r["id"], key=r["key"], name=r["name"], description=r["description"], created_at=str(r["created_at"]))
            return None

    def create_project(self, key: str, name: str, description: str = "") -> int:
        clean_key = key.strip().upper()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO projects (key, name, description) VALUES (?, ?, ?);",
                (clean_key, name.strip(), description.strip())
            )
            conn.commit()
            return cursor.lastrowid

    def delete_project(self, project_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?;", (project_id,))
            conn.commit()

    # --- Status Operations ---
    def get_statuses(self) -> List[Status]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, sort_order, color, bg_color FROM statuses ORDER BY sort_order ASC;")
            rows = cursor.fetchall()
            return [Status(id=r["id"], name=r["name"], sort_order=r["sort_order"], color=r["color"], bg_color=r["bg_color"]) for r in rows]

    # --- Issue Operations ---
    def get_next_issue_number(self, project_id: int) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(MAX(issue_number), 0) + 1 FROM issues WHERE project_id = ?;", (project_id,))
            return cursor.fetchone()[0]

    def create_issue(self, project_id: int, title: str, description: str = "",
                     issue_type: str = "Task", priority: str = "Medium", status_id: int = 1) -> int:
        next_num = self.get_next_issue_number(project_id)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO issues 
                (project_id, issue_number, title, description, issue_type, priority, status_id, position)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0);
            """, (project_id, next_num, title.strip(), description.strip(), issue_type, priority, status_id))
            conn.commit()
            return cursor.lastrowid

    def update_issue(self, issue_id: int, title: str, description: str,
                     issue_type: str, priority: str, status_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE issues 
                SET title = ?, description = ?, issue_type = ?, priority = ?, status_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
            """, (title.strip(), description.strip(), issue_type, priority, status_id, issue_id))
            conn.commit()

    def update_issue_status(self, issue_id: int, new_status_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE issues 
                SET status_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
            """, (new_status_id, issue_id))
            conn.commit()

    def delete_issue(self, issue_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM issues WHERE id = ?;", (issue_id,))
            conn.commit()

    def get_issues(self, project_id: Optional[int] = None, search_query: Optional[str] = None,
                   status_id: Optional[int] = None, priority: Optional[str] = None) -> List[Issue]:
        query = """
            SELECT 
                i.id, i.project_id, i.issue_number, i.title, i.description, 
                i.issue_type, i.priority, i.status_id, i.position, 
                i.created_at, i.updated_at,
                p.key as project_key,
                s.name as status_name,
                COALESCE(SUM(w.minutes_spent), 0) as total_minutes
            FROM issues i
            JOIN projects p ON i.project_id = p.id
            JOIN statuses s ON i.status_id = s.id
            LEFT JOIN worklogs w ON i.id = w.issue_id
            WHERE 1=1
        """
        params = []
        if project_id:
            query += " AND i.project_id = ?"
            params.append(project_id)
        if status_id:
            query += " AND i.status_id = ?"
            params.append(status_id)
        if priority and priority != "All":
            query += " AND i.priority = ?"
            params.append(priority)
        if search_query:
            query += " AND (i.title LIKE ? OR i.description LIKE ? OR (p.key || '-' || i.issue_number) LIKE ?)"
            term = f"%{search_query.strip()}%"
            params.extend([term, term, term])

        query += " GROUP BY i.id ORDER BY s.sort_order ASC, i.position ASC, i.id DESC;"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            issues = []
            for r in rows:
                issues.append(Issue(
                    id=r["id"],
                    project_id=r["project_id"],
                    issue_number=r["issue_number"],
                    title=r["title"],
                    description=r["description"],
                    issue_type=r["issue_type"],
                    priority=r["priority"],
                    status_id=r["status_id"],
                    position=r["position"],
                    created_at=str(r["created_at"]),
                    updated_at=str(r["updated_at"]),
                    project_key=r["project_key"],
                    status_name=r["status_name"],
                    total_minutes=r["total_minutes"]
                ))
            return issues

    def get_issue_by_id(self, issue_id: int) -> Optional[Issue]:
        issues = self.get_issues()
        for i in issues:
            if i.id == issue_id:
                return i
        return None

    # --- Worklog Operations ---
    def add_worklog(self, issue_id: int, minutes_spent: int, notes: str = "") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO worklogs (issue_id, minutes_spent, notes) VALUES (?, ?, ?);",
                (issue_id, minutes_spent, notes.strip())
            )
            conn.commit()
            return cursor.lastrowid

    def get_worklogs(self, issue_id: int) -> List[Worklog]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, issue_id, minutes_spent, notes, logged_at FROM worklogs WHERE issue_id = ? ORDER BY logged_at DESC;",
                (issue_id,)
            )
            rows = cursor.fetchall()
            return [Worklog(id=r["id"], issue_id=r["issue_id"], minutes_spent=r["minutes_spent"], notes=r["notes"], logged_at=str(r["logged_at"])) for r in rows]

    # --- Statistics ---
    def get_statistics(self, project_id: Optional[int] = None) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            proj_clause = "WHERE project_id = ?" if project_id else ""
            params = [project_id] if project_id else []

            cursor.execute(f"SELECT COUNT(*) FROM issues {proj_clause};", params)
            total_issues = cursor.fetchone()[0]

            cursor.execute(f"""
                SELECT COUNT(*) FROM issues i 
                JOIN statuses s ON i.status_id = s.id 
                WHERE s.name = 'In Progress' {'AND i.project_id = ?' if project_id else ''};
            """, params)
            in_progress = cursor.fetchone()[0]

            cursor.execute(f"""
                SELECT COUNT(*) FROM issues i 
                JOIN statuses s ON i.status_id = s.id 
                WHERE s.name = 'Done' {'AND i.project_id = ?' if project_id else ''};
            """, params)
            done_count = cursor.fetchone()[0]

            cursor.execute(f"""
                SELECT COALESCE(SUM(w.minutes_spent), 0) FROM worklogs w
                JOIN issues i ON w.issue_id = i.id
                {'WHERE i.project_id = ?' if project_id else ''};
            """, params)
            total_minutes = cursor.fetchone()[0]

            hours = total_minutes // 60
            mins = total_minutes % 60
            formatted_time = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

            return {
                "total": total_issues,
                "in_progress": in_progress,
                "done": done_count,
                "total_minutes": total_minutes,
                "formatted_time": formatted_time
            }
