#!/usr/bin/env python

import os
import multiprocessing
import time


Test_Target = {"10.123.12.252": "abc-co-01",
               "10.123.12.254": "abc00dmvpn2",
               "10.123.13.244": "abc00ap1",
               "10.123.13.245": "abc00ap2",
               "10.123.13.248": "abc00ap3",
               "10.84.10.24": "abc00DMVPN4",
               "10.36.164.163": "TM4U5202M",
               "10.36.164.153": "10.36.164.153"
}

def Ping_Test(k,v):
    Ping_Result = os.popen("ping -O %s | while read pong; do echo \"$(date): $pong\"; done >>/home/pi/%s.txt"%(k,v))



if __name__ == '__main__':
    # multiprocessing.freeze_support()
    # multiprocessing.set_start_method('spawn')
    M = multiprocessing.Manager()
    MultiPro_Dict = M.dict()
    for k, v in Test_Target.items():
        MultiPro_Dict[k] = v

    pool = multiprocessing.Pool(processes=len(MultiPro_Dict))
    for k,v in MultiPro_Dict.items():
        r1 = multiprocessing.Process(target=Ping_Test, args=(k,v,))
        r1.start()
