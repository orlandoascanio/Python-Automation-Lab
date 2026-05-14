from tabulate import tabulate
from datetime import datetime

# Invoice Details
client = "Wayne Enterprises"
date = datetime.now().strftime("%Y-%m-%d")
items = [
    ("Consulting Services", 150.00, 10),
    ("Server Setup", 500.00, 1),
    ("Maintenance", 150.00, 5),
]

# Calculate Totals
processed_items = []
grand_total = 0

for desc, rate, qty in items:
    total = rate * qty
    grand_total += total
    processed_items.append([desc, qty, rate, total])

# The "Professional" Output
print("-" * 40)
print(f"INVOICE FOR: {client.upper()}")
print(f"DATE:        {date}")
print("-" * 40)

print(tabulate(
    processed_items,
    headers=["Description", "Qty", "Rate ($)", "Total ($)"],
    tablefmt="fancy_grid", # Looks like a real document
    floatfmt=",.2f"
))

print(f"\n{'TOTAL DUE:':>30} ${grand_total:,.2f}")
print("-" * 40)