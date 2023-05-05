"""
By Huilin Zhang

Description
   Check reachability for all lab devices.

Usage:
  pings = Ping(configsFile)
      
  pingAllDevices(): use threading to ping all ip addresses listed in excel sheet

  Example:
    configsFile = '/Users/huilzhan/Documents/Python/project_2/pingConfigs.yml'
    test1 = Ping(configsFile)
    test1.pingAllDevices()
    test1.writeToFile()

Command line:
   Modify yaml file:
    - Excel file(full path) and sheet name
    - Header names
        - Device name column
        - Device ip address column
    - Text file for summary

   python3 entercommand.py -d pings -i pingConfigs.yml
"""

import re
from threading import *
from time import *
from ruamel.yaml import YAML
from subprocess import Popen, PIPE
import pandas as pd

class Ping:
    def __init__(self, configsFile) -> None:
        self.configsFile = configsFile
        self.ipList = []
        self.deviceList = []
        self.failureDevices = []
        self.passedDevices = []
        self.inputFile = ''
        self.validConfigs = self.__readConfigs()
        pass

    # Load configs file
    def __readConfigs(self):
        yaml = YAML()
        yaml.explicit_start = False
        yaml.indent(mapping=3)
        yaml.preserve_quotes = True

        with open(self.configsFile) as configs:
            loadInfo = yaml.load(configs)

        try:
            self.inputFile  = loadInfo['inputFile']
            sheetName  = loadInfo['sheetName']
            headerRefs = loadInfo['headerRefs']
        except:
            print(f'Error parsing configs file: {self.configsFile}')
            return False

        print(f'\nInput File: {self.inputFile}')
        calabases_lab_devop = pd.read_excel(self.inputFile, sheet_name=sheetName)
        deviceIpIndex  = headerRefs['deviceIP']
        deviceName     = headerRefs['deviceName']

        for i, row in calabases_lab_devop.iterrows(): 
            ip = self.__parseIpAddress(str(row[deviceIpIndex]))
            if ip == '-1' or row[deviceIpIndex] == None or str(row[deviceName]) == 'nan':
                continue
            self.ipList.append(ip)
            self.deviceList.append(row[deviceName])
        return True

    # Parse IP address into a form of 00.000.0.00
    def __parseIpAddress(self, ipAddress):
        # Searching for IP address pattern.
        parseIP = '-1'
        match = re.search('(http://|https://)?([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)(:([0-9]+))?', ipAddress)
        if match:
            parseIP = match.group(2)
        return parseIP

    # Single ping method used in threading
    def __ipPinger(self, ip_list, device_list):
        device = device_list[0]
        ip = ip_list[0]
        with Popen(f"ping -c 1 {ip}".split(), stdout=PIPE, text=True) as pingProcess:
            pingProcess.wait()
            if pingProcess.poll():
                print(f'{ip} [{device}] is down')
                failureDevice = { 'deviceName': device, 'IP': ip }
                self.failureDevices.append(failureDevice)

            else:
                print(f'{ip} [{device}] is up')
                passDevice = { 'deviceName': device, 'IP': ip }
                self.passedDevices.append(passDevice)

    # Determine whether user entered correct configs file.
    def getValidConfigs(self):
        return self.validConfigs

    # Ping devices at once using threading
    def pingAllDevices(self):
        myThread = []
        for i in range(len(self.ipList)):
            t = Thread(target=self.__ipPinger, args=(self.ipList[i:i+1], self.deviceList[i:i+1],))
            myThread.append(t)
            t.start()

        # wait for all threads to finish
        for t in myThread:
            t.join()

    # Write a summary report for all ping failures
    def writeToFile(self, output):
        print('\nWriting to file...\n')
        with open(output, 'a') as data:
            print("Rechable devices:")
            data.write("Rechable devices:\n")
            index = 1
            for device in self.passedDevices:
                print("{0:2}. {1:16} {2}".format(index, device['IP'], device['deviceName']))
                data.write("{0:2}. {1:16} {2}\n".format(index, device['IP'], device['deviceName']))
                index += 1
            data.write('\n')
            print("\nDevices below are not reachable:")
            data.write("Devices below are not reachable:\n")
            index = 1
            for device in self.failureDevices:
                print("{0:2}. {1:16} {2}".format(index, device['IP'], device['deviceName']))
                data.write("{0:2}. {1:16} {2}\n".format(index, device['IP'], device['deviceName']))
                index += 1
            data.write('\n')
        print('Done.')


