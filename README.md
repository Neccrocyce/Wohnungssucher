## Description
Wohnungssucher automatically searches for rental apartments and notifies users by email when new listings are found. 
It supports customizable search criteria including maximum rent, minimum apartment size, and more. 
To avoid repetition, it keeps track of already known listings and only informs users about truly new offers.
Currently supported portals include:
- Mietwohnungsboerse
- GVG


## Installation
### Linux
Run
```
setup.sh
systemctl enable wohnungssucher.timer
systemctl start wohnungssucher.timer
```

This sets up a systemd service named wohnungssucher, which runs daily at 2:00 p.m. under a dedicated user account, wsuser.

### Windows
Create a scheduled task that runs main.py once per day.


## Configuration
All configuration settings must be defined in the user_configuration.py file. 
If you followed the Linux installation guide, this file is located at:  ```/opt/wohnungssucher/user_configuration.py```


## Usage
If you've completed the steps above, wohnungssucher will run automatically once per day. No additional action is necessary.

### Manual execution
Execute
```
main.py
```

### Test email service
Execute to send a test email
```commandline
mail_tester.py
```
