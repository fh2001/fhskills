# Name: Ptrade量化交易网格操作技能 (NetGrid Operation)

## 技能概述

Ptrade量化交易网格操作技能（NetGrid Operation）是一个基于API通知机制的自动化交易管理系统，专门用于管理网格交易策略。该技能通过API接口与交易网关通信，支持对多个股票进行网格交易策略的配置和管理。

## 核心功能

### 1. API通知系统
- 支持netgrid网格交易策略：
- 提供发送和接收API通知的功能
- 支持多种通知类型和策略控制命令

### 2. 策略控制命令
- **查询在线网格策略计划**: `--opplan show`
- **上传网格策略计划**: `--opplan upload`
- **修改个股参与金额**: `--stockcode <股票代码> --amount <金额>`
- **修改个股策略类型**: `--stockcode <股票代码> --pcytype <策略类型>`
- **批量修改所有个股策略类型**: `--pcytype <策略类型>`

### 3. 策略类型说明
- **P (Pause)**: 暂停策略
- **N (NetGrid)**: 网格交易类型
- **A1 (After Buy)**: 次日买入类型
- **T (价高于网格区间)**: 价高于网格区间

## 策略计划文件结构

`netgrid_opplan.json` 文件包含以下关键字段：

| 字段 | 描述 |
|------|------|
| `stcode_f` | 股票代码（标准格式） |
| `stcode_gs` | 股票代码（国盛格式） |
| `stcode_sb` | 股票代码（申宝格式） |
| `stname` | 股票名称 |
| `pcytype` | 策略类型（P/N/A1/T） |
| `prc_low` | 价格下限 |
| `prc_high` | 价格上限 |
| `gridnum` | 网格数量 |
| `lowprice` | 最低价 |
| `highprice` | 最高价 |
| `amount` | 参与金额 |

## 使用方法

### 1. 查询在线网格策略计划 netgrid_opplan
```bash
python3 netgrid_op.py --opplan show
```

### 2. 上传网格策略计划
```bash
python3 netgrid_op.py --opplan upload
```

### 3. 修改个股参与金额
```bash
python3 netgrid_op.py --stockcode 002001.SZ --amount 150000
```

### 4. 修改个股策略类型
```bash
python3 netgrid_op.py --stockcode 002001.SZ --pcytype P
```

### 5. 批量修改所有个股策略类型
```bash
python3 netgrid_op.py --pcytype N
```

## API接口说明

### 发送通知接口
- **URL**: `https://sinru.com/send`
- **方法**: POST
- **请求体**:
```json
{
  "api_key": "<API_KEY>",
  "subject": "<主题>",
  "body": "<内容>",
  "source": "<来源>"
}
```

### 获取通知接口
- **URL**: `https://sinru.com/api/messages`
- **方法**: GET
- **认证**: Authorization头部使用Notice方案

## 命令类型详解

### 1. 获取策略计划
- 主题: `getopplan`
- 来源: `netgrid`
- 用途: 从服务器获取当前的网格策略计划

### 2. 设置策略计划
- 主题: `setopplan`
- 来源: `netgrid`
- 用途: 向服务器上传新的网格策略计划

### 3. 更改策略类型
- 主题: `command`
- 内容: `{"command":"chgpcytype", "stcode_f":"<股票代码>", "pcytype":"<策略类型>"}`
- 用途: 修改特定股票的策略类型

### 4. 更改参与金额
- 主题: `command`
- 内容: `{"command":"chgamount", "stcode_f":"<股票代码>", "amount":<金额>}`
- 用途: 修改特定股票的参与金额

## 错误处理

- 网络请求错误会捕获并打印详细信息
- 文件未找到时会显示警告信息
- 无效策略名称会提示用户正确设置

## 依赖项

- `requests`: HTTP请求处理
- `pandas`: JSON数据处理
- `argparse`: 命令行参数解析
- `urllib3`: HTTP客户端库

## 注意事项

1. 股票代码格式需严格按照 `XXXXXX.EX` 格式（如: 002001.SZ，600001.SH，688001.BJ，09988.HK）
2. API密钥需妥善保管，避免泄露
3. 在生产环境中应确保网络连接的安全性
4. 定期检查和更新策略计划文件

## 开发者信息

- 适用于Ptrade量化交易平台
- 支持多市场（A股、港股等）
- 提供灵活的策略控制机制

