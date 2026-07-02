# StarsailX 打包说明

## 环境准备（首次）

```powershell
cd c:\Users\admin\Desktop\StarsailX
.\setup_build_env.ps1
```

需要：Python 3.10+ 64 位、Inno Setup 6（生成安装包时）。

## 一键打包

```powershell
.\build.ps1
```

仅便携版（不生成安装包）：

```powershell
.\build.ps1 -PortableOnly
```

## 输出

| 产物 | 路径 |
|------|------|
| 便携版 | `release\StarsailX_纯净版\` |
| 安装包 | `release\StarsailX_Setup_2.2.0.exe` |
| 构建日志 | `build.log` |

## 必需资源（仓库内）

- `logo.ico` / `logo.png` — 应用与安装向导图标
- `audio\Starsail.mp3` — 消息提示音
- `audio\video.mp3` — 来电铃声（可选）
- `installer_wizard.bmp` / `installer_wizard_small.bmp` — 安装向导侧边图
- `安装导读.txt` — 安装前中文导语

## 数据目录

运行时数据独立于安装目录，默认 `D:\StarsailX`。  
可通过环境变量 `STARSAILX_DATA_ROOT` 覆盖。

## 独立工程说明

本目录为 StarsailX 独立仓库，不依赖 TeamsX / DDDA 等其他项目路径。
