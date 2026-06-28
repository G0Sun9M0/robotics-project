from setuptools import setup
import os
from glob import glob

package_name = 'line_follower_agv'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # launch 파일 설치
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='SUNGMO',
    maintainer_email='gsm9384@gmail.com',
    description='라인트레이싱 운반 로봇(AGV) ROS2 패키지',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # `ros2 run line_follower_agv <name>` 으로 실행되는 노드들
            'sensor_node = line_follower_agv.sensor_node:main',
            'controller_node = line_follower_agv.controller_node:main',
            'data_logger_node = line_follower_agv.data_logger_node:main',
            'mqtt_bridge_node = line_follower_agv.mqtt_bridge_node:main',
        ],
    },
)
