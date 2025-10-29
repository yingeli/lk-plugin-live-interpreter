# Makefile for Azure Live Interpreter Plugin
# 简化常用开发和测试命令

.PHONY: help setup test test-quick clean install dev lint format run-simple run-multi docs

# 默认目标：显示帮助
help:
	@echo "Azure Live Interpreter Plugin - 开发命令"
	@echo ""
	@echo "设置和安装:"
	@echo "  make setup          - 运行自动化开发环境设置"
	@echo "  make install        - 安装插件（开发模式）"
	@echo "  make dev            - 安装开发依赖"
	@echo ""
	@echo "测试:"
	@echo "  make test           - 运行所有测试"
	@echo "  make test-quick     - 快速验证安装"
	@echo "  make test-unit      - 运行单元测试"
	@echo "  make test-coverage  - 运行测试并生成覆盖率报告"
	@echo ""
	@echo "运行示例:"
	@echo "  make run-simple     - 运行简单双语翻译示例"
	@echo "  make run-multi      - 运行多语言会议示例"
	@echo "  make run-custom     - 运行自定义语音示例"
	@echo ""
	@echo "代码质量:"
	@echo "  make lint           - 运行代码检查"
	@echo "  make format         - 格式化代码"
	@echo "  make type-check     - 运行类型检查"
	@echo ""
	@echo "清理:"
	@echo "  make clean          - 清理临时文件"
	@echo "  make clean-all      - 清理所有生成文件（包括虚拟环境）"
	@echo ""
	@echo "文档:"
	@echo "  make docs           - 查看文档列表"
	@echo ""

# 设置开发环境
setup:
	@echo "运行自动化设置脚本..."
	./setup_local_dev.sh

# 安装插件（开发模式）
install:
	@echo "安装插件（开发模式）..."
	@if [ ! -d "venv" ]; then \
		echo "错误: 虚拟环境不存在。请先运行 'make setup'"; \
		exit 1; \
	fi
	@. venv/bin/activate && \
		cd livekit-plugins/livekit-plugins-azure && \
		pip install -e . && \
		cd ../..
	@echo "✓ 插件安装完成"

# 安装开发依赖
dev:
	@echo "安装开发依赖..."
	@. venv/bin/activate && \
		pip install pytest pytest-asyncio pytest-cov black flake8 mypy python-dotenv
	@echo "✓ 开发依赖安装完成"

# 快速验证测试
test-quick:
	@echo "运行快速验证测试..."
	@. venv/bin/activate && python examples/test_local.py

# 运行单元测试
test-unit:
	@echo "运行单元测试..."
	@. venv/bin/activate && \
		cd livekit-plugins/livekit-plugins-azure && \
		pytest tests/ -v && \
		cd ../..

# 运行测试并生成覆盖率
test-coverage:
	@echo "运行测试并生成覆盖率报告..."
	@. venv/bin/activate && \
		cd livekit-plugins/livekit-plugins-azure && \
		pytest --cov=livekit.plugins.azure --cov-report=html --cov-report=term tests/ && \
		cd ../..
	@echo "✓ 覆盖率报告生成在 livekit-plugins/livekit-plugins-azure/htmlcov/"

# 运行所有测试
test: test-quick test-unit
	@echo "✓ 所有测试完成"

# 运行简单示例
run-simple:
	@echo "运行简单双语翻译示例..."
	@. venv/bin/activate && python examples/simple_interpreter.py

# 运行多语言示例
run-multi:
	@echo "运行多语言会议示例..."
	@. venv/bin/activate && python examples/multi_language_meeting.py

# 运行自定义语音示例
run-custom:
	@echo "运行自定义语音示例..."
	@if [ -z "$$AZURE_SPEAKER_PROFILE_ID" ]; then \
		echo "警告: AZURE_SPEAKER_PROFILE_ID 未设置"; \
		echo "请设置环境变量或在 .env 文件中配置"; \
		exit 1; \
	fi
	@. venv/bin/activate && python examples/custom_voice_interpreter.py

# 代码检查
lint:
	@echo "运行代码检查..."
	@. venv/bin/activate && \
		cd livekit-plugins/livekit-plugins-azure && \
		flake8 livekit/ --max-line-length=100 --ignore=E203,W503 && \
		cd ../..
	@echo "✓ 代码检查通过"

# 格式化代码
format:
	@echo "格式化代码..."
	@. venv/bin/activate && \
		cd livekit-plugins/livekit-plugins-azure && \
		black livekit/ tests/ && \
		cd ../..
	@echo "✓ 代码格式化完成"

# 类型检查
type-check:
	@echo "运行类型检查..."
	@. venv/bin/activate && \
		cd livekit-plugins/livekit-plugins-azure && \
		mypy livekit/ --ignore-missing-imports && \
		cd ../..
	@echo "✓ 类型检查通过"

# 清理临时文件
clean:
	@echo "清理临时文件..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ 临时文件清理完成"

# 清理所有生成文件
clean-all: clean
	@echo "清理虚拟环境..."
	@rm -rf venv
	@echo "清理构建文件..."
	@rm -rf livekit-plugins/livekit-plugins-azure/dist
	@rm -rf livekit-plugins/livekit-plugins-azure/build
	@echo "✓ 所有生成文件清理完成"

# 显示文档列表
docs:
	@echo "可用文档:"
	@echo ""
	@echo "入门指南:"
	@echo "  - QUICKSTART.md              5分钟快速开始"
	@echo "  - LOCAL_TESTING.md           完整本地测试指南"
	@echo "  - LOCAL_TESTING_SUMMARY.md   测试资源总览"
	@echo ""
	@echo "部署指南:"
	@echo "  - DEPLOYMENT.md              部署到 LiveKit Cloud"
	@echo "  - PLAYGROUND_GUIDE.md        Playground 测试指南"
	@echo ""
	@echo "技术文档:"
	@echo "  - ARCHITECTURE.md            技术架构"
	@echo "  - README.md                  项目总览"
	@echo ""
	@echo "示例代码:"
	@echo "  - examples/simple_interpreter.py"
	@echo "  - examples/multi_language_meeting.py"
	@echo "  - examples/custom_voice_interpreter.py"
	@echo ""

# 检查环境变量
check-env:
	@echo "检查环境变量配置..."
	@if [ ! -f ".env" ]; then \
		echo "警告: .env 文件不存在"; \
		echo "请运行 'make setup' 或手动创建 .env 文件"; \
		exit 1; \
	fi
	@echo "✓ .env 文件存在"
	@. venv/bin/activate && python -c "\
import os; \
from dotenv import load_dotenv; \
load_dotenv(); \
required = ['AZURE_SPEECH_KEY', 'AZURE_SPEECH_REGION', 'LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET']; \
missing = [k for k in required if not os.getenv(k)]; \
if missing: \
    print(f'错误: 缺少必需的环境变量: {missing}'); \
    exit(1); \
print('✓ 所有必需的环境变量已设置')"

# 完整的开发流程
dev-setup: setup install dev
	@echo ""
	@echo "✓ 开发环境设置完成！"
	@echo ""
	@echo "下一步:"
	@echo "  1. 配置环境变量: vim .env"
	@echo "  2. 验证安装: make test-quick"
	@echo "  3. 运行示例: make run-simple"
	@echo ""

# CI/CD 流程
ci: lint type-check test-unit
	@echo "✓ CI 检查通过"

# 显示状态
status:
	@echo "项目状态:"
	@echo ""
	@if [ -d "venv" ]; then \
		echo "✓ 虚拟环境已创建"; \
	else \
		echo "✗ 虚拟环境未创建 (运行 'make setup')"; \
	fi
	@if [ -f ".env" ]; then \
		echo "✓ .env 文件存在"; \
	else \
		echo "✗ .env 文件不存在 (运行 'make setup')"; \
	fi
	@if [ -d "livekit-plugins/livekit-plugins-azure/livekit.egg-info" ]; then \
		echo "✓ 插件已安装"; \
	else \
		echo "✗ 插件未安装 (运行 'make install')"; \
	fi
	@echo ""
