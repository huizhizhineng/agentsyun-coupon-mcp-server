#!/bin/bash
set -ex
cd `dirname $0`

# 设置环境变量（如果需要）
export PYTHONPATH=$PYTHONPATH:./site-packages

# 启动 agentsyun-coupon-mcp-server 服务,根据你的需求修改启动参数，
# 推荐本地部署使用uv的方式
exec python3 -m agentsyun_coupon_mcp_server streamable-http
