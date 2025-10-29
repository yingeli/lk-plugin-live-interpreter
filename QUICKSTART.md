# 快速开始指南 (Quick Start Guide)

5 分钟快速上手 Azure Live Interpreter 插件本地测试。

## 前提条件

- Python 3.9+
- Azure Speech Service 订阅 (获取 Key 和 Region)
- LiveKit 账号 (免费注册: https://cloud.livekit.io)

## 快速设置

### 1. 自动化设置（推荐）

```bash
# 克隆或进入项目目录
cd lk-plugin-live-interpreter

# 运行自动化设置脚本
./setup_local_dev.sh
```

这个脚本会自动：
- ✓ 创建虚拟环境
- ✓ 安装所有依赖
- ✓ 以开发模式安装插件
- ✓ 创建 .env 模板

### 2. 配置凭证

编辑 `.env` 文件：

```bash
vim .env
```

填入您的凭证：

```bash
# Azure Speech Service
AZURE_SPEECH_KEY=your_actual_key_here
AZURE_SPEECH_REGION=eastus

# LiveKit (从 https://cloud.livekit.io 获取)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```

### 3. 验证安装

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行测试脚本
python examples/test_local.py
```

如果看到 "所有测试通过！✨"，说明配置成功！

### 4. 运行示例

```bash
# 简单双语翻译 (英语 → 法语 + 西班牙语)
python examples/simple_interpreter.py

# 多语言会议 (8 种语言同声传译)
python examples/multi_language_meeting.py
```

## 手动设置（可选）

如果您更喜欢手动设置：

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install livekit-agents livekit-cli

# 3. 安装插件（开发模式）
cd livekit-plugins/livekit-plugins-azure
pip install -e .
cd ../..

# 4. 配置环境变量（同上）
vim .env

# 5. 测试
python examples/test_local.py
```

## 测试方法

### 方法 1: LiveKit Playground（最简单）

1. 访问 https://cloud.livekit.io
2. 进入您的项目
3. 点击 "Playground"
4. 创建测试房间
5. 启用麦克风，开始说话

### 方法 2: LiveKit CLI

```bash
# 安装 CLI
pip install livekit-cli

# 创建房间令牌
lk token create \
  --api-key $LIVEKIT_API_KEY \
  --api-secret $LIVEKIT_API_SECRET \
  --join --room test-room \
  --identity user1 \
  --valid-for 24h
```

### 方法 3: Web 客户端

使用 LiveKit 的示例应用: https://meet.livekit.io/

## 基本使用示例

创建您自己的 Agent：

```python
# my_interpreter.py
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.plugins import azure

async def entrypoint(ctx: JobContext):
    # 创建翻译模型
    model = azure.realtime.LiveInterpreterModel(
        target_languages=["fr", "es", "de"],  # 法语、西班牙语、德语
        use_personal_voice=True,              # 使用个人语音
        sample_rate=16000,                    # 采样率
    )

    # 创建 Agent 会话
    session = AgentSession(llm=model)
    await session.start(room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

运行：

```bash
python my_interpreter.py
```

## 支持的语言

90+ 种语言，包括：

| 语言 | 代码 | 语言 | 代码 |
|------|------|------|------|
| 法语 | fr | 西班牙语 | es |
| 德语 | de | 中文(简体) | zh-Hans |
| 日语 | ja | 韩语 | ko |
| 阿拉伯语 | ar | 俄语 | ru |

完整列表: [models.py](livekit-plugins/livekit-plugins-azure/livekit/plugins/azure/models.py)

## 常见问题

### Q: "No module named build" 错误

**A**: 不需要构建包进行本地测试。直接使用 `pip install -e .` 以开发模式安装。

### Q: Azure 认证失败

**A**: 检查：
1. Key 和 Region 是否正确
2. Azure 订阅是否有效
3. 是否有 Speech Service 配额

### Q: LiveKit 连接失败

**A**: 检查：
1. URL 格式是否正确 (wss://...)
2. API Key 和 Secret 是否有效
3. 网络连接是否正常

### Q: 如何启用调试日志？

**A**: 设置环境变量：
```bash
export LIVEKIT_LOG_LEVEL=debug
python examples/simple_interpreter.py
```

## 下一步

- 📖 [完整本地测试指南](LOCAL_TESTING.md) - 详细的测试方法和调试技巧
- 🚀 [部署指南](DEPLOYMENT.md) - 部署到 LiveKit Cloud
- 🎮 [Playground 指南](PLAYGROUND_GUIDE.md) - 在线测试
- 🏗️ [架构文档](ARCHITECTURE.md) - 技术实现细节

## 获取帮助

- 查看 [LOCAL_TESTING.md](LOCAL_TESTING.md) 的故障排查部分
- 访问 LiveKit Discord: https://livekit.io/discord
- Azure 支持: https://azure.microsoft.com/support/

祝使用愉快！🎉
