# Level attempted : advanced

import csv
import datetime
import os

MOVIE_FILE = "movies.csv"


def get_starter_movies():
    """Returns the five-movie starter collection"""
    return [
        {
            "title": "Inception",
            "year": 2010,
            "genres": ["Sci-Fi", "Thriller"],
            "rating": 8.8,
        },
        {
            "title": "The Shawshank Redemption",
            "year": 1994,
            "genres": ["Drama"],
            "rating": 9.3,
        },
        {
            "title": "The Godfather",
            "year": 1972,
            "genres": ["Crime", "Drama"],
            "rating": 9.2,
        },
        {
            "title": "The Matrix",
            "year": 1999,
            "genres": ["Action", "Sci-Fi"],
            "rating": 8.7,
        },
        {
            "title": "Se7en",
            "year": 1995,
            "genres": ["Crime", "Thriller"],
            "rating": 8.6,
        },
    ]


def normalize_genre_name(genre):
    """Normalizes a genre name into consistent title case."""
    return genre.strip().title()


def normalize_genres(genres):
    """Normalizes a list of genres."""
    return [normalize_genre_name(genre) for genre in genres if genre.strip()]


def create_movie(title, year, genres, rating):
    """Creates and returns a movie dictionary."""
    return {
        "title": title.strip(),
        "year": year,
        "genres": normalize_genres(genres),
        "rating": rating,
    }


def display_movies(movies, heading):
    """Displays a formatted movie table"""
    print(f"\n{heading}")
    print("-" * len(heading))

    if not movies:
        print("No movies in this collection.")
        return

    print(f"{'Title':<30} {'Year':<6} {'Genres':<35} {'Rating':>8}")
    print("-" * 85)

    for movie in movies:
        genres_text = " / ".join(movie["genres"])
        print(
            f"{movie['title']:<30} {movie['year']:<6} {genres_text:<35} {movie['rating']:>8.2f}"
        )


def find_top_rated(movies, n):
    """Returns the top n movies by rating without modifying the original list"""
    sorted_movies = sorted(movies, key=lambda movie: movie["rating"], reverse=True)
    return sorted_movies[:n]


def get_average_rating(movies):
    """Returns the average movie rating rounded to two decimals"""
    if not movies:
        return 0.0

    total = 0.0
    for movie in movies:
        total += movie["rating"]

    return round(total / len(movies), 2)


def get_unique_genres(movies):
    """Returns a sorted list of unique genres from the collection"""
    unique_genres = []
    for movie in movies:
        for genre in movie["genres"]:
            if all(genre.lower() != existing.lower() for existing in unique_genres):
                unique_genres.append(genre)

    unique_genres.sort(key=lambda text: text.lower())
    return unique_genres


def filter_by_genre(movies, genre):
    """Returns movies that contain the requested genre"""
    target = genre.lower().strip()
    matches = []

    for movie in movies:
        for movie_genre in movie["genres"]:
            if movie_genre.lower() == target:
                matches.append(movie)
                break

    return matches


def update_rating(movies, title, new_rating):
    """Updates a movie rating in place and returns True if found"""
    target = title.lower().strip()

    for movie in movies:
        if movie["title"].lower() == target:
            movie["rating"] = new_rating
            return True

    return False


def get_genre_stats(movies):
    """Returns a list of (genre, average_rating, count) tuples sorted by average rating"""
    unique_genres = get_unique_genres(movies)
    stats = []

    for genre in unique_genres:
        total = 0.0
        count = 0

        for movie in movies:
            genre_match = False
            for movie_genre in movie["genres"]:
                if movie_genre.lower() == genre.lower():
                    genre_match = True
                    break

            if genre_match:
                total += movie["rating"]
                count += 1

        average = round(total / count, 2) if count else 0.0
        stats.append((genre, average, count))

    stats.sort(key=lambda item: item[1], reverse=True)
    return stats


def sort_movies(movies, sort_key, reverse=False):
    """Returns a new sorted list based on title, year or rating"""
    key_map = {
        "title": lambda movie: movie["title"].lower(),
        "year": lambda movie: movie["year"],
        "rating": lambda movie: movie["rating"],
    }

    if sort_key not in key_map:
        return movies

    return sorted(movies, key=key_map[sort_key], reverse=reverse)


def build_genre_catalog(movies):
    """Builds a nested dictionary keyed by each movie's primary genre"""
    catalog = {}

    for movie in movies:
        genres = movie["genres"]
        primary_genre = genres[0] if genres else "Unknown"

        if primary_genre in catalog:
            catalog[primary_genre].append(movie)
        else:
            catalog[primary_genre] = [movie]

    return catalog


def display_genre_catalog(catalog):
    """Displays the nested genre catalog"""
    print("\n===== Genre Catalog =====")

    if not catalog:
        print("No movies in this collection.")
        return

    for genre, genre_movies in catalog.items():
        print(f"\n{genre}")
        print("-" * len(genre))

        sorted_movies = sorted(genre_movies, key=lambda movie: movie["rating"], reverse=True)
        for movie in sorted_movies:
            print(f"  {movie['title']:<35} {movie['rating']:>5.2f}")


def get_rating_lookup(movies):
    """Returns a dictionary comprehension mapping title to rating"""
    return {movie["title"]: movie["rating"] for movie in movies}


def find_genre_champions(catalog):
    """Returns the top-rated movie title for each genre in the catalog"""
    champions = {}

    for genre, genre_movies in catalog.items():
        if not genre_movies:
            continue

        best_movie = genre_movies[0]
        for movie in genre_movies[1:]:
            if movie["rating"] > best_movie["rating"]:
                best_movie = movie

        champions[genre] = best_movie["title"]

    return champions


def load_from_csv(filename):
    """Loads movies from CSV or returns the starter list if the file does not exist"""
    try:
        with open(filename, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # to skip the header row
            movies = []

            for row in reader:
                if not row:
                    continue
                if len(row) < 4:
                    continue

                title = row[0].strip()
                year = int(row[1].strip())
                genres = normalize_genres(row[2].split("|"))
                rating = float(row[3].strip())
                movies.append(create_movie(title, year, genres, rating))

            return movies if movies else get_starter_movies()
    except FileNotFoundError:
        return get_starter_movies()


def save_to_csv(movies, filename):
    """Saves the movie collection to CSV and returns the number of movies written"""
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["title", "year", "genres", "rating"])

        for movie in movies:
            writer.writerow(
                [
                    movie["title"],
                    movie["year"],
                    "|".join(movie["genres"]),
                    f"{movie['rating']:.2f}",
                ]
            )

    return len(movies)


def prompt_for_int(prompt_text):
    """Prompts until the user enters a valid integer"""
    while True:
        raw_value = input(prompt_text).strip()
        try:
            return int(raw_value)
        except ValueError:
            print("Please enter a whole number.")


def prompt_for_float(prompt_text):
    """Prompts until the user enters a valid float"""
    while True:
        raw_value = input(prompt_text).strip()
        try:
            return float(raw_value)
        except ValueError:
            print("Please enter a valid number.")


def prompt_yes_no(prompt_text):
    """Prompts until the user enters yes or no"""
    while True:
        response = input(prompt_text).strip().lower()
        if response in {"yes", "y"}:
            return True
        if response in {"no", "n"}:
            return False
        print("Please enter yes or no.")


def display_genre_stats(stats):
    """Displays the genre statistics table"""
    print("\n===== Genre Statistics =====")

    if not stats:
        print("No genre statistics available.")
        return

    print(f"{'Genre':<20} {'Avg Rating':>12} {'Count':>8}")
    print("-" * 44)
    for genre, average, count in stats:
        print(f"{genre:<20} {average:>12.2f} {count:>8}")


def display_genre_champions(champions):
    """Displays the highest-rated movie in each genre"""
    print("\n===== Genre Champions =====")

    if not champions:
        print("No genre champions available.")
        return

    print(f"{'Genre':<20} {'Champion':<35}")
    print("-" * 55)
    for genre, champion in champions.items():
        print(f"{genre:<20} {champion:<35}")


def main():
    movies = load_from_csv(MOVIE_FILE)

    display_movies(movies, "Your Movie Collection")

    for index in range(2):
        print(f"\n--- Add Movie {index + 1} ---")
        title = input("Title: ").strip()
        year = prompt_for_int("Year: ")
        genres_text = input("Genres (comma-separated): ").strip()
        genres = normalize_genres(genres_text.split(","))
        if not genres:
            genres = ["Unknown"]
        rating = prompt_for_float("Rating: ")

        new_movie = create_movie(title, year, genres, rating)
        movies.append(new_movie)

    movies.sort(key=lambda movie: movie["year"])
    display_movies(movies, "All Movies Sorted by Year")

    top_three = find_top_rated(movies, 3)
    display_movies(top_three, "Top 3 Rated Movies")

    average_rating = get_average_rating(movies)
    print(f"\nCollection average rating: {average_rating:.2f}")

    unique_genres = get_unique_genres(movies)
    print("\n===== Unique Genres =====")
    if unique_genres:
        print(", ".join(unique_genres))
    else:
        print("No genres found.")

    genre_choice = input("\nEnter a genre to filter by: ").strip()
    filtered_movies = filter_by_genre(movies, genre_choice)
    if filtered_movies:
        display_movies(filtered_movies, f"Movies Matching Genre: {genre_choice}")
    else:
        print("No movies match that genre.")

    if prompt_yes_no("\nWould you like to update a rating? (yes/no): "):
        title_to_update = input("Enter the movie title: ").strip()
        new_rating = prompt_for_float("Enter the new rating: ")
        updated = update_rating(movies, title_to_update, new_rating)
        if updated:
            print("Rating updated successfully.")
            display_movies(movies, "Updated Movie Collection")
        else:
            print("Movie not found.")

    genre_stats = get_genre_stats(movies)
    display_genre_stats(genre_stats)

    sort_key = input("\nSort by title, year, or rating? ").strip().lower()
    sort_order = input("Sort ascending or descending? ").strip().lower()
    reverse = sort_order.startswith("d")
    sorted_movies = sort_movies(movies, sort_key, reverse=reverse)
    display_movies(sorted_movies, "Custom Sorted Movie Collection")

    catalog = build_genre_catalog(movies)
    display_genre_catalog(catalog)

    rating_lookup = get_rating_lookup(movies)
    lookup_title = input("\nEnter a movie title to look up its rating: ").strip()
    if lookup_title in rating_lookup:
        print(f"{lookup_title}: {rating_lookup[lookup_title]:.2f}")
    else:
        print("Movie title not found in rating lookup.")

    champions = find_genre_champions(catalog)
    display_genre_champions(champions)

    saved_count = save_to_csv(movies, MOVIE_FILE)
    print(f"\nSaved {saved_count} movies to {MOVIE_FILE}.")


if __name__ == "__main__":
    main()
