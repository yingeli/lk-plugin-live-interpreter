# 部署故障排查指南

本文档记录了在部署 Azure Live Interpreter Agent 到 LiveKit Cloud 时遇到的问题和解决方案。

## 问题 1: Docker 构建失败

### 错误信息

```
ERROR [7/8] COPY requirements.txt* /app/ || true
unable to create agent: build failed
failed to compute cache key: "/app": not found
```

### 原因

Dockerfile 中使用了不支持的语法：
```dockerfile
COPY requirements.txt* /app/ || true
```

Docker 的 `COPY` 指令不支持 shell 操作符（`||`、`2>/dev/null` 等）。

### 解决方案

修改 Dockerfile，直接复制文件：
```dockerfile
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
```

### 状态
✅ **已修复** - 参见 [DOCKER_FIX.md](DOCKER_FIX.md)

---

## 问题 2: Agent 不连接到房间

### 错误信息

```
Usage: multi_language_meeting.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  connect         Connect to a specific room
  console         Start a new conversation inside the console
  dev             Start the worker in development mode
  download-files  Download plugin dependency files
  start           Start the worker in production mode.
```

### 原因

LiveKit Agents CLI 需要一个命令参数（`start`、`dev`、`connect` 等），但 Dockerfile 的 CMD 中缺少这个参数。

### 解决方案

修改 Dockerfile，添加 `start` 命令：
```dockerfile
CMD ["python", "examples/multi_language_meeting.py", "start"]
```

### 状态
✅ **已修复** - 参见 [LIVEKIT_CLI_COMMANDS.md](LIVEKIT_CLI_COMMANDS.md)

---

## 完整的修复后的 Dockerfile

```dockerfile
# LiveKit Azure Live Interpreter Agent Docker Image

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy plugin source code
COPY livekit-plugins/livekit-plugins-azure /app/livekit-plugins-azure

# Install the plugin
RUN pip install --no-cache-dir /app/livekit-plugins-azure

# Copy requirements.txt
COPY requirements.txt /app/requirements.txt

# Install additional dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy example agents
COPY examples /app/examples

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Expose port for agent (if needed)
EXPOSE 8080

# Default command - run the multi-language meeting agent
CMD ["python", "examples/multi_language_meeting.py", "start"]
```

---

## 验证部署

### 1. 重新构建和部署

```bash
# 在项目根目录
lk agent create
```

### 2. 查看 Agent 日志

```bash
# 查看最新日志
lk agent logs

# 持续查看日志
lk agent logs --follow

# 查看特定 agent
lk agent logs --agent <agent-id>
```

### 3. 检查 Agent 状态

```bash
# 列出所有 agent
lk agent list

# 查看特定 agent 详情
lk agent get <agent-id>
```

### 4. 测试 Agent

#### 方法 1: 使用 LiveKit Playground

1. 访问 https://cloud.livekit.io
2. 进入您的项目
3. 点击 "Playground"
4. 创建或加入测试房间
5. 启用麦克风并开始说话

#### 方法 2: 使用 LiveKit Meet

1. 访问 https://meet.livekit.io/
2. 输入您的项目 URL
3. 创建房间
4. Agent 应该自动加入

#### 方法 3: 使用 lk CLI

```bash
# 创建测试房间
lk room create test-room

# 生成加入令牌
lk token create \
  --api-key $LIVEKIT_API_KEY \
  --api-secret $LIVEKIT_API_SECRET \
  --join --room test-room \
  --identity user1 \
  --valid-for 24h
```

---

## 常见部署问题

### 问题: "No such file or directory: requirements.txt"

**原因**: requirements.txt 文件不存在

**解决方案**:
```bash
# 确保 requirements.txt 存在
ls -la requirements.txt

# 如果不存在，创建它
cat > requirements.txt << 'EOF'
livekit-agents>=1.2.0
azure-cognitiveservices-speech>=1.40.0
aiohttp>=3.9.0
python-dotenv>=1.0.0
EOF
```

### 问题: "Permission denied" 错误

**原因**: 文件权限问题

**解决方案**:
```bash
# 确保脚本可执行
chmod +x examples/multi_language_meeting.py

# 检查文件权限
ls -la examples/
```

### 问题: "Module not found" 错误

**原因**: 插件未正确安装

**解决方案**:
```dockerfile
# 确保 Dockerfile 中正确安装插件
RUN pip install --no-cache-dir /app/livekit-plugins-azure
```

### 问题: Agent 启动后立即退出

**原因**: 缺少环境变量或配置错误

**检查清单**:
- [ ] LIVEKIT_URL 已设置
- [ ] LIVEKIT_API_KEY 已设置
- [ ] LIVEKIT_API_SECRET 已设置
- [ ] AZURE_SPEECH_KEY 已设置
- [ ] AZURE_SPEECH_REGION 已设置

**解决方案**:
```bash
# 在 LiveKit Cloud 中设置环境变量
# Dashboard > Agents > Your Agent > Environment Variables

# 或在 agent.yaml 中配置
apiVersion: v1
kind: Agent
metadata:
  name: azure-live-interpreter
spec:
  env:
    - name: AZURE_SPEECH_KEY
      valueFrom:
        secretKeyRef:
          name: azure-credentials
          key: speech-key
    - name: AZURE_SPEECH_REGION
      value: eastus
```

### 问题: "Connection timeout" 错误

**原因**: 网络配置或防火墙问题

**解决方案**:
1. 检查 LiveKit URL 是否正确
2. 确保容器可以访问外部网络
3. 检查防火墙规则

### 问题: Azure API 认证失败

**原因**: Azure 凭证无效或过期

**解决方案**:
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
```

---

## 调试技巧

### 1. 启用详细日志

在 Dockerfile 中：
```dockerfile
ENV LOG_LEVEL=DEBUG
ENV LIVEKIT_LOG_LEVEL=debug
```

或在运行时：
```bash
docker run -e LOG_LEVEL=DEBUG -e LIVEKIT_LOG_LEVEL=debug your-image
```

### 2. 本地测试 Docker 镜像

```bash
# 构建镜像
docker build -t azure-live-interpreter .

# 本地运行测试
docker run -it \
  -e LIVEKIT_URL=$LIVEKIT_URL \
  -e LIVEKIT_API_KEY=$LIVEKIT_API_KEY \
  -e LIVEKIT_API_SECRET=$LIVEKIT_API_SECRET \
  -e AZURE_SPEECH_KEY=$AZURE_SPEECH_KEY \
  -e AZURE_SPEECH_REGION=$AZURE_SPEECH_REGION \
  azure-live-interpreter

# 使用 shell 进入容器调试
docker run -it --entrypoint /bin/bash azure-live-interpreter
```

### 3. 检查容器日志

```bash
# 查看容器日志
docker logs <container-id>

# 持续查看日志
docker logs -f <container-id>

# 查看最后 100 行
docker logs --tail 100 <container-id>
```

### 4. 验证插件安装

```bash
# 进入容器
docker run -it --entrypoint /bin/bash azure-live-interpreter

# 验证插件
python -c "from livekit.plugins import azure; print('Plugin OK')"

# 检查依赖
pip list | grep livekit
pip list | grep azure
```

---

## 部署检查清单

在部署前，确保完成以下检查：

### 代码和配置
- [ ] Dockerfile 语法正确
- [ ] requirements.txt 存在且正确
- [ ] 所有示例脚本可执行
- [ ] agent.yaml 配置正确

### 环境变量
- [ ] LIVEKIT_URL 已配置
- [ ] LIVEKIT_API_KEY 已配置
- [ ] LIVEKIT_API_SECRET 已配置
- [ ] AZURE_SPEECH_KEY 已配置
- [ ] AZURE_SPEECH_REGION 已配置

### 测试
- [ ] 本地测试通过
- [ ] Docker 镜像构建成功
- [ ] 本地 Docker 运行成功
- [ ] 插件导入正常

### 部署
- [ ] lk agent create 成功
- [ ] Agent 日志正常
- [ ] Agent 状态为 running
- [ ] 可以连接到测试房间

---

## 成功部署的标志

当您看到以下日志时，说明部署成功：

```
INFO Starting Multi-Language Interpreter in room: <room-name>
INFO Target languages: fr, es, de, zh-Hans, ja, ko, ar, ru
INFO Multi-language interpreter ready
```

---

## 获取帮助

如果问题仍未解决：

1. **查看文档**
   - [DEPLOYMENT.md](DEPLOYMENT.md) - 完整部署指南
   - [DOCKER_FIX.md](DOCKER_FIX.md) - Docker 修复说明
   - [LIVEKIT_CLI_COMMANDS.md](LIVEKIT_CLI_COMMANDS.md) - CLI 命令参考

2. **检查日志**
   ```bash
   lk agent logs --follow
   ```

3. **社区支持**
   - LiveKit Discord: https://livekit.io/discord
   - Azure 支持: https://azure.microsoft.com/support/
   - GitHub Issues: 提交问题报告

4. **本地调试**
   - 参考 [LOCAL_TESTING.md](LOCAL_TESTING.md)
   - 使用 `make test-quick` 验证环境

---

**最后更新**: 2025-10-29

**修复状态**: ✅ 所有已知问题已修复
