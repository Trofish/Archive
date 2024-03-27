__author__ = "Yong Peng"
__version__ = "1.2"

import os
import re
import ipaddress
import textfsm

# get a configuration file list
file_name = os.popen("dir show_run | find \"txt\" ")
file_name_ist = []
for i in file_name:
    file_name_ist.append(i.split(" ")[-1].strip())

if not os.path.exists("./output"):
    os.mkdir("./output")

print("show run file number: %i \n" % len(file_name_ist))

header = re.compile("^interface\s+.*\d$")  # interface x/y/z, interface vlan x
# check_point1 = re.compile("^ip help.*\d$")  # ip help-address w.x.y.z, ip helper-address n w.x.y.z
# check_point2 = re.compile("^ip dhcp relay address\s+")  # for NXOS

mark_interface = re.compile("^interface\s+.*\d$")  # interface x/y/z, interface vlan x
mark_interface_ip = re.compile(
    "^ip address\s\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}[(\s\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|(\/\d{1,2})]+")


def ip_convert(i):
    if re.match(mark_interface_ip, i):
        if "/" in i:
            i = str(i.split()[2])
            interface_ip = ipaddress.IPv4Interface(i)
            return str(interface_ip.network)
        else:
            # i = str(i.split()[2]) + str(i.split()[3])
            mask_length = sum(bin(int(x)).count('1') for x in i.split()[3].split('.'))
            i = str(i.split()[2]) + "/" + str(mask_length)
            interface_ip = ipaddress.IPv4Interface(i)
            return str(interface_ip.network)


"""
Part 1: Go through each running configuration file, produce a dict as below.
{'CSJ-MDF2-MD-01': {'loopback 1': ['10.70.255.247/32', '11.71.255.247/32'], 'ethernet 1/2/5': ['10.70.255.8/31'], 
'ethernet 2/2/5': ['10.70.255.10/31']}}
"""

common_dict = {}

for file in file_name_ist:
    with open("./show_run/%s" % file, 'r') as r:

        # in case of "hostname" configuration is missing, name the new file same as backup file.
        host_name = file
        for i in r.readlines():
            i = i.strip()
            if i.startswith("hostname"):
                host_name = i.split()[1]
                # print(host_name)
                break
        r.seek(0)  # back to the beginning.

        # check each interface/SVI configuration
        config_dict = dict()
        config_list = []
        flag = True

        for j in r.readlines():
            j = j.strip()  # if an empty line in the file, j equals to "\n"
            if re.match(header, j):
                k = j
                config_dict[k] = config_list
                flag = False

            if not re.match(header, j) and not flag:
                # if j == "!" or j == "":  # "!" or an empty line means a new beginning.
                if j == "!" or j == "":  # "!" or an empty line means a new beginning.
                    flag = True
                    config_list = []  # 清空列表，供下一轮使用
                    continue
                else:
                    config_dict[k].append(j)

        # 过滤列表
        subnet_dict = {}

        for k, v in config_dict.items():
            v_list = []
            for i in v:
                if i.startswith("ip add"):
                    i = ip_convert(i)
                    v_list.append(i)
            if v_list:
                subnet_dict[k.strip("interface").strip()] = v_list

        # print(subnet_dict)

    if subnet_dict:
        common_dict[host_name] = subnet_dict

    # print(common_dict)

print("Combination of hostname, interface name and subnet: ")
for a, b in common_dict.items():
    print(a,b)
print(30 * "#", "\n")

"""
Part 2: check each subnet in "show ip route" output. 
if the subnet exists, check if it's pointing to FW.
if it exists and not pointing to FW, search the dict to figure out the hostname / interface name.
"""

svi = re.compile("^[V|v]")  # interface x/y/z, interface vlan x

with open("subnets.txt", 'r') as f:
    subnets = [i.strip() for i in f.readlines()]

print("subnets need to be checked: %i\n" % (len(subnets)))
for c in subnets:
    print(c)
print(30 * "#", "\n")

with open("c:/script/textfsm_customization/route_check_Arista.textfsm") as textfsm_f:
    fsm = textfsm.TextFSM(textfsm_f)
    with open("show_ip_route.txt", 'r') as f:
        result = fsm.ParseText(f.read())

# with open("c:/script/textfsm_customization/route_check_NXOS.textfsm") as textfsm_f:
#     fsm = textfsm.TextFSM(textfsm_f)
#     with open("show_ip_route.txt", 'r') as f:
#         result = fsm.ParseText(f.read())

# with open("c:/script/textfsm_customization/route_check_Ruckus.textfsm") as textfsm_f:
#     fsm = textfsm.TextFSM(textfsm_f)
#     with open("show_ip_route.txt", 'r') as f:
#         result = fsm.ParseText(f.read())

# result = result1 + result2 +result3

route = [i[0].strip() for i in result]

print("Routing Table Output:")

for x in result:
    print(x)
print(30 * "#")
print("\n\n")

# for y in route:
#     print(y)
# print(30 * "#")
# print("\n\n")

fw = ["10.186.1.1", "10.186.1.9", "10.186.1.17", "10.198.8.35", "10.198.8.129", ]

list_not_exist_1 = []   # 路由表中不可见,但有svi
list_not_exist_2 = []   # 路由表中不可见,但有l3 interface (not svi)
list_not_exist_3 = []   # 路由表中不可见,也没有任何svi/l3 interface
list_exist_with_svi = []
list_exist_l3_not_svi = []
list_exist_without_any_l3 = []
list_exist_without_l3_and_behind_fw = []


print("Validation summary(for copy and paste):")
print(50 * "@",)
for i in subnets:
    if i not in route:
        # print(i, "Not_Exist")
        # list_not_exist.append(i)

        set_mark = False
        for k1, v1 in common_dict.items():  # 查找是否有SVI
            for k2, v2 in v1.items():
                if i in v2:
                    if re.match(svi, k2):
                        print(i, "not_in_routing_table" + "_" + k1 + "_" + k2)
                        list_not_exist_1.append(i)
                        set_mark = True
                        break

                    else:
                        print(i, "not_in_routing_table" + "_" + k1 + "_" + k2)
                        list_not_exist_2.append(i)
                        set_mark = True
                        break

            if set_mark:
                break

        if i not in list_not_exist_1 and i not in list_not_exist_2:
            print(i, "not_in_routing_table,no_l3,no_svi")
            list_not_exist_3.append(i)

    elif i in route:  # 先看是否有SVI, 再看是否下一跳为firewall.
        set_mark = False
        for k1, v1 in common_dict.items():  # 查找是否有SVI
            for k2, v2 in v1.items():
                if i in v2:
                    if re.match(svi, k2):
                        print(i, "In_routing_table" + "_" + k1 + "_" + k2)
                        list_exist_with_svi.append(i)
                        set_mark = True
                        break

                    else:
                        print(i, "In_routing_table" + "_" + k1 + "_" + k2)
                        list_exist_l3_not_svi.append(i)
                        set_mark = True
                        break

            if set_mark:
                break

        if i not in list_exist_with_svi and i not in list_exist_l3_not_svi:
            n = route.index(i)

            for fw_ip in fw:
                if fw_ip in result[n][1]:  # 路由表中找到subnet, 查看下一跳是否为firewall
                    print(i, "In_routing_table_without_l3_and_behind_of_firewall")
                    list_exist_without_l3_and_behind_fw.append(i)
                    break

            if i not in list_exist_without_l3_and_behind_fw:
                print(i, "In_routing_table_without_l3")
                list_exist_without_any_l3.append(i)

print(50 * "@", "\n\n")


print("Subnets can NOT be seen in routing table, but svi can be seen (%i): " % len(list_not_exist_1))
for i in list_not_exist_1:
    print(i)
else:
    print("\n\n")

print("Subnets can NOT be seen in routing table, but l3 interface(not svi) can be seen (%i): " % len(list_not_exist_2))
for i in list_not_exist_2:
    print(i)
else:
    print("\n\n")

print("Subnets can NOT be seen in routing table, no any l3 interface/svi can be seen (%i): " % len(list_not_exist_3))
for i in list_not_exist_3:
    print(i)
else:
    print("\n\n")

print("Subnets can be seen in routing table and SVI can be seen in configuration (%i): " % len(list_exist_with_svi))
for i in list_exist_with_svi:
    print(i)
else:
    print("\n\n")

print("Subnets can be seen in routing table, they're on l3 interfaces but not svi (%i): " % len(list_exist_l3_not_svi))
for i in list_exist_l3_not_svi:
    print(i)
else:
    print("\n\n")

print("Subnets can be seen in routing table and the next hop is FW, but no l3 interfaces/svi can be seen (%i): "
      % len(list_exist_without_l3_and_behind_fw))
for i in list_exist_without_l3_and_behind_fw:
    print(i)
else:
    print("\n\n")

print("Subnets can be seen in routing table. No l3 interface/svi, next hop is NOT FW: (%i)"
      % len(list_exist_without_any_l3))

for i in list_exist_without_any_l3:
    print(i)
