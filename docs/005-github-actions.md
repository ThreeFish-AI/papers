# GitHub Actions 工作流说明

## 概述

本项目使用 GitHub Actions 进行 CI/CD 自动化，包括测试、代码质量检查、安全扫描、Docker 构建和发布流程。

## 工作流文件

- **`.github/workflows/ci.yml`**: 主要的 CI/CD 流水线配置
- **`.github/workflows/auto-fix-ruff.yml`**: Ruff 代码质量自动修复工作流

## 工作流说明

### CI/CD 流水线 (`.github/workflows/ci.yml`)

**触发条件**: PR 和 push 到 main/master/release 分支

**任务包括**:

- **测试**: Python 3.12/3.13，Ruff 检查，MyPy，单元/集成测试，覆盖率报告
- **安全扫描**: Safety (依赖漏洞) 和 Bandit (代码安全)
- **Docker**: 多平台构建，推送到 Docker Hub (仅 main/master)
- **性能测试**: 运行性能基准测试 (仅 PR)
- **发布**: 构建 Python 包，创建 GitHub Release (仅 main/master)

### 自动代码质量修复 (`.github/workflows/auto-fix-ruff.yml`)

**触发条件**: 所有分支的 push

**功能**:

- 自动修复 Ruff 发现的代码问题
- 格式化代码
- 创建/更新 PR 提交修复
- 支持通知配置 (Slack/邮件)

## 必需的 Secrets

在 GitHub 仓库设置中配置以下 secrets：

```
ANTHROPIC_API_KEY    # API 认证密钥
DOCKER_USERNAME      # Docker Hub 用户名
DOCKER_PASSWORD      # Docker Hub 访问令牌
SLACK_WEBHOOK_URL    # Slack 通知 Webhook URL (可选)
EMAIL_USERNAME       # 邮件通知用户名 (可选)
EMAIL_PASSWORD       # 邮件通知密码 (可选)
EMAIL_FROM          # 邮件发送地址 (可选，默认为 github.actor)
```

### Docker Hub 访问令牌配置

为了安全地推送 Docker 镜像，建议使用访问令牌而非密码：

1. **创建访问令牌**：

   - 登录 [Docker Hub](https://hub.docker.com/)
   - 进入 Account Settings → Security
   - 创建新令牌，命名为 `github-actions-ci`
   - 权限：Read, Write, Delete

2. **配置 GitHub Secrets**：
   - `DOCKER_USERNAME`: 您的 Docker Hub 用户名
   - `DOCKER_PASSWORD`: 创建的访问令牌（非密码）

## 邮件通知配置

Ruff 自动修复工作流支持邮件通知功能，当检测到问题并创建 PR 时会自动发送通知。

### 配置步骤

1. **启用通知功能**

   在 Repository Variables 中添加：

   ```
   Name: NOTIFICATION_ENABLED
   Value: true
   ```

2. **配置接收邮箱**

   在 Repository Variables 中添加：

   ```
   Name: EMAIL_NOTIFICATIONS
   Value: user@example.com,admin@example.com  # 多个地址用逗号分隔
   ```

3. **配置 SMTP 服务（可选）**

   默认使用 Gmail，如需自定义：

   ```
   SMTP_SERVER: smtp.gmail.com  # SMTP 服务器地址
   SMTP_PORT: 587               # SMTP 端口
   ```

4. **配置发送账户**

   在 Repository Secrets 中添加：

   ```
   EMAIL_USERNAME: your-smtp-username
   EMAIL_PASSWORD: your-app-password  # Gmail 请使用应用专用密码
   EMAIL_FROM: sender@example.com      # 可选，发件人地址
   ```

### Gmail 应用专用密码获取步骤

1. **开启两步验证**

   - 访问 [Google 账户安全设置](https://myaccount.google.com/security)
   - 找到"登录 Google"部分
   - 开启"两步验证"

2. **生成应用专用密码**

   - 直接访问：https://myaccount.google.com/apppasswords
   - 选择应用：选择"其他（自定义名称）"
   - 输入名称：如 `github-actions-ruff`
   - 点击"生成"

3. **复制密码**

   - 系统显示 16 位密码（格式：xxxx xxxx xxxx xxxx）
   - 立即复制保存，此密码只显示一次

4. **配置到 GitHub Secrets**
   ```
   EMAIL_PASSWORD: xxxx xxxx xxxx xxxx  # 生成的密码（包含空格）
   ```

### 注意事项

- 密码生成后只显示一次，建议保存在密码管理器中
- 应用专用密码比主密码更安全
- 可随时撤销不再使用的密码
- 如果看不到应用专用密码选项，确认：
  - 两步验证已开启
  - 不是由管理员控制的 Google Workspace 账户
  - 尝试更换浏览器或清除缓存

配置完成后，邮件将包含修复状态、分支信息、PR 链接等详细信息。

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

## Mypy 类型检查

Mypy 用于静态类型检查，帮助提前发现潜在的类型错误。由于类型错误的复杂性，大部分需要手动修复。

### 本地使用

```bash
# 运行类型检查
mypy agents/

# 查看详细错误信息
mypy agents/ --show-error-codes
```

### 常见处理策略

- 优先修复核心逻辑的类型错误
- 对于复杂问题使用 `# type: ignore` 并注释原因
- 采用渐进式方法逐步完善类型注解

### 配置建议

在 `pyproject.toml` 中设置：

```toml
[tool.mypy]
ignore_missing_imports = true
disallow_untyped_defs = false
```

## 故障排除

### 常见问题

- **API Key 错误**: 检查仓库 secrets 配置
- **Docker 构建失败**: 验证 Dockerfile 和 Hub 凭据
- **Docker 认证失败**: 确认 DOCKER_USERNAME 和 DOCKER_PASSWORD 配置正确
- **测试失败**: 查看日志，检查环境配置
- **PR 创建失败**: 确认 GITHUB_TOKEN 权限
- **通知失败**: 验证 Webhook URL 或 SMTP 配置

### 调试方法

- 查看 workflow 运行日志
- 使用 GitHub Actions 调试功能
- 本地复现失败的命令
- 检查 auto-fix 的 Step Summary
