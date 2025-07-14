#!/usr/bin/env python3
"""
Demo script to showcase the enhanced Log Viewer UI
"""

import time
import random


def main():
    """Generate sample log output for demonstration."""
    messages = [
        "Starting application...",
        "Loading configuration files",
        "Connecting to database",
        "Initializing user interface",
        "Starting background services",
        "Ready to accept connections",
        "Processing user request #1",
        "Query executed successfully",
        "Cache updated",
        "Background job completed",
        "Processing user request #2",
        "Validation passed",
        "Data saved to database",
        "Notification sent",
        "Processing batch job",
        "Memory usage: 45%",
        "CPU usage: 12%",
        "Active connections: 23",
        "Request processed in 127ms",
        "Scheduled task executed",
    ]

    error_messages = [
        "Connection timeout occurred",
        "Invalid input parameter",
        "Database query failed",
        "Network unreachable",
        "Permission denied",
    ]

    print("🎯 Enhanced Log Viewer Demo")
    print("=" * 50)

    for i in range(100):
        # Mostly normal messages
        if random.random() < 0.85:
            message = random.choice(messages)
            print(f"[{i+1:03d}] {message}")
        else:
            # Occasional errors
            error = random.choice(error_messages)
            print(f"ERROR: {error}", file=__import__("sys").stderr)

        # Random delay to simulate real-time logging
        time.sleep(random.uniform(0.1, 1.0))

    print("Demo completed!")


if __name__ == "__main__":
    main()
