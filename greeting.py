#!/usr/bin/env python3
"""
Simple greeting script
"""
import datetime
import os

# Get current time
now = datetime.datetime.now()
hour = now.hour

# Greeting based on time
if hour < 12:
    greeting = "Good morning!"
elif hour < 18:
    greeting = "Good afternoon!"
else:
    greeting = "Good evening!"

# User info (we can customize this later)
username = os.getenv("USER") or os.getenv("USERNAME") or "User"

# Print the greeting
print(f"\n{greeting}")
print(f"Welcome, {username}!")
print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print("\n--- System Info ---")
print(f"Working directory: {os.getcwd()}")
print(f"Python version: {os.sys.version.split()[0]}")
print("\n✅ Script executed successfully!\n")
