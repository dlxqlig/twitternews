# Twitter News Monitor 🚀

[English](#english) | [中文](#chinese)

<a name="chinese"></a>
## 📖 项目简介

Twitter News Monitor 是一个智能的 Twitter 内容监控系统，能够自动监控指定的 Twitter List，使用 LLM（大语言模型）分析推文内容的相关性和价值，自动翻译英文内容为中文，并通过 Telegram 推送高价值推文。

### ✨ 核心功能

- 🔍 **智能监控**：自动监控多个 Twitter List，实时获取最新推文
- 🤖 **AI 分析**：支持 Gemini、OpenAI、通义千问等多种 LLM，智能评估推文价值（0.0-1.0 评分）
- 🌐 **自动翻译**：英文推文自动翻译为中文，便于阅读理解
- 📱 **Telegram 推送**：高价值推文即时推送到 Telegram，不错过重要信息
- 🖥️ **Web 控制台**：美观的 Web 界面，查看历史推文、调整参数、手动刷新
- ⏰ **定时任务**：可配置的自动检查间隔，灵活调整监控频率
- 🔐 **安全认证**：密码保护的管理后台

### 🎯 适用场景

- 科技新闻追踪
- AI/机器学习领域动态监控
- 加密货币市场资讯
- 行业 KOL 观点聚合
- 竞品动态跟踪

---

## 📋 环境要求

- Python 3.8+
- Twitter 账号（用于获取认证 Token）
- Telegram Bot（用于消息推送）
- LLM API Key（Gemini/OpenAI/通义千问任选其一）

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/twitternews.git
cd twitternews
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件（或复制 `.env.example`）：

```bash
# 安全配置
SECRET_KEY=your-secret-key-change-in-production
ADMIN_PASSWORD=your_admin_password

# 数据库
DATABASE_URL=sqlite:///./database/automation.db

# Twitter 认证（必需）⚠️ 重要：请参考 docs/TWITTER_AUTH_GUIDE.md 获取
TWITTER_AUTH_TOKEN=your_twitter_auth_token
TWITTER_CT0_TOKEN=your_twitter_ct0_token
TWITTER_LIST_URLS=https://x.com/i/lists/123456,https://x.com/i/lists/789012

# LLM 配置（三选一）
LLM_PROVIDER=gemini  # 可选: gemini, openai, qwen
DEFAULT_LLM_MODEL=gemini-1.5-pro

# Gemini
GEMINI_API_KEY=your_gemini_api_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# 通义千问
QWEN_API_KEY=your_qwen_api_key

# Telegram 推送（必需）
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# 自动化配置
AUTOMATION_CHECK_INTERVAL_MINUTES=5
DEFAULT_SCORE_THRESHOLD=0.85
```

### 4. 启动服务

#### 开发模式

```bash
python -m app.main
```

或使用 uvicorn：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 生产模式（systemd）

```bash
# 修改 twitternews.service 中的路径
sudo cp twitternews.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable twitternews
sudo systemctl start twitternews

# 查看状态
sudo systemctl status twitternews
```

### 5. 访问 Web 界面

打开浏览器访问：http://localhost:8000

默认密码：`admin123`（请及时修改 `.env` 中的 `ADMIN_PASSWORD`）

---

## 🔑 关键配置说明

### Twitter 认证获取

**必看文档**：[Twitter 认证 Token 获取指南](docs/TWITTER_AUTH_GUIDE.md)

简要步骤：
1. 在浏览器中登录 Twitter/X
2. 打开开发者工具（F12）
3. 切换到 Network 标签
4. 刷新页面，找到任意请求
5. 在 Request Headers 中找到：
   - `authorization: Bearer ...` → 复制整个值到 `TWITTER_AUTH_TOKEN`
   - `cookie` 中的 `ct0=...` → 复制值到 `TWITTER_CT0_TOKEN`

### Twitter List 配置

**详细文档**：[Twitter List 使用指南](docs/TWITTER_LIST_GUIDE.md)

- 支持多个 List，用逗号分隔
- 格式：`https://x.com/i/lists/LIST_ID`
- 运行中途可直接修改 `.env` 并重启服务

### LLM 提供商配置

| 提供商 | 设置 `LLM_PROVIDER` | API Key 变量 | 推荐模型 |
|--------|-------------------|--------------|---------|
| Google Gemini | `gemini` | `GEMINI_API_KEY` | `gemini-1.5-pro` |
| OpenAI | `openai` | `OPENAI_API_KEY` | `gpt-4` |
| 阿里通义千问 | `qwen` | `QWEN_API_KEY` | `qwen-turbo` |

### Telegram Bot 配置

1. 与 [@BotFather](https://t.me/BotFather) 对话创建 Bot
2. 获取 `TELEGRAM_BOT_TOKEN`
3. 与你的 Bot 对话，发送 `/start`
4. 访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` 获取 `chat_id`

---

## 📚 项目结构

```
twitternews/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 主入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models.py            # SQLAlchemy 模型
│   ├── routers/
│   │   ├── web.py           # Web 界面路由
│   ├── services/
│   │   ├── llm.py           # LLM 分析服务
│   │   ├── scheduler.py     # 定时任务
│   │   ├── telegram.py      # Telegram 推送
│   │   └── twitter.py       # Twitter API 封装
│   └── templates/           # Jinja2 模板
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       └── settings.html
├── database/                # SQLite 数据库目录
├── logs/                    # 日志目录
├── docs/                    # 文档目录
│   ├── TWITTER_AUTH_GUIDE.md
│   └── TWITTER_LIST_GUIDE.md
├── .env                     # 环境变量（需自行创建）
├── requirements.txt         # Python 依赖
├── twitternews.service      # Systemd 服务文件
└── README.md
```

---

## 🎮 使用说明

### Web 控制台功能

1. **推文浏览**
   - 按日期浏览历史推文
   - 根据评分筛选（0.0 - 1.0）
   - 查看 AI 翻译和摘要

2. **设置面板**
   - 调整自动检查间隔（分钟）
   - 实时生效，无需重启

3. **手动刷新**
   - 点击右下角刷新按钮
   - 立即触发一次推文抓取和分析

### Telegram 通知格式

```
🚨 发现高价值推文 (评分: 0.92)

👤 Elon Musk (@elonmusk)
📝 翻译：特斯拉全自动驾驶系统将在下周推送重大更新...
🧾 摘要：特斯拉 FSD 更新，改进城市道路驾驶能力

🔗 https://x.com/elonmusk/status/123456789
```

---

## ⚙️ 高级配置

### 自定义 LLM Prompt

修改 `app/config.py` 中的 `DEFAULT_PROMPT`：

```python
DEFAULT_PROMPT: str = """
你是一名精通中英文的科技新闻编辑，需要按照以下步骤处理推文：
1. 判断推文语言；如果不是中文，请先将整段推文准确翻译成中文，写入 translation 字段，内容以"翻译："开头。
2. 基于中文内容分析其与科技、人工智能或加密货币的相关性，给出 0.0~1.0 的评分，写入 score 字段（浮点数）。
3. 用中文撰写简洁要点，写入 summary 字段，内容以"摘要："开头。
4. 仅返回严格的 JSON，字段顺序不限，不要额外文本。

Tweet: {tweet_text}

Output format (JSON):
{{"score": 0.8, "translation": "翻译：...", "summary": "摘要：..."}}
"""
```

### 调整评分阈值

修改 `.env` 中的 `DEFAULT_SCORE_THRESHOLD`（默认 0.85）：

```bash
DEFAULT_SCORE_THRESHOLD=0.75  # 降低阈值，接收更多推文
```

---

## 🐛 故障排查

### Twitter 抓取失败

- **症状**：日志显示 GraphQL 请求失败
- **原因**：Twitter 的 API Query ID 可能已变化
- **解决**：
  1. 打开浏览器开发者工具
  2. 访问 Twitter List 页面
  3. 找到 `ListLatestTweetsTimeline` 请求
  4. 复制新的 `queryId`
  5. 更新 `app/services/twitter.py` 中的 `QUERY_ID`

### LLM 分析失败

- 检查 API Key 是否正确
- 检查网络连接（某些 LLM 可能需要代理）
- 查看日志：`journalctl -u twitternews -n 50`

### Telegram 推送失败

- 确认 Bot Token 正确
- 确认 Chat ID 正确
- 确认已与 Bot 对话并发送过 `/start`

---

## 📝 开发指南

### 运行测试

```bash
# 测试 LLM 连接
python test_qwen.py

# 查看日志
tail -f logs/app.log
```

### 代码风格

- 遵循 PEP 8
- 使用类型提示
- 添加必要的注释

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [APScheduler](https://apscheduler.readthedocs.io/)
- [Google Gemini](https://ai.google.dev/)
- [OpenAI](https://openai.com/)
- [阿里通义千问](https://dashscope.aliyun.com/)

---

## 📮 联系方式

如有问题或建议，请：
- 提交 [Issue](https://github.com/yourusername/twitternews/issues)
- 发送邮件至 your.email@example.com

---

<a name="english"></a>
## English Version

### Overview

Twitter News Monitor is an intelligent Twitter content monitoring system that automatically monitors specified Twitter Lists, uses LLM (Large Language Models) to analyze tweet relevance and value, automatically translates English content to Chinese, and pushes high-value tweets via Telegram.

### Key Features

- 🔍 **Smart Monitoring**: Automatically monitor multiple Twitter Lists
- 🤖 **AI Analysis**: Support for Gemini, OpenAI, Qwen with intelligent scoring (0.0-1.0)
- 🌐 **Auto Translation**: Automatically translate English tweets to Chinese
- 📱 **Telegram Push**: Real-time notifications for high-value tweets
- 🖥️ **Web Console**: Beautiful web interface for browsing and management
- ⏰ **Scheduled Tasks**: Configurable automatic check intervals
- 🔐 **Secure Authentication**: Password-protected admin panel

### Quick Start

See Chinese documentation above for detailed setup instructions.

### Documentation

- [Twitter Authentication Guide](docs/TWITTER_AUTH_GUIDE.md)
- [Twitter List Guide](docs/TWITTER_LIST_GUIDE.md)

---

**⭐ If you find this project helpful, please give it a star!**
