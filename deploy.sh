#!/bin/bash
# ============================================
# 智能题库与试卷生成平台 - 阿里云部署脚本
# 适用系统: Ubuntu 24.04
# ============================================

set -e

echo "===== 1. 安装 Docker ====="

if ! command -v docker &> /dev/null; then
    apt update
    apt install -y ca-certificates curl
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
        > /etc/apt/sources.list.d/docker.list
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable docker --now
    echo "Docker 安装完成"
else
    echo "Docker 已安装"
fi

echo ""
echo "===== 2. 配置 .env ====="

if [ ! -f .env ]; then
    if [ -f .env.docker ]; then
        cp .env.docker .env
        echo "已从 .env.docker 创建 .env，请修改 SECRET_KEY 等敏感值"
    else
        echo "请先创建 .env 文件（参考 .env.docker）"
        exit 1
    fi
else
    echo ".env 已存在"
fi

echo ""
echo "===== 3. 构建并启动 ====="

docker compose up -d --build

echo ""
echo "===== 4. 检查状态 ====="

sleep 3
docker compose ps

echo ""
echo "===== 部署完成 ====="
echo "访问地址: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_IP')"
echo ""
echo "常用命令:"
echo "  docker compose ps          # 查看服务状态"
echo "  docker compose logs -f     # 查看日志"
echo "  docker compose restart     # 重启服务"
echo "  docker compose down        # 停止服务"
echo "  docker compose up -d       # 启动服务"
