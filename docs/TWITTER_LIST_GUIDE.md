# Twitter List 监控使用指南

## 📋 什么是 Twitter List？

Twitter List 是一个精选的 Twitter 账号集合。您可以创建 List 来组织关注的账号，或关注他人创建的 List。

## 🔍 如何找到 Twitter List ID

### 方法 1：从 URL 直接查看（最简单）

访问您想监控的 List，查看浏览器地址栏：

#### 格式 A：数字 ID（推荐）
```
https://x.com/i/lists/1234567890123456789
                      ^^^^^^^^^^^^^^^^^^^
                      这就是 List ID
```

#### 格式 B：自定义名称
```
https://x.com/username/lists/my-list-name
```
这种格式需要使用下面的方法转换为数字 ID

### 方法 2：使用我们提供的工具

我们提供了一个命令行工具来帮您提取 List ID：

```bash
# 在容器内运行
docker exec auto-ski-info-subscribe-backend-1 python get_list_id.py "您的List URL"
```

**示例：**
```bash
docker exec auto-ski-info-subscribe-backend-1 python get_list_id.py "https://x.com/i/lists/1234567890"
```

**输出：**
```
✅ 提取成功！
List ID: 1234567890

您可以使用以下 API 调用添加此 List：
curl -X POST http://localhost:8000/api/monitor/lists/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"list_url": "1234567890"}'
```

### 方法 3：使用浏览器开发者工具

1. **打开 List 页面**
   - 访问 https://x.com 登录
   - 导航到您想监控的 List

2. **打开开发者工具**
   - Windows/Linux: 按 `F12` 或 `Ctrl+Shift+I`
   - Mac: 按 `Cmd+Option+I`

3. **查看网络请求**
   - 点击 "Network" (网络) 标签
   - 刷新页面 (`F5` 或 `Cmd+R`)
   - 在筛选框中输入 "ListByRestId"

4. **找到 List ID**
   - 点击找到的请求
   - 查看 "Preview" 或 "Response" 标签
   - 搜索 `"rest_id"` 字段，其值就是 List ID

### 方法 4：从页面源代码查找

1. **查看源代码**
   - 右键点击页面
   - 选择 "查看页面源代码" 或 "View Page Source"

2. **搜索 rest_id**
   - 使用浏览器的查找功能 (`Ctrl+F` 或 `Cmd+F`)
   - 搜索 `"rest_id"`
   - 找到类似这样的内容：
   ```json
   "rest_id":"1234567890123456789"
   ```

## 🚀 如何添加 List 监控

### 方式 1：使用 API（命令行）

```bash
# 1. 获取您的 API Token
# 登录前端 http://localhost:5000
# Token 会保存在浏览器 localStorage 中

# 2. 添加 List
curl -X POST http://localhost:8000/api/monitor/lists/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"list_url": "https://x.com/i/lists/1234567890"}'

# 3. 手动触发抓取
curl -X POST http://localhost:8000/api/monitor/lists/1/fetch_latest/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# 4. 查看推文
curl -X GET http://localhost:8000/api/monitor/lists/1/tweets/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### 方式 2：使用前端界面（即将推出）

前端界面正在开发中，将支持：
- 可视化添加/删除 List
- 配置监控间隔
- 查看 List 推文时间线
- AI 智能过滤

## 📊 支持的 List URL 格式

系统智能识别以下所有格式：

```bash
# ✅ 完整 URL（推荐）
https://x.com/i/lists/1234567890123456789
https://twitter.com/i/lists/1234567890123456789

# ✅ 自定义 List URL
https://x.com/username/lists/my-awesome-list

# ✅ 仅 List ID
1234567890123456789
```

## ⚙️ List 监控配置

添加 List 后，您可以配置：

### 监控间隔
- **30分钟** - 高活跃 List（成员经常发推）
- **1小时** - 中活跃 List
- **4小时** - 低活跃 List（默认）
- **12小时** - 极低活跃 List

### AI 智能过滤
启用后，只保存 AI 判断为相关的推文，节省存储空间并提高信息质量。

## 🎯 使用场景示例

### 场景 1：监控行业专家
创建一个包含您所在行业专家的 List，系统会自动收集他们的推文。

### 场景 2：新闻聚合
订阅新闻媒体的 List，获取实时新闻更新。

### 场景 3：竞品分析
创建竞争对手公司账号的 List，追踪他们的动态。

### 场景 4：技术学习
关注技术大牛的 List，不错过任何有价值的技术分享。

## 📝 API 端点完整列表

```
GET    /api/monitor/lists/              # 获取所有 List
POST   /api/monitor/lists/              # 添加新 List
GET    /api/monitor/lists/{id}/         # 获取 List 详情
PATCH  /api/monitor/lists/{id}/         # 更新 List 配置
DELETE /api/monitor/lists/{id}/         # 删除 List
POST   /api/monitor/lists/{id}/fetch_latest/  # 手动抓取
GET    /api/monitor/lists/{id}/tweets/  # 获取 List 推文
GET    /api/monitor/lists/{id}/logs/    # 获取监控日志
GET    /api/monitor/list-logs/          # 获取所有 List 日志
```

## ❓ 常见问题

### Q: 为什么找不到 List ID？
A: 确保您已登录 Twitter/X，并且有权访问该 List。私有 List 需要是 List 成员才能访问。

### Q: 可以监控私有 List 吗？
A: 可以，只要您上传的 Cookie 对应的账号有权访问该 List。

### Q: List 中的推文多久更新一次？
A: 根据您设置的监控间隔（30分钟到12小时）。您也可以随时手动触发更新。

### Q: 会保存 List 中所有人的推文吗？
A: 系统只保存24小时内的新推文。您可以通过日期范围参数查询历史推文。

### Q: 可以同时监控多少个 List？
A: 没有硬性限制，但建议根据您的服务器资源合理配置。

## 💡 提示

1. **使用数字 List ID** 比使用自定义名称更稳定，因为用户可能会重命名 List。

2. **合理设置监控间隔** 以平衡信息实时性和服务器资源消耗。

3. **启用 AI 过滤** 可以大幅减少无关推文，提高信息质量。

4. **定期查看日志** 确保监控正常运行，及时发现问题。

## 🔗 相关文档

- [API 文档](http://localhost:8000/swagger/)
- [账号监控指南](./README.md)
- [AI 过滤配置](./AI_FILTER_GUIDE.md)

---

如有问题，请查看日志或联系技术支持。
