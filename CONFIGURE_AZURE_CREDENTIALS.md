# 配置 Azure 凭证到 LiveKit Cloud

## 当前问题

Agent 已成功部署，但缺少 Azure Speech Service 凭证：

```
ValueError: Azure Speech subscription key is required.
Set AZURE_SPEECH_KEY environment variable or pass subscription_key parameter.
```

## 解决步骤

### 步骤 1: 获取 Azure 凭证

如果您还没有 Azure Speech Service 凭证：

1. 访问 [Azure Portal](https://portal.azure.com)
2. 搜索 "Speech Services"
3. 创建新的 Speech Service 资源（或使用现有的）
4. 进入资源页面
5. 在左侧菜单中点击 "Keys and Endpoint"
6. 复制以下信息：
   - **Key 1** 或 **Key 2**（任选其一）
   - **Location/Region**（例如：eastus, westus2）

### 步骤 2: 在 LiveKit Cloud 中配置环境变量

#### 方法 A: 使用 Dashboard（推荐）

1. **访问 LiveKit Cloud**
   - 打开 https://cloud.livekit.io
   - 登录您的账号

2. **进入项目**
   - 选择项目 `live-interpreter`

3. **导航到 Agents**
   - 在左侧菜单中点击 "Agents"
   - 找到您的 agent：`azure-live-interpreter` 或 `CA_e8eWYXDteoGC`

4. **配置环境变量**
   - 点击 agent 名称进入详情页
   - 找到 "Environment Variables" 或 "Settings" 标签
   - 点击 "Add Variable" 或 "Edit"

5. **添加以下变量**

   **必需变量**:
   ```
   名称: AZURE_SPEECH_KEY
   值: <your_azure_subscription_key>
   类型: Secret (勾选 "Secret" 选项以隐藏值)
   ```

   ```
   名称: AZURE_SPEECH_REGION
   值: eastus (或您的 Azure 资源所在区域)
   类型: Plain text
   ```

   **可选变量**（如果使用 Personal Voice）:
   ```
   名称: AZURE_SPEAKER_PROFILE_ID
   值: <your_speaker_profile_id>
   类型: Secret
   ```

6. **保存配置**
   - 点击 "Save" 或 "Update"

7. **重新部署 Agent**
   - 环境变量更新后，agent 会自动重启
   - 或手动触发重新部署

#### 方法 B: 使用 lk CLI

如果您更喜欢使用命令行：

```bash
# 设置环境变量（使用 secret 方式）
lk agent env set \
  --agent azure-live-interpreter \
  --secret AZURE_SPEECH_KEY=your_subscription_key

lk agent env set \
  --agent azure-live-interpreter \
  AZURE_SPEECH_REGION=eastus

# 可选：Personal Voice
lk agent env set \
  --agent azure-live-interpreter \
  --secret AZURE_SPEAKER_PROFILE_ID=your_profile_id

# 查看环境变量
lk agent env list --agent azure-live-interpreter

# 重新部署
lk agent deploy --agent azure-live-interpreter
```

### 步骤 3: 验证配置

1. **查看 Agent 日志**
   ```bash
   lk agent logs --follow
   ```

2. **期望看到的日志**
   ```json
   {"message": "Starting Multi-Language Interpreter in room: ...", "level": "INFO"}
   {"message": "Target languages: fr, es, de, zh-Hans, ja, ko, ar, ru", "level": "INFO"}
   {"message": "Multi-language interpreter ready", "level": "INFO"}
   ```

3. **如果仍有错误**
   - 检查 Key 是否正确（没有多余空格）
   - 检查 Region 是否匹配 Azure 资源
   - 确认 Azure 订阅是否有效

### 步骤 4: 测试 Agent

1. **访问 LiveKit Playground**
   - 在 LiveKit Cloud Dashboard 中点击 "Playground"
   - 或访问 https://cloud.livekit.io/projects/live-interpreter/playground

2. **创建或加入房间**
   - 输入房间名称
   - 点击 "Join Room"

3. **启用麦克风**
   - 允许浏览器访问麦克风
   - 开始说话

4. **验证翻译**
   - Agent 应该自动加入房间
   - 您应该听到翻译后的音频
   - 查看日志确认翻译正在进行

## 常见问题

### Q1: 环境变量设置后 Agent 仍报错

**检查**:
- 环境变量名称是否正确（区分大小写）
- 值中是否有多余的空格或引号
- Agent 是否已重启

**解决方案**:
```bash
# 删除旧的环境变量
lk agent env delete --agent azure-live-interpreter AZURE_SPEECH_KEY

# 重新设置
lk agent env set --agent azure-live-interpreter --secret AZURE_SPEECH_KEY=new_value

# 强制重新部署
lk agent deploy --agent azure-live-interpreter --force
```

### Q2: 如何验证 Azure 凭证是否有效？

**本地测试**:
```bash
# 使用 Python 验证
python -c "
import os
from azure.cognitiveservices.speech import SpeechConfig

# 设置凭证
os.environ['AZURE_SPEECH_KEY'] = 'your_key'
os.environ['AZURE_SPEECH_REGION'] = 'eastus'

# 测试
config = SpeechConfig(
    subscription=os.environ['AZURE_SPEECH_KEY'],
    region=os.environ['AZURE_SPEECH_REGION']
)
print('✓ Azure credentials are valid!')
"
```

### Q3: 如何查看已设置的环境变量？

**使用 Dashboard**:
- Agents > Your Agent > Environment Variables

**使用 CLI**:
```bash
lk agent env list --agent azure-live-interpreter
```

注意：Secret 类型的变量值会被隐藏。

### Q4: 可以在 agent.yaml 中直接设置值吗？

**不推荐**，因为：
1. 凭证会暴露在代码仓库中
2. 不安全
3. 难以管理不同环境的配置

**正确做法**:
- agent.yaml 中只声明变量名
- 在 LiveKit Cloud Dashboard 中设置实际值
- 或使用 lk CLI 设置 secret

### Q5: 如何为不同环境配置不同的凭证？

**使用 LiveKit Cloud 的环境功能**:
```bash
# 开发环境
lk agent env set --agent azure-live-interpreter --env dev \
  --secret AZURE_SPEECH_KEY=dev_key

# 生产环境
lk agent env set --agent azure-live-interpreter --env prod \
  --secret AZURE_SPEECH_KEY=prod_key
```

## 安全最佳实践

### 1. 使用 Secret 类型

始终将敏感信息标记为 Secret：
```bash
lk agent env set --secret AZURE_SPEECH_KEY=value
```

### 2. 定期轮换凭证

- 定期更新 Azure Speech Service Keys
- 在 Azure Portal 中重新生成 Key
- 更新 LiveKit Cloud 中的环境变量

### 3. 使用最小权限原则

- 只授予必要的 Azure 权限
- 使用专用的 Speech Service 资源
- 不要共享生产环境凭证

### 4. 监控使用情况

- 在 Azure Portal 中监控 API 使用量
- 设置使用配额和警报
- 检查异常活动

## 完整配置示例

### LiveKit Cloud Dashboard 配置

```
Agent: azure-live-interpreter
Environment Variables:
  ✓ AZURE_SPEECH_KEY (Secret)     = ********************************
  ✓ AZURE_SPEECH_REGION           = eastus
  ○ AZURE_SPEAKER_PROFILE_ID      = (Optional)
  ○ LOG_LEVEL                     = INFO
```

### 验证命令

```bash
# 1. 检查环境变量
lk agent env list --agent azure-live-interpreter

# 2. 查看 agent 状态
lk agent get azure-live-interpreter

# 3. 查看日志
lk agent logs --follow

# 4. 测试连接
lk room create test-room
# Agent 应该自动加入
```

## 下一步

配置完成后：

1. ✅ 验证 Agent 日志中没有错误
2. ✅ 在 Playground 中测试翻译功能
3. ✅ 检查所有目标语言是否正常工作
4. ✅ 监控性能和成本

## 相关文档

- [DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md) - 部署故障排查
- [PLAYGROUND_GUIDE.md](PLAYGROUND_GUIDE.md) - Playground 使用指南
- [Azure Speech Service 文档](https://learn.microsoft.com/azure/ai-services/speech-service/)

---

**最后更新**: 2025-10-29

**当前状态**: 等待配置 Azure 凭证
