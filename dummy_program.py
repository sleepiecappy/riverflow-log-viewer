#!/usr/bin/env python3
"""
Dummy program that outputs messages at random intervals to simulate a long-running process.
"""

import time
import random
import sys
import threading
from datetime import datetime


def stdin_reader():
    """Function to read from stdin and echo commands."""
    try:
        while True:
            line = input()
            if line.strip():
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] [ECHO] Command received: {line}")
                sys.stdout.flush()

                # Handle special commands
                if line.strip().lower() == "quit" or line.strip().lower() == "exit":
                    print(
                        f"[{timestamp}] [ECHO] Exit command received, shutting down..."
                    )
                    sys.stdout.flush()
                    sys.exit(0)
                elif line.strip().lower() == "status":
                    print(f"[{timestamp}] [ECHO] Status: Process running normally")
                    sys.stdout.flush()
    except EOFError:
        # This happens when stdin is closed
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [ECHO] Stdin closed")
        sys.stdout.flush()
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [ECHO] Error reading stdin: {e}")
        sys.stdout.flush()


def main():
    """Main function that runs the dummy process."""
    print("Starting dummy long-running process...")
    print("Press Ctrl+C to stop")
    print("Type commands and press Enter to test stdin forwarding")
    print("Special commands: 'status', 'quit', 'exit'")

    # Start stdin reader thread
    stdin_thread = threading.Thread(target=stdin_reader, daemon=True)
    stdin_thread.start()

    # Various messages to output
    messages = [
        "Processing data batch...",
        "Connecting to database...",
        "Validating input parameters...",
        "Performing calculations...",
        "Writing to log file...",
        "Checking system resources...",
        "Running background task...",
        "Updating configuration...",
        "Sending notification...",
        "Cleaning up temporary files...",
        "Monitoring system health...",
        "Synchronizing data...",
        "Generating report...",
        "Backing up data...",
        "Optimizing performance...",
    ]

    counter = 0

    try:
        while True:
            # Random interval between 0.5 and 3 seconds
            sleep_time = random.uniform(0.5, 3.0)
            time.sleep(sleep_time)

            # Select a random message
            message = random.choice(messages)

            # Output with timestamp and counter
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            counter += 1

            output = f"[{timestamp}] [{counter:04d}] {message}"
            print(output)

            # Flush output to ensure it appears immediately
            sys.stdout.flush()

            # Occasionally output some "error" or "warning" messages
            if random.random() < 0.1:  # 10% chance
                error_messages = [
                    "WARNING: Temporary connection timeout, retrying...",
                    "INFO: Memory usage at 75%",
                    "WARNING: Disk space running low",
                    "ERROR: Failed to connect, attempting fallback...",
                    "INFO: Cache cleared successfully",
                ]
                error_msg = random.choice(error_messages)
                print(f"[{timestamp}] [{counter:04d}] {error_msg}")
                sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nShutting down dummy process...")
        print("Process terminated gracefully.")


if __name__ == "__main__":
    main()
