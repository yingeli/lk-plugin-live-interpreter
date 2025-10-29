# LiveKit Playground 测试指南

快速指南：如何在 LiveKit Cloud Playground 中测试 Azure Live Interpreter Agent

## 🚀 快速开始（5 分钟）

### 步骤 1：部署 Agent 到 LiveKit Cloud

#### 方法 A：通过 Dashboard（推荐）

1. **登录 LiveKit Cloud**
   - 访问：https://cloud.livekit.io/
   - 使用你的账号登录

2. **创建 Agent**
   - 点击左侧菜单 "Agents"
   - 点击 "New Agent"
   - 填写信息：
     ```
     Name: azure-realtime
     Description: Real-time speech translation
     ```

3. **配置 Source**

   **选项 1：From Git（推荐）**
   ```yaml
   Source Type: Git Repository
   Repository URL: https://github.com/your-username/lk-plugin-realtime
   Branch: main
   Entry Point: examples/multi_language_meeting.py
   ```

   **选项 2：From Docker**
   ```yaml
   Source Type: Docker Image
   Image: your-registry/azure-realtime:latest
   Pull Policy: Always
   ```

4. **设置 Secrets**
   - 点击 "Secrets" 标签
   - 添加以下 secrets：
     ```
     AZURE_SPEECH_KEY: your-subscription-key-here
     AZURE_SPEECH_REGION: eastus
     AZURE_SPEAKER_PROFILE_ID: (可选)
     ```

5. **配置 Resources**
   ```
   Memory: 512 MB
   CPU: 0.5 cores
   Replicas: 1
   ```

6. **部署**
   - 点击 "Deploy" 按钮
   - 等待状态变为 "Running"（约 1-2 分钟）

#### 方法 B：通过 CLI

```bash
# 1. 设置环境变量
export LIVEKIT_CLOUD_URL="wss://your-project.livekit.cloud"
export LIVEKIT_API_KEY="your-api-key"
export LIVEKIT_API_SECRET="your-api-secret"

# 2. 使用配置文件部署
livekit-cli deploy create -f cloud-deploy.yaml
```

### 步骤 2：在 Playground 中测试

#### 使用 LiveKit Playground Web

1. **访问 Playground**
   - 打开：https://meet.livekit.io/
   - 或在 LiveKit Cloud Dashboard 点击 "Playground"

2. **配置连接**
   ```
   Server URL: wss://your-project.livekit.cloud
   Token: (点击 "Generate Token" 自动生成)
   Room Name: translator-test-room
   Identity: user-1
   ```

3. **加入房间**
   - 点击 "Connect"
   - 允许麦克风权限
   - 等待 agent 加入（会看到 "azure-translator" 参与者）

4. **开始测试**
   - 对着麦克风说话（任意语言）
   - Agent 会自动检测语言
   - 实时翻译成配置的目标语言
   - 翻译以文字和音频形式显示

#### 使用 LiveKit CLI

```bash
# 加入房间进行测试
livekit-cli join-room \
  --url wss://your-project.livekit.cloud \
  --api-key your-api-key \
  --api-secret your-api-secret \
  --room translator-test-room \
  --identity test-user
```

### 步骤 3：验证翻译功能

#### 测试场景 1：英语到法语/西班牙语

1. 用英语说："Hello, how are you today?"
2. 预期输出：
   ```
   [en-US] Hello, how are you today?
   [fr] Bonjour, comment allez-vous aujourd'hui?
   [es] Hola, ¿cómo estás hoy?
   ```

#### 测试场景 2：中文到多语言

1. 用中文说："你好，今天天气怎么样？"
2. 预期输出：
   ```
   [zh-CN] 你好，今天天气怎么样？
   [en] Hello, how's the weather today?
   [fr] Bonjour, quel temps fait-il aujourd'hui?
   [ja] こんにちは、今日の天気はどうですか？
   ```

#### 测试场景 3：语言切换

1. 先用英语说话
2. 切换到西班牙语
3. 再切换到日语
4. Agent 应该自动检测每次的语言变化

## 📊 监控和调试

### 查看 Agent 日志

**在 Dashboard 中：**
1. 进入 "Agents" → "azure-realtime"
2. 点击 "Logs" 标签
3. 实时查看日志：
   ```
   INFO: Starting Multi-Language Interpreter in room: translator-test-room
   INFO: Target languages: fr, es, de, zh-Hans, ja, ko, ar, ru
   INFO: Recognized [en-US]: Hello world
   INFO:   → [fr]: Bonjour le monde
   INFO:   → [es]: Hola mundo
   INFO: Audio synthesized: 15360 bytes
   ```

### 常见日志消息

**正常运行：**
```
INFO: Live Interpreter session started
INFO: Recognized [language]: text
INFO: Audio synthesized: X bytes
```

**错误情况：**
```
ERROR: Azure Speech Service error: Invalid subscription key
ERROR: Failed to connect to Azure Speech Service
WARNING: No speech could be recognized
```

### 性能指标

在 Dashboard → Agents → Metrics 查看：
- **Active Sessions**: 当前活跃翻译会话数
- **Translations/min**: 每分钟翻译次数
- **Latency**: 平均翻译延迟
- **Error Rate**: 错误率
- **Resource Usage**: CPU 和内存使用率

## 🔧 故障排查

### 问题 1：Agent 无法启动

**症状：**
- Dashboard 显示 "Failed" 状态
- 日志显示认证错误

**解决方案：**
```bash
# 检查 secrets 配置
1. 进入 Dashboard → Agents → azure-realtime → Secrets
2. 验证 AZURE_SPEECH_KEY 正确
3. 验证 AZURE_SPEECH_REGION 正确（如 "eastus"）
4. 重新部署
```

### 问题 2：Agent 加入房间但无输出

**症状：**
- Agent 显示在参与者列表
- 但没有翻译输出

**检查清单：**
- [ ] 麦克风权限已授予
- [ ] 麦克风工作正常
- [ ] 音量足够大
- [ ] Personal Voice 访问已批准

**调试步骤：**
```bash
# 1. 检查 agent 日志
# 寻找："push_audio" 相关消息

# 2. 测试麦克风
# 在 playground 中查看音频波形

# 3. 降低音频要求
# 临时禁用 personal voice 进行测试
```

### 问题 3：高延迟

**症状：**
- 翻译延迟 > 3 秒

**优化措施：**

1. **减少目标语言**
   ```python
   # 从 8 种语言减少到 2-3 种
   target_languages=["fr", "es"]  # 而不是 8 种
   ```

2. **选择更近的 Azure 区域**
   ```bash
   AZURE_SPEECH_REGION=westus2  # 选择最近的区域
   ```

3. **增加 Agent 资源**
   ```yaml
   resources:
     memory: 1Gi
     cpu: "1"
   ```

### 问题 4：音频质量差

**解决方案：**

```python
# 使用更高音频质量
azure.realtime.LiveInterpreterModel(
    target_languages=["fr", "es"],
    sample_rate=24000,  # 从 16000 升级到 24000
    use_personal_voice=True,
)
```

## 🎮 高级测试场景

### 场景 1：多人会议

1. **设置**：
   - 3+ 用户同时加入房间
   - 每人使用不同语言

2. **测试**：
   - 用户 1 说英语
   - 用户 2 说中文
   - 用户 3 说西班牙语
   - Agent 应为每个人提供翻译

### 场景 2：长时间会话

1. **设置**：
   - 持续对话 30+ 分钟

2. **监控**：
   - 内存使用是否稳定
   - 延迟是否增加
   - 连接是否稳定

### 场景 3：快速语言切换

1. **测试**：
   - 快速在 3 种语言间切换
   - 每种语言说 1-2 句话

2. **预期**：
   - Agent 正确识别每次切换
   - 无明显延迟增加

## 📱 移动设备测试

### iOS Safari

1. 访问 https://meet.livekit.io/
2. 允许麦克风权限
3. 测试翻译功能

**已知问题：**
- iOS Safari 可能需要点击激活音频
- 后台时可能暂停

### Android Chrome

1. 访问 playground URL
2. 允许所有权限
3. 正常测试

## 🔐 安全测试

### 测试未授权访问

```bash
# 尝试不带 token 加入
# 应该被拒绝
livekit-cli join-room --url wss://your-project.livekit.cloud --room test
```

### 测试 Rate Limiting

```bash
# 快速发送大量请求
# 验证 rate limiting 是否生效
```

## 📈 性能基准

### 预期性能指标

| 指标 | 目标值 | 可接受范围 |
|------|--------|-----------|
| 首字延迟 (TTFT) | < 2 秒 | < 3 秒 |
| 翻译延迟 | < 500ms | < 1 秒 |
| 音频质量 | 优秀 | 良好+ |
| 错误率 | < 1% | < 5% |
| 可用性 | > 99% | > 95% |

### 负载测试

```bash
# 使用多个客户端同时连接
for i in {1..10}; do
  livekit-cli join-room \
    --url wss://your-project.livekit.cloud \
    --room load-test \
    --identity user-$i &
done
```

## 💰 成本估算

### Azure 成本（示例）

**配置：** 8 种目标语言，personal voice，24kHz

| 使用量 | 每月成本（估算） |
|--------|-----------------|
| 10 小时 | ~$50 |
| 100 小时 | ~$500 |
| 1000 小时 | ~$5000 |

**成本优化：**
- 减少到 2 种语言：成本减少 60%
- 使用标准语音：成本减少 30%
- 使用 16kHz：成本减少 20%

### LiveKit 成本

- 按参与者分钟计费
- Agent 算作 1 个参与者
- 查看具体定价：https://livekit.io/pricing

## 🎯 下一步

完成 playground 测试后：

1. **生产部署**
   - 参见 [DEPLOYMENT.md](DEPLOYMENT.md)
   - 配置监控和告警

2. **集成到应用**
   - 使用 LiveKit SDK
   - 自定义 UI

3. **优化配置**
   - 根据测试结果调整参数
   - 实施成本优化措施

## 📚 相关资源

- [完整部署指南](DEPLOYMENT.md)
- [快速开始](QUICKSTART.md)
- [架构文档](ARCHITECTURE.md)
- [LiveKit 文档](https://docs.livekit.io/)
- [Azure 语音服务文档](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/)

---

**测试清单**

- [ ] Agent 成功部署
- [ ] Agent 出现在 playground 参与者列表
- [ ] 麦克风工作正常
- [ ] 能够听到翻译音频
- [ ] 能够看到翻译文本
- [ ] 多语言检测正常
- [ ] 延迟在可接受范围
- [ ] 音频质量良好
- [ ] 日志无错误
- [ ] 监控指标正常

**祝测试顺利！** 🎉
