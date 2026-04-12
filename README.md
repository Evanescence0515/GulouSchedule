# GulouSchedule（鼓楼课表）

<p align="right">
  <strong>Language:</strong>
  <a href="#gulouschedule鼓楼课表">简体中文</a> |
  <a href="#english-version">English</a>
</p>

> 💡 自动跳转说明：GitHub README 不支持基于浏览器语言的真正“自动重定向”。
> 这里提供了顶部语言导航，点击即可一键跳转到对应语言部分。

---

## 中文版

一个基于 **Kivy** 的课程表应用，主要用于将鼓楼医院相关教学排班整理为更清晰的可视化课表，并支持按周查看、课程详情弹窗、以及从 Seatable 在线导入课表数据。

### ✨ 功能简介

- 按周展示课程表（周一到周日，1~12 节次网格视图）。
- 点击课程格可查看课程详细信息（教师、地点、内容等）。
- 支持从网络（Seatable）导入课程数据并自动按周切分。
- 内置中文字体与配色方案，适配中文教学场景。

### 📁 项目结构

```text
GulouSchedule/
├── README.md
└── GulouClass/
    ├── main.py                  # 应用入口
    ├── src/
    │   ├── screen1.py           # 主课表页（按周显示）
    │   ├── screen2.py           # 工具页（导入入口）
    │   ├── screen3.py           # 网络导入配置页
    │   └── __init__.py          # 全局组件与样式封装
    ├── assets/
    │   ├── conf/                # 课表缓存、颜色配置、分周数据
    │   ├── font/                # 中文字体
    │   └── func/                # 数据导入/解析相关函数
    ├── kvfile/
    └── images/
```

### 🚀 快速开始

#### 1) 环境准备

建议使用 Python 3.8+。

```bash
pip install kivy
```

> 说明：项目中保留了 Excel 导入相关代码（`excel2dict.py`），如需启用可自行补充 `pandas` 等依赖并完善该模块。

#### 2) 运行应用

```bash
python GulouClass/main.py
```

### 🌐 数据导入（Seatable）

应用内路径：**工具 → 从网络导入**。

你需要填写：

1. 课程网站地址（Seatable 外部应用地址）
2. 学校名称（例如：南京大学）
3. 年级/班级关键字（例如：2021临床医学）

导入完成后，程序会：

- 拉取筛选后的课程数据；
- 写入 `assets/conf/internetData*.txt`；
- 计算起始日期并更新缓存；
- 返回主页面显示对应周次的课表。

### 🧠 使用说明

- 主页面左上角 `Weeks` 可切换周次。
- 点击具体课程单元格可查看课程详情。
- 如果周次超出已有数据范围，会显示空白课表。

### ⚠️ 注意事项

- 当前项目是桌面端 Kivy 应用，不是 Web 项目。
- 仓库中包含若干缓存数据文件（`assets/conf`），它们会随着导入操作更新。
- 若网络导入失败，通常与 Seatable 地址不可达、授权获取失败或筛选条件不匹配有关。

---

## English Version

A **Kivy-based** class schedule app for organizing Gulou Hospital-related teaching schedules into a cleaner visual timetable. It supports weekly views, class detail popups, and online import from Seatable.

### ✨ Features

- Weekly timetable view (Monday to Sunday, 12 periods grid).
- Click any class cell to view detailed information (teacher, location, content).
- Import schedule data from Seatable and split data by week automatically.
- Built-in Chinese font and color theme for medical teaching scenarios.

### 📁 Project Structure

```text
GulouSchedule/
├── README.md
└── GulouClass/
    ├── main.py                  # App entry point
    ├── src/
    │   ├── screen1.py           # Main timetable screen
    │   ├── screen2.py           # Tools / import entry
    │   ├── screen3.py           # Online import setup
    │   └── __init__.py          # Shared UI components and styles
    ├── assets/
    │   ├── conf/                # Cached schedule data and config
    │   ├── font/                # Fonts
    │   └── func/                # Data import and parsing helpers
    ├── kvfile/
    └── images/
```

### 🚀 Quick Start

#### 1) Requirements

Python 3.8+ is recommended.

```bash
pip install kivy
```

> Note: The repository still contains legacy Excel import code (`excel2dict.py`). If you want to enable it, add `pandas` and complete that module.

#### 2) Run the app

```bash
python GulouClass/main.py
```

### 🌐 Seatable Import Flow

In app: **Tools → Import from Internet**.

Input fields:

1. Seatable external app URL
2. University name (e.g., Nanjing University)
3. Grade/class keyword (e.g., `2021临床医学`)

After importing, the app will:

- fetch filtered schedule records,
- write data to `assets/conf/internetData*.txt`,
- compute start date and refresh local cache,
- return to the main screen with the proper week displayed.

### ⚠️ Notes

- This is a desktop Kivy app, not a web app.
- Files under `assets/conf` are runtime cache/config files and may change after import.
- Import failures are usually caused by inaccessible Seatable URL, authorization issues, or unmatched filter keywords.

### 📄 License

No explicit open-source license is included yet. Consider adding a `LICENSE` file (e.g., MIT / Apache-2.0) before public distribution.
