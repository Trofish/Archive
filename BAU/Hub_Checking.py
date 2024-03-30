import textfsm


with open("c:/hub/10.141.4.53.txt") as f:
    with open("c:/script/textfsm_customization/hub_checking.textfsm") as textfsm_f:
        fsm = textfsm.TextFSM(textfsm_f)
        result = fsm.ParseText(f.read())

# print(result)
# print(len(result))

interface_set = set()

for i in result:
    interface_set.add(i[1])

temp_list = list()
temp_dict = dict()
for i in result:
    temp_list.append(i[0])
    temp_list.append(i[1])

for i in interface_set:
    temp_dict[i] = temp_list.count(i)

for i,j in temp_dict.items():
    # print(i,j)
    if j >1:
        print(i,j)