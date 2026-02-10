# from gevent import monkey
# monkey.patch_all()

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
import os

app = Flask(__name__)
# 允许跨域，确保局域网访问无阻碍
socketio = SocketIO(app, cors_allowed_origins="*")

# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")

# 确保资源目录存在
if not os.path.exists(RESOURCES_DIR):
    os.makedirs(RESOURCES_DIR)


@app.route('/')
def index():
    return render_template('index.html')


# 这是一个特殊的路由，允许浏览器访问 resources 目录下的图片
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(RESOURCES_DIR, filename)


# 监听来自 client.py 的广播事件
@socketio.on('broadcast_event')
def handle_broadcast(data):
    print(f"🔄 Server: 收到 Client 图片 {data.get('image')}, 正在转发给 iPhone...")

    # 将数据转发给前端 (index.html)
    socketio.emit('update_content', {
        'image_url': f"/images/{data['image']}",
        'text': data['text']
    })


if __name__ == '__main__':
    # host='0.0.0.0' 极其重要，否则 iPhone 无法访问
    print("🚀 Web Server 启动中... 请在 iPhone 上访问 http://你的MacIP:5050")
    socketio.run(app, host='0.0.0.0', port=5050, allow_unsafe_werkzeug=True)
