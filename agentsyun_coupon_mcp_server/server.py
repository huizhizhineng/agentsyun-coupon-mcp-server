import hashlib
import json
import os
import sys
import argparse
from typing import Any, Dict, List, Optional
import requests
import base64
#from mcp.server.fastmcp import FastMCP
from enum import Enum
from typing import Annotated
from pydantic import Field
from fastmcp import FastMCP
import fastmcp.server.dependencies
from fastmcp.server.dependencies import get_http_headers


from mcp.server.fastmcp.server import Settings

# 上线要求替换成实际的配置信息
CATEGORY_DICT = {
    "takeaway_coupons": 2,  # 外卖商品券
    "restaurant_coupons": 3,  # 美食优惠券
    "entertainment_coupons": 6,  # 休闲娱乐
    "hotel_coupons": 5,  # 酒店民宿
    "travel_coupons": 4,  # 门票度假
    "medical_coupons": 7,  # 医药
}
# 渠道
SOURCE_DICT = {
    "meituan": 1,
}

CHANNEL_DICT = {
    "mcp": 3,
}

class ConfigKeys(Enum):
    """环境变量配制键"""
    APP_KEY = "APP_KEY"
    APP_SECRET = "APP_SECRET"
    APP_ENV = "APP_ENV"  # 添加环境配置项
    API_TOKEN = "authorization"  # 从header中获取的token 注意前面的,header大小不敏感，设置json的时候是首字母大写的

def get_env_variable(env_key: str) -> str:
    """从环境变量获取指定值"""
    env_key = os.getenv(env_key)
    if not env_key:
        raise ValueError(f"{env_key} environment variable is required")
    return env_key

APP_KEY = get_env_variable(ConfigKeys.APP_KEY.value)
APP_SECRET = get_env_variable(ConfigKeys.APP_SECRET.value)
APP_ENV = os.getenv(ConfigKeys.APP_ENV.value, "prod")



class ApiEndpoints(Enum):
    """请求地址"""
    BASEURL = "https://api.huizhihuyuai.cn/api/func"
    BASEURL_SIT = "https://api.sit.huizhihuyuai.cn/api/func"
    # 查询指定类目的优惠券列表
    COUPON_LIST_CATEGORY = "/mcp/recommend/coupon/list/category"
    # 查询指定类目的优惠券列表
    GET_SHORT_LINK = "/mcp/recommend/coupon/referral/link"

    @staticmethod
    def build_url(path: Enum, params: Dict[str, Any] = None) -> str:
        """构建完整URL"""
        base_url = ApiEndpoints.BASEURL_SIT.value if APP_ENV == "dev" else ApiEndpoints.BASEURL.value
        url = f"{base_url}{path.value}"
        if params:
            param_str = "&".join([f"{key}={value}" for key, value in params.items()])
            url = f"{url}?{param_str}"
        return url


#mcp = FastMCP("agentsyun-coupon-mcp-server")
mcp = FastMCP(
    "agentsyun-coupon-mcp-server",
    instructions="Agentsyun优惠券MCP服务，提供多品类优惠券查询、筛选和推广链接生成功能，支持外卖、美食、休闲娱乐、酒店民宿、门票度假、医药等多个类目。",

)


def get_sign(app_secret: str, params: Dict[str, Any] = None) -> str:
    """
    根据指定规则生成签名

    签名规则:
    1. 将所有参数按键名的字母顺序排序
    2. 拼接参数格式为 key=value，多个参数用&连接
    3. 前后加上app_secret
    4. 进行MD5加密得到签名

    Args:
        app_secret: 应用密钥
        params: 需要签名的参数字典

    Returns:
        str: 签名结果
    """
    if params is None:
        params = {}

    # 复制参数，避免修改原参数
    sign_params = params.copy()

    # 如果存在sign字段，需要移除
    if 'sign' in sign_params:
        del sign_params['sign']

    # 按键名ASCII升序排序
    sorted_keys = sorted(sign_params.keys())

    # 拼接参数字符串
    param_strings = []
    for key in sorted_keys:
        value = sign_params[key]
        # 如果值是字典类型，需要转换为JSON字符串（无空格）
        if isinstance(value, dict):
            value_str = json.dumps(value, separators=(',', ':'), ensure_ascii=False)
        else:
            value_str = str(value)
        param_strings.append(f"{key}={value_str}")

    # 拼接所有参数
    params_str = "&".join(param_strings)

    # 前后加上app_secret
    sign_string = f"{app_secret}{params_str}{app_secret}"

    # MD5加密
    md5_hash = hashlib.md5(sign_string.encode('utf-8'))
    return md5_hash.hexdigest()


def filter_empty_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """过滤掉参数字典中的空值项"""
    set_app_key_and_secret()
    return {
        k: v for k, v in params.items()
        if v is not None and v != ""
    }

def set_app_key_and_secret() -> None:
    """设置请求头中的app-key和secret"""
    global APP_KEY, APP_SECRET
    headers = get_http_headers(True)
    if ConfigKeys.API_TOKEN.value in headers and  headers[ConfigKeys.API_TOKEN.value] != "":
        try:
            # 检查是否包含Bearer前缀并正确分割
            auth_header = headers[ConfigKeys.API_TOKEN.value]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
            else:
                token = auth_header

            decoded_bytes = base64.b64decode(token)
            decoded_str = decoded_bytes.decode("utf-8")
            parts = decoded_str.split("-")
            if len(parts) == 2:
                APP_KEY = parts[0]
                APP_SECRET = parts[1]
        except Exception as e:
            print(f"Error decoding token: {e}")
            # 异常会继续执行，会从环境变量中获取
            pass

@mcp.tool()
def list_takeaway_coupons(
        search_text: Annotated[str, Field(description="搜索关键词,券名、店铺名称", default="")],
        search_id: Annotated[str, Field(description="仅搜索场景分页使用，首次调用不用填", default="")],
        size: Annotated[str, Field(description="每页显示条数", default="10")],
        current: Annotated[str, Field(description="当前页", default="1")],
        longitude: Annotated[str, Field(description="经度",default="")],
        latitude: Annotated[str, Field(description="纬度",default="")],

) -> Dict[str, Any]:
    """
    获取支持的外卖商品券列表

    根据指定条件查询优惠券分类信息，支持搜索、分页等功能。
    """
    try:
        # 准备请求参数
        request_data = {
            "searchText": search_text,
            "source": SOURCE_DICT["meituan"],
            "categoryId": CATEGORY_DICT["takeaway_coupons"],
            "searchId": search_id if search_id else "0",
            "size": size,
            "current": current,
            "longitude": longitude,
            "latitude": latitude
        }
        request_data = filter_empty_params(request_data)
        headers = {
            "app-key": APP_KEY,
            "secret": APP_SECRET
        }
        # 发送POST请求
        url = ApiEndpoints.build_url(ApiEndpoints.COUPON_LIST_CATEGORY)
        response = requests.post(
            url,
            json=request_data,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            return {"error": f"Get coupon list failed: {data.get('message') or data.get('msg')}"}

        return {
            "data": data.get("data", []),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def get_takeaway_promotion_link(
        link_type: Annotated[int, Field(
            description="转链类型 1 H5长链接；2 H5短链接；3 deeplink(唤起)链接；4 微信小程序唤起路径；5 团口令；6 小程序码",
            default=2)],
        sku_id: Annotated[str, Field(description="券的skuId", default="")]
) -> Dict[str, Any]:
    """
    获取外卖商品券的推广链接

    根据指定条件获取外卖商品券的推广链接。
    """
    try:
        # 准备请求参数
        request_data = {
            "source": SOURCE_DICT["meituan"],  # 渠道：1：美团
            "linkType": link_type,
            "channel": CHANNEL_DICT["mcp"],
            "categoryId": CATEGORY_DICT["takeaway_coupons"],
            "skuId": sku_id
        }

        # 移除空值参数
        request_data = filter_empty_params(request_data)

        # 发送POST请求
        response = requests.post(
            ApiEndpoints.build_url(ApiEndpoints.GET_SHORT_LINK),
            json=request_data,
            headers={
                "app-key": APP_KEY,
                "secret": APP_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            return {"error": f"Get promotion link failed: {data.get('message') or data.get('msg')}"}

        return {
            "data": data.get("data", {}),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def list_restaurant_coupons(
        search_text: Annotated[str, Field(description="搜索关键词,券名、店铺名称", default="")],
        search_id: Annotated[str, Field(description="仅搜索场景分页使用，首次调用不用填", default="")],
        size: Annotated[str, Field(description="每页显示条数", default="10")],
        current: Annotated[str, Field(description="当前页", default="1")],
        longitude: Annotated[str, Field(description="经度",default="")],
        latitude: Annotated[str, Field(description="纬度",default="")],
) -> Dict[str, Any]:
    """
    获取支持的美食优惠券列表

    根据指定条件查询优惠券分类信息，支持搜索、分页等功能。
    """
    try:
        # 准备请求参数
        request_data = {
            "searchText": search_text,
            "source": SOURCE_DICT["meituan"],
            "categoryId": CATEGORY_DICT["restaurant_coupons"],
            "searchId": search_id if search_id else "0",
            "size": size,
            "current": current,
            "longitude": longitude,
            "latitude": latitude
        }
        request_data = filter_empty_params(request_data)
        response = requests.post(
            ApiEndpoints.build_url(ApiEndpoints.COUPON_LIST_CATEGORY),
            json=request_data,
            headers={
                "app-key": APP_KEY,
                "secret": APP_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            return {"error": f"Get coupon list failed: {data.get('message') or data.get('msg')}"}

        return {
            "data": data.get("data", []),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def get_restaurant_promotion_link(
        link_type: Annotated[int, Field(
            description="转链类型 1 H5长链接；2 H5短链接；3 deeplink(唤起)链接；4 微信小程序唤起路径；5 团口令；6 小程序码")] = 2,
        sku_id: Annotated[str, Field(description="券的skuId")] = ""
) -> Dict[str, Any]:
    """
    获取美食的推广链接

    根据指定条件获取美食的推广链接。
    """
    try:
        # 准备请求参数
        request_data = {
            "source": SOURCE_DICT["meituan"],  # 渠道：1：美团
            "linkType": link_type,
            "channel": CHANNEL_DICT["mcp"],
            "categoryId": CATEGORY_DICT["restaurant_coupons"],
            "skuId": sku_id
        }

        # 移除空值参数
        request_data = {
            k: v for k, v in request_data.items()
            if v is not None and v != ""
        }

        # 发送POST请求
        response = requests.post(
            ApiEndpoints.build_url(ApiEndpoints.GET_SHORT_LINK),
            json=request_data,
            headers={
                "app-key": APP_KEY,
                "secret": APP_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            return {"error": f"Get promotion link failed: {data.get('message') or data.get('msg')}"}

        return {
            "data": data.get("data", {}),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def list_entertainment_coupons(
        search_text: Annotated[str, Field(description="搜索关键词,券名、店铺名称", default="")],
        search_id: Annotated[str, Field(description="仅搜索场景分页使用，首次调用不用填", default="")],
        size: Annotated[str, Field(description="每页显示条数", default="10")],
        current: Annotated[str, Field(description="当前页", default="1")],
        longitude: Annotated[str, Field(description="经度",default="")],
        latitude: Annotated[str, Field(description="纬度",default="")],
) -> Dict[str, Any]:
    """
    获取支持的休闲娱乐优惠券列表

    根据指定条件查询优惠券分类信息，支持搜索、分页等功能。
    """
    try:
        # 准备请求参数
        request_data = {
            "searchText": search_text,
            "source": SOURCE_DICT["meituan"],
            "categoryId": CATEGORY_DICT["entertainment_coupons"],
            "searchId": search_id if search_id else "0",
            "size": size,
            "current": current,
            "longitude": longitude,
            "latitude": latitude
        }
        request_data = filter_empty_params(request_data)

        response = requests.post(
            ApiEndpoints.build_url(ApiEndpoints.COUPON_LIST_CATEGORY),
            json=request_data,
            headers={
                "app-key": APP_KEY,
                "secret": APP_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            return {"error": f"Get coupon list failed: {data.get('message') or data.get('msg')}"}

        return {
            "data": data.get("data", []),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def get_entertainment_promotion_link(
        link_type: Annotated[int, Field(
            description="转链类型 1 H5长链接；2 H5短链接；3 deeplink(唤起)链接；4 微信小程序唤起路径；5 团口令；6 小程序码")] = 2,
        sku_id: Annotated[str, Field(description="券的skuId")] = ""
) -> Dict[str, Any]:
    """
    获取休闲娱乐的推广链接

    根据指定条件获取休闲娱乐的推广链接。
    """
    try:
        # 准备请求参数
        request_data = {
            "source": SOURCE_DICT["meituan"],  # 渠道：1：美团
            "linkType": link_type,
            "channel": CHANNEL_DICT["mcp"],
            "categoryId": CATEGORY_DICT["entertainment_coupons"],
            "skuId": sku_id
        }

        # 移除空值参数
        request_data = filter_empty_params(request_data)

        # 发送POST请求
        response = requests.post(
            ApiEndpoints.build_url(ApiEndpoints.GET_SHORT_LINK),
            json=request_data,
            headers={
                "app-key": APP_KEY,
                "secret": APP_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            return {"error": f"Get promotion link failed: {data.get('message') or data.get('msg')}"}

        return {
            "data": data.get("data", {}),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def list_hotel_coupons(
        search_text: Annotated[str, Field(description="搜索关键词,券名、店铺名称", default="")],
        search_id: Annotated[str, Field(description="仅搜索场景分页使用，首次调用不用填", default="")],
        size: Annotated[str, Field(description="每页显示条数", default="10")],
        current: Annotated[str, Field(description="当前页", default="1")],
        longitude: Annotated[str, Field(description="经度",default="")],
        latitude: Annotated[str, Field(description="纬度",default="")],
) -> Dict[str, Any]:
    """
    获取支持的酒店民宿优惠券列表

    根据指定条件查询优惠券分类信息，支持搜索、分页等功能。
    """
    try:
        # 准备请求参数
        request_data = {
            "searchText": search_text,
            "source": SOURCE_DICT["meituan"],
            "categoryId": CATEGORY_DICT["hotel_coupons"],
            "searchId": search_id if search_id else "0",
            "size": size,
            "current": current,
            "longitude": longitude,
            "latitude": latitude
        }
        request_data = filter_empty_params(request_data)

        response = requests.post(
            ApiEndpoints.build_url(ApiEndpoints.COUPON_LIST_CATEGORY),
            json=request_data,
            headers={
                "app-key": APP_KEY,
                "secret": APP_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            return {"error": f"Get coupon list failed: {data.get('message') or data.get('msg')}"}

        return {
            "data": data.get("data", []),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def get_hotel_promotion_link(
        link_type: Annotated[int, Field(
            description="转链类型 1 H5长链接；2 H5短链接；3 deeplink(唤起)链接；4 微信小程序唤起路径；5 团口令；6 小程序码")] = 2,
        sku_id: Annotated[str, Field(description="券的skuId")] = ""
) -> Dict[str, Any]:
    """
    获取酒店民宿的推广链接

    根据指定条件获取酒店民宿的推广链接。
    """
    try:
        # 准备请求参数
        request_data = {
            "source": SOURCE_DICT["meituan"],  # 渠道：1：美团
            "linkType": link_type,
            "channel": CHANNEL_DICT["mcp"],
            "categoryId": CATEGORY_DICT["hotel_coupons"],
            "skuId": sku_id
        }

        # 移除空值参数
        request_data = filter_empty_params(request_data)

        # 发送POST请求
        response = requests.post(
            ApiEndpoints.build_url(ApiEndpoints.GET_SHORT_LINK),
            json=request_data,
            headers={
                "app-key": APP_KEY,
                "secret": APP_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            return {"error": f"Get promotion link failed: {data.get('message') or data.get('msg')}"}

        return {
            "data": data.get("data", {}),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def list_travel_coupons(
        search_text: Annotated[str, Field(description="搜索关键词,券名、店铺名称", default="")],
        search_id: Annotated[str, Field(description="仅搜索场景分页使用，首次调用不用填", default="")],
        size: Annotated[str, Field(description="每页显示条数", default="10")],
        current: Annotated[str, Field(description="当前页", default="1")],
        longitude: Annotated[str, Field(description="经度",default="")],
        latitude: Annotated[str, Field(description="纬度",default="")],
) -> Dict[str, Any]:
    """
    获取支持的门票度假优惠券列表

    根据指定条件查询优惠券分类信息，支持搜索、分页等功能。
    """
    try:
        # 准备请求参数
        request_data = {
            "searchText": search_text,
            "source": SOURCE_DICT["meituan"],
            "categoryId": CATEGORY_DICT["travel_coupons"],
            "searchId": search_id if search_id else "0",
            "size": size,
            "current": current,
            "longitude": longitude,
            "latitude": latitude
        }
        request_data = filter_empty_params(request_data)

        response = requests.post(
            ApiEndpoints.build_url(ApiEndpoints.COUPON_LIST_CATEGORY),
            json=request_data,
            headers={
                "app-key": APP_KEY,
                "secret": APP_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            return {"error": f"Get coupon list failed: {data.get('message') or data.get('msg')}"}

        return {
            "data": data.get("data", []),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def get_travel_promotion_link(
        link_type: Annotated[int, Field(
            description="转链类型 1 H5长链接；2 H5短链接；3 deeplink(唤起)链接；4 微信小程序唤起路径；5 团口令；6 小程序码")] = 2,
        sku_id: Annotated[str, Field(description="券的skuId")] = ""
) -> Dict[str, Any]:
    """
    获取门票度假的推广链接

    根据指定条件获取门票度假的推广链接。
    """
    try:
        # 准备请求参数
        request_data = {
            "source": SOURCE_DICT["meituan"],  # 渠道：1：美团
            "linkType": link_type,
            "channel": CHANNEL_DICT["mcp"],
            "categoryId": CATEGORY_DICT["travel_coupons"],
            "skuId": sku_id
        }

        # 移除空值参数
        request_data = filter_empty_params(request_data)

        # 发送POST请求
        response = requests.post(
            ApiEndpoints.build_url(ApiEndpoints.GET_SHORT_LINK),
            json=request_data,
            headers={
                "app-key": APP_KEY,
                "secret": APP_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            return {"error": f"Get promotion link failed: {data.get('message') or data.get('msg')}"}

        return {
            "data": data.get("data", {}),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def list_medical_coupons(
        search_text: Annotated[str, Field(description="搜索关键词,券名、店铺名称", default="")],
        search_id: Annotated[str, Field(description="仅搜索场景分页使用，首次调用不用填", default="")],
        size: Annotated[str, Field(description="每页显示条数", default="10")],
        current: Annotated[str, Field(description="当前页", default="1")],
        longitude: Annotated[str, Field(description="经度",default="")],
        latitude: Annotated[str, Field(description="纬度",default="")],
) -> Dict[str, Any]:
    """
    获取支持的医药优惠券列表

    根据指定条件查询优惠券分类信息，支持搜索、分页等功能。
    """
    try:
        # 准备请求参数
        request_data = {
            "searchText": search_text,
            "source": SOURCE_DICT["meituan"],
            "categoryId": CATEGORY_DICT["medical_coupons"],
            "searchId": search_id if search_id else "0",
            "size": size,
            "current": current,
            "longitude": longitude,
            "latitude": latitude
        }
        request_data = filter_empty_params(request_data)

        response = requests.post(
            ApiEndpoints.build_url(ApiEndpoints.COUPON_LIST_CATEGORY),
            json=request_data,
            headers={
                "app-key": APP_KEY,
                "secret": APP_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            return {"error": f"Get coupon list failed: {data.get('message') or data.get('msg')}"}

        return {
            "data": data.get("data", []),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def get_medical_promotion_link(
        link_type: Annotated[int, Field(
            description="转链类型 1 H5长链接；2 H5短链接；3 deeplink(唤起)链接；4 微信小程序唤起路径；5 团口令；6 小程序码",
            default=2)],
        sku_id: Annotated[str, Field(description="券的skuId", default="")]
) -> Dict[str, Any]:
    """
    获取医药的推广链接

    根据指定条件获取医药的推广链接。
    """
    try:
        # 准备请求参数
        request_data = {
            "source": SOURCE_DICT["meituan"],  # 渠道：1：美团
            "linkType": link_type,
            "channel": CHANNEL_DICT["mcp"],
            "categoryId": CATEGORY_DICT["medical_coupons"],
            "skuId": sku_id
        }

        # 移除空值参数
        request_data = filter_empty_params(request_data)

        # 发送POST请求
        response = requests.post(
            ApiEndpoints.build_url(ApiEndpoints.GET_SHORT_LINK),
            json=request_data,
            headers={
                "app-key": APP_KEY,
                "secret": APP_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            return {"error": f"Get promotion link failed: {data.get('message') or data.get('msg')}"}

        return {
            "data": data.get("data", {}),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="agentsyun coupon MCP Server")
    parser.add_argument('transport', nargs='?', default='stdio', choices=['stdio', 'sse', 'streamable-http'],
                        help='Transport type (stdio, sse, or streamable-http)')
    # parser.add_argument('port', type=int, default=8000, help='Port to listen on (for HTTP transports)')
    args = parser.parse_args()

    # 设置监听所有接口的8000端口
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000
    # Run the MCP server with the specified transport
    # mcp.settings.port = args.port
    mcp.run(transport=args.transport)
