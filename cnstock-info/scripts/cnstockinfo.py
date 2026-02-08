#!/usr/bin/env python3
"""A股港股行情查询 - 使用国内免费（大陆股市：新浪数据源,香港股市：东方财富数据源） """
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
        
        # 找到等号的位置并分割
        eq_pos = data.find('=')
        if eq_pos == -1:
            return None, "未找到数据"
        
        line = data[eq_pos + 1:].strip()
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        
        values = line.split(',')
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

def get_hk_stock_eastmoney(symbol: str):
    """获取港股数据 - 东方财富"""
    # 股票代码整理
    if symbol.upper().endswith('.HK'):
        code = symbol[:-3]
    else:
        code = symbol
    
    # 去除前导非数字字符，并确保是数字
    code = ''.join(filter(str.isdigit, code))
    # 左侧补零至5位
    hk_code = code.zfill(5)
    
    url = f"https://push2.eastmoney.com/api/qt/stock/get?secid=116.{hk_code}&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60"
    
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        
        if data.get('rc') != 0 or not data.get('data'):
            return None, "未找到数据"
        
        stock_data = data['data']
        name = stock_data.get('f58', '')
        current_price = stock_data.get('f43', 0) / 1000
        yesterday_close = stock_data.get('f60', 0) / 1000
        
        change_pct = round((current_price - yesterday_close) * 100 / yesterday_close, 2) if yesterday_close > 0 else 0
        open_price = stock_data.get('f46', 0) / 1000
        high = stock_data.get('f44', 0) / 1000
        low = stock_data.get('f45', 0) / 1000
        volume = stock_data.get('f47', 0) / 10000
        amount = stock_data.get('f48', 0) / 10000 / 10000
        
        return {
            "name": name,
            "code": symbol,
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

def get_stock_data(code):
    """获取股票数据"""
    if code.upper().endswith('.HK'):
        data, error = get_hk_stock_eastmoney(code)
        if data:
            return data, None
        else:
            return None, error
    else:
        return get_a_stock(code)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 cnstockinfo.py <股票代码>")
        print("A股示例: python3 cnstockinfo.py 600519 (贵州茅台)")
        print("港股示例: python3 cnstockinfo.py 9988.HK (腾讯控股)")
        sys.exit(1)
    
    code = sys.argv[1]
    data, error = get_stock_data(code)
    
    if error:
        print(f"❌ 错误: {error}")
        sys.exit(1)
    
    change_emoji = "📈" if data["change"] >= 0 else "📉"
    
    print(f" {'='*50}")
    print(f" {data['name']} ({data['code']}) [{data['market']}]")
    print(f"{'='*50}")
    print(f" 当前价: {data['current']:.2f} {change_emoji}")
    if data["change"] != 0:
        print(f" 涨跌: {data['change']:+.2f} ({data['change_pct']:+.2f}%)")
    print(f" 开盘: {data['open']:.2f}")
    print(f" 最高: {data['high']:.2f}")
    print(f" 最低: {data['low']:.2f}")
    print(f" 成交量: {data['volume']:,} 万股")
    print(f"{'='*50} ")

if __name__ == "__main__":
    main()
