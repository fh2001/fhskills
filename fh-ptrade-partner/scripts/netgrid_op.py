# from io import StringIO
import requests
import urllib3 
import pandas as pd
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class APINotice:
    """
    API通知类，用于发送和接收API通知。pip

    """
    def __init__(self, policyName: str = "netgrid"):
        self.urlSend = "https://sinru.com/send"
        self.urlGet = "https://sinru.com/api/messages"
        self.setApikeyByPolicy(policyName=policyName)

    def setApikeyByPolicy(self,policyName: str = "netgrid"):
        if policyName =="netgrid":
            self.api_key = "your_netgrid_api_key_here"
        else:
            self.api_key = None
            print("请设置正确的策略名称")   
            return  

    def sendNotice(self,title="设置国盛参数",content="",source = "netgrid_opplan"):
        try:
            mydata={"api_key" : self.api_key, 
                    "subject" : title,
                    "body" : content,
                    "source" : source
                    }  #自有APP
            headers = {"Content-Type": "application/json"}  # 关键：声明 JSON 格式
            url = self.urlSend
            res = requests.post(url, json=mydata, headers=headers,verify=False)       
        except Exception as e:
            print(str(e))   

    # getNotice 函数用以从Gateway获取sendNotice发出的消息
    def getNotice(self):
        """
        获取已发送的通知消息
        
        Returns:
            dict: 包含请求结果的响应数据
        """
        try:
            # 使用相同的API密钥和基础URL
            api_key = self.api_key
            url = self.urlGet  # 获取通知的端点

            # 设置请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Notice {api_key}"  # 常见的身份验证方式
            }
            
            # 发送GET请求获取通知
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()  # 检查HTTP错误
            
            return response.json()  # 返回JSON格式的响应数据
            
        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: {str(e)}")
            return None
        except Exception as e:
            print(f"获取通知时发生错误: {str(e)}")
            return None

    # read_opplan_json 函数从同目录读取网络策略计划文件(如：netgrid_opplan.json)
    @staticmethod
    def read_opplan_json(filename):
        try:
            with open(filename,'r') as data:
                df_file = pd.read_json(data,dtype = {'c_date':str,'b_date':str,'c_date_hb':str,
                                                    'o_date':str,'lastbuydate':str,
                                                    'trade_date':str,'low_date':str,'first_time':str,
                                                    'last_time':str},convert_dates=False)
                return df_file    
        except FileNotFoundError:
            print(f"Warning>>>:{filename}文件未找到！")
            return pd.DataFrame()
                # read_opplan_json 函数从同目录读取网络策略计划文件(如：netgrid_opplan.json)

    @staticmethod
    def read_key_json(keyfile):
        try:
            with open(keyfile,'r') as data:
                data = pd.read_json(data)

                df_file = pd.read_json(data,dtype = {'c_date':str,'b_date':str,'c_date_hb':str,
                                                    'o_date':str,'lastbuydate':str,
                                                    'trade_date':str,'low_date':str,'first_time':str,
                                                    'last_time':str},convert_dates=False)
                return df_file    
        except FileNotFoundError:
            print(f"Warning>>>:{filename}文件未找到！")
            return pd.DataFrame()

def main():
    print("用法: python3 netgrid_op.py -h --stockcode <股票代码> --opplan <计划操作> --pcytype <策略类型> --amount <参与金额>")
    print("查询在线网格策略计划示例: python3 netgrid_op.py --opplan show")
    print("上传网格策略计划示例: python3 netgrid_op.py --opplan upload")
    print("更改某个股的网格策略计划的参与金额（amount）示例: python3 netgrid_op.py --stockcode <股票代码> --amount <amount>")
    print("更改某个股的网格策略计划的策略类型（pcytype）示例: python3 netgrid_op.py --stockcode <股票代码> --pcytype <pcytype>")
    print("更改所有个股的网格策略计划的策略类型（pcytype）示例: python3 netgrid_op.py --pcytype <pcytype>")

    parser = argparse.ArgumentParser(description="查询 API 通知")
    parser.add_argument("--stockcode", type=str, default="0", help="股票代码, 格式如: 002001.SZ，600001.SH，688001.BJ，09988.HK，9988.HK")
    parser.add_argument("--opplan", type=str, default="0", help="策略计划操作， show：查询在线opplan， upload：上传opplan")
    parser.add_argument("--pcytype", type=str, default="0", help="设置策略类型， P：暂停， N：网格， A1：次日买入")
    parser.add_argument("--amount", type=int, default=0, help="设置个股参与金额， 格式如: 100000， 默认0")

    args = parser.parse_args()

    stockcode = args.stockcode.upper()

    opplan = args.opplan.upper()
    pcytype = args.pcytype.upper()
    amount = args.amount

    notice = APINotice()
    if opplan == "SHOW" :    # netgrid策略，获取opplan
        subject = "getopplan"
        body = "获取opplan"  
        source="netgrid"
        notice.sendNotice(subject,body,source)
        print("已发送获取opplan请求，请等待2分钟后，在知更鸟通知中查看结果...")
    elif opplan == "UPLOAD" :    # netgrid策略，设置opplan
        subject = "setopplan"
        source="netgrid"
        df = notice.read_opplan_json('netgrid_opplan.json')
        #将df转换成字符串
        body = df.to_json()
        # print(body)
        notice.sendNotice(subject,body,source)
        print("已发送设置opplan请求，请等待2分钟后，在知更鸟通知中查看结果...")
    elif stockcode != "0" and pcytype != "0":    # netgrid策略，更改股票的pcytype
        subject = "command"
        source="netgrid"
        #（1）更改某监控股的pcytype,body={"command":"chgpcytype", "stcode_f":"000001.SZ", "pcytype":"P"}
        cmd={"command":"chgpcytype", "stcode_f":stockcode, "pcytype":pcytype}
        body = str(cmd)
        notice.sendNotice(subject,body,source)
        print("已发送更改股票的pcytype请求，请等待2分钟后，在知更鸟通知中查看结果...")
    elif stockcode == "0" and pcytype != "0":    # 更改所有个股的网格策略计划的策略类型（pcytype）
        subject = "command"
        source="netgrid"
        #（1）更改某监控股的pcytype,body={"command":"chgpcytype", "stcode_f":"000001.SZ", "pcytype":"P"}
        cmd={"command":"chgpcytype", "stcode_f":"000000.00", "pcytype":pcytype}
        body = str(cmd)
        notice.sendNotice(subject,body,source)
        print("已发送更改所有个股的pcytype请求，请等待2分钟后，在知更鸟通知中查看结果...")
    elif stockcode != "0" and amount != 0:    # netgrid策略，更改股票的 amount
        subject = "command"
        source="netgrid"
        #（1）更改某监控股的amount,body={"command":"chgamount", "stcode_f":"000001.SZ", "amount":150000}
        cmd={"command":"chgamount", "stcode_f":stockcode, "amount":amount}
        body = str(cmd)
        notice.sendNotice(subject,body,source)
        print("已发送更改股票的amount请求，请等待2分钟后，在知更鸟通知中查看结果...")

if __name__ == "__main__":
    main()