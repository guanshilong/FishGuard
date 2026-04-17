#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Face Alert Skill - QClaw Skill 插件
人脸监控警报系统 - 检测到人脸靠近时捕获摄像头照片并发送微信通知

功能：
- 实时监控人脸
- 检测到靠近时自动捕获摄像头画面
- 通过 QClaw 发送微信通知
- 支持配置阈值和接收者
"""

import os
import sys
import time
import json
import signal
import subprocess
import glob
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading

# OpenCV
import cv2

# 请求库（用于调用 QClaw API）
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class FaceAlertConfig:
    """配置类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "camera_index": 0,
        "check_interval": 0.1,
        "debounce_time": 5.0,
        "min_face_area": 15000,
        "screenshot_dir": "./screenshots",
        "qclaw_api": "http://localhost:8080/api/send_message",
        "wechat_receiver": "qclaw_butler"
    }
    
    def __init__(self, config_dict: Optional[Dict] = None):
        """初始化配置"""
        self.config = self.DEFAULT_CONFIG.copy()
        if config_dict:
            self.config.update(config_dict)
        
        # 确保截屏目录存在
        os.makedirs(self.config["screenshot_dir"], exist_ok=True)


class FaceDetector:
    """人脸检测器"""
    
    def __init__(self, camera_index: int = 0):
        """
        初始化人脸检测器
        
        Args:
            camera_index: 摄像头索引
        """
        self.camera_index = camera_index
        self.cap = None
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def start(self) -> bool:
        """启动摄像头"""
        self.cap = cv2.VideoCapture(self.camera_index)
        return self.cap.isOpened()
    
    def stop(self):
        """停止摄像头"""
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def detect_faces(self) -> tuple:
        """
        检测人脸
        
        Returns:
            (人脸列表, 当前帧) - 人脸列表每个元素包含 {x, y, w, h, area}
        """
        if not self.cap or not self.cap.isOpened():
            return [], None
        
        ret, frame = self.cap.read()
        if not ret:
            return [], None
        
        # 转换为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5
        )
        
        # 计算面积
        face_list = []
        for (x, y, w, h) in faces:
            face_list.append({
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h),
                "area": int(w * h)
            })
        
        return face_list, frame
    
    def get_frame(self):
        """获取当前帧"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            return frame if ret else None
        return None


class CameraCapture:
    """摄像头画面捕获工具"""
    
    def __init__(self, save_dir: str = "./screenshots"):
        """
        初始化摄像头捕获工具
        
        Args:
            save_dir: 截屏保存目录
        """
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def capture(self, frame, faces: Optional[List[Dict]] = None, filename: Optional[str] = None) -> str:
        """
        捕获摄像头画面
        
        Args:
            frame: 摄像头画面帧（numpy array）
            faces: 人脸列表（可选，用于标注）
            filename: 文件名（可选）
        
        Returns:
            图片保存路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alert_{timestamp}.png"
        
        filepath = os.path.join(self.save_dir, filename)
        
        # 复制画面用于标注
        annotated_frame = frame.copy()
        
        # 如果提供了人脸信息，绘制人脸框
        if faces:
            for face in faces:
                x, y, w, h = face['x'], face['y'], face['w'], face['h']
                area = face['area']
                
                # 绘制人脸框（红色）
                cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                
                # 添加面积标签
                label = f"Area: {area}"
                cv2.putText(annotated_frame, label, (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # 添加时间戳
        timestamp_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(annotated_frame, timestamp_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 保存图片
        cv2.imwrite(filepath, annotated_frame)
        
        return filepath


class QClawMessenger:
    """QClaw 消息发送器"""
    
    def __init__(self, api_endpoint: str, receiver: str):
        """
        初始化消息发送器
        
        Args:
            api_endpoint: QClaw API 端点
            receiver: 接收者（微信管家 ID）
        """
        self.api_endpoint = api_endpoint
        self.receiver = receiver
    
    def send_alert(self, message: str, screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """
        发送警报消息和图片
        
        Args:
            message: 消息内容
            screenshot_path: 图片路径（可选）
        
        Returns:
            发送结果
        """
        if not REQUESTS_AVAILABLE:
            return {
                "success": False,
                "error": "requests 库未安装，无法发送消息"
            }
        
        try:
            # 步骤 1: 发送文本消息
            text_data = {
                "receiver": self.receiver,
                "message": message,
                "type": "text"
            }
            
            text_response = requests.post(
                self.api_endpoint,
                json=text_data,
                timeout=10
            )
            
            # 步骤 2: 如果有图片，发送图片文件
            if screenshot_path and os.path.exists(screenshot_path):
                # 修改 API 端点为文件上传端点
                file_endpoint = self.api_endpoint.replace('/send_message', '/send_file')
                
                # 读取图片文件
                with open(screenshot_path, 'rb') as f:
                    files = {
                        'file': (
                            os.path.basename(screenshot_path),
                            f,
                            'image/png'
                        )
                    }
                    data = {
                        'receiver': self.receiver
                    }
                    
                    # 发送文件
                    file_response = requests.post(
                        file_endpoint,
                        files=files,
                        data=data,
                        timeout=30  # 文件上传可能需要更长时间
                    )
                    
                    if file_response.status_code != 200:
                        return {
                            "success": False,
                            "error": f"图片发送失败: {file_response.status_code}",
                            "text_sent": text_response.status_code == 200
                        }
            
            # 返回结果
            if text_response.status_code == 200:
                return {
                    "success": True,
                    "message": "消息和图片发送成功"
                }
            else:
                return {
                    "success": False,
                    "error": f"消息发送失败: {text_response.status_code}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class FaceAlertSkill:
    """
    Face Alert Skill 主类
    
    功能：
    - 监控人脸
    - 触发警报时截屏
    - 发送微信通知
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化 Skill
        
        Args:
            config: 配置字典
        """
        self.config = FaceAlertConfig(config)
        
        # 初始化组件
        self.detector = FaceDetector(self.config.config["camera_index"])
        self.camera_capture = CameraCapture(self.config.config["screenshot_dir"])
        self.messenger = QClawMessenger(
            self.config.config["qclaw_api"],
            self.config.config["wechat_receiver"]
        )
        
        # 状态
        self.is_monitoring = False
        self.alert_count = 0
        self.last_alert_time = 0
        self.monitor_thread = None
        
        # 最新警报结果（用于 QClaw 查询）
        self.last_alert_result = None
    
    def should_alert(self, faces: List[Dict]) -> bool:
        """
        判断是否应该触发警报
        
        Args:
            faces: 检测到的人脸列表
        
        Returns:
            是否触发警报
        """
        if not faces:
            return False
        
        # 检查是否有人脸面积超过阈值
        min_area = self.config.config["min_face_area"]
        for face in faces:
            if face["area"] >= min_area:
                return True
        
        return False
    
    def check_debounce(self) -> bool:
        """
        检查防抖
        
        Returns:
            是否可以触发（True: 可以，False: 需要等待）
        """
        current_time = time.time()
        debounce_time = self.config.config["debounce_time"]
        
        if current_time - self.last_alert_time < debounce_time:
            return False
        
        return True
    
    def trigger_alert(self, faces: List[Dict], frame) -> Dict[str, Any]:
        """
        触发警报
        
        Args:
            faces: 检测到的人脸列表
            frame: 当前摄像头画面帧
        
        Returns:
            警报结果（符合 QClaw 标准）
        """
        # 检查防抖
        if not self.check_debounce():
            return {
                "status": "skipped",
                "message": "防抖中，跳过此次警报"
            }
        
        # 更新时间
        self.last_alert_time = time.time()
        self.alert_count += 1
        
        # 捕获摄像头画面（带人脸标注）
        screenshot_path = self.camera_capture.capture(frame, faces)
        abs_image_path = os.path.abspath(screenshot_path)
        
        # 构建消息
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""🚨 人脸监控警报
时间: {timestamp}
人脸数量: {len(faces)}
最大面积: {max(f['area'] for f in faces)}
摄像头照片已保存: {abs_image_path}"""
        
        # 发送消息
        send_result = self.messenger.send_alert(message, screenshot_path)
        
        # 构建返回结果
        result = {
            "status": "success",
            "message": message,
            "image_path": abs_image_path,  # QClaw 可用的绝对路径
            "screenshot_path": screenshot_path,  # 向后兼容
            "message_sent": send_result["success"],
            "alert_count": self.alert_count,
            "faces_detected": len(faces),
            "timestamp": timestamp
        }
        
        # 保存最新的警报结果（供 QClaw 查询）
        self.last_alert_result = result
        
        return result
    
    def monitor_loop(self):
        """监控循环（在主线程中运行，macOS AVFoundation 要求）"""
        # macOS: 必须在主线程中打开摄像头，否则 AVFoundation 无法初始化
        if not self.detector.start():
            print("❌ 无法启动摄像头")
            self.is_monitoring = False
            return
        
        print("✅ 人脸监控已启动，摄像头已打开")
        
        while self.is_monitoring:
            # 检测人脸并获取当前帧
            faces, frame = self.detector.detect_faces()
            
            # 判断是否触发警报
            if self.should_alert(faces) and frame is not None:
                result = self.trigger_alert(faces, frame)
                print(f"🚨 警报触发: {result}")
            
            # 等待
            time.sleep(self.config.config["check_interval"])
        
        self.detector.stop()
        print("✅ 人脸监控已停止")
    
    def start_monitoring(self) -> Dict[str, Any]:
        """
        启动监控
        
        注意：在 macOS 上，AVFoundation 要求摄像头在主线程中初始化。
        因此 monitor_loop 应该在主线程中调用，整个脚本作为后台进程运行。
        
        Returns:
            启动结果（符合 QClaw 标准）
        """
        if self.is_monitoring:
            return {
                "status": "already_running",
                "message": "人脸监控已在运行中",
                "is_monitoring": True,
                "alert_count": self.alert_count
            }
        
        self.is_monitoring = True
        
        # 直接在当前线程（主线程）运行监控循环
        # 整个脚本应该作为后台进程启动，而不是在子线程中运行
        self.monitor_loop()
        
        return {
            "status": "success",
            "message": "✅ 人脸监控已启动，正在后台运行",
            "is_monitoring": True,
            "alert_count": self.alert_count,
            "config": {
                "threshold": self.config.config["min_face_area"],
                "screenshot_dir": os.path.abspath(self.config.config["screenshot_dir"]),
                "wechat_receiver": self.config.config["wechat_receiver"]
            }
        }
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """
        停止监控
        
        Returns:
            停止结果（符合 QClaw 标准）
        """
        if not self.is_monitoring:
            return {
                "status": "not_running",
                "message": "人脸监控未在运行",
                "is_monitoring": False,
                "alert_count": self.alert_count
            }
        
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        return {
            "status": "success",
            "message": "✅ 人脸监控已停止",
            "is_monitoring": False,
            "alert_count": self.alert_count
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取状态
        
        Returns:
            状态信息（符合 QClaw 标准）
        """
        result = {
            "status": "success",
            "message": f"人脸监控状态: {'运行中' if self.is_monitoring else '已停止'}",
            "is_monitoring": self.is_monitoring,
            "alert_count": self.alert_count,
            "last_alert_time": self.last_alert_time,
            "config": {
                "threshold": self.config.config["min_face_area"],
                "screenshot_dir": os.path.abspath(self.config.config["screenshot_dir"]),
                "wechat_receiver": self.config.config["wechat_receiver"]
            }
        }
        
        # 如果有最新的警报结果，也返回
        if self.last_alert_result:
            result["last_alert"] = self.last_alert_result
        
        return result
    
    def check_alert(self) -> Dict[str, Any]:
        """
        检查是否有新的警报（专门为 QClaw 轮询设计）
        
        Returns:
            警报信息（如果有）
        """
        if not self.last_alert_result:
            return {
                "status": "no_alert",
                "message": "暂无警报",
                "is_monitoring": self.is_monitoring,
                "alert_count": self.alert_count
            }
        
        # 返回最新的警报结果
        result = self.last_alert_result.copy()
        result["is_monitoring"] = self.is_monitoring
        return result
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Skill 主入口（符合 QClaw 规范）
        
        Args:
            input_data: 输入数据
                {
                    "action": "start | stop | status",
                    "threshold": 15000,  # 可选：人脸面积阈值
                    "wechat_receiver": "qclaw_butler"  # 可选：微信接收者
                }
        
        Returns:
            输出数据（符合 QClaw 标准）
                {
                    "status": "success | failed | already_running | not_running",
                    "message": "操作结果消息",
                    "image_path": "...",  # 图片绝对路径（警报触发时）
                    "is_monitoring": true/false,
                    "alert_count": 5
                }
        
        Examples:
            >>> # 启动监控
            >>> result = run({"action": "start"})
            >>> print(result["message"])
            "✅ 人脸监控已启动，正在后台运行"
            
            >>> # 查看状态
            >>> result = run({"action": "status"})
            >>> print(result["is_monitoring"])
            True
            
            >>> # 停止监控
            >>> result = run({"action": "stop"})
            >>> print(result["message"])
            "✅ 人脸监控已停止"
        """
        action = input_data.get("action", "start")
        
        # 更新配置（如果提供）
        if "threshold" in input_data:
            self.config.config["min_face_area"] = input_data["threshold"]
        
        if "wechat_receiver" in input_data:
            self.config.config["wechat_receiver"] = input_data["wechat_receiver"]
            self.messenger.receiver = input_data["wechat_receiver"]
        
        # 执行操作
        if action == "start":
            return self.start_monitoring()
        elif action == "stop":
            return self.stop_monitoring()
        elif action == "status":
            return self.get_status()
        elif action == "check_alert":
            return self.check_alert()
        else:
            return {
                "status": "failed",
                "message": f"未知操作: {action}。支持的操作: start, stop, status, check_alert"
            }


# ============== QClaw Skill 入口函数 ==============

def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    QClaw Skill 标准入口
    
    Args:
        input_data: {
            "action": "start | stop | status",
            "threshold": 15000,  # 可选
            "wechat_receiver": "qclaw_butler"  # 可选
        }
    
    Returns:
        {
            "status": "success | failed | already_running | not_running",
            "message": "操作结果消息",
            "image_path": "...",  # 图片绝对路径（警报触发时）
            "is_monitoring": true/false,
            "alert_count": 5
        }
    
    Examples:
        >>> # 启动监控
        >>> result = run({"action": "start", "threshold": 15000})
        >>> print(result["status"])
        "success"
        >>> print(result["message"])
        "✅ 人脸监控已启动，正在后台运行"
        
        >>> # 查看状态
        >>> result = run({"action": "status"})
        >>> print(result["is_monitoring"])
        True
        
        >>> # 停止监控
        >>> result = run({"action": "stop"})
        >>> print(result["message"])
        "✅ 人脸监控已停止"
        
        >>> # 当警报触发时，返回值包含 image_path
        >>> {
        ...     "status": "success",
        ...     "message": "🚨 人脸监控警报\\n时间: 2026-04-16 17:30:00\\n人脸数量: 1\\n最大面积: 18500",
        ...     "image_path": "/Users/xxx/FishGuard/face_alert_skill/screenshots/alert_20260416_173000.png",
        ...     "alert_count": 1,
        ...     "message_sent": true
        ... }
    """
    skill = FaceAlertSkill()
    return skill.run(input_data)


# ============== 独立运行模式 ==============

if __name__ == "__main__":
    import argparse
    import subprocess
    import glob
    
    parser = argparse.ArgumentParser(description="Face Alert Skill - 人脸监控警报系统")
    parser.add_argument(
        "--action",
        choices=["start", "stop", "status", "check_alert", "get_latest_photo"],
        default="start",
        help="操作类型: start(启动) | stop(停止) | status(状态) | check_alert(检查警报) | get_latest_photo(获取最新照片)"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=15000,
        help="人脸面积阈值（默认 15000）"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="以守护进程模式运行（后台运行）"
    )
    
    args = parser.parse_args()
    
    # 获取脚本目录
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PID_FILE = os.path.join(SCRIPT_DIR, ".face-alert.pid")
    
    # 特殊处理：获取最新照片（供 QClaw 调用）
    if args.action == "get_latest_photo":
        screenshots_dir = os.path.join(SCRIPT_DIR, "screenshots")
        photos = glob.glob(os.path.join(screenshots_dir, "alert_*.png"))
        
        if not photos:
            print(json.dumps({
                "status": "no_photo",
                "message": "暂无照片"
            }, ensure_ascii=False))
        else:
            # 按修改时间排序，获取最新的
            latest_photo = max(photos, key=os.path.getmtime)
            photo_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(latest_photo)))
            
            print(json.dumps({
                "status": "success",
                "message": f"最新照片: {photo_time}",
                "image_path": latest_photo,
                "photo_time": photo_time
            }, ensure_ascii=False))
        sys.exit(0)
    
    # 特殊处理：启动守护进程
    if args.action == "start" and args.daemon:
        # 检查是否已在运行
        if os.path.exists(PID_FILE):
            try:
                with open(PID_FILE, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)
                print(json.dumps({
                    "status": "already_running",
                    "message": "人脸监控已在运行中",
                    "pid": pid
                }, ensure_ascii=False))
                sys.exit(0)
            except (ValueError, ProcessLookupError):
                os.remove(PID_FILE)
        
        # 启动 daemon.py
        daemon_path = os.path.join(SCRIPT_DIR, "daemon.py")
        subprocess.Popen(
            [sys.executable, daemon_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # 等待启动
        time.sleep(2)
        
        # 检查是否启动成功
        if os.path.exists(PID_FILE):
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            print(json.dumps({
                "status": "success",
                "message": "✅ 人脸监控已启动，正在后台运行",
                "pid": pid,
                "threshold": args.threshold
            }, ensure_ascii=False))
        else:
            print(json.dumps({
                "status": "failed",
                "message": "❌ 启动失败，请检查摄像头权限"
            }, ensure_ascii=False))
        sys.exit(0)
    
    # 特殊处理：停止守护进程
    if args.action == "stop":
        if not os.path.exists(PID_FILE):
            print(json.dumps({
                "status": "not_running",
                "message": "人脸监控未在运行"
            }, ensure_ascii=False))
            sys.exit(0)
        
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            
            print(json.dumps({
                "status": "success",
                "message": "✅ 人脸监控已停止"
            }, ensure_ascii=False))
        except ProcessLookupError:
            os.remove(PID_FILE)
            print(json.dumps({
                "status": "not_running",
                "message": "人脸监控未在运行"
            }, ensure_ascii=False))
        sys.exit(0)
    
    # 特殊处理：查看状态
    if args.action == "status":
        STATUS_FILE = os.path.join(SCRIPT_DIR, ".face-alert-status.json")
        
        if not os.path.exists(PID_FILE):
            print(json.dumps({
                "status": "success",
                "message": "人脸监控状态: 已停止",
                "is_monitoring": False
            }, ensure_ascii=False))
        else:
            try:
                with open(PID_FILE, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)
                
                # 读取状态文件
                if os.path.exists(STATUS_FILE):
                    with open(STATUS_FILE, "r") as f:
                        status = json.load(f)
                    print(json.dumps({
                        "status": "success",
                        "message": "人脸监控状态: 运行中",
                        "is_monitoring": True,
                        "alert_count": status.get("alert_count", 0),
                        "pid": pid
                    }, ensure_ascii=False))
                else:
                    print(json.dumps({
                        "status": "success",
                        "message": "人脸监控状态: 运行中",
                        "is_monitoring": True,
                        "pid": pid
                    }, ensure_ascii=False))
            except ProcessLookupError:
                os.remove(PID_FILE)
                print(json.dumps({
                    "status": "success",
                    "message": "人脸监控状态: 已停止",
                    "is_monitoring": False
                }, ensure_ascii=False))
        sys.exit(0)
    
    # 默认行为：交互式运行（前台运行）
    print("=" * 60)
    print("Face Alert Skill - 人脸监控警报系统")
    print("=" * 60)
    print()
    
    # 创建 Skill 实例
    skill = FaceAlertSkill({
        "min_face_area": args.threshold,
        "screenshot_dir": "./screenshots",
        "qclaw_api": "http://localhost:8080/api/send_message",
        "wechat_receiver": "qclaw_butler"
    })
    
    # 启动监控
    print("🚀 启动人脸监控...")
    result = skill.run({"action": "start"})
    print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result["status"] == "success":
        print("\n✅ 监控已启动，按 Ctrl+C 停止")
        print(f"   阈值: {skill.config.config['min_face_area']}")
        print(f"   截屏目录: {skill.config.config['screenshot_dir']}")
        print(f"   QClaw API: {skill.config.config['qclaw_api']}")
        print()
        
        try:
            # 保持运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 停止监控...")
            result = skill.run({"action": "stop"})
            print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    print("\n👋 程序结束")
