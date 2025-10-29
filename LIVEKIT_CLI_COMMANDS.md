# LiveKit Agents CLI 命令参考

## 概述

LiveKit Agents 使用 `cli.run_app()` 提供了一个命令行接口，用于运行和管理 agent workers。

## 可用命令

### 1. start - 生产模式启动

```bash
python examples/multi_language_meeting.py start
```

**用途**: 在生产模式下启动 worker

**特点**:
- 自动连接到 LiveKit 服务器
- 等待房间分配
- 处理多个并发会话
- 适合生产部署

**环境变量**:
- `LIVEKIT_URL` - LiveKit 服务器 URL
- `LIVEKIT_API_KEY` - API Key
- `LIVEKIT_API_SECRET` - API Secret

**示例**:
```bash
export LIVEKIT_URL=wss://your-project.livekit.cloud
export LIVEKIT_API_KEY=your_api_key
export LIVEKIT_API_SECRET=your_api_secret
python examples/multi_language_meeting.py start
```

### 2. dev - 开发模式启动

```bash
python examples/multi_language_meeting.py dev
```

**用途**: 在开发模式下启动 worker

**特点**:
- 启用详细日志
- 热重载（代码修改后自动重启）
- 适合本地开发和调试

**示例**:
```bash
python examples/multi_language_meeting.py dev
```

### 3. connect - 连接到特定房间

```bash
python examples/multi_language_meeting.py connect --room <room-name>
```

**用途**: 直接连接到指定的房间

**参数**:
- `--room` - 房间名称（必需）
- `--participant-identity` - 参与者身份（可选）

**特点**:
- 直接加入指定房间
- 不等待 LiveKit 分配
- 适合测试特定房间

**示例**:
```bash
# 连接到测试房间
python examples/multi_language_meeting.py connect --room test-room

# 指定参与者身份
python examples/multi_language_meeting.py connect \
  --room test-room \
  --participant-identity interpreter-bot
```

### 4. console - 控制台模式

```bash
python examples/multi_language_meeting.py console
```

**用途**: 在控制台中启动交互式对话

**特点**:
- 不需要 LiveKit 房间
- 直接在终端中交互
- 适合快速测试 agent 逻辑

**示例**:
```bash
python examples/multi_language_meeting.py console
```

### 5. download-files - 下载依赖文件

```bash
python examples/multi_language_meeting.py download-files
```

**用途**: 下载插件所需的依赖文件

**特点**:
- 下载模型文件
- 下载配置文件
- 通常在首次运行前执行

## Docker 中使用

### Dockerfile CMD

在 Docker 容器中，使用 `start` 命令以生产模式运行：

```dockerfile
CMD ["python", "examples/multi_language_meeting.py", "start"]
```

### 覆盖 CMD

可以在运行容器时覆盖默认命令：

```bash
# 使用 dev 模式
docker run your-image python examples/multi_language_meeting.py dev

# 连接到特定房间
docker run your-image python examples/multi_language_meeting.py connect --room test-room

# 控制台模式
docker run -it your-image python examples/multi_language_meeting.py console
```

## LiveKit Cloud 部署

### agent.yaml 配置

在 `agent.yaml` 中指定启动命令：

```yaml
apiVersion: v1
kind: Agent
metadata:
  name: azure-live-interpreter
spec:
  # 入口点脚本
  entrypoint: examples/multi_language_meeting.py

  # 启动命令（默认为 start）
  command: start

  # 或者指定完整命令
  # command: ["python", "examples/multi_language_meeting.py", "start"]
```

### 使用 lk CLI

```bash
# 创建 agent（使用默认 start 命令）
lk agent create

# 查看 agent 日志
lk agent logs

# 查看 agent 状态
lk agent list
```

## 常见使用场景

### 场景 1: 本地开发测试

```bash
# 1. 开发模式启动
python examples/multi_language_meeting.py dev

# 2. 在另一个终端创建测试房间
lk room create test-room

# 3. 使用 LiveKit Meet 加入房间
# 访问 https://meet.livekit.io/
```

### 场景 2: 连接到现有房间测试

```bash
# 1. 创建房间
lk room create my-test-room

# 2. Agent 连接到房间
python examples/multi_language_meeting.py connect --room my-test-room

# 3. 用户加入房间测试
```

### 场景 3: 生产部署

```bash
# 1. 设置环境变量
export LIVEKIT_URL=wss://production.livekit.cloud
export LIVEKIT_API_KEY=prod_api_key
export LIVEKIT_API_SECRET=prod_api_secret

# 2. 生产模式启动
python examples/multi_language_meeting.py start

# 或使用 Docker
docker run -d \
  -e LIVEKIT_URL=wss://production.livekit.cloud \
  -e LIVEKIT_API_KEY=prod_api_key \
  -e LIVEKIT_API_SECRET=prod_api_secret \
  your-image
```

### 场景 4: 快速功能测试

```bash
# 使用控制台模式快速测试
python examples/multi_language_meeting.py console
```

## 命令行选项

### 全局选项

所有命令都支持以下选项：

```bash
--help              # 显示帮助信息
--log-level LEVEL   # 设置日志级别 (debug, info, warning, error)
--log-format FORMAT # 设置日志格式 (json, pretty)
```

**示例**:
```bash
# 启用调试日志
python examples/multi_language_meeting.py start --log-level debug

# JSON 格式日志
python examples/multi_language_meeting.py start --log-format json
```

### start 命令选项

```bash
--num-workers N     # Worker 数量（默认: 1）
--worker-type TYPE  # Worker 类型（默认: room）
```

**示例**:
```bash
# 启动 3 个 worker
python examples/multi_language_meeting.py start --num-workers 3
```

### connect 命令选项

```bash
--room ROOM                    # 房间名称（必需）
--participant-identity ID      # 参与者身份
--participant-name NAME        # 参与者显示名称
--participant-metadata META    # 参与者元数据
```

## 环境变量

### 必需的环境变量

```bash
# LiveKit 连接
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Azure Speech Service
AZURE_SPEECH_KEY=your_subscription_key
AZURE_SPEECH_REGION=eastus
```

### 可选的环境变量

```bash
# 日志配置
LIVEKIT_LOG_LEVEL=info          # debug, info, warning, error
LOG_LEVEL=INFO                  # Python logging level

# Personal Voice
AZURE_SPEAKER_PROFILE_ID=your_profile_id

# Worker 配置
LIVEKIT_WORKER_TYPE=room        # room, participant
LIVEKIT_NUM_WORKERS=1           # Worker 数量
```

## 故障排查

### 问题 1: "No module named 'livekit'"

**解决方案**:
```bash
pip install livekit-agents
```

### 问题 2: "Missing required environment variables"

**解决方案**:
```bash
# 检查环境变量
echo $LIVEKIT_URL
echo $LIVEKIT_API_KEY
echo $LIVEKIT_API_SECRET

# 设置环境变量
export LIVEKIT_URL=wss://your-project.livekit.cloud
export LIVEKIT_API_KEY=your_api_key
export LIVEKIT_API_SECRET=your_api_secret
```

### 问题 3: "Connection failed"

**检查**:
1. LIVEKIT_URL 格式是否正确（wss://...）
2. API Key 和 Secret 是否有效
3. 网络连接是否正常

**解决方案**:
```bash
# 测试连接
lk room list \
  --url $LIVEKIT_URL \
  --api-key $LIVEKIT_API_KEY \
  --api-secret $LIVEKIT_API_SECRET
```

### 问题 4: Agent 启动但不连接到房间

**原因**: 缺少命令参数

**解决方案**:
```bash
# 错误
python examples/multi_language_meeting.py

# 正确
python examples/multi_language_meeting.py start
```

## 最佳实践

### 1. 开发环境

```bash
# 使用 dev 模式进行开发
python examples/multi_language_meeting.py dev

# 或使用 connect 直接测试特定房间
python examples/multi_language_meeting.py connect --room dev-test
```

### 2. 生产环境

```bash
# 使用 start 命令
python examples/multi_language_meeting.py start

# 配置多个 worker
python examples/multi_language_meeting.py start --num-workers 3

# 使用环境变量文件
source .env.production
python examples/multi_language_meeting.py start
```

### 3. CI/CD

```bash
# 在 CI/CD 中使用环境变量
docker run \
  -e LIVEKIT_URL=$LIVEKIT_URL \
  -e LIVEKIT_API_KEY=$LIVEKIT_API_KEY \
  -e LIVEKIT_API_SECRET=$LIVEKIT_API_SECRET \
  -e AZURE_SPEECH_KEY=$AZURE_SPEECH_KEY \
  -e AZURE_SPEECH_REGION=$AZURE_SPEECH_REGION \
  your-image
```

## 相关文档

- [LiveKit Agents 文档](https://docs.livekit.io/agents/)
- [DEPLOYMENT.md](DEPLOYMENT.md) - 部署指南
- [LOCAL_TESTING.md](LOCAL_TESTING.md) - 本地测试指南
- [DOCKER_FIX.md](DOCKER_FIX.md) - Docker 修复说明

---

**最后更新**: 2025-10-29
