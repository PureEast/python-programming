# Level attempted : advanced

import csv
import datetime
import os
from typing import List, Tuple

EXPENSE_FILE = "expenses.csv"
REPORT_FILE = "expense_report.txt"


def build_record(description: str, amount: float, category: str) -> str:
    """Builds a comma separated record string for today's expense """
    today_text = str(datetime.date.today())
    safe_description = description[:30]
    amount_text = f"{amount:.2f}"
    return ",".join([today_text, safe_description, amount_text, category])


def record_line_to_fields(record_line: str) -> List[str]:
    """Converts a comma-separated record string into the four CSV fields """
    parts = next(csv.reader([record_line]))
    if len(parts) < 4:
        raise ValueError(f"Malformed expense record: {record_line}")

    date_text = parts[0].strip()
    category = parts[-1].strip()
    amount_text = parts[-2].strip()
    description = ",".join(part.strip() for part in parts[1:-2]).strip()
    return [date_text, description, amount_text, category]


def load_records(filename: str) -> List[List[str]]:
    """Loads expense records from a CSV file and returns them as a list of rows """
    if not os.path.exists(filename):
        return []

    records: List[List[str]] = []
    try:
        with open(filename, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue

                normalized = [cell.strip() for cell in row]
                if len(normalized) == 4 and normalized[0].lower() == "date" and normalized[1].lower() == "description":
                    continue

                if len(normalized) != 4:
                    raise ValueError(f"Malformed expense record found in {filename}: {row}")

                records.append(normalized)
    except FileNotFoundError:
        return []

    return records


def append_record(filename: str, record_line: str) -> None:
    """Appends one expense record to the CSV file, writing a header row if needed """
    file_exists = os.path.exists(filename)
    fields = record_line_to_fields(record_line)

    with open(filename, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Description", "Amount", "Category"])
        writer.writerow(fields)


def display_records(records: List[List[str]]) -> None:
    """Displays expense records in aligned columns """
    if not records:
        print("No expenses on record yet.")
        return

    print(f"{'Date':<12} {'Description':<30} {'Amount':>12} {'Category':<20}")
    print("-" * 78)
    for record in records:
        if len(record) != 4:
            raise ValueError(f"Malformed expense record: {record}")

        date_text, description, amount_text, category = record
        amount_value = float(amount_text)
        print(f"{date_text:<12} {description[:30]:<30} ${amount_value:>10.2f} {category:<20}")


def search_expenses(records: List[List[str]], keyword: str) -> List[List[str]]:
    """Returns records where the keyword appears in the description or category """
    keyword_lower = keyword.lower().strip()
    matches: List[List[str]] = []

    for record in records:
        if len(record) != 4:
            raise ValueError(f"Malformed expense record: {record}")

        description = record[1].lower()
        category = record[3].lower()
        if keyword_lower in description or keyword_lower in category:
            matches.append(record)

    return matches


def calculate_totals(records: List[List[str]]) -> List[Tuple[str, float]]:
    """Calculates total spending by category and returns tuples sorted highest first """
    totals: List[Tuple[str, float]] = []

    for record in records:
        if len(record) != 4:
            raise ValueError(f"Malformed expense record: {record}")

        category = record[3].strip()
        amount = float(record[2])
        found_index = -1

        for index, (existing_category, _) in enumerate(totals):
            if existing_category.lower() == category.lower():
                found_index = index
                break

        if found_index >= 0:
            existing_category, existing_total = totals[found_index]
            totals[found_index] = (existing_category, round(existing_total + amount, 2))
        else:
            totals.append((category, round(amount, 2)))

    totals.sort(key=lambda item: item[1], reverse=True)
    return totals


def calculate_total_spending(records: List[List[str]]) -> float:
    """Sums all expense amounts using a loop """
    total = 0.0
    for record in records:
        if len(record) != 4:
            raise ValueError(f"Malformed expense record: {record}")
        total += float(record[2])
    return round(total, 2)


def filter_by_month(records: List[List[str]], year: str, month: str) -> List[List[str]]:
    """Returns only the records whose date matches the given year and month """
    filtered: List[List[str]] = []

    for record in records:
        if len(record) != 4:
            raise ValueError(f"Malformed expense record: {record}")

        date_text = record[0].strip()
        if date_text[:4] == year and date_text[5:7] == month:
            # Parse the stored date string so we use datetime.date on record values too.
            datetime.date.fromisoformat(date_text)
            filtered.append(record)

    return filtered


def generate_report(records: List[List[str]], filename: str) -> int:
    """Writes the summary report to a file and returns the number of lines written."""
    lines = build_summary_report(records)

    with open(filename, "w", encoding="utf-8") as file:
        for line in lines:
            file.write(line + "\n")

    return len(lines)


# input functions for prompting user
def prompt_for_amount() -> float:
    """Prompts until the user enters a valid amount """
    while True:
        raw_amount = input("Amount: ").strip()
        try:
            amount = float(raw_amount)
            return amount
        except ValueError:
            print("Please enter a valid numeric amount.")


def prompt_for_category() -> str:
    """Prompts until the user enters a category that starts with a letter """
    invalid_prefixes = tuple("0123456789!@#$%^&*()-_=+[]{}|;:'\"<>,.?/\\ ")
    while True:
        category = input("Category: ").strip()
        if category and not category.startswith(invalid_prefixes) and category[0].isalpha():
            return category
        print("Category must start with a letter. Please try again.")


def prompt_for_positive_int(prompt_text: str) -> int:
    """Prompts until the user enters a non-negative whole number """
    while True:
        raw_value = input(prompt_text).strip()
        try:
            value = int(raw_value)
            if value < 0:
                print("Please enter 0 or a positive whole number.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number.")


def build_summary_report(records: List[List[str]]) -> List[str]:
    """Builds the formatted summary report lines."""
    today = datetime.date.today()
    current_year = f"{today.year:04d}"
    current_month = f"{today.month:02d}"
    month_label = today.strftime("%B %Y")

    month_records = filter_by_month(records, current_year, current_month)
    totals_by_category = calculate_totals(records)
    total_spending = calculate_total_spending(records)
    month_spending = calculate_total_spending(month_records)

    lines: List[str] = [
        "===================================",
        "EXPENSE SUMMARY REPORT",
        f"Generated: {today.isoformat()}",
        "===================================",
        f"\nTotal records: {len(records)}",
        f"Total spending: ${total_spending:.2f}",
        "\n==== Spending by Category ====",
    ]

    if totals_by_category:
        for category, total in totals_by_category:
            lines.append(f"{category:<20} ${total:>10.2f}")
    else:
        lines.append("No category totals available.")

    lines.extend(
        [
            f"\n==== This Month ({month_label}) ====",
            f"Records this month: {len(month_records)}",
            f"Spending this month: ${month_spending:.2f}",
            "===================================",
        ]
    )

    return lines


def run_tracker() -> None:
    """Runs the expense tracker workflow """
    print("Welcome to the Personal Expense Tracker!")

    records = load_records(EXPENSE_FILE)
    print("\n===== Your Expense Records =====")
    display_records(records)

    num_new_expenses = prompt_for_positive_int("\nHow many expenses do you want to add? ")

    for index in range(num_new_expenses):
        print(f"--- Expense {index + 1} ---")
        description = input("Description: ").strip()
        amount = prompt_for_amount()
        category = prompt_for_category()

        record_line = build_record(description, amount, category)
        append_record(EXPENSE_FILE, record_line)

    updated_records = load_records(EXPENSE_FILE)
    print("\n===== Updated Expense Records =====")
    display_records(updated_records)

    search_choice = input("\nWould you like to search your expenses? (yes/no): ").strip().lower()
    if search_choice.startswith("y"):
        keyword = input("Enter a keyword to search for: ").strip()
        matching_records = search_expenses(updated_records, keyword)
        print("===== Search Results =====")
        if matching_records:
            display_records(matching_records)
        else:
            print("No matching expenses found.")

    print("\n===== Summary Report =====")
    for line in build_summary_report(updated_records):
        print(line)

    line_count = generate_report(updated_records, REPORT_FILE)
    print(f"\nReport saved to {REPORT_FILE} ({line_count} lines written).")


# main program
if __name__ == "__main__":
    try:
        run_tracker()
    except FileNotFoundError as exc:
        print(f"File not found: {exc}")
    except ValueError as exc:
        print(f"Invalid input or data error: {exc}")
    except Exception as exc:
        print(f"An unexpected error occurred: {exc}")
    finally:
        print("Thank you for using Expense Tracker. Goodbye!")
