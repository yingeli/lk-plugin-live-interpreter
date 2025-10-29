# 本地测试指南 (Local Testing Guide)

本指南将帮助您在本地环境中测试 Azure Live Interpreter 插件和示例 Agent，无需部署到云端。

## 前提条件

### 1. Azure 资源
- Azure 订阅账号
- Azure Speech Service 资源
  - 获取 Subscription Key
  - 获取 Region (例如: eastus, westus2)
- （可选）Personal Voice 配置
  - Speaker Profile ID（如需使用个人语音克隆）

### 2. LiveKit 服务器
您可以选择以下任一方式：

#### 选项 A: 使用 LiveKit Cloud（推荐用于快速测试）
1. 访问 https://cloud.livekit.io
2. 创建免费项目
3. 获取：
   - `LIVEKIT_URL` (wss://your-project.livekit.cloud)
   - `LIVEKIT_API_KEY`
   - `LIVEKIT_API_SECRET`

#### 选项 B: 本地运行 LiveKit Server
```bash
# 使用 Docker 运行 LiveKit Server
docker run -d \
  --name livekit-server \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 7882:7882/udp \
  -v $PWD/livekit-config.yaml:/etc/livekit.yaml \
  livekit/livekit-server \
  --config /etc/livekit.yaml
```

### 3. Python 环境
- Python 3.9 或更高版本
- 虚拟环境（推荐）

## 快速开始

### 步骤 1: 创建虚拟环境

```bash
# 在项目根目录
cd /home/yingeli/repos/yingeli/lk-plugin-live-interpreter

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
# venv\Scripts\activate  # Windows
```

### 步骤 2: 安装插件（开发模式）

```bash
# 安装 LiveKit Agents 核心库
pip install livekit-agents

# 以可编辑模式安装插件（用于开发和测试）
cd livekit-plugins/livekit-plugins-azure
pip install -e .

# 返回项目根目录
cd ../..
```

### 步骤 3: 配置环境变量

创建 `.env` 文件：

```bash
# 在项目根目录创建 .env 文件
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
EOF
```

**重要**: 将上述占位符替换为您的实际凭证。

### 步骤 4: 运行测试示例

#### 测试 1: 简单双语翻译

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 运行简单示例
python examples/simple_interpreter.py
```

这个示例会启动一个 Agent，将英语翻译成法语和西班牙语。

#### 测试 2: 多语言会议翻译

```bash
python examples/multi_language_meeting.py
```

这个示例支持 8 种语言的同声传译。

#### 测试 3: 自定义语音翻译

```bash
# 需要先设置 AZURE_SPEAKER_PROFILE_ID 环境变量
export AZURE_SPEAKER_PROFILE_ID=your_speaker_profile_id

python examples/custom_voice_interpreter.py
```

## 测试方法

### 方法 1: 使用 LiveKit CLI（推荐）

安装 LiveKit CLI：

```bash
# 安装 lk CLI 工具
pip install livekit-cli

# 或使用 brew (Mac)
# brew install livekit
```

创建测试房间并连接：

```bash
# 创建房间令牌
lk token create \
  --api-key $LIVEKIT_API_KEY \
  --api-secret $LIVEKIT_API_SECRET \
  --join --room test-room \
  --identity user1 \
  --valid-for 24h

# 使用生成的令牌连接到房间
# 您可以使用 LiveKit 的 Web 示例应用进行测试
```

### 方法 2: 使用 LiveKit Playground

1. 访问 https://cloud.livekit.io
2. 进入您的项目
3. 点击 "Playground"
4. 创建或加入测试房间
5. 启用麦克风
6. 开始说话进行测试

### 方法 3: 使用自定义测试脚本

创建简单的测试客户端：

```python
# test_client.py
import asyncio
from livekit import rtc
import os

async def main():
    url = os.environ["LIVEKIT_URL"]
    token = "your_room_token_here"  # 使用 lk token create 生成

    room = rtc.Room()

    @room.on("track_subscribed")
    def on_track_subscribed(track: rtc.Track, *_):
        print(f"Subscribed to track: {track.sid}")
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            print("Receiving translated audio!")

    await room.connect(url, token)
    print(f"Connected to room: {room.name}")

    # 保持连接
    await asyncio.sleep(300)  # 5 分钟
    await room.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

运行测试客户端：

```bash
python test_client.py
```

## 调试技巧

### 1. 启用详细日志

在运行示例前设置日志级别：

```bash
export LIVEKIT_LOG_LEVEL=debug
python examples/simple_interpreter.py
```

### 2. 检查 Agent 状态

在示例代码中添加日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. 监控 Azure API 调用

检查 Azure Speech Service 使用情况：
1. 访问 Azure Portal
2. 进入 Speech Service 资源
3. 查看 "Metrics" 和 "Logs"

### 4. 测试音频流

验证音频输入/输出：

```python
# 在 realtime_model.py 中添加调试代码
async def _send_audio_task(self):
    async for frame in self._input_audio_stream:
        print(f"Sending audio frame: {len(frame.data)} bytes")
        # ... 现有代码
```

## 常见问题排查

### 问题 1: "No module named 'livekit'"

**解决方案**:
```bash
pip install livekit-agents
```

### 问题 2: "Azure Speech Service authentication failed"

**检查**:
- `AZURE_SPEECH_KEY` 是否正确
- `AZURE_SPEECH_REGION` 是否匹配资源区域
- Azure 订阅是否有效

**解决方案**:
```bash
# 测试 Azure 凭证
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

### 问题 3: "Cannot connect to LiveKit server"

**检查**:
- `LIVEKIT_URL` 格式是否正确 (应以 wss:// 开头)
- API Key 和 Secret 是否有效
- 网络连接是否正常

**解决方案**:
```bash
# 测试 LiveKit 连接
lk room list \
  --url $LIVEKIT_URL \
  --api-key $LIVEKIT_API_KEY \
  --api-secret $LIVEKIT_API_SECRET
```

### 问题 4: "Personal Voice not working"

**检查**:
- Speaker Profile ID 是否已创建
- 是否有权限使用 Personal Voice 功能
- 区域是否支持 Personal Voice

**解决方案**: 参考 Azure 文档创建 Speaker Profile

### 问题 5: 音频质量问题

**调整采样率**:
```python
model = azure.realtime.LiveInterpreterModel(
    target_languages=["fr", "es"],
    sample_rate=24000,  # 尝试更高的采样率
)
```

## 性能测试

### 测试延迟

创建延迟测试脚本：

```python
# test_latency.py
import time
import asyncio
from livekit.plugins import azure

async def test_latency():
    model = azure.realtime.LiveInterpreterModel(
        target_languages=["fr"],
    )

    session = model.session()

    start_time = time.time()

    # 发送测试音频
    # ... 实现音频发送逻辑

    # 等待翻译结果
    async for event in session:
        if event.type == "translation_received":
            latency = time.time() - start_time
            print(f"Translation latency: {latency:.2f}s")
            break

asyncio.run(test_latency())
```

### 测试并发

测试多个同时连接：

```bash
# 启动多个 Agent 实例
for i in {1..5}; do
    python examples/simple_interpreter.py &
done

# 等待所有实例完成
wait
```

## 单元测试

运行插件的单元测试：

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行测试
cd livekit-plugins/livekit-plugins-azure
pytest tests/

# 运行特定测试
pytest tests/test_models.py -v

# 查看测试覆盖率
pip install pytest-cov
pytest --cov=livekit.plugins.azure tests/
```

## 开发工作流

### 1. 修改代码

由于使用了 `-e` (editable) 模式安装，您可以直接修改源代码：

```bash
# 编辑插件代码
vim livekit-plugins/livekit-plugins-azure/livekit/plugins/azure/realtime/realtime_model.py

# 无需重新安装，直接测试
python examples/simple_interpreter.py
```

### 2. 添加日志

在关键位置添加日志以便调试：

```python
import logging
logger = logging.getLogger(__name__)

class LiveInterpreterSession:
    async def _send_audio_task(self):
        logger.debug("Starting audio send task")
        # ... 代码
```

### 3. 热重载

使用 `watchdog` 实现代码修改后自动重启：

```bash
pip install watchdog

# 创建监控脚本
cat > watch_and_run.py << 'EOF'
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.restart()

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"Detected change in {event.src_path}, restarting...")
            self.restart()

    def restart(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.process = subprocess.Popen(self.command)

if __name__ == "__main__":
    handler = RestartHandler(sys.argv[1:])
    observer = Observer()
    observer.schedule(handler, ".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
EOF

# 使用监控脚本
python watch_and_run.py python examples/simple_interpreter.py
```

## 集成测试场景

### 场景 1: 双人对话翻译

1. 启动 Agent
2. 两个用户加入房间（一个说英语，一个说法语）
3. 验证双向翻译是否正常工作

### 场景 2: 多人会议

1. 启动多语言会议 Agent
2. 多个用户加入，使用不同语言
3. 验证每个用户都能听到其他人的翻译

### 场景 3: 语言自动检测

1. 启动 Agent
2. 用户在对话中切换语言
3. 验证系统是否自动检测并正确翻译

## 下一步

完成本地测试后，您可以：

1. **优化配置**: 根据测试结果调整参数
2. **添加功能**: 实现自定义功能
3. **部署到生产**: 参考 [DEPLOYMENT.md](DEPLOYMENT.md) 部署到 LiveKit Cloud
4. **监控和分析**: 设置日志和监控系统

## 资源链接

- [LiveKit Agents 文档](https://docs.livekit.io/agents/)
- [Azure Speech Service 文档](https://learn.microsoft.com/azure/ai-services/speech-service/)
- [LiveKit Playground](https://cloud.livekit.io)
- [项目 GitHub](https://github.com/livekit/agents)

## 获取帮助

如果遇到问题：

1. 检查日志输出
2. 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 的故障排查部分
3. 访问 LiveKit Discord 社区
4. 提交 GitHub Issue

祝测试顺利！
