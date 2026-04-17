#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Face Alert Skill - 命令行工具
通过命令行启动/停止人脸监控

Usage:
    python cli.py start [--threshold 15000] [--receiver qclaw_butler]
    python cli.py stop
    python cli.py status
    python cli.py test
"""

import sys
import os
import json
import argparse

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run as skill_run, FaceAlertSkill


def print_json(data):
    """美化输出 JSON"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_start(args):
    """启动监控"""
    print("🚀 启动人脸监控...")
    
    result = skill_run({
        "action": "start",
        "threshold": args.threshold,
        "wechat_receiver": args.receiver
    })
    
    print_json(result)
    
    if result["status"] == "success":
        print("\n✅ 监控已启动！")
        print(f"   人脸面积阈值: {args.threshold}")
        print(f"   微信接收者: {args.receiver}")
        print("\n   检测到人脸靠近时将：")
        print("   1. 捕获摄像头照片")
        print("   2. 发送微信通知")
        print("   3. 返回图片路径给 QClaw")
        print("\n   使用以下命令停止监控：")
        print("   python cli.py stop")
    
    return result["status"] == "success"


def cmd_stop(args):
    """停止监控"""
    print("🛑 停止人脸监控...")
    
    result = skill_run({"action": "stop"})
    print_json(result)
    
    if result["status"] == "success":
        print(f"\n✅ 监控已停止！累计触发警报: {result['alert_count']} 次")
    
    return result["status"] == "success"


def cmd_status(args):
    """查看状态"""
    print("📊 查看监控状态...")
    
    result = skill_run({"action": "status"})
    print_json(result)
    
    if result["is_monitoring"]:
        print("\n✅ 监控正在运行")
        print(f"   累计警报次数: {result['alert_count']}")
    else:
        print("\n⏸️  监控未运行")
    
    return True


def cmd_test(args):
    """测试功能"""
    print("🧪 测试人脸检测...")
    
    # 创建临时 Skill 实例测试
    skill = FaceAlertSkill({
        "min_face_area": 15000,
        "screenshot_dir": "./test_screenshots"
    })
    
    # 测试摄像头
    print("\n1. 测试摄像头连接...")
    if skill.detector.start():
        print("   ✅ 摄像头连接成功")
        
        # 测试人脸检测
        print("\n2. 测试人脸检测...")
        faces, frame = skill.detector.detect_faces()
        if frame is not None:
            print(f"   ✅ 检测到 {len(faces)} 个人脸")
            for i, face in enumerate(faces, 1):
                print(f"      人脸 {i}: 面积 = {face['area']}")
            
            # 测试图片保存
            if faces:
                print("\n3. 测试图片保存...")
                path = skill.camera_capture.capture(frame, faces, "test_capture.png")
                print(f"   ✅ 图片已保存: {os.path.abspath(path)}")
        else:
            print("   ⚠️  未检测到人脸（请确保摄像头前有人）")
        
        skill.detector.stop()
    else:
        print("   ❌ 摄像头连接失败")
        return False
    
    # 测试 QClaw 连接
    print("\n4. 测试 QClaw 连接...")
    try:
        import requests
        response = requests.get(
            skill.config.config["qclaw_api"].replace("/send_message", "/../health"),
            timeout=5
        )
        if response.status_code == 200:
            print("   ✅ QClaw 服务连接成功")
        else:
            print(f"   ⚠️  QClaw 服务响应异常: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  QClaw 服务未启动: {e}")
        print("   💡 请先启动 QClaw: qclaw start")
    
    print("\n✅ 测试完成！")
    return True


def cmd_daemon(args):
    """守护进程模式（保持运行）"""
    print("🤖 启动守护进程模式...")
    
    # 启动监控
    result = skill_run({
        "action": "start",
        "threshold": args.threshold,
        "wechat_receiver": args.receiver
    })
    
    if result["status"] not in ["success", "already_running"]:
        print(f"❌ 启动失败: {result.get('message', 'Unknown error')}")
        return False
    
    print(result["message"])
    
    if result["status"] == "already_running":
        print("   监控已在运行中")
    
    print("\n📊 监控运行中...")
    print("   按 Ctrl+C 停止")
    
    try:
        # 保持运行
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 停止监控...")
        result = skill_run({"action": "stop"})
        print(result["message"])
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Face Alert Skill - 人脸监控警报系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动监控
  python cli.py start
  
  # 启动监控并设置阈值
  python cli.py start --threshold 20000
  
  # 查看状态
  python cli.py status
  
  # 停止监控
  python cli.py stop
  
  # 测试功能
  python cli.py test
  
  # 守护进程模式
  python cli.py daemon
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # start 命令
    start_parser = subparsers.add_parser("start", help="启动人脸监控")
    start_parser.add_argument(
        "--threshold", 
        type=int, 
        default=15000,
        help="人脸面积阈值（默认: 15000）"
    )
    start_parser.add_argument(
        "--receiver",
        type=str,
        default="qclaw_butler",
        help="微信接收者（默认: qclaw_butler）"
    )
    start_parser.set_defaults(func=cmd_start)
    
    # stop 命令
    stop_parser = subparsers.add_parser("stop", help="停止人脸监控")
    stop_parser.set_defaults(func=cmd_stop)
    
    # status 命令
    status_parser = subparsers.add_parser("status", help="查看监控状态")
    status_parser.set_defaults(func=cmd_status)
    
    # test 命令
    test_parser = subparsers.add_parser("test", help="测试功能")
    test_parser.set_defaults(func=cmd_test)
    
    # daemon 命令
    daemon_parser = subparsers.add_parser("daemon", help="守护进程模式运行")
    daemon_parser.add_argument(
        "--threshold",
        type=int,
        default=15000,
        help="人脸面积阈值（默认: 15000）"
    )
    daemon_parser.add_argument(
        "--receiver",
        type=str,
        default="qclaw_butler",
        help="微信接收者（默认: qclaw_butler）"
    )
    daemon_parser.set_defaults(func=cmd_daemon)
    
    # 解析参数
    args = parser.parse_args()
    
    # 执行命令
    if args.command is None:
        parser.print_help()
        return
    
    try:
        success = args.func(args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
