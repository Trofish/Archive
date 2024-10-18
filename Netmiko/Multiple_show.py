__author__ = "Yong Peng"
__version__ = "1.3"

import getpass
import os
from netmiko import ConnectHandler

"""
纯粹的脚本.
通过Netmiko对批量的相同平台的设备通过双因素认证后，执行批量的相同命令.
"""

with open('./device_list.txt', 'r') as f:
    device_list = [i.strip() for i in f.readlines() if len(i.strip()) != 0]  # read the device list.

list_failed = []

print("Data will be collected on below devices:")
for device in device_list:
    print(device)

go = input("\nTotal %i device(s).\nPress y to continue: " % (len(device_list)))

if go != "y" and go != "Y":
    exit(2)

u_id = input("Please input login ID:")
factor_1 = getpass.getpass("ID Password for login:")

with open("show_cmd.txt", 'r') as f:
    cmd_4_IOS = [i for i in f.readlines() if i.strip()]


def send_show_command(devices, commands):
    # outputPath = './output/' + str(device['host']) + '.txt'
    # result = open(OutputPath, 'w')
    if not os.path.exists("./output"):
        os.mkdir("./output")

    flag = True
    output = dict()
    try:
        with ConnectHandler(**devices) as ssh:
            ssh.enable()
            for command in commands:
                output[command] = ssh.send_command(command, strip_command=False, strip_prompt=False, read_timeout=20, )
                # result.write(output + "\n" + 30 * '+' + "\n" + "\n")

        output_path = './output/' + str(devices['host']) + '.txt'
        with open(output_path, "w") as f:
            for k, v in output.items():
                f.write(k + "\n" + v + "\n" + 40 * "#" + "\n\n\n")

    except Exception as error:
        print(error)
        flag = False
    # result.close()
    if flag:
        print("Data collection on %s is done. \n \n" % (j))
    else:
        print("Data collection for %s is NOT done. \n \n" % (j))
        list_failed.append(j)


indicator = 0
switch = {}

for j in device_list:
    # switch["device_type"] = "ruckus_fastiron"
    # switch["device_type"] = "cisco_nxos"
    switch["device_type"] = "cisco_ios"
    # switch["device_type"] = "arista_eos"
    switch["host"] = j
    switch["username"] = u_id
    indicator += 1
    factor_2 = str(input("Trying to login to %s, enter DUO Code (%i/%i):" % (j, indicator, len(device_list))))
    switch["password"] = str(factor_1) + str(factor_2)
    switch['secret'] = ''
    switch['port'] = 22
    send_show_command(switch, cmd_4_IOS, )

print("All collection is done.")

if len(list_failed) != 0:
    print("Data collection failed on %i device(s):" % (len(list_failed)))
    for i in list_failed:
        print(i)
