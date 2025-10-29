# 部署文件清单

## 📁 部署相关文件总览

所有必需的部署文件已创建完成，可以直接用于 LiveKit Cloud 部署。

### 核心配置文件 (5 个)

| 文件 | 用途 | 必需性 |
|------|------|--------|
| [agent.yaml](agent.yaml) | LiveKit Agent 配置 | 推荐 |
| [Dockerfile](Dockerfile) | Docker 镜像构建 | 必需（Docker 方法） |
| [requirements.txt](requirements.txt) | Python 依赖 | 必需 |
| [cloud-deploy.yaml](cloud-deploy.yaml) | LiveKit Cloud 配置 | 推荐 |
| [deploy.sh](deploy.sh) | 自动化部署脚本 | 推荐 |

### 文档文件 (3 个)

| 文件 | 内容 | 目标读者 |
|------|------|---------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | 完整部署指南 | DevOps |
| [PLAYGROUND_GUIDE.md](PLAYGROUND_GUIDE.md) | Playground 测试 | 测试人员 |
| [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) | 部署方案总结 | 所有人 |

## 🚀 快速开始

### 方法 1：LiveKit Cloud Dashboard

1. 登录 https://cloud.livekit.io/
2. 上传 [cloud-deploy.yaml](cloud-deploy.yaml)
3. 配置 Secrets
4. 点击部署

### 方法 2：使用自动化脚本

```bash
# 设置环境变量
export AZURE_SPEECH_KEY="your-key"
export AZURE_SPEECH_REGION="eastus"

# 一键构建和测试
./deploy.sh build
./deploy.sh test
```

### 方法 3：Docker 手动部署

```bash
# 使用 Dockerfile
docker build -t azure-realtime .
docker run -it --rm \
  -e AZURE_SPEECH_KEY="key" \
  -e AZURE_SPEECH_REGION="region" \
  azure-realtime
```

## 📋 文件详细说明

### agent.yaml

**用途：** LiveKit Agent 元数据和配置

**关键配置：**
```yaml
name: azure-realtime
entrypoint: examples/multi_language_meeting.py
runtime:
  python_version: "3.11"
dependencies:
  - livekit-agents>=0.8.0
  - azure-cognitiveservices-speech>=1.40.0
```

**何时使用：**
- 通过 LiveKit CLI 部署
- 需要标准化配置
- CI/CD 流程

### Dockerfile

**用途：** 构建包含插件和示例的 Docker 镜像

**关键步骤：**
1. Python 3.11 基础镜像
2. 安装系统依赖
3. 复制插件源码
4. 安装 Python 依赖
5. 设置入口点

**何时使用：**
- Docker 部署方法
- 自定义环境需求
- 本地测试

**构建命令：**
```bash
docker build -t azure-realtime:latest .
```

### requirements.txt

**用途：** Python 包依赖列表

**核心依赖：**
```
livekit-agents>=0.8.0
azure-cognitiveservices-speech>=1.40.0
aiohttp>=3.9.0
python-dotenv>=1.0.0
```

**何时使用：**
- 所有部署方法
- 本地开发
- CI/CD 环境

### cloud-deploy.yaml

**用途：** LiveKit Cloud 完整配置（Kubernetes 风格）

**包含内容：**
- Agent 规范
- 资源限制
- Auto-scaling 配置
- Secret 管理
- 健康检查
- 监控配置

**何时使用：**
- LiveKit Cloud Dashboard 部署
- 需要完整配置
- 生产环境

**关键部分：**
```yaml
apiVersion: agents.livekit.io/v1alpha1
kind: Agent
metadata:
  name: azure-realtime
spec:
  source:
    git:
      url: https://github.com/your-username/repo
  env:
    - name: AZURE_SPEECH_KEY
      valueFrom:
        secretKeyRef:
          name: azure-credentials
```

### deploy.sh

**用途：** 自动化部署脚本

**功能：**
- 构建 Docker 镜像
- 本地测试
- 推送到 registry
- 部署到 cloud

**使用方法：**
```bash
# 单步执行
./deploy.sh build    # 构建镜像
./deploy.sh test     # 本地测试
./deploy.sh push     # 推送镜像
./deploy.sh deploy   # 部署到 cloud

# 一键部署
./deploy.sh all      # 执行所有步骤
```

**环境变量：**
```bash
AZURE_SPEECH_KEY          # 必需
AZURE_SPEECH_REGION       # 必需
DOCKER_REGISTRY           # push 时需要
LIVEKIT_CLOUD_URL         # deploy 时需要
LIVEKIT_CLOUD_API_KEY     # deploy 时需要
LIVEKIT_CLOUD_API_SECRET  # deploy 时需要
```

## 📚 文档文件

### DEPLOYMENT.md

**完整部署指南，包含：**
- 3 种部署方法详解
- 步骤说明
- 配置选项
- 故障排查
- 监控设置
- 成本优化
- 生产清单

**适合：** 第一次部署，需要详细指导

### PLAYGROUND_GUIDE.md

**Playground 测试指南，包含：**
- 5 分钟快速开始
- 测试场景示例
- 监控和调试
- 性能基准
- 故障排查

**适合：** 测试验证，功能演示

### DEPLOYMENT_SUMMARY.md

**部署方案总结，包含：**
- 部署方法对比
- 配置要点
- 成本估算
- 常见场景
- 快速参考

**适合：** 快速查阅，方案选择

## 🎯 使用场景指南

### 场景 1：快速原型测试

**推荐文件：**
- PLAYGROUND_GUIDE.md（测试指南）
- cloud-deploy.yaml（Dashboard 上传）

**步骤：**
1. 阅读 PLAYGROUND_GUIDE.md
2. 在 Dashboard 上传 cloud-deploy.yaml
3. 配置 secrets
4. 在 playground 测试

### 场景 2：本地开发调试

**推荐文件：**
- Dockerfile（容器化）
- deploy.sh（自动化）
- requirements.txt（依赖）

**步骤：**
1. `./deploy.sh build`
2. `./deploy.sh test`
3. 调试和修改
4. 重复步骤 1-2

### 场景 3：生产环境部署

**推荐文件：**
- DEPLOYMENT.md（完整指南）
- cloud-deploy.yaml（配置）
- deploy.sh（自动化）

**步骤：**
1. 阅读 DEPLOYMENT.md
2. 配置 cloud-deploy.yaml
3. 使用 deploy.sh 部署
4. 配置监控和告警

## ✅ 部署前检查清单

### 文件准备

- [ ] 所有配置文件已下载
- [ ] Azure 凭据已准备
- [ ] LiveKit 账号已创建
- [ ] Docker 已安装（如需要）

### 配置检查

- [ ] AZURE_SPEECH_KEY 已设置
- [ ] AZURE_SPEECH_REGION 已设置
- [ ] Personal Voice 访问已批准
- [ ] 目标语言已确定

### 环境检查

- [ ] 网络连接正常
- [ ] Azure 区域可访问
- [ ] LiveKit Cloud 可访问
- [ ] Docker daemon 运行中（如需要）

## 🔄 更新和维护

### 更新配置

```bash
# 1. 修改配置文件
vim cloud-deploy.yaml

# 2. 重新部署
./deploy.sh deploy
# 或在 Dashboard 中更新
```

### 更新代码

```bash
# 1. Pull 最新代码
git pull origin main

# 2. 重新构建
./deploy.sh build

# 3. 测试
./deploy.sh test

# 4. 部署
./deploy.sh push
./deploy.sh deploy
```

### 回滚

```bash
# 在 LiveKit Cloud Dashboard
Agents → azure-realtime → Versions → 选择旧版本 → Deploy
```

## 📞 获取帮助

### 文档顺序

1. **DEPLOYMENT_SUMMARY.md** - 快速了解部署方案
2. **PLAYGROUND_GUIDE.md** - 快速测试
3. **DEPLOYMENT.md** - 完整部署

### 常见问题

**Q: 使用哪个文件进行部署？**
A: Dashboard 用户用 cloud-deploy.yaml，Docker 用户用 Dockerfile + deploy.sh

**Q: 如何修改配置？**
A: 修改对应的 YAML 文件或在 Dashboard 中直接修改

**Q: 如何查看日志？**
A: Dashboard → Agents → azure-realtime → Logs

**Q: 如何监控性能？**
A: Dashboard → Agents → azure-realtime → Metrics

## 🎉 部署完成后

1. ✅ 在 Playground 测试功能
2. 📊 查看监控指标
3. 📝 记录配置参数
4. 🔔 设置告警规则
5. 💰 监控成本使用

---

**文件版本：** 1.0.0  
**创建日期：** 2024-10-28  
**状态：** ✅ 完整
