---
name: face-alert
description: "人脸监控警报系统 - 实时检测人脸，自动捕获照片并发送通知。支持启动、停止、状态查询和警报检查。"
version: "1.0.0"
user-invocable: true
---

# Face Alert Skill

> 人脸监控警报系统 - 实时检测人脸，自动捕获照片并发送通知

## 触发条件

当用户说以下任意内容时启动：
- `/face-alert`
- "启动人脸监控"
- "人脸监控"
- "启动监控"
- "停止人脸监控"
- "查看监控状态"
- "有没有检测到人脸"

---

## 功能特性

- ✅ **实时人脸监控** - 持续检测摄像头画面中的人脸
- ✅ **自动捕获照片** - 检测到人脸时自动拍照并标注
- ✅ **图片路径返回** - 返回图片绝对路径，由 QClaw 上传云端
- ✅ **命令控制** - 支持启动、停止、状态查询、警报检查
- ✅ **防抖机制** - 避免频繁触发（默认 5 秒）
- ✅ **可配置阈值** - 调整人脸面积触发阈值

---

## 使用方式

### 1. 启动监控

**用户说：**
- "启动人脸监控"
- "启动监控"

**Skill 行为：**
调用 `main.py` 启动后台监控线程，返回启动成功消息。

**返回格式：**
```json
{
  "status": "success",
  "message": "✅ 人脸监控已启动，正在后台运行",
  "is_monitoring": true,
  "config": {
    "threshold": 15000,
    "screenshot_dir": "/path/to/screenshots"
  }
}
```

### 2. 停止监控

**用户说：**
- "停止人脸监控"
- "停止监控"

**Skill 行为：**
停止后台监控线程，返回停止成功消息。

**返回格式：**
```json
{
  "status": "success",
  "message": "✅ 人脸监控已停止",
  "is_monitoring": false,
  "alert_count": 3
}
```

### 3. 查看状态

**用户说：**
- "查看监控状态"
- "监控状态"

**Skill 行为：**
返回当前监控状态和警报次数。

**返回格式：**
```json
{
  "status": "success",
  "message": "人脸监控状态: 运行中",
  "is_monitoring": true,
  "alert_count": 3,
  "last_alert_time": "2026-04-17 10:30:00",
  "config": {
    "threshold": 15000,
    "screenshot_dir": "/path/to/screenshots"
  }
}
```

### 4. 检查警报

**用户说：**
- "有没有检测到人脸？"
- "检查警报"
- "人脸警报"

**Skill 行为：**
返回最新的警报结果（如果有），包括图片路径。

**返回格式（有警报）：**
```json
{
  "status": "success",
  "message": "🚨 人脸监控警报\n时间: 2026-04-17 10:30:00\n人脸数量: 1",
  "image_path": "/absolute/path/to/screenshot.png",
  "screenshot_path": "/absolute/path/to/screenshot.png",
  "alert_count": 1,
  "timestamp": "2026-04-17 10:30:00"
}
```

**返回格式（无警报）：**
```json
{
  "status": "no_alert",
  "message": "暂无警报",
  "is_monitoring": true,
  "alert_count": 0
}
```

---

## 技术实现

### 调用方式

Skill 通过 Python 模块调用：

```python
from main import run

# 启动监控
result = run({'action': 'start', 'threshold': 15000})

# 停止监控
result = run({'action': 'stop'})

# 查看状态
result = run({'action': 'status'})

# 检查警报
result = run({'action': 'check_alert'})
```

### 监控流程

1. **启动监控** (`action: start`)
   - 初始化摄像头（macOS 使用 AVFoundation）
   - 启动后台监控线程
   - 持续检测人脸（使用 OpenCV CascadeClassifier）

2. **人脸检测**
   - 检测画面中的人脸
   - 计算人脸面积
   - 当面积超过阈值（默认 15000）时触发警报

3. **警报触发**
   - 捕获当前帧并保存到 `screenshots/` 目录
   - 在图片上标注人脸位置
   - 返回图片绝对路径给 QClaw

4. **图片处理**
   - QClaw 接收到 `image_path` 后
   - 自动上传到云端
   - 返回云端链接给用户

### 防抖机制

- 默认 5 秒内不重复触发
- 可通过 `alert_cooldown` 参数调整

### 配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `action` | string | "start" | 操作类型：start/stop/status/check_alert |
| `threshold` | int | 15000 | 人脸面积阈值（像素） |
| `alert_cooldown` | int | 5 | 警报冷却时间（秒） |

---

## 文件结构

```
FishGuard/
├── SKILL.md          # Skill 配置文件（Markdown 格式）
├── main.py           # Skill 主程序
├── cli.py            # 命令行工具（可选）
├── requirements.txt  # Python 依赖
└── screenshots/      # 图片保存目录
```

---

## 依赖

- `opencv-python` - 人脸检测和图片处理
- `numpy` - 数值计算
- `pyyaml` - 配置文件解析

---

## 示例对话

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
       
       图片已保存，QClaw 正在上传到云端...
       [图片链接: https://cloud.example.com/image.png]
```

### 示例 3：查看状态

```
用户: 查看监控状态
QClaw: 📊 人脸监控状态
       状态: 运行中
       警报次数: 3
       阈值: 15000
```

### 示例 4：停止监控

```
用户: 停止人脸监控
QClaw: ✅ 人脸监控已停止
       累计警报次数: 3
```

---

## 注意事项

1. **摄像头权限** - 首次使用需要授权摄像头访问权限
2. **后台运行** - 监控在后台线程运行，不影响其他操作
3. **图片存储** - 图片保存在 `screenshots/` 目录，可手动清理
4. **云端上传** - 图片路径由 QClaw 自动上传，无需额外配置

---

## 快速开始

1. 将 `FishGuard` 文件夹放到 QClaw 的 Skills 目录
2. 在 QClaw 中输入 "启动人脸监控"
3. 开始使用！

---

## 技术支持

- **作者**: FishGuard Team
- **版本**: 1.0.0
- **GitHub**: [项目地址]
