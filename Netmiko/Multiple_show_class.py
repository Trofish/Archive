__author__ = "Yong Peng"
__version__ = "1.3"

import os
from netmiko import ConnectHandler

"""
基于Netmiko的类, 方便在其它脚本调用.
通过Netmiko对批量的相同平台的设备通过双因素认证后，执行批量的相同命令.
"""

class MultipleShow(object):
    def __init__(self, device_file="device_list.txt", cmd_set="show_cmd.txt", list_failed=[]):
        self.device_file = device_file
        self.cmd_set = cmd_set
        self.list_failed = list_failed
        self.u_id = None
        self.factor_1 = None
        self.device_type = None

        with open(self.device_file, 'r') as f:
            self.device_list = [i.strip() for i in f.readlines() if len(i.strip()) != 0]  # read the device list.

        with open(self.cmd_set, 'r') as f:
            self.cmd = [i for i in f.readlines() if i.strip()]

        print("Data will be collected on below devices:")
        for device in self.device_list:
            print(device)

        go = input("\nTotal %i device(s).\nPress y to continue: " % (len(self.device_list)))

        if go != "y" and go != "Y":
            exit(2)

    def send_show_command(self, devices, commands):
        # outputPath = 'c:/script/output/' + str(device['host']) + '.txt'
        # result = open(OutputPath, 'w')
        if not os.path.exists("c:/script/output"):
            os.mkdir("c:/script/output")

        flag = True
        output = dict()
        try:
            with ConnectHandler(**devices) as ssh:
                ssh.enable()
                for command in commands:
                    output[command] = ssh.send_command(command, strip_command=False, strip_prompt=False, read_timeout=20, )
                    # result.write(output + "\n" + 30 * '+' + "\n" + "\n")

            output_path = 'c:/script/output/' + str(devices['host']) + '.txt'
            with open(output_path, "w") as f:
                for k, v in output.items():
                    f.write(k + "\n" + v + "\n" + 40 * "#" + "\n\n\n")

        except Exception as error:
            print(error)
            flag = False
        # result.close()
        if flag:
            print("Data collection on %s is done. \n \n" % (devices['host']))
        else:
            print("Data collection for %s is NOT done. \n \n" % (devices['host']))
            self.list_failed.append(devices['host'])

    def run(self, u_id, factor_1, device_type="cisco_ios"):
        self.u_id = u_id
        self.factor_1 = factor_1
        self.device_type = device_type

        indicator = 0
        switch = {}

        for j in self.device_list:
            # switch["device_type"] = "ruckus_fastiron"
            # switch["device_type"] = "cisco_nxos"
            # switch["device_type"] = "cisco_ios"
            # switch["device_type"] = "arista_eos"
            switch["device_type"] = self.device_type
            switch["host"] = j
            # switch["username"] = u_id
            switch["username"] = self.u_id
            indicator += 1
            factor_2 = str(input("Trying to login to %s, enter DUO Code (%i/%i):" % (j, indicator, len(self.device_list))))
            switch["password"] = str(self.factor_1) + str(factor_2)
            switch['secret'] = ''
            switch['port'] = 22
            self.send_show_command(switch, self.cmd, )

            print("All collection is done.")

            if len(self.list_failed) != 0:
                print("Data collection failed on %i device(s):" % (len(self.list_failed)))
                for i in self.list_failed:
                    print(i)
