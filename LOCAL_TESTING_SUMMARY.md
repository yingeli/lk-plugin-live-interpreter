# 本地测试资源总结

本文档总结了所有本地测试相关的文件和资源。

## 📁 文件清单

### 核心文档

| 文件 | 用途 | 适用场景 |
|------|------|----------|
| [LOCAL_TESTING.md](LOCAL_TESTING.md) | 完整的本地测试指南 | 详细的开发和调试 |
| [QUICKSTART.md](QUICKSTART.md) | 5分钟快速开始 | 快速上手 |
| [README.md](README.md) | 项目总览 | 了解项目概况 |

### 自动化脚本

| 文件 | 用途 | 命令 |
|------|------|------|
| [setup_local_dev.sh](setup_local_dev.sh) | 自动化开发环境设置 | `./setup_local_dev.sh` |
| [examples/test_local.py](examples/test_local.py) | 验证安装和配置 | `python examples/test_local.py` |

### 示例代码

| 文件 | 用途 | 命令 |
|------|------|------|
| [examples/simple_interpreter.py](examples/simple_interpreter.py) | 简单双语翻译 | `python examples/simple_interpreter.py` |
| [examples/multi_language_meeting.py](examples/multi_language_meeting.py) | 多语言会议 | `python examples/multi_language_meeting.py` |
| [examples/custom_voice_interpreter.py](examples/custom_voice_interpreter.py) | 自定义语音 | `python examples/custom_voice_interpreter.py` |

### 配置文件

| 文件 | 用途 | 说明 |
|------|------|------|
| `.env` | 环境变量配置 | 需要手动创建和配置 |
| `.gitignore` | Git 忽略规则 | 自动创建 |
| `requirements.txt` | Python 依赖 | 用于生产部署 |

## 🚀 快速开始流程

### 方法 1: 自动化设置（推荐）

```bash
# 1. 运行自动化设置
./setup_local_dev.sh

# 2. 配置环境变量
vim .env

# 3. 验证安装
python examples/test_local.py

# 4. 运行示例
python examples/simple_interpreter.py
```

### 方法 2: 手动设置

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install livekit-agents livekit-cli

# 3. 安装插件
cd livekit-plugins/livekit-plugins-azure
pip install -e .
cd ../..

# 4. 配置环境变量
cat > .env << 'EOF'
AZURE_SPEECH_KEY=your_key
AZURE_SPEECH_REGION=eastus
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
EOF

# 5. 验证和测试
python examples/test_local.py
```

## 📋 测试检查清单

### 环境准备
- [ ] Python 3.9+ 已安装
- [ ] 虚拟环境已创建
- [ ] 所有依赖已安装
- [ ] 插件以开发模式安装

### Azure 配置
- [ ] Azure Speech Service 资源已创建
- [ ] Subscription Key 已获取
- [ ] Region 已确认
- [ ] （可选）Personal Voice 已配置

### LiveKit 配置
- [ ] LiveKit Cloud 账号已创建
- [ ] 项目已创建
- [ ] API Key 和 Secret 已获取
- [ ] URL 格式正确 (wss://...)

### 环境变量
- [ ] `.env` 文件已创建
- [ ] `AZURE_SPEECH_KEY` 已设置
- [ ] `AZURE_SPEECH_REGION` 已设置
- [ ] `LIVEKIT_URL` 已设置
- [ ] `LIVEKIT_API_KEY` 已设置
- [ ] `LIVEKIT_API_SECRET` 已设置

### 验证测试
- [ ] `python examples/test_local.py` 通过
- [ ] 所有导入测试通过
- [ ] Azure 连接测试通过
- [ ] LiveKit 连接测试通过
- [ ] 插件实例化测试通过

### 功能测试
- [ ] 简单示例运行成功
- [ ] 多语言示例运行成功
- [ ] 音频输入正常
- [ ] 翻译输出正常

## 🔧 常见问题和解决方案

### 1. 虚拟环境问题

**问题**: "externally-managed-environment" 错误

**解决方案**:
```bash
# 使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install <package>
```

### 2. 导入错误

**问题**: "No module named 'livekit'"

**解决方案**:
```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 安装依赖
pip install livekit-agents

# 安装插件
cd livekit-plugins/livekit-plugins-azure
pip install -e .
```

### 3. Azure 认证失败

**问题**: "Azure Speech Service authentication failed"

**解决方案**:
```bash
# 验证凭证
python -c "
import os
from azure.cognitiveservices.speech import SpeechConfig
config = SpeechConfig(
    subscription=os.environ['AZURE_SPEECH_KEY'],
    region=os.environ['AZURE_SPEECH_REGION']
)
print('Valid!')
"
```

### 4. LiveKit 连接失败

**问题**: "Cannot connect to LiveKit server"

**解决方案**:
```bash
# 测试连接
lk room list \
  --url $LIVEKIT_URL \
  --api-key $LIVEKIT_API_KEY \
  --api-secret $LIVEKIT_API_SECRET
```

### 5. 构建错误

**问题**: "No module named build"

**解决方案**:
```bash
# 本地开发不需要构建
# 直接使用开发模式安装
cd livekit-plugins/livekit-plugins-azure
pip install -e .
```

## 📊 测试脚本功能对比

| 脚本 | 用途 | 测试内容 | 运行时间 |
|------|------|----------|----------|
| `setup_local_dev.sh` | 环境设置 | - 创建虚拟环境<br>- 安装依赖<br>- 创建配置文件 | ~2-3 分钟 |
| `examples/test_local.py` | 验证安装 | - 环境变量检查<br>- Azure 连接<br>- LiveKit 连接<br>- 插件导入 | ~10-20 秒 |
| `examples/simple_interpreter.py` | 功能测试 | - 双语翻译<br>- 实时音频处理 | 持续运行 |
| `examples/multi_language_meeting.py` | 高级功能 | - 多语言翻译<br>- 会议场景 | 持续运行 |

## 🎯 测试场景

### 场景 1: 首次安装验证

```bash
# 1. 运行自动化设置
./setup_local_dev.sh

# 2. 配置 .env
vim .env

# 3. 运行验证测试
python examples/test_local.py

# 预期结果: 所有测试通过 ✓
```

### 场景 2: 代码修改后测试

```bash
# 1. 修改插件代码
vim livekit-plugins/livekit-plugins-azure/livekit/plugins/azure/realtime/realtime_model.py

# 2. 无需重新安装（开发模式）

# 3. 直接运行测试
python examples/simple_interpreter.py

# 预期结果: 新代码生效
```

### 场景 3: 调试问题

```bash
# 1. 启用调试日志
export LIVEKIT_LOG_LEVEL=debug

# 2. 运行示例
python examples/simple_interpreter.py

# 3. 查看详细日志
# 预期结果: 详细的调试信息
```

### 场景 4: 单元测试

```bash
# 1. 进入插件目录
cd livekit-plugins/livekit-plugins-azure

# 2. 运行测试
pytest tests/ -v

# 3. 查看覆盖率
pytest --cov=livekit.plugins.azure tests/

# 预期结果: 所有单元测试通过
```

## 📚 文档导航

### 新手入门
1. 阅读 [QUICKSTART.md](QUICKSTART.md) - 5分钟快速开始
2. 运行 `./setup_local_dev.sh` - 自动化设置
3. 运行 `python examples/test_local.py` - 验证安装
4. 运行 `python examples/simple_interpreter.py` - 第一个示例

### 深入学习
1. 阅读 [LOCAL_TESTING.md](LOCAL_TESTING.md) - 完整测试指南
2. 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) - 技术架构
3. 阅读插件源码 - 理解实现细节
4. 编写自定义 Agent - 实践应用

### 部署上线
1. 阅读 [DEPLOYMENT.md](DEPLOYMENT.md) - 部署指南
2. 阅读 [PLAYGROUND_GUIDE.md](PLAYGROUND_GUIDE.md) - Playground 测试
3. 配置生产环境
4. 监控和优化

## 🔗 相关资源

### 官方文档
- [LiveKit Agents 文档](https://docs.livekit.io/agents/)
- [Azure Speech Service 文档](https://learn.microsoft.com/azure/ai-services/speech-service/)
- [Azure Live Interpreter API](https://learn.microsoft.com/azure/ai-services/speech-service/how-to-translate-speech)

### 社区资源
- [LiveKit Discord](https://livekit.io/discord)
- [LiveKit GitHub](https://github.com/livekit/agents)
- [Azure 支持](https://azure.microsoft.com/support/)

### 工具
- [LiveKit Cloud](https://cloud.livekit.io) - 免费注册
- [Azure Portal](https://portal.azure.com) - 管理资源
- [LiveKit Meet](https://meet.livekit.io) - 测试客户端

## 💡 最佳实践

### 开发工作流
1. 使用虚拟环境隔离依赖
2. 以开发模式安装插件 (`pip install -e .`)
3. 使用 `.env` 文件管理凭证
4. 启用调试日志进行问题排查
5. 运行单元测试验证修改

### 测试策略
1. 先运行 `test_local.py` 验证环境
2. 使用简单示例测试基本功能
3. 使用复杂示例测试高级功能
4. 在 Playground 中进行端到端测试
5. 监控日志和性能指标

### 代码管理
1. 不要提交 `.env` 文件到 Git
2. 使用 `.gitignore` 排除敏感文件
3. 定期运行测试确保代码质量
4. 记录重要的配置和决策

## ✅ 完成标志

当您完成以下所有项目时，说明本地测试环境已完全就绪：

- [x] 所有文档已阅读
- [x] 开发环境已设置
- [x] 所有依赖已安装
- [x] 环境变量已配置
- [x] 验证测试已通过
- [x] 示例运行成功
- [x] 能够修改代码并测试
- [x] 理解基本架构和工作流程

恭喜！您现在可以开始开发和测试 Azure Live Interpreter 插件了！🎉

## 下一步

- 🔨 开发自定义功能
- 🧪 编写更多测试
- 📦 准备部署到生产环境
- 📊 优化性能和成本

祝开发顺利！
