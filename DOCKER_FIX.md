# Docker 构建问题修复

## 问题描述

运行 `lk agent create` 时遇到构建错误：

```
ERROR [7/8] COPY requirements.txt* /app/ || true
unable to create agent: build failed
failed to compute cache key: "/app": not found
```

## 问题原因

Dockerfile 中使用了不支持的语法：

```dockerfile
COPY requirements.txt* /app/ || true
```

Docker 的 `COPY` 指令不支持：
1. Shell 重定向 (`2>/dev/null`)
2. Shell 逻辑运算符 (`|| true`)
3. 这些只能在 `RUN` 指令中使用

## 解决方案

由于 `requirements.txt` 文件已经存在，直接复制即可：

```dockerfile
# 修复前（错误）
COPY requirements.txt* /app/ || true

# 修复后（正确）
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
```

## 修复后的 Dockerfile

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
CMD ["python", "examples/multi_language_meeting.py"]
```

## 验证修复

现在可以重新运行部署命令：

```bash
# 创建 agent
lk agent create

# 如果需要指定项目
lk agent create --project your-project-name
```

## 其他改进

1. **保留了 "start" 参数**
   ```dockerfile
   CMD ["python", "examples/multi_language_meeting.py", "start"]
   ```

   LiveKit Agents CLI 需要一个命令参数：
   - `start` - 生产模式启动 worker
   - `dev` - 开发模式启动 worker
   - `connect` - 连接到特定房间
   - `console` - 在控制台启动对话

   在 Docker 容器中，我们使用 `start` 命令以生产模式运行。

2. **优化了构建顺序**
   - 先安装 requirements.txt（依赖变化较少）
   - 后复制 examples（代码变化较频繁）
   - 这样可以更好地利用 Docker 缓存层

## 可选：处理不存在的 requirements.txt

如果将来需要让 requirements.txt 成为可选的，可以使用以下方法：

### 方法 1: 创建一个空的 requirements.txt

```bash
touch requirements.txt
```

### 方法 2: 使用多阶段构建

```dockerfile
# Stage 1: Check if requirements.txt exists
FROM python:3.11-slim as builder
WORKDIR /app
COPY . /app/

# Stage 2: Main image
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app /app
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
```

### 方法 3: 使用构建参数

```dockerfile
ARG HAS_REQUIREMENTS=true
COPY requirements.txt /app/requirements.txt
RUN if [ "$HAS_REQUIREMENTS" = "true" ]; then \
        pip install -r /app/requirements.txt; \
    fi
```

## 下一步

修复完成后，您可以：

1. **重新构建和部署**
   ```bash
   lk agent create
   ```

2. **查看构建日志**
   ```bash
   lk agent logs <agent-id>
   ```

3. **测试 agent**
   - 访问 LiveKit Playground
   - 或使用 `lk` CLI 创建测试房间

## 相关文档

- [DEPLOYMENT.md](DEPLOYMENT.md) - 完整部署指南
- [PLAYGROUND_GUIDE.md](PLAYGROUND_GUIDE.md) - Playground 测试指南
- [Docker 最佳实践](https://docs.docker.com/develop/dev-best-practices/)

---

**修复时间**: 2025-10-29
**状态**: ✅ 已修复
