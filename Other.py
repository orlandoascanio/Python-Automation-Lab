from tabulate import tabulate

# Raw Data: [Month, Revenue, Expenses]
financials = [
    ("Jan", 5000, 12000),
    ("Feb", 6500, 11500),
    ("Mar", 8000, 14000),
]

starting_cash = 50000
report_data = []

current_cash = starting_cash

for month, rev, exp in financials:
    net_burn = rev - exp
    current_cash += net_burn
    
    # Logic: If cash is low (< 30k), mark it!
    status = "⚠ LOW" if current_cash < 30000 else "OK"
    
    report_data.append([month, rev, exp, net_burn, current_cash, status])

# The "CEO Dashboard" Output
print(f"\nSTARTING CASH: ${starting_cash:,.2f}")
print(tabulate(
    report_data, 
    headers=["Month", "Revenue", "Expenses", "Net Burn", "Cash Left", "Status"],
    tablefmt="simple",
    floatfmt=",.2f" # format all floats with commas and 2 decimals
))