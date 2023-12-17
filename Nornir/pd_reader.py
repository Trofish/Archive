import pandas as pd

"""
This class is to Convert excel spreadsheet to a Python list which consists of dictionaries.
Later, I will pass the dictionaries to Nornir Inventory by using FlatDataInventory inventory plugin. 

The purpose of all of this is that, when I leverage the advantages of Nornir which Netmiko doesn't have, I have to
tackle with 2 factors authentication. 

将excel文件转换为字典, 以列表形式传递给Nornir, 传递过程中，执行最关键的操作: 完成登录设备时的双因素动态密码认证. 
"""

class Pd_Reader(object):
    def __init__(self, ):
        pass

    @classmethod
    def read_excel(self, excel_file_name):
        self.excel_file_name = excel_file_name
        df = pd.read_excel(self.excel_file_name, converters={"No.": int, "SSH Port": int})

        """
        Make sure we can print all columns in one line.
        """
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)

        # delete empty rows, or rows where any of the 4 columns "No.", "Hostname", "Host IP", "OS Type" is null

        # df = df[~df["No."].isnull()]
        # df = df[df["No."].notnull()]
        subset = ["Name", "Hostname", "Platform"]
        df = df.dropna(subset=subset)

        # delete empty columns
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        # delete duplicated rows based on "Hostname"
        df.drop_duplicates(subset="Name", keep="first", inplace=True, ignore_index=True)

        # Replace NAN as an empty string "".  otherwise, when generate a dictionary, it will be an invalid
        # K, V pair: "UID":NAN

        df = df.fillna("")

        # generate a dictionary, key is column name, value is cell
        col = df.columns.tolist()  # put columns in a list
        my_inventory = list()

        for i in df.values:
            k = dict(zip(col, i))  # generate a dict
            my_inventory.append(k)

        return my_inventory
