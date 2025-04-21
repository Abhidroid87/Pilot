"""
Edge Profile Automation CLI - Command-line interface for the Edge Profile Manager.
This tool provides a user-friendly interface to manage and automate Microsoft Edge profiles.
"""

import os
import sys
import argparse
import time
from edge_profile_manager import EdgeProfileManager

def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="Microsoft Edge Profile Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add profile command
    add_parser = subparsers.add_parser("add", help="Add a new Edge profile")
    add_parser.add_argument("name", help="Profile name")
    add_parser.add_argument("--path", "-p", help="Profile directory path (e.g., 'Profile 1'). If not provided, will use auto-generated path.")
    add_parser.add_argument("--language", "-l", help="Preferred language (e.g., en-US, es, fr)")

    # Remove profile command
    remove_parser = subparsers.add_parser("remove", help="Remove an Edge profile")
    remove_parser.add_argument("name", help="Profile name to remove")

    # List profiles command
    list_parser = subparsers.add_parser("list", help="List all profiles")

    # Open profile command
    open_parser = subparsers.add_parser("open", help="Open Edge with a specific profile")
    open_parser.add_argument("name", help="Profile name to open")

    # Open multiple profiles command
    open_multiple_parser = subparsers.add_parser("open-multiple", help="Open multiple Edge profiles")
    open_multiple_parser.add_argument("names", nargs="+", help="Profile names to open")
    open_multiple_parser.add_argument("--delay", "-d", type=int, default=2,
                                     help="Delay in seconds between opening profiles")
    open_multiple_parser.add_argument("--no-skip", action="store_true",
                                     help="If set, will raise an error when a profile doesn't exist instead of skipping it")

    # Switch profile command
    switch_parser = subparsers.add_parser("switch", help="Switch from one profile to another")
    switch_parser.add_argument("from_profile", help="Current profile name")
    switch_parser.add_argument("to_profile", help="Profile name to switch to")

    # Set language command
    language_parser = subparsers.add_parser("set-language", help="Set preferred language for a profile")
    language_parser.add_argument("name", help="Profile name")
    language_parser.add_argument("language", help="Language code (e.g., en-US, es, fr)")

    # Show history command
    history_parser = subparsers.add_parser("history", help="Show profile access history")
    history_parser.add_argument("--name", "-n", help="Profile name (if not specified, shows all)")

    # Close all profiles command
    close_parser = subparsers.add_parser("close-all", help="Close all open Edge profiles")

    # Parse arguments
    args = parser.parse_args()

    # Initialize the profile manager
    manager = EdgeProfileManager()

    # Execute the appropriate command
    if args.command == "add":
        success = manager.add_profile(args.name, args.path, args.language)
        if success:
            profile_info = manager.list_profiles()[args.name]
            path = profile_info.get("path", "Unknown")
            print(f"Profile '{args.name}' added successfully with path '{path}'")
        else:
            print(f"Failed to add profile '{args.name}' (it may already exist)")

    elif args.command == "remove":
        success = manager.remove_profile(args.name)
        if success:
            print(f"Profile '{args.name}' removed successfully")
        else:
            print(f"Failed to remove profile '{args.name}' (it may not exist)")

    elif args.command == "list":
        profiles = manager.list_profiles()
        if profiles:
            print("Available profiles:")
            for name, data in profiles.items():
                language = data.get("preferred_language", "Not set")
                print(f"- {name}: Path={data.get('path')}, Language={language}")
        else:
            print("No profiles found. Add profiles using the 'add' command.")

    elif args.command == "open":
        try:
            driver = manager.open_profile(args.name)
            print(f"Opened Edge with profile '{args.name}'")
            print("Press Ctrl+C to close the browser and exit")
            try:
                # Keep the script running until interrupted
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nClosing browser...")
                driver.quit()
                print("Browser closed")
        except Exception as e:
            print(f"Error opening profile '{args.name}': {e}")

    elif args.command == "open-multiple":
        try:
            print(f"Opening {len(args.names)} profiles with {args.delay}s delay between them...")
            # Use skip_missing=False if --no-skip is provided
            skip_missing = not args.no_skip
            drivers = manager.open_multiple_profiles(args.names, args.delay, skip_missing=skip_missing)
            opened_count = len(drivers)
            print(f"Successfully opened {opened_count} out of {len(args.names)} profiles")

            if opened_count > 0:
                print("Press Ctrl+C to close all browsers and exit")
                try:
                    # Keep the script running until interrupted
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nClosing all browsers...")
                    manager.close_all_profiles()
                    print("All browsers closed")
        except Exception as e:
            print(f"Error opening multiple profiles: {e}")

    elif args.command == "switch":
        try:
            driver = manager.switch_to_profile(args.from_profile, args.to_profile)
            print(f"Switched from '{args.from_profile}' to '{args.to_profile}'")
            print("Press Ctrl+C to close the browser and exit")
            try:
                # Keep the script running until interrupted
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nClosing browser...")
                driver.quit()
                print("Browser closed")
        except Exception as e:
            print(f"Error switching profiles: {e}")

    elif args.command == "set-language":
        success = manager.set_language_preference(args.name, args.language)
        if success:
            print(f"Set preferred language for '{args.name}' to '{args.language}'")
        else:
            print(f"Failed to set language for profile '{args.name}' (it may not exist)")

    elif args.command == "history":
        if args.name:
            history = manager.get_profile_history(args.name)
            if history:
                print(f"History for profile '{args.name}':")
                print(f"- Last opened: {history.get('last_opened', 'Never')}")
                print(f"- Open count: {history.get('open_count', 0)}")
            else:
                print(f"No history found for profile '{args.name}'")
        else:
            history = manager.get_profile_history()
            if history:
                print("Profile access history:")
                for name, data in history.items():
                    print(f"- {name}:")
                    print(f"  - Last opened: {data.get('last_opened', 'Never')}")
                    print(f"  - Open count: {data.get('open_count', 0)}")
            else:
                print("No profile access history found")

    elif args.command == "close-all":
        count = manager.close_all_profiles()
        print(f"Closed {count} Edge browser instances")

    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
