import getpass

import urllib3
from infoblox_client import connector
from infoblox_client import objects

urllib3.disable_warnings()
opts = {'host': 'ipam.wdc.com', 'username': 'user1234', 'password': '1234'}

username = input("Username for IB login: : ")
pwd = getpass.getpass("Password for IB login: ")

dy_pwd = input("DUO or Ubikey: ")
opts["password"] = str(pwd) + str(dy_pwd)
opts["username"] = username

# subnet = '10.70.201.0/24'
subnet = input("Subnet for checking: ")

conn = connector.Connector(opts)
# get all network_views
network_views = conn.get_object('networkview')
# search network by cidr in specific network view
# network = conn.get_object('network', {'network': '10.70.201.0/24', 'network_view': 'HGST'},
#                           {"extattrs":[]})
# network_update = conn.update_object(ref='network/ZG5zLm5ldHdvcmskMTAuNzAuMjAxLjAvMjQvMA:10.70.201.0/24/HGST',
#                                     payload={'extattrs':{'VLAN#':{'value': '103'}}})

network = conn.get_object('network', {'network': subnet, 'network_view': 'HGST'},
                          {"extattrs":[]})

# network = conn.get_object('networkcontainer', {'network': subnet, 'network_view': 'HGST'},
#                           {"extattrs":[]})

print(network_views)
print("=============")
print(network)

for d in network:
    for i,j in d.items():
        if type(j) is dict:
            for k,l in j.items():
                j = l
                if k == "VLAN#":
                    print(j["value"])

