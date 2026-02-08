#!/usr/bin/env python3
"""
A股港股行情查询 Plus - 使用国内数据源
"""

import sys
import requests
import json

def get_a_stock(code):
    """获取A股数据 - 新浪财经"""
    if code.startswith('sh') or code.startswith('sz'):
        url = f"http://hq.sinajs.cn/list={code}"
    elif code.startswith('6') or code.startswith('9') or code.startswith('5'):
        url = f"http://hq.sinajs.cn/list=sh{code}"
    else:
        url = f"http://hq.sinajs.cn/list=sz{code}"
    
    headers = {"Referer": "http://finance.sina.com.cn/"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.encoding = 'gbk'
        data = resp.text
        
        line = data.split('\n')[0]
        parts = line.split('=')
        
        if len(parts) < 2:
            return None, "未找到数据"
        
        values = parts[1].split(',')
        
        if len(values) < 32:
            return None, "数据不完整"
        
        name = values[0]
        open_price = float(values[1])
        yesterday_close = float(values[2])
        current_price = float(values[3])
        high = float(values[4])
        low = float(values[5])
        volume = int(values[8]) // 100
        amount = float(values[9]) / 10000
        
        change = current_price - yesterday_close
        change_pct = (change / yesterday_close) * 100 if yesterday_close > 0 else 0
        
        return {
            "name": name,
            "code": code,
            "market": "A股",
            "current": current_price,
            "open": open_price,
            "high": high,
            "low": low,
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "amount": round(amount, 2),
        }, None
    except Exception as e:
        return None, str(e)

def get_hk_stock_eastmoney(symbol: str) -> str:
    ## 股票代码整理
    # 移除 .HK（不区分大小写）
    if symbol.upper().endswith('.HK'):
        code = symbol[:-3]
    else:
        code = symbol  # 如果没有 .HK，直接当作代码处理
    
    # 去除前导非数字字符（如空格），并确保是数字
    code = ''.join(filter(str.isdigit, code))
    
    # 左侧补零至5位
    hk_code = code.zfill(5)

    """获取港股数据 - 东方财富"""
    #hk_code = code.replace('.HK', '')
    
    # 东方财富港股接口
    '''
    "f43": 581000,   	# 最新
    "f44": 601500,		# 最高
    "f45": 561000,		# 最低
    "f46": 598500,		# 今开
    "f47": 65128647,	# 总量（股）
    "f48": 37562016512,	# 金额（元）
    "f49": 36024849,	# 外盘 (元）
    "f50": 267			# 量比 *100
    "f51": 683000,			#52周最高
    "f52": 414500,			#52周最低 
    "f55": 25.621011096,		#收益TTM
    "f57": "00700",			# 股票代码
    "f58": "腾讯控股",		# 股票名称
    "f60": 598500		# 昨收	
    "f71": 576736,			#均价
    "f84": 9122883125,		#总股本（股）
    "f85": 9122883125,		# 港䝘本 （股）
    "f92": 140.7226097		#净资产
    "f107": 116,			# 市场代号
    "f110": 116				#市场代号
    "f112": "HK",				# 市场代码
    "f116": 5300395095625,		# 总值
    "f117": 5300395095625,		# 港值
    "f126": 0.77,			# 股息率ITM
    "f127": "软件服务",		# 行业
    "f130": 598500			# 昨收	
    "f164": 2268,		# PE (TTM)
    "f167": 413,		# 市净率
    "f168": 71,			# 换手 *10000
    '''
    url = f"https://push2.eastmoney.com/api/qt/stock/get?secid=116.{hk_code}&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60"

    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        
        if data.get('rc') != 0 or not data.get('data'):
            return None, "未找到数据"
        
        stock_data = data['data']
        name = stock_data.get('f58', '')                    #名称  f58
        current_price = stock_data.get('f43', 0)  /1000     #最新  f43
        yesterday_close = stock_data.get('f60', 0) /1000    #昨收 f60
        change_pct = round((current_price - yesterday_close)*100/yesterday_close, 2) if yesterday_close > 0 else 0      #涨跌幅 （最新-昨收）/昨收
        open_price = stock_data.get('f46', 0) / 1000        #今开 f46
        high = stock_data.get('f44', 0) / 1000              #最高  f44
        low = stock_data.get('f45', 0)  / 1000              #最低  f45
        volume = stock_data.get('f47', 0) / 10000           # 成交量（万） f47 / 10000
        amount = stock_data.get('f48', 0) / 10000 /10000  # 成交量(亿) f48 / 10000  / 10000 
        # 东方财富没有涨跌幅数据，用当前价计算
        return {
            "name": name,
            "code": code,
            "market": "港股",
            "current": current_price,
            "open": open_price,
            "high": high,
            "low": low,
            "change": current_price - yesterday_close,
            "change_pct": change_pct,
            "volume": round(volume, 2),
            "amount": amount,
        }, None
    except Exception as e:
        return None, str(e)

def get_hk_stock_tencent(code):
    """获取港股数据 - 腾讯"""
    hk_code = code.replace('.HK', '')
    url = f"http://qt.gtimg.cn/q={hk_code}"
    
    try:
        resp = requests.get(url, timeout=5)
        resp.encoding = 'gbk'
        
        parts = resp.text.split('~')
        if len(parts) < 32:
            return None, "数据格式错误"
        
        name = parts[1]
        current_price = float(parts[3])
        open_price = float(parts[5])
        high = float(parts[33])
        low = float(parts[34])
        volume = int(parts[36]) / 100 / 10000
        amount = float(parts[37]) / 10000
        change = float(parts[32])
        change_pct = float(parts[31])
        
        return {
            "name": name,
            "code": code,
            "market": "港股",
            "current": current_price,
            "open": open_price,
            "high": high,
            "low": low,
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": round(volume, 2),
            "amount": round(amount, 2),
        }, None
    except Exception as e:
        return None, str(e)

def get_stock_data(code):
    """获取股票数据"""
    if code.endswith('.HK'):
        # 先试东方财富
        data, error = get_hk_stock_eastmoney(code)
        if data:
            return data, None
        # 再试腾讯
        return get_hk_stock_tencent(code)
    else:
        return get_a_stock(code)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 stock.py <股票代码>")
        print("示例: python3 stock.py 600519  (A股)")
        print("       python3 stock.py 9988.HK (港股)")
        sys.exit(1)
    
    code = sys.argv[1]
    data, error = get_stock_data(code)
    
    if error:
        print(f"❌ 错误: {error}")
        sys.exit(1)
    
    change_emoji = "📈" if data["change"] >= 0 else "📉"
    
    print(f"\n{'='*50}")
    print(f"  {data['name']} ({data['code']}) [{data['market']}]")
    print(f"{'='*50}")
    print(f"  当前价: {data['current']:.2f}  {change_emoji}")
    if data["change"] != 0:
        print(f"  涨跌:   {data['change']:+.2f} ({data['change_pct']:+.2f}%)")
    print(f"  开盘:   {data['open']:.2f}")
    print(f"  最高:   {data['high']:.2f}")
    print(f"  最低:   {data['low']:.2f}")
    print(f"  成交量: {data['volume']:,} 万股")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
