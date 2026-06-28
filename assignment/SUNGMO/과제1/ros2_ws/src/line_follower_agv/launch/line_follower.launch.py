"""
line_follower.launch.py — 라인트레이싱 AGV 노드 일괄 실행

사용: ros2 launch line_follower_agv line_follower.launch.py
네 개 노드(sensor / controller / data_logger / mqtt_bridge)를 한 번에 띄운다.
"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='line_follower_agv',
            executable='sensor_node',
            name='sensor_node',
            output='screen',
            parameters=[{'num_ir_sensors': 5, 'threshold': 500}],
        ),
        Node(
            package='line_follower_agv',
            executable='controller_node',
            name='controller_node',
            output='screen',
            parameters=[{'kp': 0.8, 'ki': 0.0, 'kd': 0.2, 'base_speed': 0.20}],
        ),
        Node(
            package='line_follower_agv',
            executable='data_logger_node',
            name='data_logger_node',
            output='screen',
        ),
        Node(
            package='line_follower_agv',
            executable='mqtt_bridge_node',
            name='mqtt_bridge_node',
            output='screen',
            parameters=[{'broker_host': 'localhost', 'broker_port': 1883}],
        ),
    ])
