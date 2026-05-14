from tabulate import tabulate

# Habit Data: (Habit Name, Days Completed, Goal)
habits = [
    ("Reading", 5, 7),
    ("Chess", 2, 7),
    ("Jump Rope", 6, 7),
]

report = []

for habit, done, goal in habits:
    percent = done / goal
    
    # Visual Progress Bar (The "Insight" touch)
    # Creates a string like "[#####  ]"
    filled_len = int(10 * percent)
    bar = "[" + "#" * filled_len + " " * (10 - filled_len) + "]"
    
    report.append([habit, f"{done}/{goal}", f"{percent:.0%}", bar])

print(f"\nWEEKLY HABIT REVIEW")
print(tabulate(
    report, 
    headers=["Activity", "Score", "%", "Progress"], 
    tablefmt="presto"
))