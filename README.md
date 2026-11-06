# GOLEGO · 乐高照相馆

上传照片，制作你的专属周年纪念海报。

为 Amazing Friday 19 周年活动制作的 LEGO 风格海报工具，包含可安装的 Codex skill、扫码上传网页、自动生成队列与浏览器领取页面。

## 海报实例

以下两张为旧版 9:16 普通纪念海报（新版输出为 2:3 六寸满版）：单人样片与双人合影测试成品（双人源图为虚构测试人物）。

| 单人海报 | 双人海报 |
| --- | --- |
| <img src="examples/single-person.png" alt="单人 LEGO 周年海报" width="320"> | <img src="examples/two-person.png" alt="双人 LEGO 周年海报" width="320"> |

点击查看原尺寸：[单人海报](examples/single-person.png) · [双人海报](examples/two-person.png)。

## 下载技能

[下载项目 ZIP](https://github.com/Redd-Zang/GOLEGO/archive/refs/heads/main.zip)，或点击仓库的 **Code → Download ZIP**。解压后将 `af19-guest-poster` 文件夹交给 Codex，并发送：

> 请安装这个 af19-guest-poster 技能，按照 references/install.md 检查环境，然后用我提供的照片测试制作一张 LEGO 海报。先验证单张制作，暂不开启扫码收图。

## 功能

- 自动依据照片主体制作单人或多人海报，无需选择人数。
- 输出六寸竖版 PNG：4×6 英寸、1200×1800 像素、300 DPI，沿用金色 19 纪念碑与 AMAZING FRIDAY 铭牌。
- 按 2:3 满版构图；比例不符时先用内置生图扩展场景，保留人物、鞋子和纪念碑。禁止白边、裁切、拉伸、镜像及模糊填边。导出仍不符比例时不交付。
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

本项目是活动内测工具，仓库附带两张已生成海报作为示例，不包含账号凭据、来宾原始照片或领取会话。生图依赖目标账号能力及其用量；仓库不附带独立免费额度。

普通模式只制作纪念海报；INVITATION、活动时间、地点及额外 Logo 仅在明确要求邀请函时添加。

[验证记录](VERIFICATION.md)
