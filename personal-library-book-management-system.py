# Level attempted : advanced

import csv
import os
from typing import List, Optional


MOVIE_FILE = "library.csv"


def normalize_genre_name(genre: str) -> str:
    """Normalizes a genre name into a consistent display format"""
    return genre.strip().title()


def normalize_genres(genres: List[str]) -> List[str]:
    """Normalizes a list of genre strings"""
    return [normalize_genre_name(genre) for genre in genres if genre.strip()]


def prompt_for_int(prompt_text: str) -> int:
    """Prompts until the user enters a valid integer"""
    while True:
        raw_value = input(prompt_text).strip()
        try:
            return int(raw_value)
        except ValueError:
            print("Please enter a whole number.")


def prompt_for_float(prompt_text: str) -> float:
    """Prompts until the user enters a valid float"""
    while True:
        raw_value = input(prompt_text).strip()
        try:
            return float(raw_value)
        except ValueError:
            print("Please enter a valid number.")


def prompt_yes_no(prompt_text: str) -> bool:
    """Prompts until the user enters yes or no"""
    while True:
        response = input(prompt_text).strip().lower()
        if response in {"yes", "y"}:
            return True
        if response in {"no", "n"}:
            return False
        print("Please enter yes or no.")


def display_book_list(books: List["Book"], heading: str) -> None:
    """Displays a list of books using each object's __str__ method"""
    print(f"\n{heading}")
    print("-" * len(heading))

    if not books:
        print("No books in this collection.")
        return

    for book in books:
        print(book)


class Book:
    """Represents a single library book"""

    def __init__(self, title, author, isbn, year, genre):
        self.title = title.strip()
        self.author = author.strip()
        self.isbn = isbn.strip()
        self.year = year
        self.genre = normalize_genre_name(genre)
        self.available = True
        self.borrower = None

    def __str__(self):
        """Returns a formatted string describing the book"""
        return (
            f"{self.isbn:<17} {self.title:<30} by {self.author:<25}: "
            f"{self.year:<4} {self.genre:<18} {self.get_status()}"
        )

    def check_out(self, patron_name):
        """Attempts to check the book out to a patron"""
        if self.available:
            self.available = False
            self.borrower = patron_name.strip()
            return True
        return False

    def return_book(self):
        """Returns the book and resets its availability"""
        self.available = True
        self.borrower = None
        return f"'{self.title}' has been returned and is now available."

    def get_status(self):
        """Returns a short string describing the current status"""
        if self.available:
            return "Available"
        return f"Checked out to {self.borrower}"


class EBook(Book):
    """Represents a digital book that can be downloaded by multiple patrons"""

    def __init__(self, title, author, isbn, year, genre, file_format, file_size_mb):
        super().__init__(title, author, isbn, year, genre)
        self.file_format = file_format.strip().upper()
        self.file_size_mb = float(file_size_mb)
        self.active_downloads = 0

    def check_out(self, patron_name):
        """Increments the download count and always succeeds"""
        self.active_downloads += 1
        return True

    def get_status(self):
        """Returns the digital availability status"""
        if self.active_downloads == 0:
            return "Digital — available for download"
        return f"Digital — {self.active_downloads} active download(s)"

    def __str__(self):
        """Returns the base book string plus digital-specific details"""
        return (
            super().__str__()
            + f"\n  [Format: {self.file_format} | {self.file_size_mb:.1f} MB]"
        )

    def get_download_info(self):
        """Returns a summary of the digital file details"""
        return (
            f"Format: {self.file_format} | Size: {self.file_size_mb:.1f} MB | "
            f"Downloads: {self.active_downloads}"
        )


class AudioBook(Book):
    """Represents an audiobook edition of a book"""

    def __init__(self, title, author, isbn, year, genre, narrator, duration_hours):
        super().__init__(title, author, isbn, year, genre)
        self.narrator = narrator.strip()
        self.duration_hours = float(duration_hours)

    def __str__(self):
        """Returns the base book string plus audiobook-specific details"""
        return (
            super().__str__()
            + f"\n  [Narrator: {self.narrator} | Duration: {self.duration_hours:.1f} hrs]"
        )

    def get_listening_info(self):
        """Returns a summary of the audiobook details"""
        message = (
            f"Narrated by {self.narrator}. Listening time: {self.duration_hours:.1f} hours."
        )
        if self.duration_hours > 10:
            message += " (Long listen — plan accordingly!)"
        return message


class ReferenceBook(Book):
    """Represents a reference book that stays in the library"""

    def __init__(self, title, author, isbn, year, genre, edition):
        super().__init__(title, author, isbn, year, genre)
        self.edition = int(edition)
        self.available = False
        self.borrower = None

    def check_out(self, patron_name):
        """Rejects checkout requests for reference books"""
        print("Reference books are for in-library use only and cannot be checked out.")
        return False

    def return_book(self):
        """Returns the fixed reference-book message without changing state"""
        return "Reference books do not need to be returned."

    def get_status(self):
        """Returns the reference-book status"""
        return f"In-Library Use Only (Edition {self.edition})"

    def __str__(self):
        """Returns the base book string plus reference-book details"""
        return super().__str__() + f"\n  [Reference — Edition {self.edition} — In-Library Use Only]"


class Library:
    """Manages a collection of Book objects"""

    def __init__(self, name):
        self.name = name.strip()
        self.collection = []

    def add_book(self, book):
        """Adds a book to the collection"""
        self.collection.append(book)

    def remove_book(self, isbn):
        """Removes a book by exact ISBN if it exists"""
        for index, book in enumerate(self.collection):
            if book.isbn == isbn:
                del self.collection[index]
                return True
        return False

    def find_by_isbn(self, isbn):
        """Returns the first book whose ISBN matches exactly"""
        for book in self.collection:
            if book.isbn == isbn:
                return book
        return None

    def find_by_author(self, author):
        """Returns books whose author contains the search text"""
        target = author.lower().strip()
        matches = []
        for book in self.collection:
            if target in book.author.lower():
                matches.append(book)
        return matches

    def find_by_genre(self, genre):
        """Returns books whose genre matches the search text"""
        target = genre.lower().strip()
        matches = []
        for book in self.collection:
            if book.genre.lower() == target:
                matches.append(book)
        return matches

    def get_available_books(self):
        """Returns books that are available"""
        return [book for book in self.collection if getattr(book, "available", False)]

    def get_checked_out_books(self):
        """Returns books that are actually checked out to a borrower"""
        return [book for book in self.collection if getattr(book, "borrower", None)]

    def generate_report(self):
        """Builds and returns a multi-line status report"""
        available_books = self.get_available_books()
        checked_out_books = self.get_checked_out_books()

        print_books = sum(1 for book in self.collection if type(book) is Book)
        ebooks = sum(1 for book in self.collection if isinstance(book, EBook))
        audiobooks = sum(1 for book in self.collection if isinstance(book, AudioBook))
        reference_books = sum(1 for book in self.collection if isinstance(book, ReferenceBook))

        lines = []
        lines.append("========================================")
        lines.append(f" LIBRARY REPORT: {self.name}")
        lines.append("========================================")
        lines.append(f"Total books in collection : {len(self.collection)}")
        lines.append(f"Available                 : {len(available_books)}")
        lines.append(f"Checked out               : {len(checked_out_books)}")
        lines.append("")
        lines.append("--- Collection by Type ---")
        lines.append(f"Print Books : {print_books}")
        lines.append(f"eBooks      : {ebooks}")
        lines.append(f"Audiobooks  : {audiobooks}")
        lines.append(f"Reference   : {reference_books}")
        lines.append("")
        lines.append("--- Currently Checked Out ---")

        if checked_out_books:
            for book in checked_out_books:
                lines.append(f" '{book.title}' -> {book.borrower}")
        else:
            lines.append(" None")

        lines.append("========================================")
        return "\n".join(lines)

    def save_to_csv(self, filename):
        """Saves the collection to CSV and returns the number of records written"""
        try:
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "type",
                    "title",
                    "author",
                    "isbn",
                    "year",
                    "genre",
                    "available",
                    "borrower",
                    "extra1",
                    "extra2",
                ])

                records_written = 0
                for book in self.collection:
                    if isinstance(book, EBook):
                        type_name = "EBook"
                        extra1 = book.file_format
                        extra2 = f"{book.file_size_mb:.1f}"
                    elif isinstance(book, AudioBook):
                        type_name = "AudioBook"
                        extra1 = book.narrator
                        extra2 = f"{book.duration_hours:.1f}"
                    elif isinstance(book, ReferenceBook):
                        type_name = "ReferenceBook"
                        extra1 = str(book.edition)
                        extra2 = ""
                    else:
                        type_name = "Book"
                        extra1 = ""
                        extra2 = ""

                    writer.writerow([
                        type_name,
                        book.title,
                        book.author,
                        book.isbn,
                        book.year,
                        book.genre,
                        str(book.available),
                        book.borrower or "",
                        extra1,
                        extra2,
                    ])
                    records_written += 1

            return records_written
        except Exception as exc:
            print(f"Unable to save the library file '{filename}': {exc}")
            return 0

    def load_from_csv(self, filename):
        """Loads the collection from CSV and returns the number of records loaded"""
        try:
            loaded_books = []
            with open(filename, "r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader, None)

                for row in reader:
                    if not row:
                        continue
                    if len(row) < 10:
                        raise ValueError(f"Malformed CSV row: {row}")

                    type_name = row[0].strip()
                    title = row[1].strip()
                    author = row[2].strip()
                    isbn = row[3].strip()
                    year = int(row[4].strip())
                    genre = row[5].strip()
                    available_str = row[6].strip()
                    borrower_str = row[7].strip()
                    extra1 = row[8].strip()
                    extra2 = row[9].strip()

                    if type_name == "Book":
                        book = Book(title, author, isbn, year, genre)
                    elif type_name == "EBook":
                        book = EBook(title, author, isbn, year, genre, extra1, float(extra2))
                    elif type_name == "AudioBook":
                        book = AudioBook(title, author, isbn, year, genre, extra1, float(extra2))
                    elif type_name == "ReferenceBook":
                        book = ReferenceBook(title, author, isbn, year, genre, int(extra1))
                    else:
                        raise ValueError(f"Unknown book type: {type_name}")

                    book.available = (available_str == "True")
                    book.borrower = borrower_str if borrower_str else None
                    loaded_books.append(book)

            self.collection = loaded_books
            return len(loaded_books)
        except FileNotFoundError:
            print(f"Info: '{filename}' was not found. Starting with the built-in starter collection.")
            return 0
        except ValueError as exc:
            print(f"Error loading library data: {exc}")
            return 0
        except Exception as exc:
            print(f"Unexpected error while loading '{filename}': {exc}")
            return 0


def get_starter_books():
    """Returns the base starter collection"""
    return [
        Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0743273565", 1925, "Classic Fiction"),
        Book("Educated", "Tara Westover", "978-0399590504", 2018, "Memoir"),
        Book("Dune", "Frank Herbert", "978-0441013593", 1965, "Science Fiction"),
        Book("The Hobbit", "J.R.R. Tolkien", "978-0547928227", 1937, "Fantasy"),
        Book("Pride and Prejudice", "Jane Austen", "978-1503290563", 1813, "Romance"),
        Book("The Martian", "Andy Weir", "978-0804139021", 2011, "Science Fiction"),
    ]


def get_polymorphism_demo_items():
    """Returns a mixed list with at least two objects of each class type"""
    return [
        Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0743273565", 1925, "Classic Fiction"),
        Book("Pride and Prejudice", "Jane Austen", "978-1503290563", 1813, "Romance"),
        EBook("Clean Code", "Robert C. Martin", "978-0132350884", 2008, "Programming", "EPUB", 1.2),
        EBook("Digital Fortress", "Dan Brown", "978-0312944926", 1998, "Thriller", "PDF", 2.8),
        AudioBook("Atomic Habits", "James Clear", "978-0735211292", 2018, "Self-Help", "James Clear", 5.6),
        AudioBook("Becoming", "Michelle Obama", "978-1524763138", 2018, "Memoir", "Michelle Obama", 19.0),
        ReferenceBook("Chicago Manual of Style", "University of Chicago Press", "978-0226287058", 2017, "Reference", 17),
        ReferenceBook("Oxford Atlas", "Oxford University Press", "978-0195219203", 2010, "Reference", 12),
    ]


def demonstrate_polymorphism():
    """Shows the same method calls on different object types"""
    print("\n--- Polymorphism Demonstration ---")
    demo_items = get_polymorphism_demo_items()

    for item in demo_items:
        print(item)
        result = item.check_out("Test Patron")
        print(f" check_out result: {result}")
        print(f" status: {item.get_status()}")


def create_book_from_menu_choice(book_type):
    """Builds a book object from menu input"""
    title = input("Title: ").strip()
    author = input("Author: ").strip()
    isbn = input("ISBN: ").strip()
    year = prompt_for_int("Year: ")
    genre = normalize_genre_name(input("Genre: ").strip())

    if book_type == "book":
        return Book(title, author, isbn, year, genre)
    if book_type == "ebook":
        file_format = input("File format (e.g. EPUB/PDF): ").strip()
        file_size_mb = prompt_for_float("File size (MB): ")
        return EBook(title, author, isbn, year, genre, file_format, file_size_mb)
    if book_type == "audiobook":
        narrator = input("Narrator: ").strip()
        duration_hours = prompt_for_float("Duration in hours: ")
        return AudioBook(title, author, isbn, year, genre, narrator, duration_hours)
    if book_type == "referencebook":
        edition = prompt_for_int("Edition: ")
        return ReferenceBook(title, author, isbn, year, genre, edition)

    return None


def main():
    library = Library("Riverside Public")

    loaded_count = library.load_from_csv(MOVIE_FILE)
    if loaded_count == 0 and not os.path.exists(MOVIE_FILE):
        library.collection = get_starter_books()

    print("=== Full Collection ===")
    if not library.collection:
        print("No books in this collection.")
    else:
        for book in library.collection:
            print(book)

    demonstrate_polymorphism()

    while True:
        print("\n=== Library Menu ===")
        print("[1] Display all books")
        print("[2] Add a book")
        print("[3] Check out a book")
        print("[4] Return a book")
        print("[5] Search by author")
        print("[6] Search by genre")
        print("[7] Display available books")
        print("[8] Generate report")
        print("[9] Remove a book")
        print("[q] Save and quit")

        choice = input("Choose an option: ").strip().lower()

        if choice in {"q", "quit"}:
            saved = library.save_to_csv(MOVIE_FILE)
            print(f"\nSaved {saved} movies to {MOVIE_FILE}.")
            break

        elif choice == "1":
            display_book_list(library.collection, "All Books")

        elif choice == "2":
            book_type = input("Book type (Book/EBook/AudioBook/ReferenceBook): ").strip().lower()
            if book_type not in {"book", "ebook", "audiobook", "referencebook"}:
                print("Unknown book type.")
                continue

            new_book = create_book_from_menu_choice(book_type)
            if new_book is None:
                print("Unable to create the book.")
            else:
                library.add_book(new_book)
                print(f"'{new_book.title}' added successfully.")

        elif choice == "3":
            isbn = input("Enter ISBN to check out: ").strip()
            book = library.find_by_isbn(isbn)
            if book is None:
                print("Book not found.")
                continue

            patron = input("Enter patron name: ").strip()
            result = book.check_out(patron)
            if result:
                print(f"'{book.title}' checked out to {patron}.")
            else:
                print(f"'{book.title}' is already checked out.")

        elif choice == "4":
            isbn = input("Enter ISBN to return: ").strip()
            book = library.find_by_isbn(isbn)
            if book is None:
                print("Book not found.")
                continue

            print(book.return_book())

        elif choice == "5":
            author = input("Enter author name to search: ").strip()
            matches = library.find_by_author(author)
            if matches:
                display_book_list(matches, f"Books by {author}")
            else:
                print("No books match that author.")

        elif choice == "6":
            genre = input("Enter genre to search: ").strip()
            matches = library.find_by_genre(genre)
            if matches:
                display_book_list(matches, f"Books in genre: {genre}")
            else:
                print("No books match that genre.")

        elif choice == "7":
            display_book_list(library.get_available_books(), "Available Books")

        elif choice == "8":
            print("\n" + library.generate_report())

        elif choice == "9":
            isbn = input("Enter ISBN to remove: ").strip()
            if library.remove_book(isbn):
                print("Book removed successfully.")
            else:
                print("Book not found.")

        else:
            print("Invalid option. Please choose one of the menu items.")


if __name__ == "__main__":
    main()
