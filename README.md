# 🦞 OpenClaw 卸载工具

macOS 图形化卸载工具，完全移除 OpenClaw 并消除其引入的安全风险。

![UI 预览](https://img.shields.io/badge/platform-macOS%2012%2B-lightgrey) ![Python](https://img.shields.io/badge/python-3.9%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

---

## 功能

- **扫描**：检测运行中进程、开放端口、开机自启服务、本地凭证、npm 包、Shell 注入
- **一键清除**：终止进程 → 移除 LaunchAgent → 卸载 npm 包 → 删除二进制 → 清除数据/凭证 → 清理 zshrc
- **动画 UI**：龙虾剥壳 CSS 动画实时展示清除进度
- **验证**：清除完成后逐项确认结果

## 清除范围

| 类型 | 内容 |
|------|------|
| 进程 | `openclaw-gateway`, `openclaw-pairing`, `openclaw-manager` 等 |
| 端口 | Gateway API 端口 18789 |
| 开机自启 | `~/Library/LaunchAgents/ai.openclaw.gateway.plist` |
| npm 包 | `openclaw`, `clawdbot`, `clawhub` |
| 二进制 | `/opt/homebrew/bin/` 中的相关文件 |
| 数据目录 | `~/.openclaw`, `~/openclaw-manager` 及 Library 下相关缓存 |
| Shell 配置 | `~/.zshrc` 中的 openclaw 相关行（自动备份） |

---

## 使用方式

### 方式一：下载预构建 App（推荐小白用户）

1. 克隆仓库并构建：
   ```bash
   git clone https://github.com/Mel0day/openclaw-uninstaller.git
   cd openclaw-uninstaller
   ./build.sh
   ```
2. 将 `dist/OpenClaw卸载工具.app` 拖到桌面
3. 双击运行

> **首次打开提示"无法打开"？** 右键点击 App → 选「打开」即可绕过 Gatekeeper。

### 方式二：直接运行后端（无需构建）

```bash
python3 server.py
```

启动后自动在浏览器打开操作界面。

---

## 构建说明

```
openclaw-uninstaller/
├── server.py            # Python HTTP 后端（扫描 + 卸载 + SSE 实时推送）
├── index.html           # 暗色 UI（龙虾剥壳 CSS 动画）
├── launcher.applescript # macOS .app AppleScript 启动器
├── make_icon.py         # 纯 stdlib 生成龙虾图标（PNG → icns，无需 Pillow）
└── build.sh             # 一键构建 dist/OpenClaw卸载工具.app
```

**依赖**：Python 3.9+（macOS 自带），无需额外安装任何第三方库。

---

## 技术实现

- **后端**：Python `http.server` + `socketserver`，随机端口，仅监听 `127.0.0.1`
- **实时进度**：Server-Sent Events (SSE)，无需 WebSocket
- **图标**：纯 Python stdlib 逐像素绘制 PNG，`iconutil` 转换为 `.icns`
- **App 打包**：`osacompile` 编译 AppleScript 为真正的 Mach-O 可执行文件，解决 Finder 无法执行 shell script 的问题

---

## 清除后建议

- 前往[飞书开放平台](https://open.feishu.cn)吊销 App Secret
- 前往 [portal.qwen.ai](https://portal.qwen.ai) 删除相关 API 密钥
- 执行 `source ~/.zshrc` 使 Shell 配置生效

---

## License

MIT
