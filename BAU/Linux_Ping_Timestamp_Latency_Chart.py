import textfsm

from textfsm import TextFSM
import matplotlib.pyplot as plt

"""
It's Powershell command on Windows, it prints timestamp.

ping.exe -l 1500 -t 8.8.8.8 |Foreach{"{0} - {1}" -f (Get-Date),$_} >> c:/Ping_1.txt
ping.exe -l 800 -t 8.8.8.8 |Foreach{"{0} - {1}" -f (Get-Date),$_} >> c:/Ping_2.txt
"""

f = open("c:/test1/FW_output.txt", 'r')
txt_f = f.read()

with open("c:/script/textfsm_customization\Linux_Ping_With_Timestamp.textfsm") as textfsm_f:
    fsm = textfsm.TextFSM(textfsm_f)
    result = fsm.ParseText(txt_f)
print(fsm.header)
print(result)


latency = list()

for i in result:
    latency.append(int(i[-1]))

print(len(result))
# print(latency)
print("Min Latency is: %s" % (min(latency)))
print("Max Latency is: %s" % (max(latency)))
print("Ping counter is: %s" % (len(latency)))

y = [i for i in range(1, len(latency) +1)]
plt.plot(y,latency,)
plt.show()