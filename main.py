import sys
import requests
import collections
import json
import os
from PyQt5 import QtWidgets, QtGui, QtCore

if not os.path.exists('config.json'):
    # 如果文件不存在，则创建文件并写入初始信息
    data = {
        "API_KEY": "your_api_key",
        "player_name": "your_player_name"
    }
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)

# 打开并加载配置文件
with open('config.json') as f:
    config = json.load(f)

# 获取 API_KEY 和 player_name 值
API_KEY = config['API_KEY']
player_name = config['player_name']

# 获取玩家UUID
session = requests.Session()
response = session.get(f'https://api.mojang.com/users/profiles/minecraft/{player_name}')
response.raise_for_status()
player_uuid = response.json()['id']

# 创建窗口
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()
window.setWindowTitle('Hypixel Skyblock Collection')
window.setWindowIcon(QtGui.QIcon('icon.ico'))
window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

# 创建滚动区域和容器
scroll_area = QtWidgets.QScrollArea()
scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
container = QtWidgets.QWidget()
scroll_area.setWidget(container)
scroll_area.setWidgetResizable(True)

# 创建布局和标签
layout = QtWidgets.QVBoxLayout(container)
labels = []

def update_collections():
    # print('Updating collections...')

    # 获取玩家collection信息
    response = session.get(f'https://api.hypixel.net/skyblock/profiles?key={API_KEY}&uuid={player_uuid}')
    response.raise_for_status()
    data = response.json()
    if 'profiles' not in data:
        # print(f'Error: failed to get collections, response: {data}')
        return

    # 处理collection信息
    counter = collections.Counter()
    for profile in data['profiles']:
        profile_collections = profile['members'][player_uuid]['collection']
        counter.update(profile_collections)

    # 删除旧标签
    for label in labels:
        label.deleteLater()
    labels.clear()

    # 创建新标签
    for item, amount in counter.most_common():
        # print(f'Creating label for collection: {item}: {amount}')
        label = QtWidgets.QLabel(f'{item}: {amount}')
        font = label.font()
        font.setPointSize(15)
        label.setFont(font)
        layout.addWidget(label)
        labels.append(label)
        # print(f'Label created with text: {label.text()}')

    # print('Collections updated.')


# 设置布局并显示窗口
window.setLayout(QtWidgets.QVBoxLayout())
window.layout().addWidget(scroll_area)
window.resize(635, 1000)
window.show()

# 在启动定时器之前调用update_collections函数
update_collections()

# 创建定时器并启动
timer = QtCore.QTimer(timerType=QtCore.Qt.VeryCoarseTimer)
timer.timeout.connect(update_collections)
timer.start(30000) # update every 30 seconds

sys.exit(app.exec_())
