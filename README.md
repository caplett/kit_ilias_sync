# kit_ilias_sync
Ilias Sync script for KIT

Have an eye for the script output for the first few files.
If you are not logged in, you see a loop.<br/>
You should see the courses from your dashboard.

## Requirements

-   python3, python3-pip and python3-venv
-   Python packages inside requirements.txt
-   [Geckodriver](https://github.com/mozilla/geckodriver/releases) - Necessary to start firefox workers


## Getting Started

Setup an Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install Python packages:
```bash
pip install -r requirements.txt
```

Copy the config and adjust it to your liking:
```bash
cp config.yml.example config.yml
$EDITOR config.yml
```

Download the [Geckodriver](https://github.com/mozilla/geckodriver/releases) and move it into an executable path:
```bash
mv $GECKODRIVER_FILE venv/include
```

Start the script:
```bash
python3 ilias_downloader.py
```

## Known issues

### Passwords

Currently passwords with a '\\' letter have problems getting escaped and do not work.<br/>
You can change your password or fix the issue.
