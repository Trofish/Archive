__author__ = "Yong Peng"
__version__ = "1.2"

import pandas as pd
import os
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
# from nornir_utils.plugins.functions import print_result

"""
I don't have a dedicated server to run script with a credential with static password.
I have to run script with my own ID and 2 factors password.

This class is to Convert excel spreadsheet to a Python list which consists of dictionaries.
Later, I will pass the dictionaries to Nornir inventory by using FlatDataInventory inventory plugin. 

The purpose of all of this is that, when I leverage the advantages of Nornir which Netmiko doesn't have, I have to
tackle with 2 factors authentication. 

将excel文件转换为字典, 以列表形式传递给Nornir, 传递过程中，执行最关键的操作: 完成登录设备时的双因素动态密码认证. 
"""


class ExcelReader(object):
    def __init__(self, ):
        pass

    """
    Read excel file and return list contains of dictionary.
    通过excel生成一个字典组成的列表. 
    """

    @classmethod
    def read_excel(cls, excel_file_name):
        cls.excel_file_name = excel_file_name
        df = pd.read_excel(excel_file_name, converters={"No.": int, "SSH Port": int})

        """
        Make sure we can print all columns in one line.
        """
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)

        # delete empty rows, or rows where any of the 4 columns "No.", "Hostname", "Host IP", "OS Type" is null

        # df = df[~df["No."].isnull()]
        # df = df[df["No."].notnull()]
        subset = ["Name", "Hostname", "Platform"]
        df = df.dropna(subset=subset)

        # delete empty columns
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        # delete duplicated rows based on "Hostname"
        df.drop_duplicates(subset="Name", keep="first", inplace=True, ignore_index=True)

        # Replace NAN as an empty string "".  otherwise, when generate a dictionary, it will be an invalid
        # K, V pair: "UID":NAN

        df = df.fillna("")

        # generate a dictionary, key is column name, value is cell
        col = df.columns.tolist()  # put columns in a list
        my_inventory = list()

        for i in df.values:
            k = dict(zip(col, i))  # generate a dict
            my_inventory.append(k)

        print("\nExecution on below devices:\n")
        for i in my_inventory:
            print(i["Name"])
        print("\nTotal above %i devices.\n" % (len(my_inventory)))

        return my_inventory


class TwoFactorAuth(object):
    def __init__(self, device_list, commands, username, password):

        # self.inventory_file = inventory_file
        # self.device_elements_list = ExcelReader.read_excel(self.inventory_file)
        # self.username = input("Please input login ID:")
        # self.password = getpass.getpass("ID Password for login:")

        self.device_list = device_list
        self.commands = commands
        self.username = username
        self.password = password

    def elements_generate(self, device_elements, numb, list_len):
        device = {'name': 'switch_1', 'hostname': '127.0.0.1',
                  'platform': 'ruckus_fastiron', 'port': 22, 'username': 'adnin',
                  'password': '1234', 'city': 'csj', 'model': 'ICX7450-48P',
                  'netmiko_timeout': 180, 'netmiko_secret': '123456',
                  'netmiko_banner_timeout': '30', 'netmiko_conn_timeout': '20'}

        """FlatDataInventory plugin"""
        device["name"] = device_elements["Name"]
        device["hostname"] = device_elements["Hostname"]

        if device_elements["UID"].strip():
            device["username"] = device_elements["UID"].strip()
            device["password"] = device_elements["PWD"].strip()
        else:
            device["username"] = self.username
            dynamic_pwd = str(input("Trying to login to %s, enter 2FA Code (%i/%i): " % (device["name"], numb, list_len)))
            device["password"] = self.password + dynamic_pwd

        if device_elements["Enable Secret"].strip():
            device['netmiko_secret'] = device_elements["Enable Secret"]

        device["platform"] = device_elements["Platform"]
        device['port'] = 22 or device_elements["SSH Port"]

        data = [device]
        return data

    def run(self,):
        with open(self.commands, 'r') as f:
            cmd_set = [i.strip() for i in f.readlines()]

        if not os.path.exists("./output"):
            os.mkdir("./output")

        failed_list = set()
        list_len = len(self.device_list)
        numb = 0

        for i in self.device_list:
            numb += 1
            data = self.elements_generate(i, numb, list_len)

            runner = {
                "plugin": "threaded",
                "options": {
                    "num_workers": 1,
                },
            }
            inventory = {
                "plugin": "FlatDataInventory",  # inventory plugin 重点
                "options": {
                    "data": data,
                },
            }

            device_name = data[0]["name"]

            nr = InitNornir(runner=runner, inventory=inventory)

            try:
                for j in cmd_set:
                    output = nr.run(task=netmiko_send_command, command_string=j, read_timeout = 300)
                    if output[device_name].failed:
                        failed_list.add(device_name)
                        print("\nERROR on login or command execution on %s!\n" % device_name)
                        break

                    with open("./output/%s.txt" % device_name, "a") as r:
                        r.write(j + ":" + "\n")
                        r.write(output[device_name].result + "\n" + 30 * '#' + "\n" + "\n" + "\n" + "\n")
                    # print(output[device_name].result)
                    # print_result(output)
                    print("Data collection has been done on %s\n\n " % device_name)


            except Exception as error:
                failed_list.add(device_name)
                print("ERROR on login or command execution on %s!" % device_name)

                """
                output = nr.run(task=netmiko_send_command, command_string="show version | in up")
                print(output[data[0]["name"]].result)
    
                # print_result(output)
                # 测试下来可以在实例化后粗暴地用这种奇葩的重复方式来执行多行命令，它不会多次登录，目前不清楚nornir什么时候断开ssh会话.
    
                output = nr.run(task=netmiko_send_command, command_string="show clock")
                print(output[data[0]["name"]].result)
                """

            if failed_list:
                print("Failed to login or execute command on below %i device(s):" % len(failed_list))
                for k in failed_list:
                    print(k)
