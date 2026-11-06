# 在另一台电脑复刻

## 安装技能

解压后把 `af19-guest-poster` 整个文件夹放入目标电脑的 Codex 技能目录。

- macOS／Linux 默认目录为 `~/.codex/skills/af19-guest-poster/`。
- Windows 默认目录为 `%USERPROFILE%\.codex\skills\af19-guest-poster\`。
- 设置了 CODEX_HOME 时使用该目录下的 `skills/af19-guest-poster/`。

已有同名技能时先比较并备份，再替换。打开新的 Codex 聊天，输入 `$af19-guest-poster` 并附照片即可调用。项目专用安装也可放到项目的 `.agents/skills/`。

## Python 依赖

使用 Python 3.12（本包验证版本），在自己的活动项目目录创建虚拟环境。下列 SKILL_PATH 替换成实际技能目录，保留引号。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r "SKILL_PATH/requirements.txt"
```

Windows 使用 `py -m venv .venv`，随后运行 `.venv\Scripts\python.exe -m pip install -r "SKILL_PATH\requirements.txt"`。下文的 python 均指该虚拟环境的解释器。

包中附带样式参考、网页插图、导出脚本、收图站和依赖清单。所有运行数据写到用户指定的活动目录。没有打包会员原始照片、旧访客领取 Cookie、账号凭据、原电脑虚拟环境或临时公网网址。

## 验证目标电脑

先让 Codex 对一张测试照片生成海报并目检。再检查 `codex --version` 与 `codex login status`。自动队列脚本通过 `codex exec` 使用内置 image_generation 能力，其开关和生成文件目录依赖目标 CLI 版本；应在目标电脑真实跑通后再开放活动收件。

```sh
python "SKILL_PATH/scripts/guest_job.py" demo photo-001 "PHOTO_PATH" --jobs "ACTIVITY_PATH/jobs"
```

使用相同的 demo、photo-001 和 jobs 路径再次运行会复用已完成成品。不同照片使用新的编号。成功任务目录含 `reference.jpg`、`scene.png`、`poster.png` 和 `state.json`。

本包采用跨平台 Python 文件锁和 Pillow 图像处理。macOS 本机迁移测试见包外验证说明；Windows／Linux 的系统环境和 CLI 生图能力仍需在目标机验证。HEIC 由 pillow-heif 解码，目标系统需能安装对应依赖。
