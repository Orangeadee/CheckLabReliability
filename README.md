# CheckLab

## DESCRIPTION
- The purpose of this script to include all 3 classes created earlier and perform all the tasks.

- The script takes an option as type of task and a configs file as input.

- The script involves 4 functions:
    - All functions are using classes implemented in other scripts.
    - The 4 functions:
        - `gitlabTest(configs)` run pytest pipeline on Gitlab.
        - `gitlabReport(configs)` get results for a specific test (using pipeline id).
        - `pingDev(configs)` ping all devices listed in excel sheet.
        - `tokalabs(configs)` tokalabs remote login, then check license expiration date.

## REQUIREMENTS
- python 3+
- A config file
- pip install pandas paramiko openpyxl PyYaml
## CAVEATS:  
- Configs file path must be full path

# Modules
# gitlabConnect

## DESCRIPTION
- The purpose of this script is to run pytest pipeline on Gitlab

- The script takes gitlab rest api as input and trigger the pipeline test remotely.

- The script involves 1 class: 3 public methods and 2 private methods.
    - Create a class object 'GitlabConnect' that loads all information from yaml file in _init_()
    - The 4 public functions:
        - `triggerPipeline()` run pytest pipeline on Gitlab.
        - `getReport()` print the result summary after pytest finished running.
        - `getValidConfigs()` return validation of configs file.
        - `printInfo()` print contents loaded from yaml file.
    - The 2 private functions:
        - `__singlePing()` ping one device at a time
        - `__multPing()` use threading to ping multiple devices at once

## REQUIREMENTS
- python 3+
- A gitConfigs.yml config file
- Gitlab Rest API and secret token for authentication.

### INSTALL PACKAGE
- `pip/pip3 install pyyaml`
- `pip/pip3 install ruamel.yaml`
- `pip/pip3 install requests`

## CAVEATS:  
- Configs file path must be full path
### Configs File
- `trigger_url` = Rest api for running a pipeline test
- `report_url` = Rest api for retrieving a test report summary
- `token` = Secret token created by user for authentication before running the test
- `branch` = Indicate the branch/tag name for pipeline test
- `hosts` = List of devices tested before running the pipeline test
### Need Help Getting Rest API?
- Go to gitlab, open settings and click on CI/CD option
- Look for Pipeline triggers and click on expand
- You will see an option "Use cURL" like this:
`curl -X POST \`
`    -F token=TOKEN \`
`    -F ref=REF_NAME \`
`    http://testops.com:8008/api/v4/projects/3/trigger/pipeline`
- Replace `testtops.com` with deveopServer ip


# ping

## DESCRIPTION
- The purpose of this script is to check reachability for all lab devices

- The script takes an excel sheet as input and ping all devices listed in the sheet.

- The script involves 1 class: 3 public methods and 3 private methods.
    - Create a class object 'Ping' that loads all information from yaml file in _init_()
    - The 3 public functions:
        - `pingAllDevices()` use threading to ping all ip addresses at once
        - `writeToFile()` write all ping failure devices to the output file
        - `getValidConfigs()` return validation of configs file.
    - The 3 private functions:
        - `_readConfigs()` loading all information from configs file
        - `_parseIpAddress()` parse ip address from excel sheet
        - `_ipPinger()` helper function for threading

## REQUIREMENTS
- python 3+
- A pingConfigs.yml config file
- Excel file for input
- A summary text file for output

### INSTALL PACKAGE
- `pip/pip3 install pyyaml`
- `pip/pip3 install ruamel.yaml`

## CAVEATS:  
- The devices will not be pinged if missing an ip address

### Configs File
- `sheetName` = the sheet name in excel file
- `headerRefs` = enter the full name of the columns instead of only number


# tokaConnect

## DESCRIPTION
- The purpose of this script is to check reachability for tokalabs and its exipration date

- The script takes a configs file as input.

- The script involves 1 class: 3 public methods.
    - Create a class object 'TokaConnect' that loads all information from yaml file in _init_()
    - The 3 public functions:
        - `pingTokalabs()` see if tokalabs is rechable
        - `checkLicense()` ssh to tokalabs and check license date by entering command 'check license'
        - `getValidConfigs()` return validation of configs file

## REQUIREMENTS
- python 3+
- A tokaConfigs.yml config file

### INSTALL PACKAGE
- `pip/pip3 install ruamel.yaml`

## CAVEATS:  
- The license cannot be checked if tokalabs is down.

### Configs File
- `tokalabIp` = ip address for lokalabs
- `username` = remote login username
- `password` = remote login password
