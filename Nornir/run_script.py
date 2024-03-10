from Two_FA_Nornir import *
import getpass

excel_file = "c:/script/Nornir_LAB/My_Inventory.xlsx"
commands = "c:/script/Nornir_LAB/show_cmd.txt"

device_list = ExcelReader.read_excel(excel_file)

uid = input("Please input login ID:")
pwd = getpass.getpass("ID Password for login:")

work = TwoFactorAuth(device_list=device_list, commands = commands, username=uid, password=pwd)
work.run()