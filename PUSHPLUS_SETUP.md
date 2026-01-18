# PushPlus 微信推送配置指南

## 📱 什么是 PushPlus？

PushPlus 是一个微信消息推送服务，可以让您通过 API 将消息推送到微信。完全免费，非常适合用于自动化通知。

---

## 🚀 快速配置步骤

### 步骤 1: 获取 PushPlus Token

1. **访问 PushPlus 官网**
   👉 https://www.pushplus.plus/

2. **扫码登录**
   - 使用微信扫描页面上的二维码登录

3. **获取 Token**
   - 登录后自动跳转到控制台
   - 复制您的 **Token**（一串随机字符）
   - Token 格式类似：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 步骤 2: 配置 GitHub Secret

浮浮酱已经帮主人准备好了配置命令喵～

请主人提供 PushPlus Token，浮浮酱会帮您自动配置到 GitHub Secrets 喵～

**或者主人也可以手动配置：**

1. 访问仓库设置页面：
   ```
   https://github.com/ccj20181-lab/daily-tech-digest/settings/secrets/actions
   ```

2. 点击 `New repository secret`

3. 添加以下信息：
   - **Name**: `PUSHPLUS_TOKEN`
   - **Value**: 粘贴您的 PushPlus Token

4. 点击 `Add secret`

### 步骤 3: 测试通知功能

配置完成后，浮浮酱可以帮您手动触发一次测试喵～

---

## 📋 通知内容说明

每次生成简报后，您会收到包含以下内容的微信通知：

### 📊 通知标题
```
📊 每日科技简报 2026-01-18
```

### 📝 通知内容
- 简报摘要（前500字）
- 在线查看链接（GitHub Pages）
- GitHub Actions 运行链接
- 生成时间

### 🔗 快速访问链接
- **在线简报**: https://ccj20181-lab.github.io/daily-tech-digest/digests/latest.md
- **历史归档**: https://ccj20181-lab.github.io/daily-tech-digest/digests/
- **GitHub 仓库**: https://github.com/ccj20181-lab/daily-tech-digest

---

## ⚙️ PushPlus 高级配置（可选）

### 1. 设置推送模板

登录 PushPlus 控制台，可以：
- 自定义消息模板
- 设置消息样式
- 配置推送时间

### 2. 群组推送（可选）

如果您想推送到微信群：
1. 在 PushPlus 创建一个群组
2. 获取群组二维码
3. 邀请成员扫码加入
4. 使用群组 Token 替代个人 Token

### 3. 查看推送记录

在 PushPlus 控制台可以查看：
- 推送历史记录
- 成功/失败状态
- 接收时间

---

## 🔧 故障排查

### 问题1: 没有收到微信通知

**可能原因**：
1. PushPlus Token 配置错误
2. GitHub Actions 运行失败
3. 网络问题

**解决方法**：
1. 检查 GitHub Secrets 中的 Token 是否正确
2. 查看 GitHub Actions 运行日志
3. 在 PushPlus 控制台查看推送记录

### 问题2: 通知内容显示异常

**可能原因**：
- Markdown 格式解析问题

**解决方法**：
- 当前使用 HTML 模板，如需调整可以修改 `scripts/send_pushplus.py`

### 问题3: 想要修改通知时间

PushPlus 推送会在简报生成成功后立即发送，因此：
- **定时推送时间** = 修改 GitHub Actions 定时任务
- 当前设置：每天北京时间 6:00

如需修改，编辑 `.github/workflows/daily-tech-digest.yml`：
```yaml
schedule:
  - cron: '0 22 * * *'  # 北京时间 6:00
```

---

## 📊 使用效果示例

### 微信通知示例
```
📊 每日科技简报 2026-01-18

# 科技简报 2026-01-18

**导语：** jQuery 4.0 的发布标志着 Web 时代的又一次迭代...

---
📅 查看完整简报: https://ccj20181-lab.github.io/daily-tech-digest/digests/latest.md

🤖 由 Claude AI + 智谱 GLM-4.7 自动生成
⏰ 生成时间: 2026-01-18 06:00:15
```

---

## 💰 费用说明

- ✅ **完全免费** - PushPlus 个人版免费使用
- ✅ **无限制推送** - 每日可发送多条消息
- ✅ **稳定可靠** - 基于微信官方公众号接口

---

## 📚 相关链接

- PushPlus 官网: https://www.pushplus.plus/
- PushPlus 文档: http://www.pushplus.plus/doc/
- API 接口说明: http://www.pushplus.plus/doc/api/

---

**创建时间**: 2026-01-18
**维护者**: Henry
**许可证**: MIT
