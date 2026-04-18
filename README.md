# MC模组更新通知插件

✨ 基于 AstrBot 的一个插件 ✨

用于订阅和管理 Minecraft 模组/整合包的更新通知。

## ✨ 功能

- 📰 **模组订阅**：在聊天软件中订阅感兴趣的 MC 模组/整合包
- 🔄 **自动检查**：每小时自动检查订阅项的更新情况
- 🔔 **主动推送**：发现新版本时主动推送更新通知
- 🌐 **多平台支持**：目前支持 MCMod中文站、XYEBBS、BBSMC 三个网站（其他WIP）
- 📋 **订阅管理**：支持查看订阅列表、取消订阅等操作

## 📝 指令列表

| 指令                  | 说明                                    |
| --------------------- | --------------------------------------- |
| `/mc订阅 <URL>`     | 订阅指定模组/整合包的更新通知           |
| `/mc取消订阅 <URL>` | 取消订阅指定模组/整合包                 |
| `/mc订阅列表`       | 查看当前会话的订阅列表                  |
| `/mc查询 <URL>`     | 查询模组/整合包的最新版本信息（不订阅） |
| `/mc强制更新`       | 手动触发所有已订阅的更新检查            |

## ⚙️ 配置说明

本插件配置包含以下数据，无需手动修改，指令会自动管理：

| 配置项                 | 说明                             |
| ---------------------- | -------------------------------- |
| `subscribe_relation` | 存储所有订阅者及其订阅的链接     |
| `modData`            | 存储所有已订阅模组的最新版本信息 |

## 📦 安装

1. 将本插件克隆到 AstrBot 插件目录：

```bash
cd AstrBot/data/plugins
git clone https://github.com/MMoon-kid/astrbot_plugin_subscribeMC
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 📌 注意事项

1. **网站支持范围**：目前仅支持 `mcmod.cn`、`xyebbs.com`、`bbsmc.net` 三个网站，不支持其他模组网站
2. **会话级订阅机制**：订阅关系基于会话（session），不同会话需要单独订阅
3. **网页结构依赖**：插件通过解析目标网页的 HTML 结构来获取数据，如果目标网站更改页面结构，爬虫可能失效
4. **网络环境**：需要能正常访问目标网站，建议在网络稳定的环境下使用

## 🛠️ 技术实现

- **网页爬虫**：使用 aiohttp + BeautifulSoup 解析 HTML
- **定时任务**：使用 APScheduler 每小时自动检查更新
- **依赖项**：aiohttp、beautifulsoup4、apscheduler、selenium、webdriver-manager

## 📝 更新日志

- 最新版本：v1.0.0
- 初始版本

## 📄 License

[GPL-3.0](LICENSE)

## 👨‍💻 开发者

- **开发者**：明辉晓月
- **仓库**：https://github.com/MMoon-kid/astrbot_plugin_subscribeMC
