# StarsailX 运行环境

## 用户运行（安装包 / 便携版）

- Windows 10 / 11 64 位
- Microsoft Edge WebView2 Runtime（通常已随系统安装）

无需安装 Python。

## 开发者源码运行

```powershell
pip install PyQt6 qtwebview2 qtpy pythonnet pywin32 certifi chardet
python -m starsailx
```

## 数据目录

默认：`D:\StarsailX`

环境变量（推荐）：

- `STARSAILX_DATA_ROOT` — 自定义数据根目录
- `STARSAILX_ENGINE` — 页面引擎，默认 `webview2`

仍兼容旧变量 `TEAMSX_DATA_ROOT` / `TEAMSX_ENGINE`。

## 打包

见 `BUILD.md`。本目录为独立工程，不依赖其他项目路径。
