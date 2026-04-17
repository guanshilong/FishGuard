---
name: face-alert
description: "人脸监控警报系统 - 实时检测人脸，自动捕获照片并上传到云端。支持启动、停止、状态查询和警报检查。"
version: "1.0.0"
user-invocable: true
---

# Face Alert Skill

> 人脸监控警报系统 - 实时检测人脸，自动捕获照片并上传到云端

## ⚠️ 重要说明

**摄像头权限：**
- 首次使用需要在 Terminal 中手动执行，触发 macOS 摄像头授权
- **授权成功后，QClaw 可以直接通过 Bash 执行启动命令**
- 已授权用户可以直接语音控制

**图片上传机制：**
- 检测到人脸后，返回图片绝对路径
- **QClaw 自动上传图片到云端**
- 返回云端链接给用户

---

## 📋 使用指南

### 首次使用（需要授权）

**如果你从未授权过 Terminal 访问摄像头：**

1. **打开终端（Terminal）**

2. **运行启动命令**：
   ```bash
   cd ~/.qclaw/skills/FishGuard && python3 main.py --action start --daemon
   ```

3. **授权摄像头**：
   - macOS 会弹出授权窗口："Terminal" 想要访问摄像头
   - 点击「允许」

4. **确认启动成功**：
   ```
   ✅ 人脸监控已启动，正在后台运行
   ```

5. **后续使用**：
   - 授权成功后，直接对 QClaw 说 "启动人脸监控" 即可
   - QClaw 会自动执行启动命令

### 已授权用户

**如果你已经授权过 Terminal 访问摄像头：**

直接对 QClaw 说：
- **"启动人脸监控"** - QClaw 自动启动监控
- **"有没有检测到人脸？"** - 获取最新照片
- **"查看监控状态"** - 查看当前状态
- **"停止人脸监控"** - 停止监控

---

## 触发条件

当用户说以下任意内容时触发：
- `/face-alert`
- "启动人脸监控"
- "人脸监控"
- "启动监控"
- "停止人脸监控"
- "查看监控状态"
- "有没有检测到人脸"

---

## 使用方式

### 1. 启动监控

**用户说：** "启动人脸监控"

**QClaw 执行：**

**Step 1**: 检查监控是否已在运行

```bash
cd ~/.qclaw/skills/FishGuard
python3 main.py --action status
```

**Step 2**: 根据状态返回结果

**情况 A：监控已在运行**

```
✅ 人脸监控已在运行中
警报次数: 3
```

**情况 B：监控未运行（已授权用户）**

**QClaw 直接执行启动命令：**

```bash
cd ~/.qclaw/skills/FishGuard
python3 main.py --action start --daemon
```

**返回结果：**

```json
{
  "status": "success",
  "message": "✅ 人脸监控已启动，正在后台运行",
  "pid": 12345
}
```

**QClaw 回复：**

```
✅ 人脸监控已启动，正在后台运行
人脸面积阈值: 15000
监控中...
```

**情况 C：启动失败（需要授权）**

如果返回失败或提示需要摄像头权限：

```
⚠️ 启动失败，需要摄像头权限

请在 **终端（Terminal）** 中运行以下命令授权：

cd ~/.qclaw/skills/FishGuard && python3 main.py --action start --daemon

首次运行时会弹出授权窗口，请点击「允许」授权摄像头。

授权成功后，以后就可以直接说 "启动人脸监控" 了。
```

---

### 2. 检查警报（获取最新照片）

**用户说：** "有没有检测到人脸？"

**QClaw 执行：**

**Step 1**: 检查监控是否在运行

```bash
cd ~/.qclaw/skills/FishGuard
python3 main.py --action status
```

**Step 2**: 如果未运行，提示用户先启动

**QClaw 回复：**

```
⚠️ 人脸监控未启动

请先在 Terminal 中运行：
cd ~/.qclaw/skills/FishGuard && python3 main.py --action start --daemon
```

**Step 3**: 如果已在运行，获取最新照片

```bash
cd ~/.qclaw/skills/FishGuard
python3 main.py --action get_latest_photo
```

**返回结果（有照片）：**

```json
{
  "status": "success",
  "message": "最新照片: 2026-04-17 16:18:15",
  "image_path": "/Users/.../screenshots/alert_20260417_161815.png",
  "photo_time": "2026-04-17 16:18:15"
}
```

**QClaw 自动上传图片到云端**

**QClaw 回复：**

```
🚨 人脸监控警报
时间: 2026-04-17 16:18:15

📸 照片已上传到云端：
https://cloud.qclaw.com/photos/abc123.png
```

**返回结果（无照片）：**

```json
{
  "status": "no_photo",
  "message": "暂无照片"
}
```

**QClaw 回复：**

```
暂无检测到人脸照片
监控正在运行中...
```

---

### 3. 查看监控状态

**用户说：** "查看监控状态"

**QClaw 执行：**

```bash
cd ~/.qclaw/skills/FishGuard
python3 main.py --action status
```

**返回结果（运行中）：**

```json
{
  "status": "success",
  "message": "人脸监控状态: 运行中",
  "is_monitoring": true,
  "alert_count": 3
}
```

**QClaw 回复：**

```
📊 人脸监控状态
状态: 运行中
警报次数: 3
```

**返回结果（未运行）：**

```json
{
  "status": "success",
  "message": "人脸监控状态: 已停止",
  "is_monitoring": false
}
```

**QClaw 回复：**

```
📊 人脸监控状态
状态: 已停止

如需启动，请在 Terminal 中运行：
cd ~/.qclaw/skills/FishGuard && python3 main.py --action start --daemon
```

---

### 4. 停止监控

**用户说：** "停止人脸监控"

**QClaw 执行：**

```bash
cd ~/.qclaw/skills/FishGuard
python3 main.py --action stop
```

**返回结果：**

```json
{
  "status": "success",
  "message": "✅ 人脸监控已停止"
}
```

**QClaw 回复：**

```
✅ 人脸监控已停止
```

---

## 命令行参数说明

### 启动监控（后台运行）

```bash
python3 main.py --action start --daemon
```

- `--action start` - 启动监控
- `--daemon` - 后台运行模式
- `--threshold 15000` - 可选，人脸面积阈值

### 停止监控

```bash
python3 main.py --action stop
```

### 查看状态

```bash
python3 main.py --action status
```

### 获取最新照片

```bash
python3 main.py --action get_latest_photo
```

返回 JSON 格式的图片路径，QClaw 自动上传到云端。

---

## 文件结构

```
~/.qclaw/skills/FishGuard/
├── SKILL.md          # Skill 配置文件
├── main.py           # 主程序（支持命令行）
├── daemon.py         # 后台守护进程
├── cli.py            # 命令行工具
├── requirements.txt  # Python 依赖
├── README.md         # 文档
└── screenshots/      # 图片保存目录
    ├── alert_20260417_161800.png
    ├── alert_20260417_161805.png
    └── ...
```

---

## 首次使用

安装 Python 依赖：

```bash
cd ~/.qclaw/skills/FishGuard
pip3 install -r requirements.txt
```

---

## 示例对话

### 示例 1：启动监控（已授权用户）

```
用户: 启动人脸监控
QClaw: 正在启动人脸监控...
       ✅ 人脸监控已启动，正在后台运行
       人脸面积阈值: 15000
       监控中...
```

### 示例 2：监控已在运行

```
用户: 启动人脸监控
QClaw: ✅ 人脸监控已在运行中
       警报次数: 3
```

### 示例 3：检测到人脸

```
用户: 有没有检测到人脸？
QClaw: 正在检查最新警报...
       
       🚨 人脸监控警报
       时间: 2026-04-17 16:18:15
       
       📸 照片已上传到云端：
       https://cloud.qclaw.com/photos/abc123.png
```

### 示例 4：查看状态

```
用户: 查看监控状态
QClaw: 📊 人脸监控状态
       状态: 运行中
       警报次数: 3
```

### 示例 5：停止监控

```
用户: 停止人脸监控
QClaw: ✅ 人脸监控已停止
```

### 示例 6：首次使用（需要授权）

```
用户: 启动人脸监控
QClaw: ⚠️ 启动失败，需要摄像头权限
       
       请在 **终端（Terminal）** 中运行以下命令授权：
       
       cd ~/.qclaw/skills/FishGuard && python3 main.py --action start --daemon
       
       首次运行时会弹出授权窗口，请点击「允许」授权摄像头。
       
       授权成功后，以后就可以直接说 "启动人脸监控" 了。
```

---

## 注意事项

1. **摄像头权限** - 首次启动时，macOS 会弹出授权窗口，请允许 Terminal 访问摄像头
2. **后台运行** - 使用 `--daemon` 参数后台运行，不影响其他操作
3. **图片存储** - 图片保存在 `screenshots/` 目录，可手动清理
4. **云端上传** - QClaw 自动上传图片，无需额外配置

---

## 快速开始

### 1. 安装依赖

```bash
cd ~/.qclaw/skills/FishGuard
pip3 install -r requirements.txt
```

### 2. 授权摄像头（仅首次）

如果你从未授权过 Terminal 访问摄像头：

```bash
cd ~/.qclaw/skills/FishGuard && python3 main.py --action start --daemon
```

点击「允许」授权摄像头访问。

### 3. 语音控制

授权后，直接对 QClaw 说：

- **"启动人脸监控"** - 启动监控
- **"有没有检测到人脸？"** - 获取最新照片
- **"查看监控状态"** - 查看状态
- **"停止人脸监控"** - 停止监控

---

## 技术支持

- **作者**: FishGuard Team
- **版本**: 1.0.0
- **关键特性**: Terminal 执行 + 云端上传 + 命令行控制
