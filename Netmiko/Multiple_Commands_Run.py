import getpass
from Multiple_Commands import Multiple_Commands

# device_type = "ruckus_fastiron"
# device_type = "cisco_nxos"
# device_type = "cisco_ios"
# device_type = "arista_eos"

job = Multiple_Commands()

job.u_id = input("Please input login ID:")
job.factor_1 = getpass.getpass("ID Password for login:")
job.device_type = "ruckus_fastiron"
job.secret = "Cisco_123"
job.show(job.switch)