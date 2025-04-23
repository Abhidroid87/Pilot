"""
Edge Profile Manager - Automation tool for managing Microsoft Edge browser profiles.
This tool allows opening and switching between different Edge profiles and remembers
which profiles have been opened.
"""

import os
import json
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import WebDriverException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("edge_profile_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EdgeProfileManager")

class EdgeProfileManager:
    """Manages Microsoft Edge browser profiles for automation."""

    def __init__(self, profiles_file="edge_profiles.json", history_file="profile_history.json", batch_config_file="batch_config.json"):
        """
        Initialize the Edge Profile Manager.

        Args:
            profiles_file (str): Path to the JSON file storing profile information
            history_file (str): Path to the JSON file storing profile access history
            batch_config_file (str): Path to the JSON file storing batch configurations
        """
        self.profiles_file = profiles_file
        self.history_file = history_file
        self.batch_config_file = batch_config_file
        self.profiles = self._load_profiles()
        self.history = self._load_history()
        self.batch_config = self._load_batch_config()
        self.active_drivers = {}

        # Ensure Edge WebDriver is available
        self._check_webdriver()

    def _check_webdriver(self):
        """Check if Edge WebDriver is available and compatible."""
        try:
            # This is a simplified check - in a real implementation,
            # you might want to check the Edge version and download the appropriate driver
            edge_options = Options()
            edge_options.add_argument("--headless")  # Just for the check
            driver = webdriver.Edge(options=edge_options)
            driver.quit()
            logger.info("Edge WebDriver is available and working")
        except WebDriverException as e:
            logger.error(f"Edge WebDriver issue: {e}")
            logger.info("Please download the appropriate Edge WebDriver from: "
                       "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
            raise

    def _load_profiles(self):
        """Load profile information from the profiles file."""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error parsing {self.profiles_file}. Using empty profiles.")
                return {}
        else:
            logger.info(f"Profiles file {self.profiles_file} not found. Creating new profiles data.")
            return {}

    def _save_profiles(self):
        """Save profile information to the profiles file."""
        with open(self.profiles_file, 'w') as f:
            json.dump(self.profiles, f, indent=4)
        logger.info(f"Profiles saved to {self.profiles_file}")

    def _load_history(self):
        """Load profile access history from the history file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error parsing {self.history_file}. Using empty history.")
                return {}
        else:
            logger.info(f"History file {self.history_file} not found. Creating new history data.")
            return {}

    def _save_history(self):
        """Save profile access history to the history file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)
        logger.info(f"History saved to {self.history_file}")

    def _load_batch_config(self):
        """Load batch configuration from JSON file."""
        try:
            with open(self.batch_config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Batch config file not found: {self.batch_config_file}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in batch config file: {self.batch_config_file}")
            return {}

    def save_batch_config(self):
        """Save batch configuration to JSON file."""
        with open(self.batch_config_file, 'w') as f:
            json.dump(self.batch_config, f, indent=4)

    def get_batch_names(self):
        """Get list of available batch names."""
        return list(self.batch_config.keys())

    def add_batch(self, batch_name, profiles, batch_size=5, profile_delay=2, batch_delay=30):
        """Add or update a batch configuration."""
        self.batch_config[batch_name] = {
            "profiles": profiles,
            "batch_size": batch_size,
            "profile_delay": profile_delay,
            "batch_delay": batch_delay
        }
        self.save_batch_config()

    def remove_batch(self, batch_name):
        """Remove a batch configuration."""
        if batch_name in self.batch_config:
            del self.batch_config[batch_name]
            self.save_batch_config()
            return True
        return False

    def run_batch(self, batch_name):
        """Run a specific batch configuration."""
        if batch_name not in self.batch_config:
            raise ValueError(f"Batch '{batch_name}' not found in configuration")

        config = self.batch_config[batch_name]
        return self.open_profiles_in_batches(
            profile_names=config["profiles"],
            batch_size=config["batch_size"],
            delay_between_profiles=config["profile_delay"],
            delay_between_batches=config["batch_delay"]
        )

    def add_profile(self, profile_name, profile_path=None, preferred_language=None):
        """
        Add a new Edge profile to the manager.

        Args:
            profile_name (str): Name of the profile
            profile_path (str, optional): Path to the Edge profile directory.
                                        If not provided, will use standard naming convention.
            preferred_language (str, optional): Preferred language for this profile

        Returns:
            bool: True if profile was added successfully, False otherwise
        """
        if profile_name in self.profiles:
            logger.warning(f"Profile '{profile_name}' already exists")
            return False

        # If profile_path is not provided, use a standard naming convention
        # Edge typically uses "Profile 1", "Profile 2", etc.
        if profile_path is None:
            # Try to determine the next available profile number
            existing_profiles = [p.get("path") for p in self.profiles.values()]
            profile_numbers = []
            for path in existing_profiles:
                if path and path.startswith("Profile "):
                    try:
                        num = int(path.split(" ")[1])
                        profile_numbers.append(num)
                    except (ValueError, IndexError):
                        pass

            next_number = 1
            if profile_numbers:
                next_number = max(profile_numbers) + 1

            profile_path = f"Profile {next_number}"
            logger.info(f"Using auto-generated profile path: {profile_path}")

        self.profiles[profile_name] = {
            "path": profile_path,
            "preferred_language": preferred_language,
            "created_at": datetime.now().isoformat()
        }
        self._save_profiles()
        logger.info(f"Added new profile: {profile_name}")
        return True

    def remove_profile(self, profile_name):
        """
        Remove a profile from the manager.

        Args:
            profile_name (str): Name of the profile to remove

        Returns:
            bool: True if profile was removed successfully, False otherwise
        """
        if profile_name not in self.profiles:
            logger.warning(f"Profile '{profile_name}' does not exist")
            return False

        del self.profiles[profile_name]
        self._save_profiles()

        # Also remove from history if exists
        if profile_name in self.history:
            del self.history[profile_name]
            self._save_history()

        logger.info(f"Removed profile: {profile_name}")
        return True

    def list_profiles(self):
        """
        List all available profiles.

        Returns:
            dict: Dictionary of all profiles
        """
        return self.profiles

    def get_unopened_profiles(self):
        """
        Get a list of profiles that have not been opened yet.

        Returns:
            list: List of profile names that have not been opened
        """
        return [name for name in self.profiles if name not in self.history]

    def open_profile(self, profile_name):
        """
        Open Microsoft Edge with the specified profile.

        Args:
            profile_name (str): Name of the profile to open

        Returns:
            webdriver.Edge: The WebDriver instance for the opened browser
        """
        if profile_name not in self.profiles:
            logger.error(f"Profile '{profile_name}' does not exist")
            raise ValueError(f"Profile '{profile_name}' does not exist")

        profile_data = self.profiles[profile_name]
        profile_path = profile_data["profile_path"] if "profile_path" in profile_data else profile_data["path"]

        # Get the Edge User Data directory
        user_data_dir = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data")

        # Set up Edge options
        edge_options = Options()
        edge_options.add_argument(f"--user-data-dir={user_data_dir}")
        edge_options.add_argument(f"--profile-directory={profile_path}")
        
        # Add these options to prevent crashes
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--remote-debugging-port=0")
        edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        # Add language preference if specified
        if profile_data.get("preferred_language"):
            edge_options.add_argument(f"--lang={profile_data['preferred_language']}")

        try:
            # Launch Edge with the specified profile
            driver = webdriver.Edge(options=edge_options)
            
            # Store the driver instance
            self.active_drivers[profile_name] = driver

            # Update history
            self.history[profile_name] = {
                "last_opened": datetime.now().isoformat(),
                "open_count": self.history.get(profile_name, {}).get("open_count", 0) + 1
            }
            self._save_history()

            logger.info(f"Opened Edge with profile: {profile_name}")
            return driver

        except WebDriverException as e:
            logger.error(f"Failed to open Edge with profile '{profile_name}': {e}")
            raise

    def switch_to_profile(self, from_profile, to_profile):
        """
        Switch from one profile to another.

        Args:
            from_profile (str): Name of the current profile
            to_profile (str): Name of the profile to switch to

        Returns:
            webdriver.Edge: The WebDriver instance for the new profile
        """
        # Close the current profile if it's open
        if from_profile in self.active_drivers:
            try:
                self.active_drivers[from_profile].quit()
                del self.active_drivers[from_profile]
                logger.info(f"Closed profile: {from_profile}")
            except WebDriverException as e:
                logger.warning(f"Error closing profile '{from_profile}': {e}")

        # Open the new profile
        return self.open_profile(to_profile)

    def set_language_preference(self, profile_name, language_code):
        """
        Set the preferred language for a profile.

        Args:
            profile_name (str): Name of the profile
            language_code (str): Language code (e.g., 'en-US', 'es', 'fr')

        Returns:
            bool: True if language preference was set successfully, False otherwise
        """
        if profile_name not in self.profiles:
            logger.error(f"Profile '{profile_name}' does not exist")
            return False

        self.profiles[profile_name]["preferred_language"] = language_code
        self._save_profiles()
        logger.info(f"Set preferred language for '{profile_name}' to '{language_code}'")
        return True

    def close_all_profiles(self):
        """
        Close all open Edge browser instances.

        Returns:
            int: Number of browser instances closed
        """
        count = 0
        for profile_name, driver in list(self.active_drivers.items()):
            try:
                driver.quit()
                del self.active_drivers[profile_name]
                count += 1
                logger.info(f"Closed profile: {profile_name}")
            except WebDriverException as e:
                logger.warning(f"Error closing profile '{profile_name}': {e}")

        return count

    def open_multiple_profiles(self, profile_names, delay_between=2, skip_missing=True):
        """
        Open multiple Edge profiles simultaneously.

        Args:
            profile_names (list): List of profile names to open
            delay_between (int): Delay in seconds between opening profiles
            skip_missing (bool): If True, will skip profiles that don't exist instead of raising an error

        Returns:
            dict: Dictionary mapping profile names to their WebDriver instances
        """
        drivers = {}
        for profile_name in profile_names:
            # Check if profile exists before trying to open it
            if profile_name not in self.profiles:
                if skip_missing:
                    logger.warning(f"Skipping non-existent profile: '{profile_name}'")
                    continue
                else:
                    logger.error(f"Profile '{profile_name}' does not exist")
                    raise ValueError(f"Profile '{profile_name}' does not exist")

            try:
                drivers[profile_name] = self.open_profile(profile_name)
                time.sleep(delay_between)  # Add delay to prevent resource issues
            except Exception as e:
                logger.error(f"Failed to open profile '{profile_name}': {e}")
                # Continue with other profiles even if this one fails

        return drivers

    def get_profile_history(self, profile_name=None):
        """
        Get the access history for a profile or all profiles.

        Args:
            profile_name (str, optional): Name of the profile to get history for.
                                         If None, returns history for all profiles.

        Returns:
            dict: Profile access history
        """
        if profile_name:
            return self.history.get(profile_name, {})
        return self.history

    def open_profiles_in_batches(self, profile_names, batch_size=5, delay_between_profiles=2, delay_between_batches=30, skip_missing=True):
        """
        Open multiple Edge profiles in batches to manage system resources better.

        Args:
            profile_names (list): List of profile names to open
            batch_size (int): Number of profiles to open in each batch
            delay_between_profiles (int): Delay in seconds between opening profiles within a batch
            delay_between_batches (int): Delay in seconds between batches
            skip_missing (bool): If True, will skip profiles that don't exist instead of raising an error

        Returns:
            dict: Dictionary containing successful and failed profile openings
        """
        results = {
            "successful": [],
            "failed": [],
            "skipped": []
        }

        # Split profiles into batches
        batches = [profile_names[i:i + batch_size] for i in range(0, len(profile_names), batch_size)]
        
        logger.info(f"Processing {len(profile_names)} profiles in {len(batches)} batches of {batch_size}")

        for batch_num, batch in enumerate(batches, 1):
            logger.info(f"Processing batch {batch_num}/{len(batches)} - Profiles: {batch}")
            
            # Process each profile in the current batch
            for profile_name in batch:
                if profile_name not in self.profiles:
                    if skip_missing:
                        logger.warning(f"Skipping non-existent profile: '{profile_name}'")
                        results["skipped"].append(profile_name)
                        continue
                    else:
                        logger.error(f"Profile '{profile_name}' does not exist")
                        raise ValueError(f"Profile '{profile_name}' does not exist")

                try:
                    self.open_profile(profile_name)
                    results["successful"].append(profile_name)
                    logger.info(f"Successfully opened profile: {profile_name}")
                    time.sleep(delay_between_profiles)
                except Exception as e:
                    logger.error(f"Failed to open profile '{profile_name}': {e}")
                    results["failed"].append({"profile": profile_name, "error": str(e)})

            # If this isn't the last batch, wait before processing the next batch
            if batch_num < len(batches):
                logger.info(f"Batch {batch_num} completed. Waiting {delay_between_batches} seconds before next batch...")
                time.sleep(delay_between_batches)

        # Log summary
        logger.info("Batch processing completed:")
        logger.info(f"- Successful: {len(results['successful'])}")
        logger.info(f"- Failed: {len(results['failed'])}")
        logger.info(f"- Skipped: {len(results['skipped'])}")

        return results


if __name__ == "__main__":
    # Example usage
    manager = EdgeProfileManager()

    # Add some example profiles (these paths are examples and may need to be adjusted)
    manager.add_profile("Work", "Profile 1", "en-US")
    manager.add_profile("Personal", "Profile 2", "en-US")

    print("Available profiles:")
    for name, data in manager.list_profiles().items():
        print(f"- {name}: {data}")

    print("\nUnopened profiles:")
    for name in manager.get_unopened_profiles():
        print(f"- {name}")

    # Uncomment to test opening profiles
    # work_driver = manager.open_profile("Work")
    # time.sleep(5)
    # personal_driver = manager.open_profile("Personal")
    # time.sleep(5)
    # manager.close_all_profiles()
