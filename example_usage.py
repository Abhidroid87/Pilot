"""
Example usage of the Edge Profile Manager as a Python library.
This demonstrates how to use the EdgeProfileManager class in your own Python scripts.
"""

import time
from edge_profile_manager import EdgeProfileManager

def main():
    # Initialize the profile manager
    manager = EdgeProfileManager()

    # Add some example profiles
    # Note: Use actual Edge profile directory names
    print("Adding example profiles...")
    manager.add_profile("Work", "Default", preferred_language="en-US")  # Main profile is usually 'Default'
    manager.add_profile("Personal", "Profile 1", preferred_language="en-US")
    manager.add_profile("Development", "Profile 2", preferred_language="en-US")

    # You can also let the system auto-generate profile paths
    # manager.add_profile("Another", preferred_language="en-US")

    # List all profiles
    print("\nAvailable profiles:")
    for name, data in manager.list_profiles().items():
        language = data.get("preferred_language", "Not set")
        print(f"- {name}: Path={data.get('path')}, Language={language}")

    # Open multiple profiles simultaneously
    print("\nOpening multiple profiles...")
    profiles_to_open = ["Work", "Personal"]
    drivers = manager.open_multiple_profiles(profiles_to_open, delay_between=2)

    # Wait for a moment to let the browsers open
    time.sleep(5)

    # Switch from one profile to another
    print("\nSwitching from 'Work' to 'Development'...")
    if "Work" in drivers:
        manager.switch_to_profile("Work", "Development")

    # Wait for a moment to see the switch
    time.sleep(5)

    # Check which profiles have been opened
    print("\nProfile access history:")
    history = manager.get_profile_history()
    for name, data in history.items():
        print(f"- {name}:")
        print(f"  - Last opened: {data.get('last_opened', 'Never')}")
        print(f"  - Open count: {data.get('open_count', 0)}")

    # Close all open browsers
    print("\nClosing all browsers...")
    count = manager.close_all_profiles()
    print(f"Closed {count} browser instances")

if __name__ == "__main__":
    main()
