#!/usr/bin/env python3
"""
controller_node — 자율주행 제어 노드 (요구사항 ②)

/line_error 를 구독해 PID 제어로 조향량을 계산하고, /cmd_vel(Twist)로 모터 명령을 발행한다.
/obstacle_distance 가 정지 거리 이내면 정지한다. (자율주행 동작 순서도의 핵심)

구독: /line_error (Float32), /obstacle_distance (Float32)
발행: /cmd_vel (geometry_msgs/Twist)
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist


class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')

        # ---- PID 및 주행 파라미터 ----
        self.declare_parameter('kp', 0.8)
        self.declare_parameter('ki', 0.0)
        self.declare_parameter('kd', 0.2)
        self.declare_parameter('base_speed', 0.20)       # 직진 속도 [m/s]
        self.declare_parameter('max_angular', 1.5)       # 최대 회전 각속도 [rad/s]
        self.declare_parameter('stop_distance', 0.20)    # 이 거리 이내면 정지 [m]
        self.declare_parameter('control_rate_hz', 50.0)

        self.kp = self.get_parameter('kp').value
        self.ki = self.get_parameter('ki').value
        self.kd = self.get_parameter('kd').value
        self.base_speed = self.get_parameter('base_speed').value
        self.max_angular = self.get_parameter('max_angular').value
        self.stop_distance = self.get_parameter('stop_distance').value
        rate = self.get_parameter('control_rate_hz').value
        self.dt = 1.0 / rate

        # ---- PID 내부 상태 ----
        self.error = 0.0
        self.integral = 0.0
        self.prev_error = 0.0
        self.obstacle = 999.0

        # ---- 통신 ----
        self.create_subscription(Float32, 'line_error', self.on_line_error, 10)
        self.create_subscription(Float32, 'obstacle_distance', self.on_obstacle, 10)
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(self.dt, self.on_control)

        self.get_logger().info(
            f'controller_node 시작 (PID kp={self.kp}, ki={self.ki}, kd={self.kd})')

    def on_line_error(self, msg):
        self.error = msg.data

    def on_obstacle(self, msg):
        self.obstacle = msg.data

    def on_control(self):
        cmd = Twist()

        # 1) 장애물 정지 (추돌 방지)
        if self.obstacle <= self.stop_distance:
            self.cmd_pub.publish(cmd)   # 전부 0 → 정지
            self.integral = 0.0
            return

        # 2) PID 계산: 목표는 error=0(선 가운데)
        self.integral += self.error * self.dt
        derivative = (self.error - self.prev_error) / self.dt
        output = self.kp * self.error + self.ki * self.integral + self.kd * derivative
        self.prev_error = self.error

        # 3) 조향: 선이 오른쪽(+)이면 오른쪽으로(angular -) 돌도록 부호 반전
        angular = max(-self.max_angular, min(self.max_angular, -output))

        cmd.linear.x = self.base_speed
        cmd.angular.z = angular
        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
