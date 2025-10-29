#!/bin/bash

# Local Development Setup Script for Azure Live Interpreter Plugin
# 本地开发环境设置脚本

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    print_header "Azure Live Interpreter Plugin - Local Development Setup"
    print_info "本地开发环境设置开始..."

    # Step 1: Check Python version
    print_info "检查 Python 版本..."
    if ! command_exists python3; then
        print_error "Python 3 未安装。请先安装 Python 3.9 或更高版本。"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python 版本: $PYTHON_VERSION"

    # Check if Python version is >= 3.9
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
        print_error "需要 Python 3.9 或更高版本，当前版本: $PYTHON_VERSION"
        exit 1
    fi

    # Step 2: Create virtual environment
    print_info "创建虚拟环境..."
    if [ -d "venv" ]; then
        print_warning "虚拟环境已存在，跳过创建。"
        print_info "如需重新创建，请先删除 venv 目录: rm -rf venv"
    else
        python3 -m venv venv
        print_success "虚拟环境创建成功"
    fi

    # Step 3: Activate virtual environment
    print_info "激活虚拟环境..."
    source venv/bin/activate
    print_success "虚拟环境已激活"

    # Step 4: Upgrade pip
    print_info "升级 pip..."
    pip install --upgrade pip > /dev/null 2>&1
    print_success "pip 已升级"

    # Step 5: Install core dependencies
    print_info "安装核心依赖..."
    pip install livekit-agents livekit-cli > /dev/null 2>&1
    print_success "核心依赖安装完成"

    # Step 6: Install plugin in editable mode
    print_info "以开发模式安装插件..."
    cd livekit-plugins/livekit-plugins-azure
    pip install -e . > /dev/null 2>&1
    cd ../..
    print_success "插件安装完成（可编辑模式）"

    # Step 7: Install development dependencies
    print_info "安装开发依赖..."
    pip install pytest pytest-asyncio pytest-cov black flake8 mypy > /dev/null 2>&1
    print_success "开发依赖安装完成"

    # Step 8: Check for .env file
    print_info "检查环境变量配置..."
    if [ -f ".env" ]; then
        print_success ".env 文件已存在"
        print_warning "请确保已配置以下环境变量:"
        echo "  - AZURE_SPEECH_KEY"
        echo "  - AZURE_SPEECH_REGION"
        echo "  - LIVEKIT_URL"
        echo "  - LIVEKIT_API_KEY"
        echo "  - LIVEKIT_API_SECRET"
    else
        print_warning ".env 文件不存在，创建模板..."
        cat > .env << 'EOF'
# Azure Speech Service 配置
AZURE_SPEECH_KEY=your_subscription_key_here
AZURE_SPEECH_REGION=eastus

# LiveKit 配置
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here

# 可选：Personal Voice 配置
# AZURE_SPEAKER_PROFILE_ID=your_speaker_profile_id_here

# 可选：日志级别
# LIVEKIT_LOG_LEVEL=debug
EOF
        print_success ".env 模板已创建"
        print_warning "请编辑 .env 文件并填入您的实际凭证"
    fi

    # Step 9: Create .gitignore if not exists
    if [ ! -f ".gitignore" ]; then
        print_info "创建 .gitignore..."
        cat > .gitignore << 'EOF'
# Virtual environment
venv/
.venv/

# Environment variables
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
EOF
        print_success ".gitignore 已创建"
    fi

    # Step 10: Verify installation
    print_info "验证安装..."
    python3 -c "
import sys
try:
    from livekit import agents
    from livekit.plugins import azure
    print('✓ LiveKit Agents imported successfully')
    print('✓ Azure plugin imported successfully')
    sys.exit(0)
except ImportError as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)
" && print_success "安装验证通过" || print_error "安装验证失败"

    # Step 11: Display next steps
    print_header "设置完成！"

    echo -e "${GREEN}下一步操作:${NC}"
    echo ""
    echo "1. 配置环境变量:"
    echo -e "   ${YELLOW}vim .env${NC}"
    echo ""
    echo "2. 激活虚拟环境 (如果还未激活):"
    echo -e "   ${YELLOW}source venv/bin/activate${NC}"
    echo ""
    echo "3. 运行测试示例:"
    echo -e "   ${YELLOW}python examples/simple_interpreter.py${NC}"
    echo ""
    echo "4. 运行单元测试:"
    echo -e "   ${YELLOW}cd livekit-plugins/livekit-plugins-azure && pytest tests/${NC}"
    echo ""
    echo "5. 查看完整测试指南:"
    echo -e "   ${YELLOW}cat LOCAL_TESTING.md${NC}"
    echo ""

    print_info "更多信息请参考 LOCAL_TESTING.md"
    print_success "祝开发顺利！"
}

# Run main function
main "$@"
