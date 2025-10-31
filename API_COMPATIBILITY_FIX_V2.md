# LiveKit Agents 1.2.16 API 完全迁移指南

## 问题总结

LiveKit Agents 1.2.16 引入了重大 API 变更：

1. ❌ `AgentSession.start()` 不再接受 `llm` 参数
2. ❌ `RoomInputOptions` 和 `RoomOutputOptions` 已移除
3. ✅ 需要创建 `Agent` 对象并传递给 `session.start()`

## 完整的 API 变更

### 错误 1: TypeError: AgentSession.start() got an unexpected keyword argument 'llm'

**旧版本 API**:
```python
session = AgentSession()

await session.start(
    llm=azure.realtime.LiveInterpreterModel(...),  # ❌ 不再支持
    room=ctx.room,
)
```

**新版本 API**:
```python
from livekit.agents.voice import Agent, AgentSession

# 1. 创建 Agent 对象
agent = Agent(
    instructions="Your agent instructions",
    llm=azure.realtime.LiveInterpreterModel(...),  # ✅ 传递给 Agent
)

# 2. 创建 session
session = AgentSession()

# 3. 启动 session
await session.start(
    agent=agent,  # ✅ 传递 Agent 对象
    room=ctx.room,
)
```

## 完整迁移示例

### 示例 1: multi_language_meeting.py

#### 修改前 ❌

```python
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.plugins import azure

async def entrypoint(ctx: JobContext):
    session = AgentSession()

    await session.start(
        llm=azure.realtime.LiveInterpreterModel(
            target_languages=["fr", "es", "de"],
        ),
        room=ctx.room,
        room_input_options=RoomInputOptions(auto_subscribe=True),
        room_output_options=RoomOutputOptions(transcription_enabled=True),
    )
```

#### 修改后 ✅

```python
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession  # 添加 Agent
from livekit.plugins import azure

async def entrypoint(ctx: JobContext):
    # 1. 创建 Agent 对象
    agent = Agent(
        instructions="You are a multi-language interpreter. Translate speech to multiple languages in real-time.",
        llm=azure.realtime.LiveInterpreterModel(
            target_languages=["fr", "es", "de"],
            use_personal_voice=True,
            sample_rate=16000,
        ),
    )

    # 2. 创建 session
    session = AgentSession()

    # 3. 启动 session
    await session.start(
        agent=agent,
        room=ctx.room,
    )
```

### 示例 2: simple_interpreter.py

#### 修改前 ❌

```python
session = AgentSession()

await session.start(
    llm=azure.realtime.LiveInterpreterModel(
        target_languages=["fr", "es"],
    ),
    room=ctx.room,
)
```

#### 修改后 ✅

```python
agent = Agent(
    instructions="You are a live interpreter. Translate speech to French and Spanish in real-time.",
    llm=azure.realtime.LiveInterpreterModel(
        target_languages=["fr", "es"],
        use_personal_voice=True,
        sample_rate=16000,
    ),
)

session = AgentSession()

await session.start(
    agent=agent,
    room=ctx.room,
)
```

## Agent 构造函数参数

`Agent` 类接受以下参数：

```python
Agent(
    instructions: str,                    # 必需：Agent 的指令
    llm: llm.LLM | llm.RealtimeModel,    # 可选：LLM 模型
    chat_ctx: llm.ChatContext,            # 可选：聊天上下文
    tools: list[llm.FunctionTool],        # 可选：工具列表
    turn_detection: TurnDetectionMode,    # 可选：轮次检测模式
    stt: stt.STT,                         # 可选：语音转文本
    vad: vad.VAD,                         # 可选：语音活动检测
    tts: tts.TTS,                         # 可选：文本转语音
    allow_interruptions: bool,            # 可选：允许打断
    # ... 更多参数
)
```

### 关键参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `instructions` | str | ✅ 是 | Agent 的行为指令 |
| `llm` | LLM/RealtimeModel | ❌ 否 | 语言模型（我们的 LiveInterpreterModel） |
| `chat_ctx` | ChatContext | ❌ 否 | 对话上下文 |
| `tools` | list | ❌ 否 | 可调用的工具 |

## 迁移检查清单

### 步骤 1: 更新导入

```python
# 添加 Agent 导入
from livekit.agents.voice import Agent, AgentSession

# 移除不需要的导入（如果有）
# from livekit.agents.voice.room_io import RoomInputOptions, RoomOutputOptions
```

### 步骤 2: 创建 Agent 对象

```python
agent = Agent(
    instructions="Your agent instructions here",
    llm=your_llm_model,
)
```

### 步骤 3: 更新 session.start() 调用

```python
# 修改前
await session.start(llm=model, room=ctx.room)

# 修改后
await session.start(agent=agent, room=ctx.room)
```

### 步骤 4: 移除旧的选项参数

```python
# 移除这些参数
# room_input_options=...
# room_output_options=...
```

## 所有修改的文件

1. ✅ `examples/multi_language_meeting.py`
   - 添加 `Agent` 导入
   - 创建 `Agent` 对象
   - 更新 `session.start()` 调用

2. ✅ `examples/simple_interpreter.py`
   - 添加 `Agent` 导入
   - 创建 `Agent` 对象
   - 更新 `session.start()` 调用

3. ✅ `examples/custom_voice_interpreter.py`
   - 添加 `Agent` 导入
   - 创建 `Agent` 对象
   - 更新 `session.start()` 调用

## 验证修复

### 本地测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行示例
python examples/multi_language_meeting.py dev
```

### 部署测试

```bash
# 重新部署
lk agent create

# 查看日志
lk agent logs --follow
```

### 预期日志

✅ **成功**:
```json
{"message": "Starting Multi-Language Interpreter in room: ...", "level": "INFO"}
{"message": "Target languages: fr, es, de, zh-Hans, ja, ko, ar, ru", "level": "INFO"}
{"message": "Multi-language interpreter ready", "level": "INFO"}
```

❌ **失败**（不应该再看到）:
```json
{"message": "TypeError: AgentSession.start() got an unexpected keyword argument 'llm'", "level": "ERROR"}
```

## 常见问题

### Q1: 为什么需要 instructions 参数？

**A**: `Agent` 类需要 `instructions` 来定义 agent 的行为。即使对于翻译任务，也需要提供基本指令。

### Q2: instructions 应该写什么？

**A**: 简要描述 agent 的职责：
```python
# 对于翻译
"You are a multi-language interpreter. Translate speech to multiple languages in real-time."

# 对于自定义语音
"You are a custom voice interpreter. Translate speech using the specified personal voice profile."
```

### Q3: 可以不提供 llm 参数吗？

**A**: 可以，但对于我们的用例，需要提供 `LiveInterpreterModel`。

### Q4: 旧的 room_input_options 功能去哪了？

**A**: 这些选项现在是默认行为，或者在 Agent 层配置。

### Q5: 如何配置音频选项？

**A**: 在 `LiveInterpreterModel` 初始化时配置：
```python
llm=azure.realtime.LiveInterpreterModel(
    target_languages=["fr", "es"],
    sample_rate=16000,              # 音频采样率
    enable_word_level_timestamps=True,  # 详细时间戳
    profanity_option="masked",      # 脏话处理
)
```

## 版本兼容性矩阵

| LiveKit Agents | AgentSession.start() | Agent 对象 | 推荐做法 |
|----------------|---------------------|-----------|----------|
| < 1.0.0 | llm 参数 | 不需要 | 使用旧 API |
| 1.0.0 - 1.2.15 | llm 参数 | 不需要 | 使用旧 API |
| >= 1.2.16 | agent 参数 | **必需** | 使用新 API |

## 迁移脚本

如果您有多个文件需要迁移，可以使用以下模式：

```bash
# 查找所有使用旧 API 的文件
grep -r "session.start.*llm=" examples/

# 对每个文件进行迁移
# 1. 添加 Agent 导入
# 2. 创建 Agent 对象
# 3. 更新 session.start() 调用
```

## 相关文档

- [LiveKit Agents 1.2.16 Release Notes](https://github.com/livekit/agents/releases)
- [DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md)
- [REDEPLOY_INSTRUCTIONS.md](REDEPLOY_INSTRUCTIONS.md)

## 总结

### 修复前的错误

1. ❌ `TypeError: RoomInputOptions.__init__() got an unexpected keyword argument 'auto_subscribe'`
2. ❌ `TypeError: AgentSession.start() got an unexpected keyword argument 'llm'`

### 修复后的状态

1. ✅ 移除了 `RoomInputOptions` 和 `RoomOutputOptions`
2. ✅ 创建 `Agent` 对象
3. ✅ 使用 `agent` 参数调用 `session.start()`
4. ✅ 所有示例文件已更新

---

**修复日期**: 2025-10-29

**影响文件**: 3 个示例文件

**状态**: ✅ 完全修复

**下一步**: 运行 `lk agent create` 重新部署
