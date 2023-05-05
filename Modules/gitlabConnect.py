"""
By Huilin Zhang

Description
   Trigger a pipeline test on Gitlab.

Usage:
  gitlab = GitlabConnect(configsFile)
      
  gitlab.triggerPipeline(): running a pipeline test
  gitlab.getReport(): printing summary for specific pipeline test result

Command line:
   Modify yaml file:
    - Enter your gitlab pipeline information.

   python3 enterCommand.py -d pipeTest -i gitConfigs.yml

"""

import requests, time, json
from threading import *
from ruamel.yaml import YAML
from subprocess import Popen, PIPE

class GitlabConnect:
    def __init__(self, configsFile) -> None:
        self.dev_names = []
        self.dev_ip = []
        # Open configs file
        self.configsFile = configsFile
        self.report_details = {'pipeline_id': '', 'testname': '', 'branch': '', 'start_time': '', 'result': ''}
        yaml = YAML()
        with open(self.configsFile) as configs:
            loadInfo = yaml.load(configs)
        
        self.validConfigs = True
        # Try loading data, set validConfigs to False if failed loading
        try:
            self.trigger_url = loadInfo['trigger_url']
            self.report_url  = loadInfo['report_url']
            self.branch      = loadInfo['branch']
            self.token       = loadInfo['token']
            self.sdbox_dev   = loadInfo['hosts']
            self.emailRecv   = loadInfo['email']
            self.pipe_id     = loadInfo['pipeId']

            for key, val in self.sdbox_dev.items():
                self.dev_names.append(key)
                self.dev_ip.append(val)
        except:
            print(f'Error: invalid configs file: {self.configsFile}')
            self.validConfigs = False
        self.failure_devices = []
        self.summary = ''

    # Single ping that will be used in threading.
    def __singlePing(self, host_list, host_name):
        ip = host_list[0]
        name = host_name[0]
        with Popen(f"ping -c 4 {host_list[0]}".split(), stdout=PIPE, text=True) as pingProcess:
            pingProcess.wait()
            if pingProcess.poll():
                print(f'{ip} {name} is down')
                self.failure_devices.append(ip)
            else:
                print(f'{ip} {name} is up')
        print()

    # Use threading to ping multiple devices at once.
    def __multPing(self):
        myThread = []
        for i in range(len(self.sdbox_dev)):
            t = Thread(target=self.__singlePing, args=(self.dev_ip[i:i+1], self.dev_names[i:i+1]))
            myThread.append(t)
            t.start()

        # wait for all threads to finish
        for t in myThread:
            t.join()

    # Determine whether user entered correct configs file.
    def getValidConfigs(self):
        return self.validConfigs

    # Return the current test status: success / failed
    def getTestStatus(self):
        return self.summary['status']

    # Start a pipeline test on gitlab
    #   - Encode secret token and branch name
    #   - Request pipeline triggering if test devices are ready.
    #   - Return a boolean stating the triggering status:
    #       - True = success; False = fail
    def triggerPipeline(self) -> bool:
        self.__multPing()
        data = {
            'token': self.token,
            'ref': self.branch
        }
        if not self.failure_devices:
            try:
                res = requests.post(self.trigger_url, json=data)
                self.summary = res.json()
                self.pipe_id = self.summary['id']

                # Overwrite pipeline id in configs
                yaml = YAML()
                with open(self.configsFile) as f:
                    doc = yaml.load(f)
                doc['pipeId'] = self.pipe_id
                with open(self.configsFile, 'w') as f:
                    yaml.dump(doc, f)
            except:
                print('Failed to start test.')
                return False
            print(f'Test started...\nThe test #{self.pipe_id} is {self.summary["status"]}\n')
            return True

        print('Devices are not ready for pipeline test, please try again later.')
        return False
        
    # Request a report for a single test
    #   - If current pipeline is still testing
    #       - wait for test to be finished
    #   - Request for test report with pipeline id
    #   - Print out summary
    def getReport(self):
        self.report_url = self.report_url + '/' + str(self.pipe_id)
        
        if self.summary != '':
            while(self.summary['status'] == 'created' or self.summary['status'] == 'running'):
                time.sleep(120)
                report = requests.get(self.report_url)
                self.summary = report.json()

        else:
            report = requests.get(self.report_url)
            self.summary = report.json()
        
        self.report_details['pipeline_id'] = self.summary['id']
        self.report_details['testname'] = self.summary['detailed_status']['details_path']
        self.report_details['branch'] = self.summary['ref']
        self.report_details['start_time'] = self.summary['started_at']
        self.report_details['result'] = self.summary['status']

        print(f'Current pipeline #{self.pipe_id} test status: {self.summary["status"]}')
        print(f'Full report: \n{self.report_details}')
        return self.report_details

    def getFailReport(self):
        fail_url = self.report_url + '/jobs?scope[]=failed'
        res = requests.get(fail_url)
        report = res.json()

        self.report_details['pipeline_id'] = self.summary['id']
        self.report_details['testname'] = report[0]['name']
        self.report_details['branch'] = report[0]['ref']
        self.report_details['start_time'] = report[0]['started_at']
        self.report_details['result'] = report[0]['status']
        print(f"\nFailed test report: \n{self.report_details}")
        return self.report_details
    
    def writeToFile(self, output, data):
        # Write result to report.txt
        data = json.dumps(data, indent = 4)
        with open(output, 'a') as file:
            file.write('Gitlab Test Result:\n')
            file.write(data)
            file.write('\n')

    def writeToFileFail(self, output, data):
        # Write failed test result to report.txt
        data = json.dumps(data, indent = 4)
        with open(output, 'a') as file:
            file.write('Gitlab Failed Test Result:\n')
            file.write(data)
            file.write('\n')
