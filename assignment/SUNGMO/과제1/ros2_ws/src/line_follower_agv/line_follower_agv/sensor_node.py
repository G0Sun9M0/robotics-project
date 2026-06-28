#!/usr/bin/env python3
"""
sensor_node — 센서 입력 노드 (요구사항 ①)

적외선 반사 어레이로 검은 선의 위치를 읽어 '오차(line_error)'를 계산하고,
초음파 센서로 전방 장애물 거리를 측정하여 토픽으로 발행한다.

발행 토픽:
  /line_error        (std_msgs/Float32)  -1.0(선이 맨 왼쪽) ~ 0(가운데) ~ +1.0(맨 오른쪽)
  /obstacle_distance (std_msgs/Float32)  전방 장애물 거리 [m]
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class SensorNode(Node):
    def __init__(self):
        super().__init__('sensor_node')

        # ---- 파라미터 (ros2 param 으로 변경 가능) ----
        self.declare_parameter('num_ir_sensors', 5)   # 적외선 센서 개수(어레이)
        self.declare_parameter('threshold', 500)       # 흑/백 판정 임계값(아날로그 기준)
        self.declare_parameter('publish_rate_hz', 50.0)

        self.num_ir = self.get_parameter('num_ir_sensors').value
        self.threshold = self.get_parameter('threshold').value
        rate = self.get_parameter('publish_rate_hz').value

        # ---- 퍼블리셔 ----
        self.line_pub = self.create_publisher(Float32, 'line_error', 10)
        self.obs_pub = self.create_publisher(Float32, 'obstacle_distance', 10)

        # ---- 주기 타이머 ----
        self.timer = self.create_timer(1.0 / rate, self.on_timer)
        self.get_logger().info(f'sensor_node 시작 (센서 {self.num_ir}개, 임계값 {self.threshold})')

    # === 하드웨어 읽기 (실장 시 GPIO/ADC 코드로 교체) ===
    def read_ir_array(self):
        """적외선 어레이 아날로그 값 리스트를 반환. 값이 작을수록 검은색."""
        # TODO: 실제 하드웨어에서는 ADC로 각 센서값을 읽는다.
        #       여기서는 구조 설명용으로 '가운데에 선이 있는' 더미값을 반환.
        return [900, 600, 200, 600, 900][: self.num_ir]

    def read_ultrasonic(self):
        """전방 장애물 거리[m]를 반환."""
        # TODO: 실제 하드웨어에서는 초음파 trig/echo 시간으로 거리 계산.
        return 1.0

    def compute_line_error(self, values):
        """
        가중 평균으로 선의 위치 오차를 계산한다.
        센서 인덱스에 -1..+1 가중치를 주고, '검은색(임계값 미만)'인 센서들의 평균 위치를 구한다.
        """
        n = len(values)
        if n == 1:
            return 0.0
        weights = [(-1.0 + 2.0 * i / (n - 1)) for i in range(n)]  # 예: [-1,-0.5,0,0.5,1]

        num, den = 0.0, 0.0
        for w, v in zip(weights, values):
            on_line = 1.0 if v < self.threshold else 0.0   # 검은 선 위면 1
            num += w * on_line
            den += on_line

        if den == 0.0:      # 선을 아예 못 찾음 → 오차 0 (직진 유지 또는 탐색 정책)
            return 0.0
        return num / den

    def on_timer(self):
        ir_values = self.read_ir_array()
        error = self.compute_line_error(ir_values)
        distance = self.read_ultrasonic()

        self.line_pub.publish(Float32(data=float(error)))
        self.obs_pub.publish(Float32(data=float(distance)))


def main(args=None):
    rclpy.init(args=args)
    node = SensorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
