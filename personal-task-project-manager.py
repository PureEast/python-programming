# Level attempted : advanced

import csv
import sqlite3
from datetime import date

DB_FILE = "tasks.db"
IMPORT_FILE = "import_tasks.csv"
EXPORT_FILE = "tasks_export.csv"


def create_connection(db_file):
    """Opens or creates the SQLite database and returns the connection."""
    try:
        return sqlite3.connect(db_file)
    except sqlite3.Error as exc:
        print(f"Database connection error: {exc}")
        return None


def setup_database(conn):
    """Creates the base tasks table if it does not already exist."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT,
                priority    TEXT    DEFAULT 'Medium',
                status      TEXT    DEFAULT 'Pending',
                due_date    TEXT,
                project_id INTEGER
            )
            """
        )
        conn.commit()
    except sqlite3.Error as exc:
        print(f"Database setup error: {exc}")


def add_task(conn, title, description, priority, due_date):
    """Adds one task and returns its generated ID."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (title, description, priority, status, due_date, project_id)
            VALUES (?, ?, ?, 'Pending', ?, ?)
            """,
            (title, description, priority, due_date, None),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as exc:
        print(f"Could not add task: {exc}")
        return None


def get_all_tasks(conn):
    """Returns all tasks ordered by priority and due date."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks ORDER BY priority, due_date"
        )
        return cursor.fetchall()
    except sqlite3.Error as exc:
        print(f"Could not retrieve tasks: {exc}")
        return []


def get_tasks_by_status(conn, status):
    """Returns tasks matching a status, ordered by priority."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE status = ? ORDER BY priority, due_date",
            (status,),
        )
        return cursor.fetchall()
    except sqlite3.Error as exc:
        print(f"Could not retrieve tasks by status: {exc}")
        return []


def update_task_status(conn, task_id, new_status):
    """Updates one task's status and reports whether a row changed."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (new_status, task_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as exc:
        print(f"Could not update task: {exc}")
        return False


def delete_task(conn, task_id):
    """Deletes one task and reports whether a row was removed."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as exc:
        print(f"Could not delete task: {exc}")
        return False


def display_tasks(tasks):
    """Displays task tuples in an aligned table."""
    if not tasks:
        print("No tasks found.")
        return

    print(
        f"{'ID':<4} {'Title':<25} {'Priority':<10} "
        f"{'Status':<14} {'Due Date':<10}"
    )
    print("-" * 70)

    for task in tasks:
        task_id, title, _description, priority, status, due_date, _project_id = task
        title_display = title[:25]
        due_display = due_date if due_date else "-"
        print(
            f"{task_id:<4} {title_display:<25} {priority:<10} "
            f"{status:<14} {due_display:<10}"
        )



class TaskManager:
    """Manages tasks, projects, tags, transactions, and database operations."""

    def __init__(self, db_file):
        """Opens the database, enables foreign keys, and creates required tables."""
        try:
            self.conn = sqlite3.connect(db_file)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self._setup_tables()
        except sqlite3.Error:
            if hasattr(self, "conn"):
                self.conn.close()
            raise

    def _setup_tables(self):
        """Creates all tables and the status index used by the advanced level."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT,
                priority    TEXT    DEFAULT 'Medium',
                status      TEXT    DEFAULT 'Pending',
                due_date    TEXT,
                project_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                description TEXT,
                status      TEXT    DEFAULT 'Active',
                due_date    TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS task_tags (
                task_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (task_id, tag_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status)"
        )
        self.conn.commit()

    def add_project(self, name, description, due_date):
        """Adds a project and returns its generated ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO projects (name, description, due_date) VALUES (?, ?, ?)",
                (name, description, due_date),
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as exc:
            print(f"Could not add project: {exc}")
            return None

    def get_all_projects(self):
        """Returns all projects ordered by name."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY name")
            return cursor.fetchall()
        except sqlite3.Error as exc:
            print(f"Could not retrieve projects: {exc}")
            return []

    def add_task(self, title, description, priority, due_date, project_id=None):
        """Adds a task, optionally linked to a project, and returns its ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO tasks (title, description, priority, due_date, project_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, description, priority, due_date, project_id),
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as exc:
            print(f"Could not add task: {exc}")
            return None


    def get_all_tasks(self):
        """Returns all tasks ordered by priority and due date."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks ORDER BY priority, due_date"
            )
            return cursor.fetchall()
        except sqlite3.Error as exc:
            print(f"Could not retrieve tasks: {exc}")
            return []
        

    def get_project_tasks(self, project_id):
        """Returns all tasks assigned to one project."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM tasks
                WHERE project_id = ?
                ORDER BY priority, due_date
                """,
                (project_id,),
            )
            return cursor.fetchall()
        except sqlite3.Error as exc:
            print(f"Could not retrieve project tasks: {exc}")
            return []

    def get_tasks_with_project_name(self):
        """Returns every task together with its project name using LEFT JOIN."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT t.id, t.title, t.priority, t.status, t.due_date, p.name
                FROM tasks t
                LEFT JOIN projects p ON t.project_id = p.id
                ORDER BY t.priority, t.due_date
                """
            )
            return cursor.fetchall()
        except sqlite3.Error as exc:
            print(f"Could not retrieve tasks with projects: {exc}")
            return []

    def get_project_summary(self, project_id):
        """Counts tasks by status for a project using GROUP BY."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT status, COUNT(*)
                FROM tasks
                WHERE project_id = ?
                GROUP BY status
                """,
                (project_id,),
            )
            return cursor.fetchall()
        except sqlite3.Error as exc:
            print(f"Could not retrieve project summary: {exc}")
            return []

    def search_tasks(self, keyword):
        """Searches task title and description using SQL LIKE."""
        pattern = "%" + keyword + "%"
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE title LIKE ? OR description LIKE ?",
                (pattern, pattern),
            )
            return cursor.fetchall()
        except sqlite3.Error as exc:
            print(f"Could not search tasks: {exc}")
            return []

    def update_task_status(self, task_id, new_status):
        """Updates task status and returns True when a row changes."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE tasks SET status = ? WHERE id = ?",
                (new_status, task_id),
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as exc:
            print(f"Could not update task status: {exc}")
            return False

    def delete_task(self, task_id):
        """Deletes a task and returns True if a row was removed."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as exc:
            print(f"Could not delete task: {exc}")
            return False

    def export_to_csv(self, filename):
        """Exports tasks with project names to CSV and returns row count."""
        try:
            rows = self.get_tasks_with_project_name()
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(
                    ["ID", "Title", "Priority", "Status", "Due Date", "Project"]
                )
                for row in rows:
                    output_row = list(row)
                    if output_row[5] is None:
                        output_row[5] = "(No Project)"
                    writer.writerow(output_row)
            return len(rows)
        except (IOError, sqlite3.Error) as exc:
            print(f"Could not export tasks: {exc}")
            return 0

    # -------------------------------------------------------------------------
    # ADVANCED LEVEL - Tags / many-to-many
    # -------------------------------------------------------------------------

    def add_tag(self, name):
        """Adds a tag if needed and returns its ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                (name,),
            )
            cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
            row = cursor.fetchone()
            self.conn.commit()
            return row[0] if row else None
        except sqlite3.Error as exc:
            print(f"Could not add tag: {exc}")
            return None

    def tag_task(self, task_id, tag_id):
        """Associates a tag with a task and reports whether a new link was made."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)",
                (task_id, tag_id),
            )
            self.conn.commit()
            return cursor.rowcount == 1
        except sqlite3.Error as exc:
            print(f"Could not tag task: {exc}")
            return False

    def get_tasks_by_tag(self, tag_name):
        """Returns all tasks associated with a tag using a three-table JOIN."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT t.*
                FROM tasks t
                JOIN task_tags tt ON t.id = tt.task_id
                JOIN tags tg ON tt.tag_id = tg.id
                WHERE tg.name = ?
                """,
                (tag_name,),
            )
            return cursor.fetchall()
        except sqlite3.Error as exc:
            print(f"Could not retrieve tasks by tag: {exc}")
            return []

    def get_tags_for_task(self, task_id):
        """Returns tag names associated with a task."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT tg.name
                FROM task_tags
                JOIN tags tg ON task_tags.tag_id = tg.id
                WHERE task_tags.task_id = ?
                ORDER BY tg.name
                """,
                (task_id,),
            )
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            print(f"Could not retrieve task tags: {exc}")
            return []

    def bulk_add_tasks(self, tasks_list):
        """Inserts multiple tasks in one explicit transaction."""
        original_isolation_level = self.conn.isolation_level
        inserted_count = 0

        try:
            self.conn.isolation_level = None
            self.conn.execute("BEGIN")

            for task in tasks_list:
                self.conn.execute(
                    """
                    INSERT INTO tasks (title, description, priority, due_date, project_id)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        task.get("title"),
                        task.get("description"),
                        task.get("priority", "Medium"),
                        task.get("due_date"),
                        task.get("project_id"),
                    ),
                )
                inserted_count += 1

            self.conn.execute("COMMIT")
            return inserted_count
        except sqlite3.Error:
            try:
                self.conn.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise
        finally:
            self.conn.isolation_level = original_isolation_level if original_isolation_level is not None else ""

    def get_connection_status(self):
        """Returns whether the database connection is still open."""
        try:
            self.conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def import_from_csv(self, filename):
        """Imports tasks from CSV using DictReader and one bulk transaction."""
        try:
            tasks = []
            with open(filename, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    project_id_text = (row.get("project_id") or "").strip()
                    project_id = int(project_id_text) if project_id_text else None
                    tasks.append(
                        {
                            "title": row.get("title"),
                            "description": row.get("description"),
                            "priority": row.get("priority") or "Medium",
                            "due_date": row.get("due_date") or None,
                            "project_id": project_id,
                        }
                    )

            return self.bulk_add_tasks(tasks)
        except FileNotFoundError:
            print(f"Import file not found: {filename}")
            return 0
        except csv.Error as exc:
            print(f"CSV import error: {exc}")
            return 0
        except sqlite3.Error as exc:
            print(f"Database import error: {exc}")
            return 0
        except ValueError as exc:
            print(f"Invalid import data: {exc}")
            return 0

    def close(self):
        """Closes the database connection."""
        try:
            self.conn.close()
        except sqlite3.Error as exc:
            print(f"Database close error: {exc}")


class DatabaseReport:
    """Builds formatted statistical reports from a TaskManager."""

    def __init__(self, task_manager):
        """Stores a TaskManager reference without opening another connection."""
        self.tm = task_manager

    def get_status_summary(self):
        """Returns task counts grouped by status."""
        try:
            cursor = self.tm.conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
            rows = cursor.fetchall()
        except sqlite3.Error:
            return "No tasks in database."

        if not rows:
            return "No tasks in database."

        lines = ["--- Status Summary ---"]
        for status, count in rows:
            lines.append(f"{status:<12} : {count} task(s)")
        return "\n".join(lines)

    def get_priority_summary(self):
        """Returns task counts grouped by priority in High/Medium/Low order."""
        try:
            cursor = self.tm.conn.cursor()
            cursor.execute(
                """
                SELECT priority, COUNT(*)
                FROM tasks
                GROUP BY priority
                ORDER BY CASE priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    ELSE 3
                END
                """
            )
            rows = cursor.fetchall()
        except sqlite3.Error:
            return "No tasks in database."

        if not rows:
            return "No tasks in database."

        lines = ["--- Priority Summary ---"]
        for priority, count in rows:
            lines.append(f"{priority:<12} : {count} task(s)")
        return "\n".join(lines)

    def get_overdue_tasks(self):
        """Returns incomplete tasks whose due date is before today using date('now')."""
        try:
            cursor = self.tm.conn.cursor()
            cursor.execute(
                """
                SELECT *
                FROM tasks
                WHERE due_date < date('now')
                  AND status != 'Done'
                ORDER BY due_date, priority
                """
            )
            return cursor.fetchall()
        except sqlite3.Error as exc:
            print(f"Could not retrieve overdue tasks: {exc}")
            return []

    def generate_full_report(self):
        """Builds and returns a complete multi-line report string."""
        today_text = date.today().isoformat()
        overdue = self.get_overdue_tasks()

        lines = [
            "========================================",
            "       TASK MANAGER REPORT",
            f"       Generated: {today_text}",
            "========================================",
            self.get_status_summary(),
            "",
            self.get_priority_summary(),
            "",
            "--- Overdue Tasks ---",
        ]

        if overdue:
            lines.append(
                f"{'ID':<4} {'Title':<25} {'Priority':<10} {'Due Date':<10}"
            )
            lines.append("-" * 55)
            for task in overdue:
                task_id, title, _description, priority, _status, due_date, _project_id = task
                lines.append(
                    f"{task_id:<4} {title[:25]:<25} {priority:<10} {due_date:<10}"
                )
        else:
            lines.append("No overdue tasks.")

        lines.append("========================================")
        return "\n".join(lines)



def display_tasks_with_projects(rows):
    """Displays JOIN results with task and project information."""
    if not rows:
        print("No tasks found.")
        return

    print(
        f"{'ID':<4} {'Title':<25} {'Priority':<10} "
        f"{'Status':<14} {'Due Date':<10} {'Project':<20}"
    )
    print("-" * 88)

    for task_id, title, priority, status, due_date, project_name in rows:
        project_display = project_name if project_name is not None else "(No Project)"
        due_display = due_date if due_date else "-"
        print(
            f"{task_id:<4} {title[:25]:<25} {priority:<10} "
            f"{status:<14} {due_display:<10} {project_display:<20}"
        )


def prompt_for_choice(prompt, valid_values):
    """Prompts until the user's lowercase response is in valid_values."""
    while True:
        value = input(prompt).strip().lower()
        if value in valid_values:
            return value
        print(f"Please choose one of: {', '.join(valid_values)}")


def prompt_for_positive_integer(prompt):
    """Prompts until a non-negative integer is entered."""
    while True:
        try:
            value = int(input(prompt).strip())
            if value < 0:
                raise ValueError
            return value
        except ValueError:
            print("Please enter a non-negative whole number.")


def print_menu():
    """Displays the interactive menu."""
    print("\n===== Personal Task & Project Manager =====")
    print("[1] Display all tasks")
    print("[2] Add a task")
    print("[3] Check task status")
    print("[4] Update task status")
    print("[5] Delete a task")
    print("[6] Search tasks")
    print("[7] Display available project tasks")
    print("[8] Generate database report")
    print("[q] Save and quit")


def run_demo_setup(tm):
    """Creates sample projects/tasks/tags required to demonstrate all advanced features."""
    print("===== Initial Database Setup =====")

    research_id = tm.add_project(
        "Research Paper",
        "University research project",
        "2026-11-20",
    )
    job_id = tm.add_project(
        "Job Search",
        "Career preparation and applications",
        "2026-12-01",
    )
    print(f"Research Paper project ID: {research_id}")
    print(f"Job Search project ID: {job_id}")

    task_data = [
        ("Write project proposal", "Draft the research proposal", "High", "2026-11-20", research_id),
        ("Find three sources", "Find peer-reviewed research sources", "Medium", "2026-11-25", research_id),
        ("Outline methodology", "Prepare methodology section", "Medium", "2026-11-28", research_id),
        ("Update resume", "Refresh resume for applications", "Low", "2026-12-01", job_id),
        ("Send follow-up email", "Follow up with recruiter", "Medium", "2026-10-08", job_id),
        ("Read chapter 4", "Review chapter 4 notes", "Low", "2026-11-18", None),
    ]

    task_ids = []
    for title, description, priority, due_date, project_id in task_data:
        task_id = tm.add_task(title, description, priority, due_date, project_id)
        task_ids.append(task_id)
        print(f"Task added with ID: {task_id}")

    if task_ids and task_ids[0]:
        print(f"Status updated for task {task_ids[0]}: {tm.update_task_status(task_ids[0], 'In Progress')}")

    tag_names = ["urgent", "research", "personal"]
    tag_ids = [tm.add_tag(name) for name in tag_names]
    for name, tag_id in zip(tag_names, tag_ids):
        print(f"Tag '{name}' ID: {tag_id}")

    if task_ids and task_ids[0] and tag_ids[0]:
        print(f"Tagged task {task_ids[0]} with urgent: {tm.tag_task(task_ids[0], tag_ids[0])}")
    if task_ids and len(task_ids) > 1 and tag_ids[1]:
        print(f"Tagged task {task_ids[1]} with research: {tm.tag_task(task_ids[1], tag_ids[1])}")
    if task_ids and len(task_ids) > 3 and tag_ids[2]:
        print(f"Tagged task {task_ids[3]} with personal: {tm.tag_task(task_ids[3], tag_ids[2])}")

    print("\n=== All Tasks with Project ===")
    display_tasks_with_projects(tm.get_tasks_with_project_name())

    if research_id:
        print(f"\n=== Project Summary: Research Paper (ID {research_id}) ===")
        for status, count in tm.get_project_summary(research_id):
            print(f"{status}: {count}")

    print("\n=== Search: 'research' ===")
    display_tasks(tm.search_tasks("research"))

    print("\n=== Tasks Tagged 'urgent' ===")
    display_tasks(tm.get_tasks_by_tag("urgent"))

    if task_ids and task_ids[0]:
        print(f"Tags for task {task_ids[0]}: {tm.get_tags_for_task(task_ids[0])}")

    bulk_tasks = [
        {
            "title": "Prepare presentation slides",
            "description": "Create slides for the research presentation",
            "priority": "High",
            "due_date": "2026-11-29",
            "project_id": research_id,
        },
        {
            "title": "Proofread report",
            "description": "Proofread the final report",
            "priority": "Medium",
            "due_date": "2026-11-30",
            "project_id": research_id,
        },
        {
            "title": "Organize files",
            "description": "Clean up project files",
            "priority": "Low",
            "due_date": "2026-11-27",
            "project_id": None,
        },
    ]
    try:
        print(f"\nBulk inserted tasks: {tm.bulk_add_tasks(bulk_tasks)}")
    except sqlite3.Error as exc:
        print(f"Bulk insert failed: {exc}")

    report = DatabaseReport(tm)
    print("\n" + report.generate_full_report())

    print("\n=== Overdue Tasks ===")
    overdue = report.get_overdue_tasks()
    if overdue:
        display_tasks(overdue)
    else:
        print("No overdue tasks.")

    exported_count = tm.export_to_csv(EXPORT_FILE)
    print(f"\nExported {exported_count} tasks to {EXPORT_FILE}.")

    # Requirement: demonstrate a successful delete operation.
    if task_ids and task_ids[-1]:
        print(f"Task {task_ids[-1]} deleted: {tm.delete_task(task_ids[-1])}")

    # Demonstrate a no-row update case as required by the base tests.
    print(f"Update non-existent task 99999: {tm.update_task_status(99999, 'Done')}")


def interactive_menu(tm):
    """Runs the required menu loop until the user chooses q or quit."""
    while True:
        print_menu()
        choice = input("Choose an option: ").strip().lower()

        if choice in {"q", "quit"}:
            return

        if choice == "1":
            print("\n=== All Tasks ===")
            display_tasks(tm.get_all_tasks())

        elif choice == "2":
            title = input("Title: ").strip()
            description = input("Description: ").strip()
            priority = prompt_for_choice("Priority (High/Medium/Low): ", {"high", "medium", "low"})
            due_date = input("Due date (YYYY-MM-DD): ").strip()
            projects = tm.get_all_projects()
            project_id = None
            if projects:
                print("Available projects:")
                for project in projects:
                    print(f"{project[0]}: {project[1]}")
                project_text = input("Project ID (blank for no project): ").strip()
                if project_text:
                    try:
                        project_id = int(project_text)
                    except ValueError:
                        print("Invalid project ID; task will have no project.")
            task_id = tm.add_task(title, description, priority.title(), due_date, project_id)
            print(f"Task added with ID: {task_id}")

        elif choice == "3":
            task_id = prompt_for_positive_integer("Task ID: ")
            rows = tm.get_tasks_with_project_name()
            match = next((row for row in rows if row[0] == task_id), None)
            if match:
                print(f"Task {task_id} status: {match[3]}")
            else:
                print("Task not found.")

        elif choice == "4":
            task_id = prompt_for_positive_integer("Task ID: ")
            new_status = prompt_for_choice(
                "New status (Pending/In Progress/Done): ",
                {"pending", "in progress", "done"},
            )
            display_status = new_status.title()
            changed = tm.update_task_status(task_id, display_status)
            print(f"Status updated for task {task_id}: {changed}")

        elif choice == "5":
            task_id = prompt_for_positive_integer("Task ID: ")
            deleted = tm.delete_task(task_id)
            print(f"Task {task_id} deleted: {deleted}")

        elif choice == "6":
            keyword = input("Keyword: ").strip()
            print("\n=== Search Results ===")
            display_tasks(tm.search_tasks(keyword))

        elif choice == "7":
            projects = tm.get_all_projects()
            if not projects:
                print("No projects found.")
                continue
            for project in projects:
                print(f"{project[0]}: {project[1]}")
            project_id = prompt_for_positive_integer("Project ID: ")
            print(f"\n=== Tasks for Project {project_id} ===")
            display_tasks(tm.get_project_tasks(project_id))

        elif choice == "8":
            report = DatabaseReport(tm)
            print("\n" + report.generate_full_report())

        else:
            print("Invalid option. Please choose a menu item.")


def main():
    """Runs the advanced task and project manager."""
    tm = None
    try:
        tm = TaskManager(DB_FILE)
        run_demo_setup(tm)

        print("\n===== Interactive Menu =====")
        interactive_menu(tm)

        try:
            if __import__("os").path.exists(IMPORT_FILE):
                imported = tm.import_from_csv(IMPORT_FILE)
                print(f"Imported {imported} tasks from {IMPORT_FILE}.")
            else:
                print(f"No {IMPORT_FILE} file found; skipping import.")
        except Exception as exc:
            print(f"Import step error: {exc}")

        final_count = tm.export_to_csv(EXPORT_FILE)
        print(f"Final export contains {final_count} task(s).")

    except sqlite3.Error as exc:
        print(f"Could not start task manager: {exc}")
    finally:
        if tm is not None:
            tm.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()
