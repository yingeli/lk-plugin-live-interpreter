# 部署总结：LiveKit Cloud 部署完整方案

## 📦 已创建的部署文件

### 核心配置文件

1. **[agent.yaml](agent.yaml)** - LiveKit Agent 配置
   - Agent 元数据
   - 依赖项定义
   - 环境变量配置
   - 资源分配
   - 自动扩展设置

2. **[Dockerfile](Dockerfile)** - Docker 镜像配置
   - Python 3.11 基础镜像
   - 插件安装
   - 示例代码打包
   - 入口点配置

3. **[requirements.txt](requirements.txt)** - Python 依赖
   - 核心依赖列表
   - 版本约束
   - 可选依赖

4. **[cloud-deploy.yaml](cloud-deploy.yaml)** - LiveKit Cloud 专用配置
   - 完整的 Kubernetes 风格配置
   - Secret 管理
   - Auto-scaling 配置
   - 监控设置

5. **[deploy.sh](deploy.sh)** - 自动化部署脚本
   - 构建 Docker 镜像
   - 本地测试
   - 推送到 registry
   - 部署到 cloud

### 文档文件

1. **[DEPLOYMENT.md](DEPLOYMENT.md)** - 完整部署指南
   - 3 种部署方法
   - 详细步骤说明
   - 故障排查
   - 成本优化
   - 生产清单

2. **[PLAYGROUND_GUIDE.md](PLAYGROUND_GUIDE.md)** - Playground 测试指南
   - 5 分钟快速开始
   - 测试场景
   - 监控和调试
   - 性能基准
   - 成本估算

## 🚀 三种部署方法

### 方法 1：LiveKit Cloud Dashboard（最简单）

```
1. 登录 LiveKit Cloud
2. 创建新 Agent
3. 配置 Git 源或 Docker 镜像
4. 设置环境变量
5. 点击部署
6. 在 Playground 测试
```

**优点：**
- 图形界面，最易用
- 无需本地工具
- 自动管理

**适用于：** 快速原型，非技术用户

### 方法 2：Docker 部署（最灵活）

```bash
# 构建
docker build -t azure-realtime .

# 测试
docker run -it --rm \
  -e AZURE_SPEECH_KEY="key" \
  -e AZURE_SPEECH_REGION="region" \
  azure-realtime

# 部署
docker push your-registry/azure-realtime
# 在 LiveKit Cloud 配置 Docker 镜像
```

**优点：**
- 完全控制
- 易于调试
- 可本地测试

**适用于：** 开发测试，自定义需求

### 方法 3：LiveKit CLI（最自动化）

```bash
# 一键部署
./deploy.sh all

# 或分步骤
./deploy.sh build
./deploy.sh test
./deploy.sh push
./deploy.sh deploy
```

**优点：**
- 自动化程度高
- 可脚本化
- CI/CD 友好

**适用于：** DevOps，生产环境

## 📋 部署步骤速查

### 前置准备

```bash
# 1. Azure 凭据
export AZURE_SPEECH_KEY="your-key"
export AZURE_SPEECH_REGION="eastus"

# 2. LiveKit 凭据（Cloud 部署需要）
export LIVEKIT_CLOUD_URL="wss://your-project.livekit.cloud"
export LIVEKIT_CLOUD_API_KEY="your-key"
export LIVEKIT_CLOUD_API_SECRET="your-secret"

# 3. Docker Registry（可选）
export DOCKER_REGISTRY="docker.io/username"
```

### 快速部署流程

```bash
# 1. 克隆代码
git clone https://github.com/your/repo
cd lk-plugin-realtime

# 2. 构建 Docker 镜像
./deploy.sh build

# 3. 本地测试
./deploy.sh test

# 4. 推送镜像（可选）
./deploy.sh push

# 5. 部署到 Cloud（通过 Dashboard 或 CLI）
# 见 DEPLOYMENT.md 详细说明
```

### 在 Playground 测试

```bash
# 1. 访问 Playground
https://meet.livekit.io/

# 2. 配置连接
Server URL: wss://your-project.livekit.cloud
Room Name: test-room

# 3. 加入并测试
# Agent 会自动加入
# 开始说话即可看到翻译
```

## 🔧 配置要点

### 必需配置

```yaml
# Secrets（在 LiveKit Cloud Dashboard 配置）
AZURE_SPEECH_KEY: "your-subscription-key"
AZURE_SPEECH_REGION: "eastus"

# Resources（基本配置）
memory: 512Mi
cpu: 500m
replicas: 1
```

### 可选配置

```yaml
# 个人语音
AZURE_SPEAKER_PROFILE_ID: "profile-id"

# 目标语言（在代码中配置）
target_languages: ["fr", "es", "de"]

# 音频质量
sample_rate: 24000  # 或 16000

# 日志级别
LOG_LEVEL: INFO
```

## 📊 部署验证清单

### 部署前

- [ ] Azure Speech Service 已创建
- [ ] Personal Voice 访问已批准
- [ ] 环境变量已配置
- [ ] Docker 已安装（如使用 Docker 方法）
- [ ] LiveKit Cloud 账号已创建

### 部署后

- [ ] Agent 状态显示 "Running"
- [ ] 日志无错误信息
- [ ] Agent 能加入测试房间
- [ ] 翻译功能正常
- [ ] 音频输出正常
- [ ] 延迟在可接受范围
- [ ] 监控指标正常

### 生产前

- [ ] 负载测试完成
- [ ] 安全审计通过
- [ ] 成本预算确认
- [ ] 监控告警配置
- [ ] 备份计划就绪
- [ ] 文档已更新

## 🎯 常见部署场景

### 场景 1：快速原型（开发环境）

```yaml
配置：
  - 方法：Dashboard 部署
  - Resources: 256Mi / 0.25 CPU
  - Replicas: 1
  - Languages: 2-3 种
  - 成本：最低
```

### 场景 2：小型生产（< 100 用户）

```yaml
配置：
  - 方法：Docker 部署
  - Resources: 512Mi / 0.5 CPU
  - Replicas: 1-2
  - Auto-scaling: 启用
  - Languages: 3-5 种
  - 成本：中等
```

### 场景 3：企业生产（1000+ 用户）

```yaml
配置：
  - 方法：CLI + CI/CD
  - Resources: 1Gi / 1 CPU
  - Replicas: 3-10
  - Auto-scaling: 启用
  - Languages: 按需
  - 监控：完整
  - 成本：按使用量
```

## 💰 成本估算

### Azure 成本

| 配置 | 100 小时/月 | 1000 小时/月 |
|------|-------------|--------------|
| 2 语言 + 标准语音 | ~$50 | ~$500 |
| 5 语言 + 标准语音 | ~$150 | ~$1500 |
| 8 语言 + Personal Voice | ~$300 | ~$3000 |

### LiveKit 成本

- 免费层：1000 分钟/月
- 生产环境：查看 https://livekit.io/pricing

### 优化建议

1. **减少语言数量** - 只配置真正需要的语言
2. **使用标准语音** - Personal Voice 成本更高
3. **降低采样率** - 16kHz vs 24kHz
4. **Auto-scaling** - 空闲时自动缩容

## 🔍 监控和维护

### 关键指标

```yaml
监控指标：
  - agent_status: Running
  - active_sessions: < 最大副本数
  - translation_latency: < 1s
  - error_rate: < 1%
  - cpu_usage: < 80%
  - memory_usage: < 80%
```

### 日志查看

```bash
# LiveKit Cloud Dashboard
Agents → azure-realtime → Logs

# 关键日志
INFO: Starting Multi-Language Interpreter
INFO: Target languages: fr, es, de
INFO: Recognized [en-US]: Hello
INFO: Audio synthesized: X bytes
```

### 告警配置

```yaml
告警规则：
  - Error rate > 5%
  - Latency > 3s
  - CPU > 90%
  - Memory > 90%
  - Agent 重启次数 > 3
```

## 🆘 故障排查快速参考

### Agent 启动失败
→ 检查 Azure 凭据
→ 查看部署日志
→ 验证 resources 配置

### 无翻译输出
→ 检查麦克风权限
→ 验证 Personal Voice 访问
→ 查看 agent 日志

### 高延迟
→ 减少目标语言
→ 选择更近的 Azure 区域
→ 增加 agent resources

### 成本过高
→ 减少语言数量
→ 禁用 Personal Voice
→ 降低音频质量
→ 优化 auto-scaling

## 📚 相关文档

- [DEPLOYMENT.md](DEPLOYMENT.md) - 详细部署指南
- [PLAYGROUND_GUIDE.md](PLAYGROUND_GUIDE.md) - Playground 测试
- [QUICKSTART.md](QUICKSTART.md) - 5 分钟快速开始
- [ARCHITECTURE.md](ARCHITECTURE.md) - 技术架构

## ✅ 下一步行动

1. **立即测试：** 使用 Dashboard 方法快速部署
2. **完整部署：** 参考 DEPLOYMENT.md 进行生产部署
3. **优化配置：** 根据实际使用调整参数
4. **设置监控：** 配置告警和日志
5. **成本优化：** 实施成本控制措施

---

**状态：** ✅ 部署方案完整  
**更新：** 2024-10-28  
**版本：** 0.1.0
