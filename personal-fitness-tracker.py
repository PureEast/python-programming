# Level attempted : advanced

def calories_per_minute(calories, duration):
    """Returns calories burned per minute rounded to one decimal place"""
    rate = calories / duration
    return round(rate, 1)


def get_intensity(rate):
    """Returns a workout intensity label based on calories per minute"""
    if rate < 5.0:
        return "Low"
    elif rate < 10.0:
        return "Moderate"
    else:
        return "High"


def calculate_total(values):
    """Returns the sum of a list of numbers using a loop and accumulator"""
    total = 0
    for value in values:
        total += value
    return total


def calculate_average(values):
    """Returns the average of a list of numbers rounded to one decimal place"""
    if len(values) == 0:
        return 0.0
    total = calculate_total(values)
    return round(total / len(values), 1)


def find_best_workout(names, calories_list):
    """Returns the name of the workout with the highest calories burned"""
    if len(names) == 0:
        return "N/A"

    best_index = 0
    best_calories = calories_list[0]

    for index in range(1, len(calories_list)):
        if calories_list[index] > best_calories:
            best_calories = calories_list[index]
            best_index = index

    return names[best_index]


def check_goal(total_calories, goal):
    """Returns a goal message based on total calories burned"""
    if total_calories >= goal:
        return f"Goal reached! You burned {total_calories} calories."
    else:
        shortfall = goal - total_calories
        return f"{shortfall} calories short of your {goal}-calorie goal."


def format_workout_row(name, duration, calories, width=20):
    """Builds and returns one formatted workout row"""
    rate = calories_per_minute(calories, duration)
    intensity = get_intensity(rate)
    return f"{name:<{width}} {duration:>8} {calories:>9} {rate:>8.1f} c/m {intensity:>10}"


def build_separator(widths):
    """Builds a separator line using a nested loop"""
    line = ""
    for width in widths:
        for _ in range(width):
            line += "-"
        line += " "
    return line.rstrip()


def print_workout_table(names, durations, calories_list):
    """Prints the full workout table"""
    print("\n===== Workout Table =====")
    header_name_width = 20
    header = f"{'Workout':<{header_name_width}} {'Duration':>8} {'Calories':>9} {'Rate':>12} {'Intensity':>10}"
    print(header)
    print(build_separator([header_name_width, 8, 9, 12, 10]))

    for index in range(len(names)):
        print(format_workout_row(names[index], durations[index], calories_list[index], header_name_width))


def analyze_trend(calories_list):
    """Analyzes whether calorie burn is improving, declining, mixed or not enough data"""
    if len(calories_list) < 2:
        return "Not enough data"

    increases = 0
    decreases = 0

    for index in range(1, len(calories_list)):
        previous = calories_list[index - 1]
        current = calories_list[index]

        if current > previous:
            increases += 1
        elif current < previous:
            decreases += 1

    if increases > 0 and decreases > 0:
        return "Mixed"
    elif decreases > 0:
        return "Declining"
    else:
        return "Improving"


def print_session_summary(names, durations, calories_list, goal):
    """Prints the session summary using several helper functions"""
    total_workouts = len(names)
    total_calories = calculate_total(calories_list)
    average_calories = calculate_average(calories_list)
    average_duration = calculate_average(durations)
    best_workout = find_best_workout(names, calories_list)
    trend = analyze_trend(calories_list)
    goal_message = check_goal(total_calories, goal)

    print("\n===== Session Summary =====")
    print(f"Workouts logged: {total_workouts}")
    print(f"Total calories burned: {total_calories}")
    print(f"Average calories per workout: {average_calories}")
    print(f"Average duration per workout: {average_duration} min")
    print(f"Best workout by calories: {best_workout}")
    print(f"Effort trend: {trend}")
    print(f"Goal check: {goal_message}")
    print("===========================")


if __name__ == "__main__":
    print("Welcome to the Personal Fitness Tracker!")
    print("You will log workouts until you type done.")

    while True:
        try:
            daily_goal = int(input("\nEnter your daily calorie burn goal: "))
            break
        except ValueError:
            print("Please enter a whole number for the goal.")

    workouts = []
    workout_names = []
    workout_durations = []
    workout_calories = []

    workout_number = 1
    while True:
        print(f"\n--- Workout {workout_number} ---")
        workout_name = input("Workout name: ").strip()

        if workout_name.lower() == "done":
            break


        while True:
            try:
                duration = int(input("Duration (minutes): "))
                if duration <= 0:
                    print("Duration must be greater than 0.")
                    continue
                break
            except ValueError:
                print("Please enter a whole number for duration.")

        while True:
            try:
                calories = int(input("Calories burned: "))
                if calories < 0:
                    print("Calories cannot be negative.")
                    continue
                break
            except ValueError:
                print("Please enter a whole number for calories burned.")

        workouts.append([workout_name, duration, calories])
        workout_names.append(workout_name)
        workout_durations.append(duration)
        workout_calories.append(calories)

        rate = calories_per_minute(calories, duration)
        intensity = get_intensity(rate)
        print(
            f"Result: {workout_name} | {duration} min | {calories} cal | "
            f"{rate:.1f} cal/min | Intensity: {intensity}\n"
        )

        workout_number += 1

    if len(workouts) == 0:
        print("No workouts were logged.")
    else:
        print_workout_table(workout_names, workout_durations, workout_calories)
        print_session_summary(workout_names, workout_durations, workout_calories, daily_goal)

    print("\nAll workouts logged. Great job staying active!")
