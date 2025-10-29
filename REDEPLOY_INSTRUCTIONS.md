# 重新部署说明

## 修复内容

已修复 LiveKit Agents API 兼容性问题：

### 问题
```
TypeError: RoomInputOptions.__init__() got an unexpected keyword argument 'auto_subscribe'
```

### 修复
移除了不兼容的 `RoomInputOptions` 和 `RoomOutputOptions` 参数，使用新版 API。

### 修改的文件
- ✅ examples/multi_language_meeting.py
- ✅ examples/simple_interpreter.py
- ✅ examples/custom_voice_interpreter.py

## 重新部署步骤

### 方法 1: 使用 lk CLI（推荐）

```bash
# 在项目根目录
cd ~/repos/yingeli/lk-plugin-live-interpreter

# 重新创建 agent（会自动构建新镜像）
lk agent create

# 或者更新现有 agent
lk agent update azure-live-interpreter
```

### 方法 2: 手动推送更新

```bash
# 1. 提交更改到 git（如果使用 git）
git add examples/
git commit -m "Fix: Update to LiveKit Agents 1.2.16 API"
git push

# 2. 触发重新部署
lk agent deploy azure-live-interpreter
```

## 验证部署

### 1. 查看日志

```bash
lk agent logs --follow
```

### 2. 预期看到的日志

✅ **成功的日志**:
```json
{"message": "Starting Multi-Language Interpreter in room: ...", "level": "INFO"}
{"message": "Target languages: fr, es, de, zh-Hans, ja, ko, ar, ru", "level": "INFO"}
{"message": "Multi-language interpreter ready", "level": "INFO"}
```

❌ **不应该看到的错误**:
```json
{"message": "TypeError: RoomInputOptions.__init__() got an unexpected keyword argument", "level": "ERROR"}
```

### 3. 测试功能

#### 在 Playground 中测试

1. 访问 https://cloud.livekit.io/projects/live-interpreter/playground
2. 创建或加入房间
3. 启用麦克风
4. 开始说话
5. 验证翻译功能正常

#### 使用 lk CLI 测试

```bash
# 创建测试房间
lk room create test-translation

# 生成加入令牌
lk token create \
  --api-key $LIVEKIT_API_KEY \
  --api-secret $LIVEKIT_API_SECRET \
  --join --room test-translation \
  --identity user1 \
  --valid-for 1h

# Agent 应该自动加入房间
```

## 部署状态检查

### 检查 Agent 状态

```bash
# 列出所有 agent
lk agent list

# 查看特定 agent 详情
lk agent get azure-live-interpreter

# 查看环境变量
lk agent env list --agent azure-live-interpreter
```

### 预期状态

```
Agent: azure-live-interpreter
Status: Running ✅
Version: Latest
Environment Variables:
  ✓ AZURE_SPEECH_KEY (Secret)
  ✓ AZURE_SPEECH_REGION
```

## 如果部署失败

### 常见问题

#### 问题 1: 构建失败

**检查**:
```bash
# 查看构建日志
lk agent logs --build
```

**解决方案**:
- 确保 Dockerfile 正确
- 确保所有文件已提交
- 检查 requirements.txt

#### 问题 2: Agent 启动失败

**检查**:
```bash
# 查看启动日志
lk agent logs --tail 100
```

**解决方案**:
- 检查环境变量是否设置
- 验证 Azure 凭证
- 检查代码语法错误

#### 问题 3: 仍然看到 API 错误

**原因**: 可能使用了缓存的旧镜像

**解决方案**:
```bash
# 强制重新构建
lk agent create --force-rebuild

# 或删除旧 agent 重新创建
lk agent delete azure-live-interpreter
lk agent create
```

## 本地测试（可选）

在部署到云端前，可以先本地测试：

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 设置环境变量
export LIVEKIT_URL=wss://live-interpreter-hh2ynsdz.livekit.cloud
export LIVEKIT_API_KEY=your_key
export LIVEKIT_API_SECRET=your_secret
export AZURE_SPEECH_KEY=your_azure_key
export AZURE_SPEECH_REGION=eastus

# 3. 运行 agent
python examples/multi_language_meeting.py dev

# 4. 在另一个终端创建测试房间
lk room create test-room
```

## 快速命令参考

```bash
# 重新部署
lk agent create

# 查看日志
lk agent logs --follow

# 查看状态
lk agent list

# 测试房间
lk room create test-room

# 停止 agent
lk agent stop azure-live-interpreter

# 启动 agent
lk agent start azure-live-interpreter

# 删除 agent
lk agent delete azure-live-interpreter
```

## 成功标志

当您看到以下内容时，说明部署成功：

1. ✅ Agent 状态为 "Running"
2. ✅ 日志中显示 "Multi-language interpreter ready"
3. ✅ 可以在 Playground 中加入房间
4. ✅ Agent 自动加入房间
5. ✅ 翻译功能正常工作

## 下一步

部署成功后：

1. **测试所有语言**
   - 测试 8 种目标语言
   - 验证翻译质量
   - 检查延迟

2. **监控性能**
   - 查看 Azure 使用量
   - 监控 LiveKit 指标
   - 检查错误率

3. **优化配置**
   - 调整采样率
   - 配置 Personal Voice
   - 优化资源分配

## 相关文档

- [API_COMPATIBILITY_FIX.md](API_COMPATIBILITY_FIX.md) - API 修复详情
- [DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md) - 故障排查
- [PLAYGROUND_GUIDE.md](PLAYGROUND_GUIDE.md) - Playground 使用指南

---

**创建时间**: 2025-10-29

**状态**: 准备重新部署

**命令**: `lk agent create`
