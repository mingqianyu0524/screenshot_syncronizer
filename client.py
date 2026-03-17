import setproctitle
import os
import subprocess
import socketio
from pynput import keyboard
from datetime import datetime
from dotenv import load_dotenv

# 引入我们之前写好的 llm 模块
from llm import analyze_image

setproctitle.setproctitle("SysInputHelper")

# 加载环境变量
load_dotenv()

# 配置
SERVER_URL = 'http://127.0.0.1:5050'
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "resources")

if not os.path.exists(RESOURCES_DIR):
    os.makedirs(RESOURCES_DIR)

# 初始化 SocketIO 客户端
sio = socketio.Client()


def connect_to_server():
    if not sio.connected:
        try:
            sio.connect(SERVER_URL)
            print("✅ Client: 已连接到本地 Web Server")
            # 通知所有浏览器：键盘监听已就绪
            sio.emit('client_ready')
        except Exception as e:
            print(f"⚠️ Client Warning: 无法连接到 Server ({e})")
            print("   (请确保先运行了 server.py)")


def take_screenshot():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(RESOURCES_DIR, filename)

    print(f"\n📸 正在截屏: {filename}")

    # macOS 截图命令 (-x 静音)
    cmd = ["screencapture", "-x", filepath]
    try:
        subprocess.run(cmd, check=True)
        return filename, filepath
    except Exception as e:
        print(f"❌ 截图失败: {e}")
        return None, None


def on_activate():
    print("⚡️ 快捷键触发！开始工作流...")

    # 1. 截图
    fname, fpath = take_screenshot()
    if not fpath: return

    # 2. 调用 Gemini 分析
    # 提示词可以根据你的喜好修改
    PROMPT = os.getenv("PROMPT")

    ai_response = analyze_image(fpath, prompt=PROMPT)

    # 3. 发送给 Server -> iPhone
    connect_to_server()  # 确保连接
    if sio.connected:
        print("📡 正在推送到 iPhone...")
        sio.emit('broadcast_event', {
            'image': fname,
            'text': ai_response
        })
        print("✅ 推送完成！")
    else:
        print("❌ 推送失败：未连接到 Server")
        print("   AI 回复内容:", ai_response)


# 定义快捷键: Cmd + Shift + P
HOTKEY = {
    keyboard.Key.cmd,
    keyboard.Key.shift,
    keyboard.KeyCode(char='p')
}

current_keys = set()


def on_press(key):
    try:
        current_keys.add(key)
        if HOTKEY.issubset(current_keys):
            on_activate()
            current_keys.clear()  # 触发后重置，防止重复触发
    except AttributeError:
        pass


def on_release(key):
    try:
        current_keys.remove(key)
    except KeyError:
        pass
    if key == keyboard.Key.esc:
        print("程序退出")
        return False


import threading

print(f"🎹 监听中... 按 Cmd+Shift+P 截图，按 ESC 退出")

# 在后台线程连接 server，不阻塞键盘监听的启动
# （避免 Cisco VPN 环境下 IPv6 连接超时导致热键无响应）
threading.Thread(target=connect_to_server, daemon=True).start()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
