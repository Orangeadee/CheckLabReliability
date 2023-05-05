"""
By Huilin Zhang

Description
   Check rechability of Tokalabs and license expiration date.

Usage:
  tokalab = TokaConnect(configsFile)

  tokalab.pingTokalabs(): ping tokalabs
  tokalab.checkLicense(): remote login and check expiration date

Command line:
   Modify yaml file:
    - Enter your gitlab pipeline information.

   python3 enterCommand.py -d pipeTest -i gitConfigs.yml
"""

import paramiko, os, time
from ruamel.yaml import YAML

class TokaConnect:
    def __init__(self, configsFile) -> None:
        self.configsFile = configsFile
        yaml = YAML()
        with open(self.configsFile) as configs:
            loadInfo = yaml.load(configs)
        
        self.validConfigs = True
        try:
            self.tokaIp    = loadInfo['tokalabIp']
            self.username  = loadInfo['username']
            self.password  = loadInfo['password']
        except:
            print(f'Error: invalid configs file: {self.configsFile}')
            self.validConfigs = False
    
    # Determine whether user entered correct configs file.
    def getValidConfigs(self) -> bool:
        return self.validConfigs

    # Check if tokalabs is rechable
    def pingTokalabs(self) -> bool:
        response = os.system("ping -c 1 " + self.tokaIp)
        if response == 0:
            print("{}, is up!".format(self.tokaIp))
            return True
        else:
            print("{}, is down!".format(self.tokaIp))
            return False

    # Tokalabs remote login, then check license expiration date
    def checkLicense(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.tokaIp, username=self.username, password=self.password)
        except paramiko.SSHException:
            raise Exception('\nSSH Failed to connect: {}.format(ip)')

        command = "show license"
        stdin, stdout, stderr = ssh.exec_command(command)
        while not stdout.channel.exit_status_ready() and not stdout.channel.recv_ready():
            time.sleep(1)
        stdoutString = stdout.readlines()
        stderrString = stderr.readlines()
        print(f"stdout: {stdoutString} \nstderr: {stderrString}")
        ssh.close()
        stdout.close()
        stderr.close()
        stdin.close()
        return stdoutString
        
