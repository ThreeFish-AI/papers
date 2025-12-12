# GitHub Actions 工作流说明

## 概述

本项目使用 GitHub Actions 进行 CI/CD 自动化，包括测试、代码质量检查、安全扫描、Docker 构建和发布流程。

## 工作流文件

- **`workflows/ci.yml`**: 主要的 CI/CD 流水线配置
- **`workflows/auto-fix-ruff.yml`**: Ruff 代码质量自动修复工作流

## 工作流任务

### 1. 测试任务 (test)

- **触发条件**: 所有 PR 和 push
- **Python 版本**: 3.12, 3.13 (矩阵测试)
- **执行内容**:
  - 代码风格检查 (ruff)
  - 类型检查 (mypy)
  - 单元测试执行
  - 集成测试执行
  - 生成覆盖率报告
  - 上传到 Codecov

### 2. 安全扫描任务 (security)

- **触发条件**: 依赖测试任务
- **执行内容**:
  - safety: 依赖漏洞检查
  - bandit: 代码安全分析
  - 上传安全报告

### 3. Docker 构建任务 (docker)

- **触发条件**: 仅在 main/master 分支 push 时执行
- **执行内容**:
  - 多平台构建 (amd64, arm64)
  - 容器健康检查
  - 推送到 Docker Hub

### 4. 文档任务 (docs)

- **触发条件**: 依赖测试任务
- **执行内容**:
  - 构建文档 (如果配置了 mkdocs)
  - 部署到 GitHub Pages

### 5. 性能测试任务 (performance)

- **触发条件**: 仅在 PR 时执行
- **执行内容**:
  - 运行性能基准测试

### 6. 发布任务 (release)

- **触发条件**: 仅在 main/master 分支 push 时执行
- **执行内容**:
  - 构建 Python 包
  - 创建 GitHub Release
  - 生成 changelog

### 7. Ruff 自动修复任务 (auto-fix-ruff)

- **触发条件**: 所有分支的 push 事件
- **Python 版本**: 3.12
- **执行内容**:
  - 检查 Ruff 代码质量问题
  - 自动修复可修复的问题 (ruff check --fix)
  - 应用代码格式化 (ruff format)
  - 创建/更新包含修复的 PR
  - 发送通知 (Slack/邮件，可选)
- **特性**:
  - 智能分支管理 (创建带时间戳的修复分支)
  - PR 去重 (更新现有 PR 而非创建新的)
  - 并发控制 (取消重复运行)
  - 双语通知支持 (中文消息)

## 必需的 Secrets

在 GitHub 仓库设置中配置以下 secrets：

```
ANTHROPIC_API_KEY    # API 认证密钥
DOCKER_USERNAME      # Docker Hub 用户名
DOCKER_PASSWORD      # Docker Hub 密码/token
SLACK_WEBHOOK_URL    # Slack 通知 Webhook URL (可选)
EMAIL_USERNAME       # 邮件通知用户名 (可选)
EMAIL_PASSWORD       # 邮件通知密码 (可选)
EMAIL_FROM          # 邮件发送地址 (可选，默认为 github.actor)
```

## 环境变量

工作流使用以下环境变量：

- `PYTHON_VERSION`: Python 版本 (默认: 3.12)
- `ANTHROPIC_API_KEY`: 从 secrets 获取
- `PR_LABELS`: PR 标签 (默认: "auto-fix,ruff")
- `NOTIFICATION_ENABLED`: 是否启用通知 (默认: false)
- `EMAIL_NOTIFICATIONS`: 邮件通知接收列表 (可选)
- `SMTP_SERVER`: SMTP 服务器地址 (默认: smtp.gmail.com)
- `SMTP_PORT`: SMTP 端口 (默认: 587)
- 其他测试环境变量从 `.env.example` 复制

## 测试覆盖率

- 最低覆盖率要求: 80%
- 覆盖率报告生成位置: `htmlcov/`
- XML 报告: `coverage.xml`

## 工作流集成说明

`auto-fix-ruff.yml` 工作流与主要的 `ci.yml` 工作流协同工作：
- `auto-fix-ruff` 在所有分支 push 时主动修复代码质量问题
- `ci` 在 PR 和 main/master 分支时进行全面的检查和测试
- 两者结合确保代码质量的同时减少手动修复工作

## 故障排除

### 常见问题

1. **ANTHROPIC_API_KEY 错误**

   - 确保 secret 已正确配置
   - 检查密钥是否有效

2. **Docker 构建失败**

   - 检查 Dockerfile 语法
   - 确认 Docker Hub 凭据正确

3. **测试失败**
   - 查看测试日志
   - 检查测试环境配置

4. **PR 创建失败**
   - 检查 GITHUB_TOKEN 权限
   - 确认分支不存在命名冲突

5. **通知配置问题**
   - 验证 SLACK_WEBHOOK_URL 有效性
   - 检查 SMTP 配置和认证

6. **并发运行问题**
   - 查看并发组配置
   - 检查是否有取消的运行

### 调试技巧

- 使用 GitHub Actions 的调试功能
- 查看 workflow 运行日志
- 本地复现失败的测试命令
- 检查 auto-fix 工作流的 Step Summary 获取详细报告
