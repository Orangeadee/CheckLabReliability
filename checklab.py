#==============================================================================
# KEYSIGHT TECHNOLOGIES SOFTWARE COPYRIGHT
#
#  Copyright (c) KEYSIGHT TECHNOLOGIES 2020.  All rights reserved.
#
# KEYSIGHT TECHNOLOGIES MAKES NO WARRANTY OF ANY KIND WITH REGARD
# TO THIS SOFTWARE, INCLUDING BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  Keysight Technologies
# shall not be liable for errors contained herein or direct, indirect,
# special, incidental, or consequential damages in connection with furnishing,
# performance, or use of this software.
#
# RESTRICTED RIGHTS LEGEND  Use, duplication or disclosure by government is
# subject to restrictions as set forth in subdivision (c)(1)(ii) of the
# Rights in Technical Data and Computer Software Clause 252.227.7013.
#
# ==============================================================================
### BEGIN_IS ###
#===============================================================================
#
#  MODULE NAME: 
#
#  SOURCE FILE: enterCommand.py
#
#  CALLED FROM: CLI
#
#  DESCRIPTION: 
#    - The script executes commands for 3 modules: gitlabConnect, ping, tokaCOnnect.
#    - The script takes a configs file as input, perform function based on options
#      that user entered.
#    - The script involves 4 functions: to perform different task in the script.
#        - pings: gitlabReport(configs), get pipeline test report on gitlab
#        - tokalabs: tokalabs(configs), check tokalabs license exipration status
#        - pipeTest: gitlab(configs), running pipeline test on gitlab
#        - pipeReport: gitlabReport(configs), get pipeline test report on gitlab
#   
#   REQUIREMENTS:
#      - python 3+
#      - pip install pandas paramiko openpyxl PyYaml
#
#   CAVEATS:  Description options are: pings | gitlabs | pipeTest | pipeReport
#             Must enter full path for configs file
#               Ex: /Users/huilzhan/Documents/Python/project_2/configs.yml
#
#   VERSION:  1.0
#
#   COMPANY:  Keysight Technologies
#
#   PROPER CALL OF THIS PROCEDURE: python3 enterCommand.py  <description>[required]  <configs file>[required]
#   ASK FOR PROPER COMMAND (HELP): python3 enterCommand.py --help | python3 enterCommand.py -h
#
#===============================================================================
#-------------------------------------------------------------------------------
# MODIFICATION HISTORY
#
# ENGINEER NAME           DATE                   DESCRIPTION
# -------------           ----                   -----------
# Huilin Zhang            04/12/2022             Create argparse
# Huilin Zhang            04/17/2022             Modified argparse
# Huilin Zhang            04/24/2022             Create full report
#-------------------------------------------------------------------------------
### END_IS ###

from Modules import gitlabConnect, ping, tokaConnect
import argparse, yaml

# Default variables
options = ['gitlabTest','gitlabReport','pings','tokalabs','all']
loadConfigs = { 'gitlab': '', 'pings': '', 'tokalabs': ''}

# Option pings: create Pings object to ping all devices listed in excel
def pingDev(configs, report):
    pings = ping.Ping(configs)
    if pings.getValidConfigs():
        pings.pingAllDevices()
        pings.writeToFile(report)
        print('Pinging process completed.\n')

# Option tokalabs: create TokaConnect object to check license expiration date
def tokalabs(configs, report):
    toka = tokaConnect.TokaConnect(configs)
    if not toka.getValidConfigs():
        return
    if toka.pingTokalabs():
        print('Tokalabs is ready, checking license...')
        res = toka.checkLicense()

        # Write result to report.txt
        with open(report, 'a') as data:
            data.write('Tokalabs License Expiration Date:\n')
            data.writelines(res)
            data.write('\n')
    else:
        print('Error: Failed to reach Tokalabs, please try again later.')

# Option gitlabTest: create GitlabConnect object to run a gitlab test
def gitlabTest(configs, report):
    gitlab = gitlabConnect.GitlabConnect(configs)
    if not gitlab.getValidConfigs():
        return
    if gitlab.triggerPipeline():
        # Print the test report
        res_json = gitlab.getReport()
        gitlab.writeToFile(report, res_json)

        if gitlab.getTestStatus() == 'failed':
            failed_json = gitlab.getFailReport()
            gitlab.writeToFileFail(report, failed_json)
        print('Triggering pipeline completed.')

# Option gitlabReport: create GitlabConnect object to request a gitlab test report
def gitlabReport(configs, report):
    gitlab = gitlabConnect.GitlabConnect(configs)
    if gitlab.getValidConfigs():
        res_json = gitlab.getReport()
        gitlab.writeToFile(report, res_json)

        if gitlab.getTestStatus() == 'failed':
            failed_json = gitlab.getFailReport()
            gitlab.writeToFileFail(report, failed_json)

# Add argument options: input - configs filename; options - type of test.
parser = argparse.ArgumentParser(
    description='Example: enterCommand.py -o option(s) -i configs.yml'
)

parser.add_argument('-o', dest = 'options', choices = options, nargs = "+", help='Options: pings / tokalabs / gitlabTest / gitlabReport / all', default = None, required = True)
parser.add_argument('-i', dest = 'configs', type = str, help = 'The main configs file name (full path)', default = None, required = False)
args = parser.parse_args()

# Read and load configs file
mainConfigs = args.configs if args.configs else '/opt/CheckLabDevices/Configs/checklabConfigs.yml'
with open(mainConfigs, 'r') as file:
    loadConfigs = yaml.safe_load(file)


pingConfigsList = loadConfigs['pings']
tokaConfigsList = loadConfigs['tokalabs']
gitlabConfigsList = loadConfigs['gitlab']
reportFile = loadConfigs['report']

# Erase all previous data in the output file
open(reportFile, 'w').close() 

# Execute one or more options
for option in args.options:

    # Option: all
    #   - Call all functions and then exit the loop
    if 'all' in args.options:
        for pingConfigs in pingConfigsList:
            pingDev(pingConfigs, reportFile)
        for tokaConfigs in tokaConfigsList:
            tokalabs(tokaConfigs, reportFile)
        for gitlabConfigs in gitlabConfigsList:
            gitlabTest(gitlabConfigs, reportFile)
        break

    if option == 'pings':
        for pingConfigs in pingConfigsList:
            pingDev(pingConfigs, reportFile)
    if option == 'tokalabs':
        for tokaConfigs in tokaConfigsList:
            tokalabs(tokaConfigs, reportFile)
    if option == 'gitlabTest':
        for gitlabConfigs in gitlabConfigsList:
            gitlabTest(gitlabConfigs, reportFile)
    if option == 'gitlabReport':
        for gitlabConfigs in gitlabConfigsList:
            gitlabReport(gitlabConfigs, reportFile)
