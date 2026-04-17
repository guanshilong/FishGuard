---
id: face-alert
name: Face Alert Skill
version: 1.0.0
author: FishGuard Team
platforms:
  - qclaw
  - openclaw
description: 人脸监控警报系统 - 检测到人脸靠近时捕获摄像头照片并发送通知
triggers:
  - "/face-alert"
  - "启动人脸监控"
  - "人脸监控"
  - "启动监控"
keywords:
  - 人脸检测
  - 监控
  - 摄像头
  - 人脸警报
  - face detection
tags:
  - face-detection
  - camera-capture
  - security-alert
  - monitoring
commands:
  - name: start
    description: 启动人脸监控
    triggers:
      - "启动人脸监控"
      - "启动监控"
  - name: stop
    description: 停止人脸监控
    triggers:
      - "停止人脸监控"
      - "停止监控"
  - name: status
    description: 查看监控状态
    triggers:
      - "查看监控状态"
      - "监控状态"
  - name: check_alert
    description: 检查是否有新警报
    triggers:
      - "检查警报"
      - "有没有检测到人脸"
      - "人脸警报"
---

# Face Alert Skill

> 人脸监控警报系统 - 实时检测人脸，自动捕获照片，返回图片路径

## 功能特性

- ✅ **实时人脸监控** - 持续检测摄像头画面中的人脸
- ✅ **自动捕获照片** - 检测到人脸时自动拍照并标注
- ✅ **图片路径返回** - 返回图片绝对路径给 QClaw，由 QClaw 上传云端
- ✅ **命令控制** - 支持启动、停止、状态查询
- ✅ **防抖机制** - 避免频繁触发（默认 5 秒）
- ✅ **可配置阈值** - 调整人脸面积触发阈值

## 使用示例

### 示例 1：启动监控

**用户输入：**
```
启动人脸监控
```

**Skill 返回：**
```
✅ 人脸监控已启动，正在后台运行
人脸面积阈值: 15000
监控中...
```

### 示例 2：检测到人脸

**用户输入：**
```
有没有检测到人脸？
```

**Skill 返回：**
```
🚨 人脸监控警报
时间: 2026-04-17 10:30:00
人脸数量: 1
最大面积: 18500

图片已保存，QClaw 正在上传到云端...
```

### 示例 3：查看状态

**用户输入：**
```
查看监控状态
```

**Skill 返回：**
```
📊 人脸监控状态
状态: 运行中
警报次数: 3
阈值: 15000
```

### 示例 4：停止监控

**用户输入：**
```
停止人脸监控
```

**Skill 返回：**
```
✅ 人脸监控已停止
累计警报次数: 3
```

## 使用方式

### 1. 启动监控

```
启动人脸监控
```

或指定参数：

```
启动监控，阈值 15000
```

### 2. 查看状态

```
查看监控状态
```

### 3. 检查警报

```
检查人脸警报
```

或

```
有没有检测到人脸？
```

### 4. 停止监控

```
停止人脸监控
```

## API 接口

### Actions

| Action | 说明 | 使用场景 |
|--------|------|---------|
| `start` | 启动人脸监控 | 用户说"启动监控" |
| `stop` | 停止监控 | 用户说"停止监控" |
| `status` | 查看监控状态 | 用户说"查看状态" |
| `check_alert` | 检查是否有新警报 | QClaw 定期轮询或用户询问 |

### 输入参数

```json
{
  "action": "start | stop | status | check_alert",
  "threshold": 15000,
  "wechat_receiver": "qclaw_butler"
}
```

### 输出格式

#### 启动监控

```json
{
  "status": "success",
  "message": "✅ 人脸监控已启动，正在后台运行",
  "is_monitoring": true,
  "alert_count": 0
}
```

#### 检测到人脸时

```json
{
  "status": "success",
  "message": "🚨 人脸监控警报\n时间: 2026-04-17 10:30:00\n人脸数量: 1\n最大面积: 18500",
  "image_path": "/Users/xxx/FishGuard/screenshots/alert_20260417_103000.png",
  "alert_count": 1,
  "is_monitoring": true,
  "timestamp": "2026-04-17 10:30:00"
}
```

**关键字段：**
- `image_path`: 图片的绝对路径，QClaw 会自动上传到云端并返回链接

#### 无警报时

```json
{
  "status": "no_alert",
  "message": "暂无警报",
  "is_monitoring": true,
  "alert_count": 0
}
```

## 工作流程

```
用户对话："启动监控"
    ↓
QClaw 调用: action=start
    ↓
Skill 返回："监控已启动"
    ↓
Skill 后台持续检测人脸
    ↓
检测到人脸 → 捕获照片 → 保存图片
    ↓
QClaw 轮询: action=check_alert
    ↓
Skill 返回图片路径: image_path
    ↓
QClaw 上传图片到云端
    ↓
QClaw 返回云端链接给用户
```

## 配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `threshold` | int | 15000 | 人脸面积阈值（越大越难触发） |
| `wechat_receiver` | string | qclaw_butler | 微信接收者 ID |
| `debounce_time` | float | 5.0 | 防抖时间（秒） |
| `check_interval` | float | 0.1 | 检测间隔（秒） |

## 技术实现

### 核心文件

- **main.py** - Skill 主程序，包含人脸检测、图片捕获、状态管理
- **cli.py** - 命令行工具，用于独立测试和调试
- **requirements.txt** - Python 依赖包
- **screenshots/** - 图片保存目录

### 人脸检测

使用 OpenCV 的 Haar Cascade 分类器进行人脸检测：

```python
# 加载预训练模型
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# 检测人脸
faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(30, 30)
)
```

### 图片捕获

检测到人脸后，自动捕获并标注：

```python
# 绘制人脸框
cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

# 添加面积标签
cv2.putText(frame, f"Area: {area}", (x, y-10), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

# 保存图片
cv2.imwrite(filepath, frame)
```

## QClaw 集成要点

### 1. 轮询机制

QClaw 需要定期调用 `check_alert` 来检查是否有新的警报：

```python
# QClaw 可以每 5-10 秒调用一次
result = run({"action": "check_alert"})

if result["status"] == "success" and "image_path" in result:
    image_path = result["image_path"]
    # QClaw 自动上传图片到云端
    # 返回云端链接给用户
```

### 2. 图片处理流程

```
Skill 返回图片路径 → QClaw 读取图片 → 上传云端 → 返回链接
```

### 3. 状态管理

Skill 使用单例模式管理监控状态：

```python
# 全局监控实例
_skill_instance = None

def run(input_data):
    global _skill_instance
    if _skill_instance is None:
        _skill_instance = FaceAlertSkill()
    return _skill_instance.run(input_data)
```

## 测试方法

### 命令行测试

```bash
# 测试功能
python3 cli.py test

# 启动监控
python3 cli.py start --threshold 15000

# 查看状态
python3 cli.py status

# 停止监控
python3 cli.py stop
```

### Python API 测试

```python
from main import run

# 启动监控
result = run({"action": "start", "threshold": 15000})
print(result["message"])

# 检查警报
result = run({"action": "check_alert"})
if "image_path" in result:
    print(f"检测到人脸！图片: {result['image_path']}")

# 停止监控
result = run({"action": "stop"})
```

## 常见问题

**Q: QClaw 如何知道检测到了人脸？**

A: QClaw 需要定期调用 `check_alert` action 来检查。建议每 5-10 秒轮询一次。

**Q: 图片如何上传到云端？**

A: Skill 只返回图片的本地路径，QClaw 接收到路径后会自动上传到云端并返回链接给用户。

**Q: 阈值如何调整？**

A: 通过 `threshold` 参数调整。数值越大，需要人脸越近才会触发。默认 15000。

**Q: 如何避免频繁触发？**

A: 默认有 5 秒防抖机制，可通过 `debounce_time` 参数调整。

**Q: 摄像头无法启动？**

A: 
- macOS: 系统偏好设置 → 安全性与隐私 → 摄像头 → 允许终端/Python
- Linux: 检查设备 `ls /dev/video*`

## 依赖说明

```
opencv-python>=4.5.0
requests>=2.25.0
```

## License

MIT License

---

**使用愉快！实时监控，安全可靠！📸🔒**
