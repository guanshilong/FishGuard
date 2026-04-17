# Face Alert Skill

> 腾讯 QClaw Skill - 人脸监控警报系统

## 功能特性

- ✅ 实时人脸监控检测
- ✅ 自动捕获摄像头照片
- ✅ 返回图片路径给 QClaw
- ✅ QClaw 自动上传云端并返回链接
- ✅ 支持命令启动/停止
- ✅ 防抖机制（默认 5 秒）

## QClaw 使用方式

### 1. 添加 Skill 到 QClaw

将整个 `FishGuard` 文件夹添加到 QClaw 的 Skills 目录中。

### 2. 通过对话控制

在 QClaw 对话界面中发送以下指令：

**启动监控：**
```
启动人脸监控
```
或
```
启动监控，阈值 15000
```

**查看状态：**
```
查看监控状态
```

**检查警报：**
```
检查人脸警报
```
或
```
有没有检测到人脸？
```

**停止监控：**
```
停止人脸监控
```

### 3. 自动上传云端

当检测到人脸时，Skill 会返回图片路径给 QClaw，QClaw 会自动：
1. 接收图片路径
2. 上传到云端存储
3. 返回云端链接给用户

## API 接口

### 输入参数

```json
{
  "action": "start | stop | status | check_alert",
  "threshold": 15000,  // 可选，人脸面积阈值
  "wechat_receiver": "qclaw_butler"  // 可选，微信接收者
}
```

### Actions 说明

| Action | 说明 | 使用场景 |
|--------|------|---------|
| `start` | 启动人脸监控 | 用户说"启动监控" |
| `stop` | 停止监控 | 用户说"停止监控" |
| `status` | 查看监控状态 | 用户说"查看状态" |
| `check_alert` | 检查是否有新警报 | QClaw 定期轮询或用户询问 |

### 输出格式

#### 启动/停止监控
```json
{
  "status": "success",
  "message": "✅ 人脸监控已启动，正在后台运行",
  "is_monitoring": true,
  "alert_count": 0
}
```

#### 检测到人脸时（check_alert 返回）
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
- `image_path`: 图片的绝对路径，QClaw 会自动上传并返回云端链接

## 工作流程

```
用户对话："启动监控"
    ↓
QClaw 调用 Skill: action=start
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

## QClaw 集成要点

### 1. 轮询机制

QClaw 需要定期调用 `check_alert` 来检查是否有新的警报：

```python
# QClaw 可以每 5 秒调用一次
result = run({"action": "check_alert"})

if result["status"] == "success" and "image_path" in result:
    image_path = result["image_path"]
    # 上传图片到云端
    # 返回云端链接给用户
```

### 2. 图片处理

当 `check_alert` 返回 `image_path` 时：

```python
# QClaw 内部处理
image_path = result["image_path"]

# 1. 读取图片
with open(image_path, 'rb') as f:
    image_data = f.read()

# 2. 上传到云端（QClaw 自动处理）
cloud_url = upload_to_cloud(image_data)

# 3. 返回给用户
return f"检测到人脸！照片已上传: {cloud_url}"
```

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `threshold` | 15000 | 人脸面积阈值（越大越难触发） |
| `wechat_receiver` | qclaw_butler | 微信接收者 ID |
| `debounce_time` | 5.0 | 防抖时间（秒） |
| `check_interval` | 0.1 | 检测间隔（秒） |

## 文件结构

```
FishGuard/
├── skill.yaml          # Skill 配置
├── main.py             # Skill 主程序
├── cli.py              # 命令行工具
├── requirements.txt    # 依赖包
├── README.md           # 说明文档
└── screenshots/        # 图片保存目录
```

## 测试

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

## 常见问题

**Q: QClaw 如何知道检测到了人脸？**

A: QClaw 需要定期调用 `check_alert` action 来检查。建议每 5-10 秒轮询一次。

**Q: 图片如何上传到云端？**

A: Skill 只返回图片的本地路径，QClaw 接收到路径后会自动上传到云端并返回链接。

**Q: 阈值如何调整？**

A: 通过 `threshold` 参数调整。数值越大，需要人脸越近才会触发。

**Q: 如何避免频繁触发？**

A: 默认有 5 秒防抖机制，可通过配置文件调整。

## License

MIT License
