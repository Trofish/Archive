import os
import re
import ipaddress
import textfsm

with open("c:/script/textfsm_customization/route_check_Arista.textfsm") as textfsm_f:
    fsm = textfsm.TextFSM(textfsm_f)
    with open("c:/URC/URC-108-CO-02.txt", 'r') as f:
        result1 = fsm.ParseText(f.read())

with open("c:/script/textfsm_customization/route_check_Arista.textfsm") as textfsm_f:
    fsm = textfsm.TextFSM(textfsm_f)
    with open("c:/URC/2.txt", 'r') as f:
        result2 = fsm.ParseText(f.read())

# with open("c:/script/textfsm_customization/route_check_NXOS.textfsm") as textfsm_f:
#     fsm = textfsm.TextFSM(textfsm_f)
#     with open("show_ip_route.txt", 'r') as f:
#         result = fsm.ParseText(f.read())
#
# with open("c:/script/textfsm_customization/route_check_Ruckus.textfsm") as textfsm_f:
#     fsm = textfsm.TextFSM(textfsm_f)
#     with open("c:/URC/urc-108-ud1.txt", 'r') as f:
#         result1 = fsm.ParseText(f.read())
#
# with open("c:/script/textfsm_customization/route_check_Ruckus.textfsm") as textfsm_f:
#     fsm = textfsm.TextFSM(textfsm_f)
#     with open("c:/URC/3.txt", 'r') as f:
#         result2 = fsm.ParseText(f.read())

# print(result)

dst_before_change = list()
dst_after_change = list()

for i in result1:
    # print(i)
    dst_before_change.append(i[0])

for i in result2:
    # print(i)
    dst_after_change.append(i[0])

set1 = set(dst_before_change)
set2 = set(dst_after_change)

print("\nTotal route entries BEFORE change: %i" % (len(result1)))
print("The set of destination contains: %i" % (len(set1)))

print("\nTotal route entries AFTER change: %i" % (len(result2)))
print("The set of destination contains: %i" % (len(set2)))

gap1 = set1 - set2
gap2 = set2 - set1

print("\nRoute entries can NOT be seen after change: %i" % (len(gap1)))
for i in gap1:
    for j in result1:
        if i == j[0]:
            print(j)

print("\nAdded route entries after change: %i" % (len(gap2)))
for i in gap2:
    for j in result2:
        if i == j[0]:
            print(j)

common = set1 & set2
gap3 = list()

print("\nRoute entries with different next hop:")
for i in common:
    n1 = dst_before_change.index(i)
    n2 = dst_after_change.index(i)
    if result1[n1] != result2[n2]:
        gap3.append(i)
        print(i, "  :  ", result1[n1], "--->>", result2[n2])

print("\n %i route entries with different next hop" % (len(gap3)))