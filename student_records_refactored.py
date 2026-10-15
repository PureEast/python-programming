# =============================================================================
# Student Record Management System
# Programming Fundamentals with Python - Week 8 Refactoring Exercise#
# This program reads student data from a CSV file and provides a menu-driven
# interface to list all students and search for a student by ID.
#
# The original top-down program used global variables. This version organizes
# student data into classes and keeps application state on StudentRoster
# =============================================================================

import csv


class Student:
    """Represents one student record loaded from the CSV file."""

    def __init__(self, student_id, student_name, major, gpa, total_credits):
        """Stores the five fields that describe a student."""
        self.student_id = str(student_id).strip()
        self.student_name = str(student_name).strip()
        self.major = str(major).strip()
        self.gpa = str(gpa).strip()
        self.total_credits = str(total_credits).strip()

    def __str__(self):
        """Returns a readable single-line summary of this student."""
        return (
            f"{self.student_id} | {self.student_name} | {self.major} | "
            f"GPA: {self.gpa} | Credits: {self.total_credits}"
        )


class GraduateStudent(Student):
    """Represents a graduate student, adding a thesis topic (bonus inheritance)."""

    def __init__(self, student_id, student_name, major, gpa, total_credits, thesis_topic):
        """Initializes inherited student fields and the thesis topic."""
        super().__init__(student_id, student_name, major, gpa, total_credits)
        self.thesis_topic = str(thesis_topic).strip()

    def __str__(self):
        """Returns the student summary with the graduate student's thesis topic."""
        return f"{super().__str__()} | Thesis: {self.thesis_topic}"


class StudentRoster:
    """Owns the collection of students and provides all menu actions."""

    # -------------------------------------------------------------------------
    # Instance Attributes (replacing the original global variables)
    # -------------------------------------------------------------------------
    def __init__(self):
        """Initialize roster state without using global variables."""
        self.students = []  # Holds all Student objects loaded from the CSV
        self.csv_loaded = False  # Tracks whether a CSV file has been loaded
        self.filename = ""  # Stores the most recently requested CSV filename

    # =========================================================================
    # Option 1: Read CSV
    # =========================================================================
    def load_csv(self, filename):
        """Loads records from CSV, replacing old rows and sorting IDs for binary search."""
        self.filename = filename.strip()
        required = {"StudentID", "StudentName", "Major", "GPA", "TotalCredits"}
        try:
            with open(self.filename, "r", newline="", encoding="utf-8-sig") as csv_file:
                reader = csv.DictReader(csv_file)
                if not required.issubset(set(reader.fieldnames or [])):
                    print("Error: CSV file does not contain the required student columns.")
                    return False
                loaded_students = []
                for row in reader:
                    if None in row or any(row.get(field) is None for field in required):
                        print("Error: CSV contains a row with an unexpected format.")
                        return False
                    loaded_students.append(Student(
                        row["StudentID"], row["StudentName"], row["Major"],
                        row["GPA"], row["TotalCredits"]
                    ))
            # Binary search requires the list to be sorted by the same normalized key.
            self.students = sorted(loaded_students, key=lambda student: student.student_id.upper())
            self.csv_loaded = True
            print()
            print(f"Success! {len(self.students)} student record(s) loaded from '{self.filename}'.")
            return True
        except FileNotFoundError:
            print(f"Error: Could not find '{self.filename}'. Please check the filename and try again.")
        except (OSError, csv.Error, UnicodeError) as exc:
            print(f"Error reading CSV file '{self.filename}': {exc}")
        return False

    # =========================================================================
    # Option 2: List CSV Contents
    # =========================================================================
    def list_students(self):
        """Displays all loaded students in the original aligned table format."""
        if not self.csv_loaded:
            print()
            print("No data loaded. Please use Option 1 to read a CSV file first.")
            return

        print()
        print("-" * 80)
        print(f"{'#':<5} {'Student ID':<12} {'Student Name':<22} {'Major':<24} {'GPA':<6} {'Credits'}")
        print("-" * 82)
        for row_number, student in enumerate(self.students, start=1):
            print(
                f"{row_number:<5}"
                f"{student.student_id:<12}"
                f"{student.student_name:<22}"
                f"{student.major:<24}"
                f"{student.gpa:<6}"
                f"{student.total_credits}"
            )
        print("-" * 82)
        print(f"Total records: {len(self.students)}")

    # =========================================================================
    # Option 3: Search for Student by ID
    # =========================================================================
    def search_by_id(self, search_id):
        """Finds a student with iterative binary search using a normalized ID key."""
        if not self.csv_loaded:
            print("No data loaded. Please use Option 1 to read a CSV file first.")
            return None

        target = search_id.strip().upper()
        left = 0
        right = len(self.students) - 1
        while left <= right:
            middle = (left + right) // 2
            middle_id = self.students[middle].student_id.strip().upper()
            if middle_id == target:
                return self.students[middle]
            if middle_id < target:
                left = middle + 1
            else:
                right = middle - 1
        return None

    def display_search_result(self, search_id, student):
        """Displays one search result or a clear not-found message."""
        print()
        if student is None:
            print(f"No student found with ID '{search_id}'.")
            return
        print("Student found!")
        print("-" * 40)
        print(f"  Student ID    : {student.student_id}")
        print(f"  Student Name  : {student.student_name}")
        print(f"  Major         : {student.major}")
        print(f"  GPA           : {student.gpa}")
        print(f"  Total Credits : {student.total_credits}")
        print("-" * 40)

    # =============================================================================
    # Main Program Loop
    # =============================================================================
    def run(self):
        """Runs the four-option student record menu until the user exits."""
        print("=" * 60)
        print("   Student Record Management System")
        print("=" * 60)

        while True:
            print()
            print("Please select an option:")
            print("  1. Read CSV")
            print("  2. List CSV Contents")
            print("  3. Search for Student by ID")
            print("  4. Exit")
            print()
            choice = input("Enter your choice (1-4): ").strip()

            # =========================================================================
            # Option 1: Read CSV
            # =========================================================================
            if choice == "1":
                filename = input("Enter the CSV filename (e.g., students.csv): ").strip()
                self.load_csv(filename)
            # =========================================================================
            # Option 2: List CSV Contents
            # =========================================================================
            elif choice == "2":
                self.list_students()
            # =========================================================================
            # Option 3: Search for Student by ID
            # =========================================================================
            elif choice == "3":
                if not self.csv_loaded:
                    print()
                    print("No data loaded. Please use Option 1 to read a CSV file first.")
                    continue
                search_id = input("Enter the Student ID to search for: ").strip()
                self.display_search_result(search_id, self.search_by_id(search_id))
            # =========================================================================
            # Option 4: Exit
            # =========================================================================
            elif choice == "4":
                print()
                print("Thank you for using the Student Record Management System. Goodbye!")
                break
            # =========================================================================
            # Invalid Input
            # =========================================================================
            else:
                print()
                print(f"'{choice}' is not a valid option. Please enter 1, 2, 3, or 4.")


def main():
    """Creates a roster and starts the application."""
    StudentRoster().run()


if __name__ == "__main__":
    main()
