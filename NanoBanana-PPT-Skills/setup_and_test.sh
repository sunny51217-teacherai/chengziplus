#!/bin/bash
# =============================================================================
# NanoBanana PPT Skills - 一键安装并测试脚本
# =============================================================================
# 用法:
#   chmod +x setup_and_test.sh
#   ./setup_and_test.sh
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo " NanoBanana PPT Skills - 安装并测试"
echo "============================================================"
echo ""

# 1. 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "[1/4] 创建 Python 虚拟环境..."
    python3 -m venv venv
else
    echo "[1/4] 虚拟环境已存在，跳过"
fi

# 2. 激活并安装依赖
echo "[2/4] 安装依赖..."
source venv/bin/activate
pip install -q google-genai pillow python-dotenv requests

# 3. 检查 .env 配置
echo "[3/4] 检查 API 配置..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "  已创建 .env 文件，请编辑填入你的 API 密钥："
    echo "  vim .env"
    echo ""
    echo "  至少需要设置以下之一："
    echo "    GEMINI_API_KEY=xxx  (Google Gemini 后端)"
    echo "    ARK_API_KEY=xxx     (即梦 Jimeng 后端)"
    echo ""
    exit 0
fi

# 判断可用的后端
BACKEND=""
ARK_KEY=$(grep "^ARK_API_KEY=" .env | cut -d'=' -f2-)
GEMINI_KEY=$(grep "^GEMINI_API_KEY=" .env | cut -d'=' -f2-)

if [ -n "$ARK_KEY" ] && [ "$ARK_KEY" != "your-ark-api-key-here" ]; then
    BACKEND="jimeng"
    echo "  使用即梦 (Jimeng) 后端"
elif [ -n "$GEMINI_KEY" ] && [ "$GEMINI_KEY" != "your-gemini-api-key-here" ]; then
    BACKEND="gemini"
    echo "  使用 Gemini 后端"
else
    echo ""
    echo "  错误: 未配置有效的 API 密钥！"
    echo "  请编辑 .env 文件，设置 ARK_API_KEY 或 GEMINI_API_KEY"
    exit 1
fi

# 4. 运行测试
echo "[4/4] 生成 3 页测试 PPT..."
echo ""

python3 generate_ppt.py \
    --plan test_plan.json \
    --style styles/gradient-glass.md \
    --backend "$BACKEND" \
    --resolution 2K \
    --output outputs/test_run

echo ""
echo "============================================================"
echo " 完成！用浏览器打开查看结果："
echo " open outputs/test_run/index.html"
echo "============================================================"
