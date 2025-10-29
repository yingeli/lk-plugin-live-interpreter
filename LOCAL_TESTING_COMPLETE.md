# 本地测试环境配置完成 ✅

恭喜！本地测试环境已完全配置完成。本文档总结了所有可用的资源和下一步操作。

## 📦 已创建的资源

### 文档 (Documentation)

| 文件 | 大小 | 用途 |
|------|------|------|
| [LOCAL_TESTING.md](LOCAL_TESTING.md) | 11K | 完整的本地测试指南，包含详细的设置步骤、测试方法、调试技巧 |
| [QUICKSTART.md](QUICKSTART.md) | 4.5K | 5分钟快速开始指南，适合快速上手 |
| [LOCAL_TESTING_SUMMARY.md](LOCAL_TESTING_SUMMARY.md) | 8.6K | 测试资源总览，包含检查清单和最佳实践 |
| [README.md](README.md) | 5.7K | 项目总览（已更新，包含本地测试说明） |

### 脚本 (Scripts)

| 文件 | 大小 | 用途 | 命令 |
|------|------|------|------|
| [setup_local_dev.sh](setup_local_dev.sh) | 5.7K | 自动化开发环境设置脚本 | `./setup_local_dev.sh` |
| [examples/test_local.py](examples/test_local.py) | 8.1K | 验证安装和配置的测试脚本 | `python examples/test_local.py` |
| [Makefile](Makefile) | 7.1K | 简化常用命令的 Makefile | `make help` |

### 配置文件 (Configuration)

| 文件 | 状态 | 说明 |
|------|------|------|
| `.env` | 需要创建 | 环境变量配置文件（运行 setup 脚本会自动创建模板） |
| `.gitignore` | 自动创建 | Git 忽略规则（setup 脚本会自动创建） |

## 🚀 快速开始

### 方法 1: 使用 Makefile（最简单）

```bash
# 1. 设置环境
make setup

# 2. 配置凭证
vim .env

# 3. 验证安装
make test-quick

# 4. 运行示例
make run-simple

# 5. 查看所有命令
make help
```

### 方法 2: 使用脚本

```bash
# 1. 运行设置脚本
./setup_local_dev.sh

# 2. 配置凭证
vim .env

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 验证安装
python examples/test_local.py

# 5. 运行示例
python examples/simple_interpreter.py
```

## 📋 Makefile 命令速查

### 设置和安装
```bash
make setup          # 运行自动化开发环境设置
make install        # 安装插件（开发模式）
make dev            # 安装开发依赖
make dev-setup      # 完整的开发环境设置（setup + install + dev）
```

### 测试
```bash
make test           # 运行所有测试
make test-quick     # 快速验证安装
make test-unit      # 运行单元测试
make test-coverage  # 运行测试并生成覆盖率报告
make check-env      # 检查环境变量配置
```

### 运行示例
```bash
make run-simple     # 运行简单双语翻译示例
make run-multi      # 运行多语言会议示例
make run-custom     # 运行自定义语音示例
```

### 代码质量
```bash
make lint           # 运行代码检查
make format         # 格式化代码
make type-check     # 运行类型检查
make ci             # CI/CD 检查（lint + type-check + test-unit）
```

### 清理
```bash
make clean          # 清理临时文件
make clean-all      # 清理所有生成文件（包括虚拟环境）
```

### 其他
```bash
make help           # 显示帮助信息
make docs           # 显示文档列表
make status         # 显示项目状态
```

## 📚 文档导航

### 我应该先看哪个文档？

根据您的需求选择：

1. **快速上手** → [QUICKSTART.md](QUICKSTART.md)
   - 5分钟快速开始
   - 适合想要快速测试的用户

2. **详细学习** → [LOCAL_TESTING.md](LOCAL_TESTING.md)
   - 完整的测试指南
   - 包含调试技巧和故障排查
   - 适合深入开发的用户

3. **资源总览** → [LOCAL_TESTING_SUMMARY.md](LOCAL_TESTING_SUMMARY.md)
   - 所有测试资源的总结
   - 检查清单和最佳实践
   - 适合需要系统化了解的用户

4. **项目概览** → [README.md](README.md)
   - 项目总体介绍
   - 功能特性和架构
   - 适合初次了解项目的用户

## ✅ 配置检查清单

在开始测试前，请确保完成以下步骤：

### 环境准备
- [ ] Python 3.9+ 已安装
- [ ] 虚拟环境已创建（`make setup` 或 `./setup_local_dev.sh`）
- [ ] 所有依赖已安装
- [ ] 插件以开发模式安装

### Azure 配置
- [ ] Azure Speech Service 资源已创建
- [ ] Subscription Key 已获取
- [ ] Region 已确认
- [ ] （可选）Personal Voice 已配置

### LiveKit 配置
- [ ] LiveKit Cloud 账号已创建（https://cloud.livekit.io）
- [ ] 项目已创建
- [ ] API Key 和 Secret 已获取
- [ ] URL 格式正确（wss://...）

### 环境变量
- [ ] `.env` 文件已创建
- [ ] `AZURE_SPEECH_KEY` 已设置
- [ ] `AZURE_SPEECH_REGION` 已设置
- [ ] `LIVEKIT_URL` 已设置
- [ ] `LIVEKIT_API_KEY` 已设置
- [ ] `LIVEKIT_API_SECRET` 已设置

### 验证
- [ ] `make test-quick` 或 `python examples/test_local.py` 通过
- [ ] 所有测试项显示 ✓

## 🎯 典型工作流程

### 开发新功能

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 修改代码
vim livekit-plugins/livekit-plugins-azure/livekit/plugins/azure/realtime/realtime_model.py

# 3. 运行测试（无需重新安装，开发模式会自动生效）
make test-quick

# 4. 运行示例验证
make run-simple

# 5. 运行单元测试
make test-unit

# 6. 代码检查和格式化
make format
make lint
```

### 调试问题

```bash
# 1. 启用调试日志
export LIVEKIT_LOG_LEVEL=debug

# 2. 运行示例
make run-simple

# 3. 查看详细日志输出

# 4. 如果需要，修改代码并重新测试
```

### 提交代码前

```bash
# 1. 格式化代码
make format

# 2. 运行所有检查
make ci

# 3. 确保所有测试通过
make test

# 4. 清理临时文件
make clean
```

## 🔍 故障排查

### 问题：虚拟环境未激活

**症状**：运行命令时提示找不到模块

**解决方案**：
```bash
source venv/bin/activate
```

### 问题：环境变量未设置

**症状**：测试脚本报告缺少环境变量

**解决方案**：
```bash
# 检查 .env 文件
cat .env

# 或使用 make 命令检查
make check-env

# 编辑 .env 文件
vim .env
```

### 问题：插件未安装

**症状**：导入 `livekit.plugins.azure` 失败

**解决方案**：
```bash
# 重新安装插件
make install

# 或手动安装
cd livekit-plugins/livekit-plugins-azure
pip install -e .
cd ../..
```

### 问题：Azure 或 LiveKit 连接失败

**症状**：测试脚本报告连接失败

**解决方案**：
```bash
# 验证 Azure 凭证
python -c "
import os
from azure.cognitiveservices.speech import SpeechConfig
config = SpeechConfig(
    subscription=os.environ['AZURE_SPEECH_KEY'],
    region=os.environ['AZURE_SPEECH_REGION']
)
print('Azure credentials valid!')
"

# 验证 LiveKit 连接
lk room list \
  --url $LIVEKIT_URL \
  --api-key $LIVEKIT_API_KEY \
  --api-secret $LIVEKIT_API_SECRET
```

## 📊 测试覆盖

### 已实现的测试

1. **环境验证测试** (`examples/test_local.py`)
   - 环境变量检查
   - Azure 连接测试
   - LiveKit 连接测试
   - 插件导入测试
   - 插件实例化测试

2. **单元测试** (`livekit-plugins/livekit-plugins-azure/tests/`)
   - 数据模型测试
   - 工具函数测试
   - 语言验证测试

3. **集成测试** (示例程序)
   - 简单双语翻译
   - 多语言会议
   - 自定义语音

### 测试命令

```bash
# 快速验证
make test-quick

# 单元测试
make test-unit

# 测试覆盖率
make test-coverage

# 所有测试
make test
```

## 🎉 下一步

完成本地测试环境配置后，您可以：

### 1. 开始开发
- 修改插件代码
- 添加新功能
- 编写测试

### 2. 深入学习
- 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解技术架构
- 研究示例代码
- 探索 LiveKit Agents 框架

### 3. 部署到生产
- 阅读 [DEPLOYMENT.md](DEPLOYMENT.md)
- 配置 Docker
- 部署到 LiveKit Cloud

### 4. 贡献代码
- 阅读 [CONTRIBUTING.md](CONTRIBUTING.md)
- 提交 Pull Request
- 参与社区讨论

## 💡 提示和技巧

### 使用 Makefile 提高效率

```bash
# 查看所有可用命令
make help

# 查看项目状态
make status

# 查看文档列表
make docs
```

### 使用开发模式

插件以 `-e` (editable) 模式安装，这意味着：
- 修改代码后无需重新安装
- 更改会立即生效
- 适合快速迭代开发

### 使用环境变量

```bash
# 临时设置环境变量
export LIVEKIT_LOG_LEVEL=debug

# 或在命令前设置
LIVEKIT_LOG_LEVEL=debug make run-simple
```

### 使用 .env 文件

```bash
# 加载 .env 文件
source .env

# 或使用 python-dotenv
pip install python-dotenv
```

## 📞 获取帮助

如果遇到问题：

1. **查看文档**
   - [LOCAL_TESTING.md](LOCAL_TESTING.md) 的故障排查部分
   - [QUICKSTART.md](QUICKSTART.md) 的常见问题

2. **检查日志**
   ```bash
   export LIVEKIT_LOG_LEVEL=debug
   make run-simple
   ```

3. **验证配置**
   ```bash
   make check-env
   make status
   ```

4. **社区支持**
   - LiveKit Discord: https://livekit.io/discord
   - Azure 支持: https://azure.microsoft.com/support/
   - GitHub Issues: 提交问题报告

## 🎊 总结

您现在拥有：

✅ 完整的本地开发环境
✅ 自动化设置脚本
✅ 验证测试脚本
✅ Makefile 简化命令
✅ 详细的文档指南
✅ 示例代码和测试

开始您的开发之旅吧！🚀

---

**最后更新**: 2025-10-29

**相关文档**:
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [LOCAL_TESTING.md](LOCAL_TESTING.md) - 完整测试指南
- [LOCAL_TESTING_SUMMARY.md](LOCAL_TESTING_SUMMARY.md) - 资源总览
- [README.md](README.md) - 项目总览
