# Profile Automation

This tool automates Microsoft Edge browser profile management, allowing you to:
- Open multiple Edge profiles simultaneously
- Switch between profiles
- Set preferred languages for profiles
- Track which profiles have been opened

## Requirements

- Python 3.7+
- Microsoft Edge browser
- Microsoft Edge WebDriver (compatible with your Edge version)

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Download the appropriate Microsoft Edge WebDriver for your Edge version from:
   https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

   Make sure the WebDriver is in your system PATH or in the same directory as the scripts.

## Usage

### Command Line Interface

The tool provides a command-line interface for easy use:

```bash
# Add a new profile (path is optional, will be auto-generated if not provided)
python edge_automation_cli.py add "Work" --language "en-US"
python edge_automation_cli.py add "Personal" --path "Profile 2" --language "en-US"

# List all profiles
python edge_automation_cli.py list

# Open a profile
python edge_automation_cli.py open "Work"

# Open multiple profiles simultaneously
python edge_automation_cli.py open-multiple "Work" "Personal" --delay 2

# Open multiple profiles and skip any that don't exist (default behavior)
python edge_automation_cli.py open-multiple "Work" "Personal" "NonExistentProfile"

# Open multiple profiles and raise an error if any don't exist
python edge_automation_cli.py open-multiple "Work" "Personal" --no-skip

# Switch from one profile to another
python edge_automation_cli.py switch "Work" "Personal"

# Set preferred language for a profile
python edge_automation_cli.py set-language "Work" "fr"

# View profile access history
python edge_automation_cli.py history
python edge_automation_cli.py history --name "Work"

# Close all open profiles
python edge_automation_cli.py close-all
```

### Finding Your Edge Profile Paths

To find your Edge profile paths:

1. Open Edge and navigate to `edge://version/`
2. Look for the "Profile Path" entry
3. The profile directory name is typically "Default", "Profile 1", "Profile 2", etc.

### Important Note About Edge Profiles

When using this tool:

1. The tool connects to your existing Edge profiles
2. It uses the standard Edge User Data directory at: `%LOCALAPPDATA%\Microsoft\Edge\User Data`
3. Profile paths should match the actual profile directories in your Edge installation
4. Common profile paths are "Default" (for the main profile) and "Profile 1", "Profile 2", etc. for additional profiles

## How It Works

The tool uses Selenium WebDriver to automate Edge browser interactions. It maintains:
- A profiles database (JSON file) with profile information
- A history database (JSON file) tracking which profiles have been opened

## Troubleshooting

If you encounter issues:

1. Make sure you have the correct Edge WebDriver version for your Edge browser
2. Check that the profile paths match your actual Edge profile directories
3. Look at the log file (`edge_profile_manager.log`) for detailed error information
4. If a profile doesn't open, try using the exact profile directory name from `edge://version/`

### Common Issues

- **"Profile doesn't exist" error**: Make sure you're using the correct profile directory name (e.g., "Default" or "Profile 1")
- **Empty browser opens**: The WebDriver might not be connecting to your existing profiles. Check the log file for details.
- **WebDriver error**: Make sure your Edge WebDriver version matches your Edge browser version

## License

This project is licensed under the MIT License - see the LICENSE file for details.
