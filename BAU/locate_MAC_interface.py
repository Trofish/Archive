__author__ = "Yong Peng"
__version__ = "1.0"

import getpass
import textfsm
from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)

device_list = ['csj-b1idf32-ma-1', 'CSJ-B1IDF33-MA-1', 'csj-b1idf33-ma-2','CSJ-B3IDF3-1']
# device_list = ['CSJ-B2IDF31-MA-1', 'CSJ-B2-IDF32-1', 'CSJ-B2IDF33-MA-1']

list_failed = []

print("Check MAC on below devices:")
for device in device_list:
    print(device)

# u_id = input("Please input login ID:")
# factor_1 = getpass.getpass("ID Password for login:")
factor_1 = 'password123,'

check_mac = []
with open("MAC.txt", 'r') as f:
    mac = f.readlines()
    for i in mac:
        m = i.lower().split("-")
        m = "show mac-address | in " + str(m[0]) + str(m[1]) + "." + str(m[2]) + str(m[3]) + "." + str(m[4]) + str(m[5].strip())
        check_mac.append(m)


switch_port = {}


def check_mac_command(commands, devices):
    output_path = 'c:/script/output/' + str(devices["host"]) + '.txt'
    result = open(output_path, 'w')
    flag = True
    try:
        with ConnectHandler(**devices) as ssh:
            ssh.enable()
            port_info_list = []
            for command in commands:
                output = ssh.send_command(command, strip_command=True, strip_prompt=False, read_timeout=20, )
                result.write(output + "\n" + 30 * '+' + "\n" + "\n")
                # textfsm for command output
                with open('check_mac.textfsm') as template:
                    fsm = textfsm.TextFSM(template)
                    port_info = fsm.ParseText(output)

                if port_info:
                    for info in port_info:
                        port_info_list.append(info)

                if port_info_list:
                    switch_port[devices["host"]] = port_info_list

    except Exception as error:
        print(error)
        flag = False
    result.close()
    if flag:
        print("MAC collection on %s is done. \n \n" % (i))
    else:
        print("MAC collection on %s is NOT done. \n \n" % (i))
        list_failed.append(i)


switch = {}
for i in device_list:
    switch["device_type"] = "ruckus_fastiron"
    # switch["device_type"] = "cisco_nxos"
    # switch["device_type"] = "cisco_ios"
    # switch["device_type"] = "arista_eos"
    switch["host"] = i.strip()
    # switch["username"] = u_id
    switch["username"] = 'yong.peng@example.com'
    factor_2 = str(input("Trying to login to %s, enter DUO Code:" % (i)))
    switch["password"] = str(factor_1) + str(factor_2)
    switch['secret'] = ''
    switch['port'] = 22
    check_mac_command(check_mac, switch)

print("Script is done.\n")

if len(list_failed) != 0:
    print("Login failed on device(s):")
    for i in list_failed:
        print(i)


# print(switch_port)
if switch_port:
    for k, v in switch_port.items():
        print(str(k) + ":")
        for i in v:
            print(i[1] + "    Eth" + i[0] + "    VLAN" + i[2])

            check_mac = [i.split(" ")[-1] for i in check_mac]
            check_mac.remove(i[1])

    if check_mac:
        print("\nBelow MAC can't be seen:")
        for i in check_mac:
            print(i)

else:
    print("\nNo any findings!")
