# Face Alert Skill

> 腾讯 QClaw Skill - 人脸监控警报系统

[![QClaw](https://img.shields.io/badge/platform-QClaw-blue)](https://qclaw.ai)
[![Python](https://img.shields.io/badge/python-3.8+-green)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

## 简介

实时人脸监控警报系统，检测到人脸靠近时自动捕获摄像头照片，并将图片路径返回给 QClaw，由 QClaw 上传云端并返回链接给用户。

## 功能特性

- ✅ 实时人脸监控检测
- ✅ 自动捕获摄像头照片
- ✅ 返回图片路径给 QClaw
- ✅ QClaw 自动上传云端并返回链接
- ✅ 支持命令启动/停止
- ✅ 防抖机制（默认 5 秒）

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### QClaw 使用

在 QClaw 对话界面中发送指令：

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

## 使用示例

### 检测到人脸时的返回

```json
{
  "status": "success",
  "message": "🚨 人脸监控警报\n时间: 2026-04-17 10:30:00\n人脸数量: 1",
  "image_path": "/Users/xxx/FishGuard/screenshots/alert_20260417_103000.png",
  "alert_count": 1,
  "is_monitoring": true
}
```

**QClaw 会自动：**
1. 接收 `image_path`
2. 上传图片到云端
3. 返回云端链接给用户

## 工作流程

```
用户："启动监控" 
  ↓
QClaw 调用 Skill
  ↓
Skill 开始后台监控
  ↓
检测到人脸 → 拍照 → 保存
  ↓
QClaw 轮询检查
  ↓
Skill 返回图片路径
  ↓
QClaw 上传云端 → 返回链接
```

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `threshold` | 15000 | 人脸面积阈值（越大越难触发） |
| `wechat_receiver` | qclaw_butler | 微信接收者 ID |
| `debounce_time` | 5.0 | 防抖时间（秒） |

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

## 常见问题

<details>
<summary>Q: QClaw 如何知道检测到了人脸？</summary>

A: QClaw 会定期调用 `check_alert` action 来检查是否有新的警报。建议轮询间隔 5-10 秒。
</details>

<details>
<summary>Q: 图片如何上传到云端？</summary>

A: Skill 只返回图片的本地路径，QClaw 接收到路径后会自动上传到云端并返回链接。
</details>

<details>
<summary>Q: 如何调整触发灵敏度？</summary>

A: 通过 `threshold` 参数调整。数值越大，需要人脸越近才会触发。
</details>

<details>
<summary>Q: 摄像头无法启动？</summary>

A: 
- **macOS**: 系统偏好设置 → 安全性与隐私 → 摄像头 → 允许终端/Python
- **Linux**: 检查设备 `ls /dev/video*`
</details>

## 开发者

详细的技术实现、API 文档、集成指南请查看 [SKILL.md](SKILL.md)。

## License

MIT License

---

**Made with ❤️ for QClaw**
