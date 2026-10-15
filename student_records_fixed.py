# =============================================================================
# Student Record Management System
# Programming Fundamentals with Python - Week 8 Refactoring Exercise#
# This program reads student data from a CSV file and provides a menu-driven
# interface to list all students and search for a student by ID.
# =============================================================================

import csv

# -----------------------------------------------------------------------------
# Global Variables
# -----------------------------------------------------------------------------
student_records = []        # Holds all student records loaded from the CSV
csv_filename = ""           # Stores the filename entered by the user
menu_choice = ""            # Stores the user's menu selection
csv_loaded = False          # Tracks whether a CSV file has been loaded

search_id = ""              # Stores the Student ID entered during a search
found_student = None        # Stores the matching student record, if found
search_index = 0             # Loop counter used during linear search

row_number = 0               # Loop counter used when printing student records
current_student = None       # Holds the current record during iteration

student_id = ""              # Fields parsed from each CSV row
student_name = ""
major = ""
gpa = ""
total_credits = ""

# =============================================================================
# Main Program Loop
# =============================================================================

print("=" * 60)
print("   Student Record Management System")
print("=" * 60)

while True:

    # -------------------------------------------------------------------------
    # Display Menu
    # -------------------------------------------------------------------------
    print()
    print("Please select an option:")
    print("  1. Read CSV")
    print("  2. List CSV Contents")
    print("  3. Search for Student by ID")
    print("  4. Exit")
    print()

    menu_choice = input("Enter your choice (1-4): ").strip()

    # =========================================================================
    # Option 1: Read CSV
    # =========================================================================
    if menu_choice == "1":
        csv_filename = input("Enter the CSV filename (e.g., students.csv): ").strip()

        try:
            # Reads into a temporary list so reloading a file does not duplicate rows.
            loaded_records = []
            with open(csv_filename, "r", newline="", encoding="utf-8-sig") as csv_file:
                csv_reader = csv.DictReader(csv_file)
                required_fields = {"StudentID", "StudentName", "Major", "GPA", "TotalCredits"}
                if not required_fields.issubset(set(csv_reader.fieldnames or [])):
                    raise ValueError("CSV is missing one or more required columns.")

                for row in csv_reader:
                    if None in row or any(row.get(field) is None for field in required_fields):
                        raise ValueError("CSV contains a row with an unexpected format.")

                    student_id = row["StudentID"].strip()
                    student_name = row["StudentName"].strip()
                    major = row["Major"].strip()
                    gpa = row["GPA"].strip()
                    total_credits = row["TotalCredits"].strip()

                    student_record = {
                        "StudentID": student_id,
                        "StudentName": student_name,
                        "Major": major,
                        "GPA": gpa,
                        "TotalCredits": total_credits,
                    }
                    loaded_records.append(student_record)

            # Replaces existing records only after the whole file loads successfully.
            student_records = loaded_records
            csv_loaded = True
            print()
            print(f"Success! {len(student_records)} student record(s) loaded from '{csv_filename}'.")
        except FileNotFoundError:
            print(f"Error: Could not find '{csv_filename}'. Please check the filename and try again.")
        except (OSError, csv.Error, UnicodeError, ValueError) as exc:
            print(f"Error reading CSV file '{csv_filename}': {exc}")

    # =========================================================================
    # Option 2: List CSV Contents
    # =========================================================================
    elif menu_choice == "2":
        if not csv_loaded:
            print()
            print("No data loaded. Please use Option 1 to read a CSV file first.")
        else:
            print()
            print("-" * 80)
            print(f"{'#':<5} {'Student ID':<12} {'Student Name':<22} {'Major':<24} {'GPA':<6} {'Credits'}")
            print("-" * 82)

            for row_number, current_student in enumerate(student_records, start=1):
                print(
                    f"{row_number:<5}"
                    f"{current_student['StudentID']:<12}"
                    f"{current_student['StudentName']:<22}"
                    f"{current_student['Major']:<24}"
                    f"{current_student['GPA']:<6}"
                    f"{current_student['TotalCredits']}"
                )

            print("-" * 82)
            print(f"Total records: {len(student_records)}")

    # =========================================================================
    # Option 3: Search for Student by ID
    # =========================================================================
    elif menu_choice == "3":

        if not csv_loaded:
            print()
            print("No data loaded. Please use Option 1 to read a CSV file first.")
        else:
            search_id = input("Enter the Student ID to search for: ").strip().upper()
            found_student = None  # Reset each time so a previous match is not reused.
            search_index = 0

            while search_index < len(student_records):
                if student_records[search_index]["StudentID"].strip().upper() == search_id:
                    found_student = student_records[search_index]
                    break
                search_index += 1

            print()
            if found_student is None:
                print(f"No student found with ID '{search_id}'.")
            else:
                print("Student found!")
                print("-" * 40)
                print(f"  Student ID    : {found_student['StudentID']}")
                print(f"  Student Name  : {found_student['StudentName']}")
                print(f"  Major         : {found_student['Major']}")
                print(f"  GPA           : {found_student['GPA']}")
                print(f"  Total Credits : {found_student['TotalCredits']}")
                print("-" * 40)

    # =========================================================================
    # Option 4: Exit
    # =========================================================================
    elif menu_choice == "4":
        print()
        print("Thank you for using the Student Record Management System. Goodbye!")
        break

    # =========================================================================
    # Invalid Input
    # =========================================================================
    else:
        print()
        print(f"'{menu_choice}' is not a valid option. Please enter 1, 2, 3, or 4.")
