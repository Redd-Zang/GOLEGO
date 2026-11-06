# GOLEGO · 乐高照相馆

上传照片，制作你的专属周年纪念海报。

为 Amazing Friday 19 周年活动制作的 LEGO 风格海报工具，包含可安装的 Codex skill、扫码上传网页、自动生成队列与浏览器领取页面。

## 功能

- 自动依据照片主体制作单人或多人海报，无需选择人数。
- 输出 1080×1920 PNG，沿用金色 19 纪念碑与 AMAZING FRIDAY 铭牌。
- 支持 JPG、PNG、HEIC，单张最大 12 MB。
- 默认最多 5 个任务同时制作，累计 50 次提交后停止接收，并提示管理员确认是否加额。
- 每个浏览器一次提交；同一浏览器、同一入口地址可返回领取。清除 Cookie 或换浏览器可重新提交，不能保证按真实身份限次。
- 等待页提示“每人限一张，等待约5min，可稍后回来领取。”5 分钟是预估，实际取决于队列及生图服务。
- 上传按钮下显示“上传即表示您同意使用该照片进行 AI 海报制作。”

## 安装与启动

需要 Python 3.12、Codex，以及已登录且可调用内置图像生成的 Codex CLI。先按[安装说明](af19-guest-poster/references/install.md)真实测试一张；仅复制 skill 不代表后台自动生图已可用。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r af19-guest-poster/requirements.txt
.venv/bin/python af19-guest-poster/scripts/qr_station.py --data-dir ./af19-data --bind 127.0.0.1 --port 8919 --workers 5 --limit 50
```

Windows 使用 `py -m venv .venv`，后续 Python 改用 `.venv\Scripts\python.exe`。Windows 和 Linux 尚待实机验证。

打开 http://127.0.0.1:8919/。运行数据保存在 `af19-data/`，不会提交到 Git。

将 `af19-guest-poster/` 复制到目标电脑的 Codex 技能目录，在新聊天里输入 `$af19-guest-poster` 并附上照片，也可直接制作或批量处理。详细流程见 [SKILL.md](af19-guest-poster/SKILL.md)。

## 扫码活动

公网接入、二维码、结果目录、额度与恢复流程见[现场模式](af19-guest-poster/references/station.md)。电脑与服务需要持续运行。临时公网域名可能变化，新的电脑需建立自己的入口，历史二维码不会自动迁移。

本项目是活动内测工具，仓库不包含账号凭据、来宾照片、历史海报或领取会话。生图依赖目标账号能力及其用量；仓库不附带独立免费额度。

普通模式只制作纪念海报；INVITATION、活动时间、地点及额外 Logo 仅在明确要求邀请函时添加。

[验证记录](VERIFICATION.md)
