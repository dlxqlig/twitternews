# Twitter 认证 Token 获取指南

本指南详细介绍如何从浏览器中获取 Twitter 的 `auth_token` 和 `ct0` token，这是使用本项目监控 Twitter List 的必要步骤。

---

## 📋 目录

- [准备工作](#准备工作)
- [方法 1：Chrome/Edge 浏览器](#方法-1chromeedge-浏览器推荐)
- [方法 2：Firefox 浏览器](#方法-2firefox-浏览器)
- [方法 3：Safari 浏览器](#方法-3safari-浏览器)
- [Token 说明](#token-说明)
- [常见问题](#常见问题)
- [安全注意事项](#安全注意事项)

---

## 准备工作

1. ✅ 确保你有一个可用的 Twitter/X 账号
2. ✅ 在浏览器中登录 Twitter/X（https://x.com 或 https://twitter.com）
3. ✅ 确认登录状态正常，能够访问你的首页和列表

---

## 方法 1：Chrome/Edge 浏览器（推荐）

### 步骤 1：打开开发者工具

1. 访问 [https://x.com](https://x.com)（确保已登录）
2. 按下快捷键打开开发者工具：
   - **Windows/Linux**: `F12` 或 `Ctrl + Shift + I`
   - **Mac**: `Cmd + Option + I`

### 步骤 2：切换到 Network（网络）标签

1. 点击开发者工具顶部的 **"Network"**（网络）标签
2. 如果看不到任何请求，刷新页面（`F5` 或 `Ctrl + R`）

![Chrome DevTools Network Tab](https://i.imgur.com/example1.png)

### 步骤 3：找到任意 Twitter API 请求

1. 在 Network 标签的过滤框中输入 `graphql` 或 `api`
2. 点击任意一个请求（通常是以 `graphql` 开头的）
3. 在右侧面板中找到 **"Headers"**（请求头）部分

### 步骤 4：获取 auth_token

1. 在 Headers 部分向下滚动，找到 **"Request Headers"**（请求标头）
2. 找到 `authorization` 字段，它的值类似于：
   ```
   Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA
   ```
3. **完整复制**整个值（包括 `Bearer ` 前缀）到你的 `.env` 文件中的 `TWITTER_AUTH_TOKEN`

   ```bash
   TWITTER_AUTH_TOKEN=Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA
   ```

### 步骤 5：获取 ct0 token

1. 在同一个请求的 Headers 部分，继续向下找到 `cookie` 字段
2. Cookie 字段会包含很多键值对，找到其中的 `ct0=...`
3. 只复制 `ct0=` 后面的值（不包括分号和其他内容）

   示例：
   ```
   cookie: auth_token=abc123...; ct0=1234567890abcdef1234567890abcdef; ...
   ```

   只复制：
   ```
   1234567890abcdef1234567890abcdef
   ```

4. 将这个值添加到 `.env` 文件中的 `TWITTER_CT0_TOKEN`

   ```bash
   TWITTER_CT0_TOKEN=1234567890abcdef1234567890abcdef
   ```

---

## 方法 2：Firefox 浏览器

### 步骤类似 Chrome

1. 访问 [https://x.com](https://x.com)
2. 按 `F12` 打开开发者工具
3. 切换到 **"网络"** 标签
4. 刷新页面
5. 点击任意 `graphql` 请求
6. 查看 **"消息头"** → **"请求头"**
7. 找到 `authorization` 和 `cookie` 字段
8. 按上述方法复制 `auth_token` 和 `ct0`

---

## 方法 3：Safari 浏览器

### 启用开发者菜单

1. 打开 Safari → 偏好设置 → 高级
2. 勾选"在菜单栏中显示开发菜单"

### 获取 Token

1. 访问 [https://x.com](https://x.com)
2. 菜单栏 → 开发 → 显示 Web 检查器（或按 `Cmd + Option + I`）
3. 切换到 **"网络"** 标签
4. 刷新页面
5. 点击任意 `graphql` 请求
6. 查看 **"请求"** 部分
7. 找到 `Authorization` 和 `Cookie`
8. 按上述方法提取值

---

## Token 说明

### TWITTER_AUTH_TOKEN

- **格式**: `Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAA...`
- **作用**: 用于 Twitter API 认证的主要凭证
- **特点**: 
  - 通常以 `Bearer` 开头
  - 长度约 100+ 字符
  - 这个 token 对所有用户是相同的（Twitter 的 Bearer token）

### TWITTER_CT0_TOKEN

- **格式**: `1234567890abcdef1234567890abcdef`（32 位十六进制字符串）
- **作用**: 防 CSRF（跨站请求伪造）的安全 token
- **特点**:
  - 与你的登录会话绑定
  - 每次登录可能不同
  - 必须与正确的 cookie 配合使用

---

## 常见问题

### Q1: 找不到 `authorization` 字段？

**A**: 确保你：
1. 已经登录 Twitter
2. 刷新了页面
3. 在 Network 标签中看到了请求
4. 查看的是 **Request Headers**（不是 Response Headers）

### Q2: Token 获取后不工作？

**A**: 可能原因：
1. ❌ 复制时包含了多余的空格或换行
2. ❌ `auth_token` 没有包含 `Bearer ` 前缀
3. ❌ `ct0` token 已过期（重新登录获取）
4. ❌ 网络问题或 Twitter API 限流

**解决方法**：
- 重新获取 token
- 确保 `.env` 文件格式正确（没有引号、空格）
- 尝试退出 Twitter 账号重新登录

### Q3: Token 会过期吗？

**A**: 是的。
- `auth_token`（Bearer token）相对稳定，但 Twitter 可能会更新
- `ct0` token 与会话绑定，退出登录后会失效
- 建议：如果项目突然无法工作，首先尝试重新获取 token

### Q4: 可以在无头浏览器/自动化中获取吗？

**A**: 可以，但不推荐。
- 手动获取更简单、更安全
- 自动化可能违反 Twitter 服务条款
- 本项目设计为一次配置，长期使用

---

## 安全注意事项

⚠️ **重要**：Token 相当于你的账号密码，请务必保管好！

### ✅ 应该做的：

- ✅ 将 `.env` 文件添加到 `.gitignore`（避免提交到 Git）
- ✅ 不要在公开渠道分享你的 token
- ✅ 定期更换 token（尤其是怀疑泄露时）
- ✅ 使用独立的 Twitter 账号（不是主账号）

### ❌ 不应该做的：

- ❌ 将 token 硬编码在代码中
- ❌ 在 GitHub 等平台公开 token
- ❌ 与他人共享你的 token
- ❌ 在不安全的网络环境中传输 token

### 如果 Token 泄露了怎么办？

1. 立即在 Twitter 上**退出登录**（所有设备）
2. 重新登录 Twitter
3. 重新获取新的 token
4. 检查账号是否有异常活动

---

## 验证 Token 是否正确

获取 token 后，可以通过以下方式验证：

### 方法 1：使用 curl 测试

```bash
curl -H "authorization: Bearer YOUR_AUTH_TOKEN_HERE" \
     -H "x-csrf-token: YOUR_CT0_TOKEN_HERE" \
     -H "cookie: ct0=YOUR_CT0_TOKEN_HERE" \
     "https://api.twitter.com/2/users/me"
```

如果返回 JSON 数据（包含你的用户信息），说明 token 正确。

### 方法 2：运行项目测试

```bash
# 配置好 .env 文件后
python -m app.main

# 查看日志
tail -f logs/app.log
```

如果日志中没有认证错误，说明 token 正确。

---

## 示例配置

完整的 `.env` 配置示例：

```bash
# Twitter 认证
TWITTER_AUTH_TOKEN=Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA
TWITTER_CT0_TOKEN=1234567890abcdef1234567890abcdef
TWITTER_LIST_URLS=https://x.com/i/lists/123456,https://x.com/i/lists/789012

# LLM 配置
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key

# Telegram 配置
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789

# 其他配置...
```

---

## 更新日志

- **2025-11-24**: 初始版本
- 如有更新，会在此处记录

---

## 相关资源

- [Twitter List 使用指南](TWITTER_LIST_GUIDE.md)
- [项目 README](../README.md)
- [Twitter API 文档](https://developer.twitter.com/en/docs)

---

## 需要帮助？

如果按照本指南操作后仍有问题：

1. 检查 [常见问题](#常见问题) 部分
2. 查看项目的 [GitHub Issues](https://github.com/yourusername/twitternews/issues)
3. 提交新的 Issue 并附上：
   - 操作系统和浏览器版本
   - 错误日志
   - 已尝试的解决方法

---

**祝你使用愉快！** 🎉
