# Codex 桌宠合集

OpenAI Codex 桌面应用的自定义桌宠，每个桌宠放在独立文件夹里，把对应文件夹复制到桌宠目录即可使用。

| 桌宠 | 风格 |
|------|------|
| [`bitty/`](bitty/) 小比特 | 8-bit 像素风方块机器人：深蓝机身 + 青色屏幕脸，屏幕会眨眼 |
| [`moonwool/`](moonwool/) 月绒 | 柔和奶油色绒团小兽：头顶星星触角，尾巴像月牙 |

## 安装

1. 把想用的桌宠文件夹（比如 `bitty/`）整个复制到 Codex 桌宠目录：

   ```
   C:\Users\xhr\.codex\pets\bitty\
   ```

   （如果目标已有同名文件夹，直接覆盖 `pet.json` 和 `spritesheet.png`）

2. 在 `C:\Users\xhr\.codex\config.toml` 的 `[desktop]` 段选中它：

   ```toml
   [desktop]
   selected-avatar-id = "custom:bitty"
   ```

   `custom:` 后面的名字要和桌宠文件夹名一致（`bitty` / `moonwool`）。

3. 重启 Codex 桌面应用（或重新打开头像选择器），桌宠就会切换。

## 桌宠包文件说明

| 文件 | 作用 |
|------|------|
| `pet.json` | 桌宠包描述：显示名、spritesheet 路径、`spriteVersionNumber: 1`（9 行布局） |
| `spritesheet.png` | 动画帧图：1536×1872，8 列 × 9 行，每格 192×208 |
| `make_spritesheet.py` | 用参数化 Python 生成 spritesheet 的脚本（Pillow，仅 bitty 有） |
| `make_preview.py` / `preview.html` | 浏览器里的 9 状态动画预览（idle 按 App 的 6 倍慢放；bitty 和 moonwool 都有） |

## 状态行布局（与 Codex App 内置一致）

| 行 | 状态 | 帧数 |
|----|------|------|
| 0 | idle 待机 | 6（App 固定 6 倍慢放） |
| 1 | running-right | 8 |
| 2 | running-left | 8 |
| 3 | waving 挥手 | 4 |
| 4 | jumping 跳跃 | 5 |
| 5 | failed 失败 | 8 |
| 6 | waiting 等待 | 6 |
| 7 | running 奔跑 | 6 |
| 8 | review 审查 | 6 |

帧时长、帧数、行布局都由 Codex App 硬编码，桌宠包只能改像素内容。

## bitty 重新生成

```bash
python make_spritesheet.py   # 重新生成 spritesheet.png
python make_preview.py       # 重新生成 preview.html
```

改动画态：编辑 `make_spritesheet.py` 里的 `spec_*()` 函数，再运行上面两条命令。
