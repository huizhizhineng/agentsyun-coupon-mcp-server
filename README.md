# Agentsyun优惠券MCP服务

这是一个基于MCP协议的优惠券服务，提供多品类优惠券查询、筛选和推广链接生成功能，支持外卖、美食、休闲娱乐、酒店民宿、门票度假、医药等多个类目。

## 功能特性

- 支持6大类优惠券查询：
  - 外卖商品券
  - 美食优惠券
  - 休闲娱乐券
  - 酒店民宿券
  - 门票度假券
  - 医药券

- 提供完整的优惠券生命周期管理：
  - 优惠券列表查询
  - 推广链接生成（支持多种链接类型）

## 工具具体说明

### 优惠券列表查询

1. `list_takeaway_coupons` - 外卖商品券列表
2. `list_restaurant_coupons` - 美食优惠券列表
3. `list_entertainment_coupons` - 休闲娱乐券列表
4. `list_hotel_coupons` - 酒店民宿券列表
5. `list_travel_coupons` - 门票度假券列表
6. `list_medical_coupons` - 医药券列表

### 推广链接生成

1. `get_takeaway_promotion_link` - 外卖商品券推广链接
2. `get_restaurant_promotion_link` - 美食优惠券推广链接
3. `get_entertainment_promotion_link` - 休闲娱乐券推广链接
4. `get_hotel_promotion_link` - 酒店民宿券推广链接
5. `get_travel_promotion_link` - 门票度假券推广链接
6. `get_medical_promotion_link` - 医药券推广链接

# 工具详细说明

## 优惠券列表查询工具

### [list_takeaway_coupons](file://D:\pyProject\agentsyun_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L130-L180)
获取外卖商品券列表
- **功能**: 根据指定条件查询外卖优惠券分类信息，支持搜索、分页等功能
- **参数**:
  - `search_text`: 搜索关键词(券名、店铺名称)
  - `search_id`: 分页ID(首次调用可不填)
  - `size`: 每页显示条数，默认10
  - `current`: 当前页码，默认1
  - `longitude`: 经度(必填)
  - `latitude`: 纬度(必填)
- **返回值**: 包含优惠券数据的字典或错误信息

### [list_restaurant_coupons](file://D:\pyProject\agentsyun_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L233-L280)
获取美食优惠券列表
- **功能**: 查询美食类优惠券信息，支持搜索和分页
- **参数**:
  - `search_text`: 搜索关键词(券名、店铺名称)
  - `search_id`: 分页ID(首次调用可不填)
  - `size`: 每页显示条数，默认10
  - `current`: 当前页码，默认1
  - `longitude`: 经度(必填)
  - `latitude`: 纬度(必填)
- **返回值**: 包含优惠券数据的字典或错误信息

### [list_entertainment_coupons](file://D:\pyProject\agentsyun_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L335-L382)
获取休闲娱乐券列表
- **功能**: 查询休闲娱乐类优惠券信息
- **参数**:
  - `search_text`: 搜索关键词(券名、店铺名称)
  - `search_id`: 分页ID(首次调用可不填)
  - `size`: 每页显示条数，默认10
  - `current`: 当前页码，默认1
  - `longitude`: 经度(必填)
  - `latitude`: 纬度(必填)
- **返回值**: 包含优惠券数据的字典或错误信息

### [list_hotel_coupons](file://D:\pyProject\agentsyun_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L434-L481)
获取酒店民宿券列表
- **功能**: 查询酒店民宿类优惠券信息
- **参数**:
  - `search_text`: 搜索关键词(券名、店铺名称)
  - `search_id`: 分页ID(首次调用可不填)
  - `size`: 每页显示条数，默认10
  - `current`: 当前页码，默认1
  - `longitude`: 经度(必填)
  - `latitude`: 纬度(必填)
- **返回值**: 包含优惠券数据的字典或错误信息

### [list_travel_coupons](file://D:\pyProject\agentsyun_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L533-L580)
获取门票度假券列表
- **功能**: 查询门票度假类优惠券信息
- **参数**:
  - `search_text`: 搜索关键词(券名、店铺名称)
  - `search_id`: 分页ID(首次调用可不填)
  - `size`: 每页显示条数，默认10
  - `current`: 当前页码，默认1
  - `longitude`: 经度(必填)
  - `latitude`: 纬度(必填)
- **返回值**: 包含优惠券数据的字典或错误信息

### [list_medical_coupons](file://D:\pyProject\agentsyun_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L632-L679)
获取医药券列表
- **功能**: 查询医药类优惠券信息
- **参数**:
  - `search_text`: 搜索关键词(券名、店铺名称)
  - `search_id`: 分页ID(首次调用可不填)
  - `size`: 每页显示条数，默认10
  - `current`: 当前页码，默认1
  - `longitude`: 经度(必填)
  - `latitude`: 纬度(必填)
- **返回值**: 包含优惠券数据的字典或错误信息

## 推广链接生成工具

### [get_takeaway_promotion_link](file://D:\pyProject\agentsyun_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L184-L229)
生成外卖商品券推广链接
- **功能**: 根据指定条件生成外卖商品券的推广链接
- **参数**:
  - `link_type`: 转链类型(1:H5长链接;2:H5短链接;3:deeplink;4:微信小程序路径;5:团口令;6:小程序码)，默认2
  - `sku_id`: 券的skuId(必填)
- **返回值**: 包含推广链接数据的字典或错误信息

### [get_restaurant_promotion_link](file://D:\pyProject\agentsyun_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L284-L331)
生成美食优惠券推广链接
- **功能**: 根据指定条件生成美食优惠券的推广链接
- **参数**:
  - `link_type`: 转链类型(1:H5长链接;2:H5短链接;3:deeplink;4:微信小程序路径;5:团口令;6:小程序码)，默认2
  - `sku_id`: 券的skuId(必填)
- **返回值**: 包含推广链接数据的字典或错误信息

### [get_entertainment_promotion_link](file://D:\pyProject\agentsyun_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L386-L430)
生成休闲娱乐券推广链接
- **功能**: 根据指定条件生成休闲娱乐券的推广链接
- **参数**:
  - `link_type`: 转链类型(1:H5长链接;2:H5短链接;3:deeplink;4:微信小程序路径;5:团口令;6:小程序码)，默认2
  - `sku_id`: 券的skuId(必填)
- **返回值**: 包含推广链接数据的字典或错误信息

### [get_hotel_promotion_link](file://D:\pyProject\agentsyun_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L485-L529)
生成酒店民宿券推广链接
- **功能**: 根据指定条件生成酒店民宿券的推广链接
- **参数**:
  - `link_type`: 转链类型(1:H5长链接;2:H5短链接;3:deeplink;4:微信小程序路径;5:团口令;6:小程序码)，默认2
  - `sku_id`: 券的skuId(必填)
- **返回值**: 包含推广链接数据的字典或错误信息

### [get_travel_promotion_link](file://D:\pyProject\agentsyun_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L584-L628)
生成门票度假券推广链接
- **功能**: 根据指定条件生成门票度假券的推广链接
- **参数**:
  - `link_type`: 转链类型(1:H5长链接;2:H5短链接;3:deeplink;4:微信小程序路径;5:团口令;6:小程序码)，默认2
  - `sku_id`: 券的skuId(必填)
- **返回值**: 包含推广链接数据的字典或错误信息

### [get_medical_promotion_link](file://D:\pyProject\agentsyun_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L683-L728)
生成医药券推广链接
- **功能**: 根据指定条件生成医药券的推广链接
- **参数**:
  - `link_type`: 转链类型(1:H5长链接;2:H5短链接;3:deeplink;4:微信小程序路径;5:团口令;6:小程序码)，默认2
  - `sku_id`: 券的skuId(必填)
- **返回值**: 包含推广链接数据的字典或错误信息


前往 [Agentsyun开放平台](http://mcp.agentsyun.com/) 获取 获取您的 your_app_key与your_app_secret


## 环境要求

- Python >= 3.12
- 环境变量配置：
  - [APP_KEY](file://D:\pyProject\huizhi_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L33-L33): 应用Key
  - [APP_SECRET](file://D:\pyProject\huizhi_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L34-L34): 应用密钥


## 快速开始

### 1. 获取认证信息
前往 [Agentsyun开放平台](https://mcp.agentsyun.com/) 获取您的 APP_KEY 与 APP_SECRET

开放平台地址：https://mcp.agentsyun.com

更为详细的开发文档：https://agentsyun.feishu.cn/wiki/ZDlfwN37PiRqgbknMwYc3kO6nqd

### 2. 开发者收益
- 开发者可以获取优惠券客户的消费佣金
- 支持美团渠道优惠券
- 支持MCP通道推广链接生成

### 3. 选择传输方式
选择以下三种传输方式之一：
- **stdio**（默认）: 本地调用
- **sse**: 远程服务调用  
- **streamable-http**: 远程服务调用

### 4. Stdio 调用方式

首先需要本地安装Python uv管理工具，安装文档：https://hellowac.github.io/uv-zh-cn/getting-started/installation/

#### stdio本地传输配置

只需在本地客户端中添加以下配置：

```json
{
  "mcpServers": {
    "agentsyun-coupon": {
      "command": "uvx",
      "args": [
        "agentsyun-coupon-mcp-server"
      ],
      "env": {
        "APP_KEY": "开放平台申请的APP_KEY",
        "APP_SECRET": "开放平台申请的APP_SECRET"
      }
    }
  }
}
```

#### 使用阿里源拉取（备用方案）

如果上述代码拉取失败，可能是网络问题，可以通过阿里源拉取：

```json
{
  "mcpServers": {
    "agentsyun-coupon": {
      "command": "uvx",
      "args": [
        "--index-url",
        "https://mirrors.aliyun.com/pypi/simple/",
        "agentsyun-coupon-mcp-server"
      ],
      "env": {
        "APP_KEY": "开放平台申请的APP_KEY",
        "APP_SECRET": "开放平台申请的APP_SECRET"
      }
    }
  }
}
```
### sse/streamable执行方式，clone代码到本地，配置环境变量再执行，详见如下：

#### 1、SSE 传输（需要拉包到本地执行）
SSE传输支持实时数据推送，适合远程部署MCP Server。

本地以SSE运行服务：
```bash
export APP_KEY=你的应用Key
export APP_SECRET=你的应用密钥
agentsyun-coupon-mcp-server sse
```

```cmd
set APP_KEY=你的应用Key
set APP_SECRET=你的应用密钥
agentsyun-coupon-mcp-server sse
```

```PowerShell
$env:APP_KEY="你的应用Key"
$env:APP_SECRET="你的应用密钥"
agentsyun-coupon-mcp-server sse
```

MCP客户端配置：
- 根据实际服务器地址进行配置


### 2、Streamable HTTP 传输（需要拉包到本地执行）
本地以Streamable HTTP运行服务：
```bash
export APP_KEY=你的应用Key
export APP_SECRET=你的应用密钥
agentsyun-coupon-mcp-server streamable-http
```

MCP客户端配置：
- 根据实际服务器地址进行配置

## 依赖项
- mcp
- requests>=2.32.5
- annotated>=0.0.2
