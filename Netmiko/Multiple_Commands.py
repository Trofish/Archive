__author__ = "Yong Peng"
__version__ = "1.4"

import os
from netmiko import ConnectHandler

"""
基于Netmiko的类, 方便在其它脚本调用.
通过Netmiko对批量的相同平台的设备通过双因素认证后，执行批量的相同命令.
此版本合并了show, configure t 两种模式.
"""

class Multiple_Commands(object):
    def __init__(self, device_file= "device_list.txt", cmd_set="cmd.txt",device_type = None, u_id = None,
                 factor_1 = None):
        self.device_file = device_file
        self.cmd_set = cmd_set
        self.device_type = device_type
        self.u_id = u_id
        self.factor_1 = factor_1
        self.secret = None
        self.list_failed = []
        self.switch = {}

        with open(self.device_file, 'r') as f:
            self.device_list = [i.strip() for i in f.readlines() if len(i.strip()) != 0]  # read the device list.

        with open(self.cmd_set, 'r') as f:
            self.cmd = [i for i in f.readlines() if i.strip()]

        print("Data will be collected on below devices:")
        for device in self.device_list:
            print(device)

        if not os.path.exists("./output"):
            os.mkdir("./output")

        go = input("\nTotal %i device(s).\nPress y to continue: " % (len(self.device_list)))

        if go != "y" and go != "Y":
            exit(2)

    def run(action):
        def wrapper_for_action(self, device_elements):
            indicator = 0

            for j in self.device_list:
                self.switch["device_type"] = self.device_type
                self.switch["host"] = j
                self.switch["username"] = self.u_id
                indicator += 1
                factor_2 = str(
                    input("Trying to login to %s, enter DUO Code (%i/%i):" % (j, indicator, len(self.device_list))))
                self.switch["password"] = str(self.factor_1) + str(factor_2)
                self.switch['secret'] = self.secret
                self.switch['port'] = 22
                # print(self.switch)
                action(self, device_elements)
        return wrapper_for_action

    @run
    def show(self, devices):
        flag = True
        output = dict()
        try:
            with ConnectHandler(**devices) as ssh:
                ssh.enable()
                for command in self.cmd:
                    output[command] = ssh.send_command(command, strip_command=True, strip_prompt=False, read_timeout=30, )
                    # result.write(output + "\n" + 30 * '+' + "\n" + "\n")

            output_path = './output/' + str(self.switch['host']) + '.txt'
            with open(output_path, "w") as f:
                for k, v in output.items():
                    f.write(k + "\n" + v + "\n" + 40 * "#" + "\n\n\n")

        except Exception as error:
            print(error)
            flag = False
        # result.close()
        if flag:
            print("Data collection on %s is done. \n \n" % (self.switch['host']))
        else:
            print("Data collection for %s is NOT done. \n \n" % (self.switch['host']))
            self.list_failed.append(self.switch['host'])

    @run
    def config(self, devices):
        flag = True
        try:
            with ConnectHandler(**devices) as ssh:
                ssh.config_mode()
                # "send_command" doesn't work in config_mode. "Generally used for show commands." - API document
                # Looks like it must be "send_config_from_file" or "send_config_set"
                # output = ssh.send_config_from_file(config_file="change_cmd.txt", strip_command=False, strip_prompt=False, read_timeout=20,)
                output = ssh.send_config_set(config_commands=self.cmd, strip_command=False, strip_prompt=False,
                                             read_timeout=20, )
                ssh.save_config()

            output_path = './output/' + str(devices['host']) + '.txt'
            with open(output_path, "w") as f:
                f.write(output + "\n" + 30 * '+' + "\n" + "\n")

        except Exception as error:
            print(error)
            flag = False

        if flag:
            print("Change on %s is done. \n \n" % (self.switch['host']))
        else:
            print("Change on %s is NOT done. \n \n" % (self.switch['host']))
            self.list_failed.append(self.switch['host'])




"""
方法一
"""
# class My_Class(object):
#     def __init__(self):
#         self.name = "Sam"
#     def my_decorator(func):   # 没有给被装饰函数传参!!!
#         def my_wrapper(self,):
#             print("Good morning.")
#             func(self, self.name)  # 这里直接调了实参!!!
#         return my_wrapper
#     @my_decorator
#     def my_func(self, arg1):     # 这里要传2个参数!!!
#         print(arg1)
#
# x = My_Class()
# x.my_func()  #TMD没任何问题!!!

"""
方法二
"""
# class My_Class(object):
#     def __init__(self):
#         self.name = "Sam"
#     def my_decorator(func):
#         def my_wrapper(self, arg_1):   # 给被装饰函数传参!!!
#             print("Good morning.")
#             func(self, arg_1)     # 这里调了形参!!!
#         return my_wrapper
#     @my_decorator
#     def my_func(self, arg_x):
#         print(arg_x)
#
# x = My_Class()
# x.my_func(x.name)      #如预期, 正常!!!