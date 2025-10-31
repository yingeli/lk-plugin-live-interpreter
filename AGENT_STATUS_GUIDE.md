# Agent 状态诊断指南

## 当前状态分析

根据 `lk agent status` 输出：

```
Status: Setting Up
Replicas: 0 / 1 / 1  (当前/就绪/期望)
CPU: 0m / 2000m
Memory: 0 / 4GB
```

### 状态说明

**"Setting Up"** 表示 Agent 正在初始化过程中，这包括：

1. 📦 拉取 Docker 镜像
2. 🚀 启动容器
3. 📥 安装依赖
4. ⚙️ 初始化应用
5. 🔌 连接到 LiveKit 服务器

### 正常时间线

| 阶段 | 预计时间 | 说明 |
|------|----------|------|
| Setting Up | 2-5 分钟 | 拉取镜像和启动容器 |
| Starting | 30-60 秒 | 应用初始化 |
| Running | - | 正常运行状态 |

## Agent 状态类型

### ✅ 正常状态

1. **Setting Up** (正在设置)
   - 首次部署或重启后的正常状态
   - 通常需要 2-5 分钟
   - 无需干预，耐心等待

2. **Starting** (正在启动)
   - 容器已启动，应用正在初始化
   - 通常需要 30-60 秒
   - 无需干预

3. **Running** (运行中)
   - Agent 正常运行
   - 可以接受任务
   - 目标状态 ✅

### ⚠️ 需要关注的状态

4. **Pending** (等待中)
   - 等待资源分配
   - 可能原因：
     - 配额不足
     - 资源不可用
     - 配置错误

5. **Failed** (失败)
   - 启动失败
   - 需要检查日志
   - 可能需要修复代码或配置

6. **CrashLoopBackOff** (崩溃循环)
   - 反复启动失败
   - 需要立即修复
   - 检查日志找出原因

## 诊断步骤

### 步骤 1: 检查当前状态

```bash
lk agent status
```

查看输出中的关键信息：
- **Status**: 当前状态
- **Replicas**: 副本数（当前/就绪/期望）
- **CPU/Memory**: 资源使用情况
- **Deployed At**: 部署时间

### 步骤 2: 等待初始化完成

如果状态是 "Setting Up"：

```bash
# 等待 2-5 分钟
# 每 30 秒检查一次状态
watch -n 30 lk agent status
```

### 步骤 3: 检查日志

当日志可用时（通常在 1-2 分钟后）：

```bash
# 查看实时日志
lk agent logs --follow

# 或查看最近的日志
lk agent logs
```

### 步骤 4: 查看错误信息

如果日志中有错误：

```bash
# 查看日志并过滤错误
lk agent logs | grep -i error

# 查看日志并过滤警告
lk agent logs | grep -i warning
```

## 常见问题和解决方案

### 问题 1: Setting Up 时间过长（超过 10 分钟）

**可能原因**:
- Docker 镜像太大
- 网络速度慢
- 依赖安装失败

**解决方案**:
```bash
# 1. 检查日志
lk agent logs

# 2. 如果卡住，重启 agent
lk agent restart

# 3. 如果仍然失败，重新部署
lk agent create
```

### 问题 2: 状态一直是 Pending

**可能原因**:
- 资源配额不足
- 配置错误
- 环境变量缺失

**解决方案**:

1. **检查环境变量**:
```bash
lk agent secrets
```

确保设置了：
- `AZURE_SPEECH_KEY`
- `AZURE_SPEECH_REGION`

2. **检查资源配置**:

查看 `agent.yaml` 中的资源设置：
```yaml
resources:
  memory: 512Mi  # 可能需要增加
  cpu: "0.5"     # 可能需要增加
```

3. **更新资源配置**:
```bash
# 编辑 agent.yaml，增加资源
# 然后重新部署
lk agent create
```

### 问题 3: 状态变为 Failed

**可能原因**:
- 代码错误
- 依赖缺失
- 环境变量错误

**解决方案**:

1. **查看详细日志**:
```bash
lk agent logs
```

2. **常见错误和修复**:

**错误**: `ModuleNotFoundError`
```bash
# 检查 requirements.txt
# 确保所有依赖都已列出
# 重新部署
lk agent create
```

**错误**: `ValueError: Azure Speech subscription key is required`
```bash
# 更新环境变量
lk agent update-secrets
# 输入 AZURE_SPEECH_KEY 和 AZURE_SPEECH_REGION
```

**错误**: `TypeError` 或 `AttributeError`
```bash
# 代码错误，需要修复代码
# 修复后重新部署
lk agent create
```

### 问题 4: Replicas 显示 0 / 0 / 1

**说明**: 没有副本在运行

**解决方案**:
```bash
# 1. 检查日志找出原因
lk agent logs

# 2. 重启 agent
lk agent restart

# 3. 如果仍然失败，删除并重新创建
lk agent delete
lk agent create
```

## 监控命令

### 实时监控状态

```bash
# 使用 watch 命令每 10 秒刷新一次
watch -n 10 lk agent status
```

### 实时监控日志

```bash
# 持续查看日志
lk agent logs --follow
```

### 检查历史版本

```bash
# 查看所有版本
lk agent versions

# 如果需要回滚
lk agent rollback --version <version-id>
```

## 当前情况的建议

根据您的 Agent 状态（Setting Up），建议：

### 1. 等待初始化完成（推荐）

```bash
# 等待 5 分钟
# 每 30 秒检查一次
watch -n 30 lk agent status
```

### 2. 监控日志

```bash
# 在另一个终端窗口
# 等待日志可用（通常 1-2 分钟）
while ! lk agent logs 2>&1 | grep -v "not yet available"; do
  echo "Waiting for logs..."
  sleep 10
done

# 日志可用后，持续监控
lk agent logs --follow
```

### 3. 预期结果

5-10 分钟后，应该看到：

```
Status: Running ✅
Replicas: 1 / 1 / 1
```

日志中应该显示：
```json
{"message": "registered worker", "level": "INFO"}
{"message": "Multi-language interpreter ready", "level": "INFO"}
```

## 快速检查脚本

创建一个脚本来自动检查状态：

```bash
#!/bin/bash
# check_agent.sh

echo "Checking agent status..."
lk agent status

echo ""
echo "Waiting for logs to be available..."
sleep 30

echo ""
echo "Checking logs..."
lk agent logs 2>&1 | head -20

echo ""
echo "Current time: $(date)"
echo "If status is still 'Setting Up', wait a few more minutes."
```

使用方法：
```bash
chmod +x check_agent.sh
./check_agent.sh
```

## 时间线参考

### 正常部署时间线

```
00:00 - lk agent create 开始
00:30 - Status: Setting Up (拉取镜像)
02:00 - Status: Setting Up (启动容器)
03:00 - Status: Starting (初始化应用)
04:00 - Status: Running ✅ (日志可用)
05:00 - Agent 完全就绪，可以接受任务
```

### 当前进度

```
09:45 - 部署开始
09:53 - 当前时间（8 分钟后）
预计: 09:50-09:55 - 应该变为 Running
```

## 下一步行动

### 如果现在是 Setting Up 状态

✅ **正常** - 继续等待 2-5 分钟

### 如果 10 分钟后仍是 Setting Up

⚠️ **需要检查** - 查看日志，可能需要重启

### 如果变为 Failed 状态

❌ **需要修复** - 查看日志，修复问题后重新部署

## 相关文档

- [DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md) - 完整故障排查
- [DEPLOYMENT_SUCCESS.md](DEPLOYMENT_SUCCESS.md) - 成功部署指南
- [CONFIGURE_AZURE_CREDENTIALS.md](CONFIGURE_AZURE_CREDENTIALS.md) - 环境变量配置

---

**创建时间**: 2025-10-29 09:53 UTC

**当前状态**: Setting Up (正常)

**建议**: 等待 5 分钟，然后检查状态
