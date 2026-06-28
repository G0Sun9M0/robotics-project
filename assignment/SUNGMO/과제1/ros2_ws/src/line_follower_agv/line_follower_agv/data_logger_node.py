#!/usr/bin/env python3
"""
data_logger_node — 데이터 기록 노드 (요구사항 ③)

이동 데이터(시각/위치/속도/회전각/센서값)를 모아 SD카드(파일)에 CSV로 저장한다.
위치·속도·회전각은 베이스 드라이버가 엔코더+IMU로 만든 /odom(Odometry)에서 가져온다.

구독: /odom (nav_msgs/Odometry), /line_error (Float32),
      /obstacle_distance (Float32), /cmd_vel (geometry_msgs/Twist)
출력: CSV 파일 (기본 ~/agv_log.csv)
"""
import csv
import math
import os
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


def yaw_from_quaternion(q):
    """쿼터니언 → yaw(진행 방향, rad)."""
    siny = 2.0 * (q.w * q.z + q.x * q.y)
    cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny, cosy)


class DataLoggerNode(Node):
    def __init__(self):
        super().__init__('data_logger_node')

        default_path = os.path.join(os.path.expanduser('~'), 'agv_log.csv')
        self.declare_parameter('csv_path', default_path)
        self.declare_parameter('log_rate_hz', 5.0)
        self.csv_path = self.get_parameter('csv_path').value
        rate = self.get_parameter('log_rate_hz').value

        # 최신값 캐시
        self.x = self.y = self.heading = 0.0
        self.distance = self.speed = 0.0
        self.line_error = 0.0
        self.obstacle = 0.0
        self._last_x = self._last_y = None  # 누적 이동거리 계산용

        # CSV 파일 열고 헤더 작성
        self.file = open(self.csv_path, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(
            ['timestamp', 'x', 'y', 'distance', 'speed',
             'heading', 'line_error', 'obstacle_cm'])

        self.create_subscription(Odometry, 'odom', self.on_odom, 10)
        self.create_subscription(Float32, 'line_error', self.on_line, 10)
        self.create_subscription(Float32, 'obstacle_distance', self.on_obs, 10)
        self.create_subscription(Twist, 'cmd_vel', self.on_cmd, 10)
        self.timer = self.create_timer(1.0 / rate, self.on_log)

        self.get_logger().info(f'data_logger_node 시작 → {self.csv_path}')

    def on_odom(self, msg):
        p = msg.pose.pose.position
        self.x, self.y = p.x, p.y
        self.heading = math.degrees(yaw_from_quaternion(msg.pose.pose.orientation))
        self.speed = msg.twist.twist.linear.x
        # 누적 이동거리
        if self._last_x is not None:
            self.distance += math.hypot(self.x - self._last_x, self.y - self._last_y)
        self._last_x, self._last_y = self.x, self.y

    def on_line(self, msg):
        self.line_error = msg.data

    def on_obs(self, msg):
        self.obstacle = msg.data

    def on_cmd(self, msg):
        pass  # 필요 시 명령 속도도 기록 가능

    def on_log(self):
        # ROS 시계로 타임스탬프(ISO 유사 문자열)
        now = self.get_clock().now().to_msg()
        ts = f'{now.sec}.{now.nanosec:09d}'
        self.writer.writerow([
            ts,
            round(self.x, 3), round(self.y, 3),
            round(self.distance, 3), round(self.speed, 3),
            round(self.heading, 1), round(self.line_error, 3),
            round(self.obstacle * 100.0, 1),  # m → cm
        ])
        self.file.flush()

    def destroy_node(self):
        try:
            self.file.close()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = DataLoggerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
