#!/usr/bin/env python3
"""
mqtt_bridge_node — 실시간 전송 노드 (요구사항 ④)

이동 데이터를 모아 JSON으로 만들어 Wi-Fi 너머의 MQTT 브로커로 실시간 발행한다.
수신측(PC/서버)은 같은 토픽을 구독해 실시간 모니터링한다.

구독: /odom, /line_error, /obstacle_distance
전송: MQTT 토픽 (기본 robot/agv01/telemetry)

필요 패키지: paho-mqtt  (pip install paho-mqtt)
"""
import json
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from nav_msgs.msg import Odometry

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


def yaw_deg(q):
    siny = 2.0 * (q.w * q.z + q.x * q.y)
    cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.degrees(math.atan2(siny, cosy))


class MqttBridgeNode(Node):
    def __init__(self):
        super().__init__('mqtt_bridge_node')

        self.declare_parameter('broker_host', 'localhost')
        self.declare_parameter('broker_port', 1883)
        self.declare_parameter('topic', 'robot/agv01/telemetry')
        self.declare_parameter('publish_rate_hz', 5.0)

        self.host = self.get_parameter('broker_host').value
        self.port = self.get_parameter('broker_port').value
        self.topic = self.get_parameter('topic').value
        rate = self.get_parameter('publish_rate_hz').value

        self.x = self.y = self.heading = self.speed = 0.0
        self.line_error = 0.0
        self.obstacle = 0.0

        self.create_subscription(Odometry, 'odom', self.on_odom, 10)
        self.create_subscription(Float32, 'line_error', self.on_line, 10)
        self.create_subscription(Float32, 'obstacle_distance', self.on_obs, 10)

        # MQTT 클라이언트 연결
        if mqtt is None:
            self.client = None
            self.get_logger().warn('paho-mqtt 미설치 → 전송 비활성화 (pip install paho-mqtt)')
        else:
            self.client = mqtt.Client()
            try:
                self.client.connect(self.host, self.port, keepalive=60)
                self.client.loop_start()
                self.get_logger().info(f'MQTT 연결: {self.host}:{self.port} → {self.topic}')
            except Exception as e:
                self.client = None
                self.get_logger().error(f'MQTT 연결 실패: {e}')

        self.timer = self.create_timer(1.0 / rate, self.on_publish)

    def on_odom(self, msg):
        p = msg.pose.pose.position
        self.x, self.y = p.x, p.y
        self.heading = yaw_deg(msg.pose.pose.orientation)
        self.speed = msg.twist.twist.linear.x

    def on_line(self, msg):
        self.line_error = msg.data

    def on_obs(self, msg):
        self.obstacle = msg.data

    def on_publish(self):
        now = self.get_clock().now().to_msg()
        payload = {
            'ts': f'{now.sec}.{now.nanosec:09d}',
            'x': round(self.x, 3),
            'y': round(self.y, 3),
            'speed': round(self.speed, 3),
            'heading': round(self.heading, 1),
            'line_err': round(self.line_error, 3),
            'obs': round(self.obstacle * 100.0, 1),
        }
        if self.client is not None:
            self.client.publish(self.topic, json.dumps(payload))

    def destroy_node(self):
        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MqttBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
