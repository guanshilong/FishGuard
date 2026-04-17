# Face Alert Skill

> 腾讯 QClaw Skill - 人脸监控警报系统

[![QClaw](https://img.shields.io/badge/platform-QClaw-blue)](https://qclaw.ai)
[![Python](https://img.shields.io/badge/python-3.8+-green)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

## 简介

实时人脸监控警报系统，检测到人脸靠近时自动捕获摄像头照片，并将图片路径返回给 QClaw，由 QClaw 上传云端并返回链接给用户。

## 快速开始

### 安装 Skill

1. **将项目添加到 QClaw Skills 目录：**
   ```bash
   # 复制项目到 QClaw Skills 目录
   cp -r /Users/guanshilong/app/ai/python/FishGuard ~/.qclaw/skills/face-alert
   ```

2. **安装 Python 依赖：**
   ```bash
   pip install -r requirements.txt
   ```

### 使用方式

在 QClaw 对话界面中，使用以下触发词：

#### 方式 1：使用触发词

```
/face-alert
```

#### 方式 2：自然语言

**启动监控：**
```
启动人脸监控
```

**查看状态：**
```
查看监控状态
```

**检查警报：**
```
有没有检测到人脸？
```

**停止监控：**
```
停止人脸监控
```

## 功能特性

- ✅ 实时人脸监控检测
- ✅ 自动捕获摄像头照片
- ✅ 返回图片路径给 QClaw
- ✅ QClaw 自动上传云端并返回链接
- ✅ 支持命令启动/停止
- ✅ 防抖机制（默认 5 秒）

## 使用示例

### 示例 1：启动监控

```
用户: 启动人脸监控
QClaw: ✅ 人脸监控已启动，正在后台运行
       人脸面积阈值: 15000
       监控中...
```

### 示例 2：检测到人脸

```
用户: 有没有检测到人脸？
QClaw: 🚨 人脸监控警报
       时间: 2026-04-17 10:30:00
       人脸数量: 1
       最大面积: 18500
       
       图片已上传: https://cloud.example.com/image.png
```

### 示例 3：查看状态

```
用户: 查看监控状态
QClaw: 📊 人脸监控状态
       状态: 运行中
       警报次数: 3
       阈值: 15000
```

## 触发词列表

| 触发词 | 说明 |
|--------|------|
| `/face-alert` | 主触发词 |
| `启动人脸监控` | 启动监控 |
| `启动监控` | 启动监控（简写） |
| `停止人脸监控` | 停止监控 |
| `停止监控` | 停止监控（简写） |
| `查看监控状态` | 查看状态 |
| `监控状态` | 查看状态（简写） |
| `有没有检测到人脸？` | 检查警报 |
| `检查警报` | 检查警报 |
| `人脸警报` | 检查警报 |

## 常见问题

<details>
<summary>Q: 为什么 QClaw 没有识别到这个 Skill？</summary>

A: 请检查：
1. Skill 是否正确安装到 `~/.qclaw/skills/` 目录
2. 文件夹名称是否正确（建议使用 `face-alert`）
3. 是否包含 `SKILL.md` 文件
4. 是否安装了 Python 依赖
</details>

<details>
<summary>Q: 如何测试 Skill 是否正常工作？</summary>

A: 使用命令行工具测试：
```bash
python3 cli.py test
python3 cli.py start
python3 cli.py status
```
</details>

<details>
<summary>Q: 图片如何上传到云端？</summary>

A: Skill 只返回图片的本地路径，QClaw 接收到路径后会自动上传到云端并返回链接。
</details>

<details>
<summary>Q: 摄像头无法启动？</summary>

A: 
- **macOS**: 系统偏好设置 → 安全性与隐私 → 摄像头 → 允许终端/Python
- **Linux**: 检查设备 `ls /dev/video*`
</details>

## 项目结构

```
FishGuard/
├── SKILL.md          # Skill 配置文件（QClaw 识别）
├── main.py           # Skill 主程序
├── cli.py            # 命令行工具
├── requirements.txt  # 依赖包
├── README.md         # 项目说明
└── screenshots/      # 图片保存目录
```

## 技术栈

- **OpenCV** - 人脸检测
- **Python** - 后端逻辑
- **QClaw** - 云端上传和用户交互

## 开发者

详细的技术实现、API 文档、集成指南请查看 [SKILL.md](SKILL.md)。

## License

MIT License

---

**Made with ❤️ for QClaw**
