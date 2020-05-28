# kit_ilias_sync
Ilias Sync script for KIT

Currently just for firefox and non pdf files *wink*

Have an eye for the script output for the first few files.
If you are not logged in you see a loop.
You should see the courses from your dashboard

## Requirements

additional to python libraries:

### Geckodriver

https://github.com/mozilla/geckodriver/releases
Necessary to start firefox workers

### Cookies

Cookies get loaded from the firefox cookies sqlite file.
You need to have active ilias cookies your firefox instance.
Open a new window and login to your ilias accout. Repeat 2 time. Dont know why its not working first time.

## Getting Started

Move config.yml.back to config.yml

Fill in config

Launch python file

## TODOs

 * [ ] Handle if user is not logged in
 * [ ] Handle pdf files
 * [ ] Handle forum
 * [ ] Update Readme
    * [ ] python requirements
    * [ ] Getting Started
