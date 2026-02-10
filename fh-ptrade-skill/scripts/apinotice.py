from io import StringIO
import requests,ast
import urllib3
# import pandas as pd
# import pystocklib.btlib as bt

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class APINotice:
    """
    API通知类，用于发送和接收API通知。
    netgrid策略使用：api_key='sf--cR3T7XP6DfjbvLYtUSMQfB2hv4RfYI7g0kVfSKUYp8'
    ltpcy策略使用：  api_key='sf-h_C4ZZIFc5w79N_P6OvAYUdGT4Z1HMfWHdthZE-yI20'
    """
    def __init__(self, policyName: str = "netgrid"):
        self.urlSend = "https://sinru.com/send"
        self.urlGet = "https://sinru.com/api/messages"
        self.setApikeyByPolicy(policyName=policyName)
    def setApikeyByPolicy(self,policyName: str = "netgrid"):
        if policyName =="ltpcy":
            self.api_key = "sf-h_C4ZZIFc5w79N_P6OvAYUdGT4Z1HMfWHdthZE-yI20"
        elif policyName =="netgrid":
            self.api_key = "sf--cR3T7XP6DfjbvLYtUSMQfB2hv4RfYI7g0kVfSKUYp8"
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

            res = requests.post(url, json=mydata, headers=headers,verify=False)            # fh 自有app post       

        except Exception as e:
            print(str(e))   

    # getNotice 函数用以获取sendNotice发出的消息
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
        
if __name__ == "__main__":
    isMain = [1]        # 获得netgrid策略的opplan 
    # isMain = [2]      # 设置netgrid策略的opplan 
    # isMain = [3]      # 变更个股pcytype
    # isMain = [31]     # 变更所有个股pcytype，(如:设为P中止所有操作)
    # isMain = [4]        # 变更个股amount
    # isMain = [99]     # 接收消息

    notice = APINotice()
    if 1 in isMain:    # netgrid策略，获取opplan
        subject = "getopplan"
        body = "获取opplan"  
        source="netgrid"
        # df = bt.read_trend_json('netgrid_opplan.json')
        #将df转换成字符串
        # body = df.to_json()
        # print(body)
        notice.sendNotice(subject,body,source)

    elif 2 in isMain:    # netgrid策略，设置opplan
        subject = "setopplan"
        body = "测试内容1"  
        source="netgrid"
        df = bt.read_trend_json('netgrid_opplan.json')
        #将df转换成字符串
        body = df.to_json()
        # print(body)
        notice.sendNotice(subject,body,source)
    elif 3 in isMain:    # netgrid策略，更改股票的pcytype
        subject = "command"
        source="netgrid"
        #（1）更改某监控股的pcytype,body={"command":"chgpcytype", "stcode_f":"000001.SZ", "pcytype":"P"}
        cmd={"command":"chgpcytype", "stcode_f":"002027.SZ", "pcytype":"N"}
        body = str(cmd)
        notice.sendNotice(subject,body,source)
    elif 31 in isMain:    # 全部股票中止操作
        subject = "command"
        source="netgrid"
        #（1）更改某监控股的pcytype,body={"command":"chgpcytype", "stcode_f":"000001.SZ", "pcytype":"P"}
        cmd={"command":"chgpcytype", "stcode_f":"000000.00", "pcytype":"P"}
        body = str(cmd)
        notice.sendNotice(subject,body,source)
    elif 4 in isMain:    # netgrid策略，更改股票的amount
        subject = "command"
        source="netgrid"
        #（1）更改某监控股的amount,body={"command":"chgamount", "stcode_f":"000001.SZ", "amount":150000}
        cmd={"command":"chgamount", "stcode_f":"000885.SZ", "amount":150000}
        body = str(cmd)
        notice.sendNotice(subject,body,source)
        
    if 99 in isMain:
        df=pd.DataFrame()
        result = notice.getNotice()
        print(result)
        if result['errCode'] == 0   :  
            last_setopplan_netgrid_message_id = 0
            last_chgpcytype_netgrid_message_id = 0
            for message in result["data"]:
                message_id = message['message_id']
                subject = message['subject']
                body = message['body']
                source = message['source']
                # 处理setopplan消息
                if subject == "setopplan" and source == "netgrid"  :
                    if message_id > last_setopplan_netgrid_message_id: #只保留最新的消息
                        last_setopplan_netgrid_message_id = message_id
                        df = pd.read_json(StringIO(body),dtype = {'c_date':str,'lastbuydate':str,'trade_date':str},convert_dates=False)
                        print(df)
                # 处理chgpcytype消息,格式示例：body={"stcode_f":"000001.SZ", "pcytype":"P"}
                elif subject == "command" and source == "netgrid"  :
                        dict_data = ast.literal_eval(body)  # 将字符串转换成字典
                        print(dict_data)
                        print(dict_data['stcode_f'])  

        if df.empty == False:  
            print("接收到消息") 
            print(df)
    
