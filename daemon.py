#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Face Alert Daemon - 后台守护进程
macOS 要求摄像头在主线程中初始化，因此作为独立进程运行
"""

import os
import sys
import json
import signal
import time

# 确保在正确的目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

from main import FaceAlertSkill

# PID 文件路径
PID_FILE = os.path.join(SCRIPT_DIR, ".face-alert.pid")
STATUS_FILE = os.path.join(SCRIPT_DIR, ".face-alert-status.json")

# 全局 skill 实例
skill = None


def write_pid():
    """写入 PID 文件"""
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


def remove_pid():
    """删除 PID 文件"""
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def update_status(status_dict):
    """更新状态文件"""
    with open(STATUS_FILE, "w") as f:
        json.dump(status_dict, f, ensure_ascii=False)


def clear_status():
    """清除状态文件"""
    if os.path.exists(STATUS_FILE):
        os.remove(STATUS_FILE)


def signal_handler(signum, frame):
    """信号处理：优雅停止"""
    global skill
    print(f"\n🛑 收到信号 {signum}，正在停止监控...")
    if skill:
        skill.is_monitoring = False
    remove_pid()
    clear_status()
    sys.exit(0)


def is_already_running():
    """检查是否已在运行"""
    if not os.path.exists(PID_FILE):
        return False
    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
        # 检查进程是否存在
        os.kill(pid, 0)
        return True
    except (ValueError, ProcessLookupError, PermissionError):
        # PID 文件过期，清理
        remove_pid()
        return False


def main():
    global skill

    # 检查是否已在运行
    if is_already_running():
        print("❌ 人脸监控已在运行中")
        sys.exit(1)

    # 注册信号处理
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # 写入 PID
    write_pid()

    print("=" * 60)
    print("Face Alert Daemon - 人脸监控守护进程")
    print("=" * 60)
    print(f"PID: {os.getpid()}")
    print()

    # 创建 Skill 实例
    skill = FaceAlertSkill({
        "min_face_area": 15000,
        "screenshot_dir": "./screenshots",
        "qclaw_api": "http://localhost:8080/api/send_message",
        "wechat_receiver": "qclaw_butler"
    })

    # 更新状态：启动中
    update_status({
        "is_monitoring": True,
        "alert_count": 0,
        "status": "starting",
        "pid": os.getpid()
    })

    # 启动摄像头并运行监控循环（在主线程中）
    print("🚀 启动摄像头...")
    if not skill.detector.start():
        print("❌ 无法启动摄像头，请检查权限")
        update_status({
            "is_monitoring": False,
            "alert_count": 0,
            "status": "camera_failed",
            "pid": os.getpid()
        })
        remove_pid()
        sys.exit(1)

    print("✅ 摄像头已打开，开始监控")
    update_status({
        "is_monitoring": True,
        "alert_count": 0,
        "status": "running",
        "pid": os.getpid()
    })

    skill.is_monitoring = True

    # 监控循环
    try:
        while skill.is_monitoring:
            faces, frame = skill.detector.detect_faces()

            if skill.should_alert(faces) and frame is not None:
                result = skill.trigger_alert(faces, frame)
                print(f"🚨 警报触发: {result}")
                update_status({
                    "is_monitoring": True,
                    "alert_count": skill.alert_count,
                    "status": "running",
                    "last_alert_time": skill.last_alert_time,
                    "pid": os.getpid()
                })

            time.sleep(skill.config.config["check_interval"])
    except KeyboardInterrupt:
        print("\n🛑 收到中断信号")
    finally:
        skill.detector.stop()
        skill.is_monitoring = False
        print("✅ 人脸监控已停止")
        remove_pid()
        clear_status()


if __name__ == "__main__":
    main()
