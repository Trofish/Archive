import textfsm
import copy
import datetime

"""
a = datetime.datetime(2023,3,11,18,3,31,333)   #2023-03-11 18:03:31.000333
b = datetime.datetime(2023,4,12,18,2,12,231)  #2023-04-12 18:02:12.000231
gap = b -a

print(type(gap))
print(gap)
print(gap.total_seconds())
"""

m = {'jan': 1, 'feb': 2,'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
         'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}

with open("c:/UFO/XRF-16.txt") as f:
    with open("c:/script/textfsm_customization/date_time.textfsm") as textfsm_f:
        fsm = textfsm.TextFSM(textfsm_f)
        result = fsm.ParseText(f.read())

# print(result)

latency = set()
interruption_list = dict()


for i in range(len(result)):
    latency.add(result[i][6])       # 取 latency 到集合中
    month = m[result[i][1].lower()]     # 将月份名称转为数字

    if i > 0:
        t2 = datetime.datetime(int(result[i][0]), month, int(result[i][2]), int(result[i][3]),
                              int(result[i][4]), int(result[i][5]))     # 提取时间, 准备进行减法运算

        t1 = datetime.datetime(int(result[(i-1)][0]), month, int(result[(i-1)][2]), int(result[(i-1)][3]),
                              int(result[(i-1)][4]), int(result[(i-1)][5]))     # 提取时间, 准备进行减法运算

        gap = t2 - t1      # 对2次ping的响应时间相减, 因为 Linux 不像Windows显示timeout.

        if gap.total_seconds() >= 2:        #如果2次响应时间超过2秒, 则认为出现中断.
            # print(gap.total_seconds())
            interruption_list[str(t1)] = gap.total_seconds()

if interruption_list:
    for k,v in interruption_list.items():
        print(k,"    ", v)

print("Total %i times successful ping. Min Latency is: %s ms. Max latency is: %s ms." %(len(result), max(latency),
                                                                                        min(latency)))
