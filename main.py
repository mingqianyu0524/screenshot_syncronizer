import subprocess
import time
import os
import signal
import sys

# 获取当前 Python解释器路径 (确保用的是 venv 里的 python)
PYTHON_EXEC = sys.executable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def start_services():
    print("🚀 正在启动服务群...")

    # 1. 启动 Server (Web/Socket)
    # stdout=subprocess.DEVNULL 可以隐藏子进程的输出，让终端更清爽
    server_process = subprocess.Popen(
        [PYTHON_EXEC, os.path.join(BASE_DIR, "server.py")],
        cwd=BASE_DIR
    )
    print(f"✅ Server PID: {server_process.pid}")

    # 等待 2 秒确保 Server 启动完毕
    time.sleep(2)

    # 2. 启动 Client (截图监听)
    client_process = subprocess.Popen(
        [PYTHON_EXEC, os.path.join(BASE_DIR, "client.py")],
        cwd=BASE_DIR
    )
    print(f"✅ Client PID: {client_process.pid}")

    print("⚡️ 系统就绪！按 Ctrl+C 退出所有服务")

    try:
        # 主进程阻塞在这里，等待中断
        server_process.wait()
        client_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        # 优雅地杀死子进程
        server_process.terminate()
        client_process.terminate()
        print("👋 Bye!")


if __name__ == "__main__":
    start_services()
