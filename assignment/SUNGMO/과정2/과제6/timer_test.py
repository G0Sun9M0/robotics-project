import rclpy
from rclpy.node import Node


class TimerNode(Node):
    """2초·3초 주기 타이머 두 개로 counter 속성을 증감하며 값을 로그로 기록하는 노드."""

    def __init__(self):
        super().__init__('timer_node')
        self.counter = 0                                                 # 클래스 속성, 초기값 0
        self.timer_2s = self.create_timer(2.0, self.timer_2s_callback)   # 2초에 한 번 콜백 호출
        self.timer_3s = self.create_timer(3.0, self.timer_3s_callback)   # 3초에 한 번 콜백 호출

    def timer_2s_callback(self):
        self.counter += 1
        self.get_logger().info(f'2 seconds passed : {self.counter}')

    def timer_3s_callback(self):
        self.counter -= 1
        self.get_logger().info(f'3 seconds passed : {self.counter}')


def main(args=None):
    rclpy.init(args=args)        # ① rclpy(통신 계층) 초기화
    node = TimerNode()           # ② 노드 객체 생성 — 타이머 2개가 이때 등록됨
    try:
        rclpy.spin(node)         # ③ 이벤트 루프 — 주기가 될 때마다 콜백을 호출
    except KeyboardInterrupt:    #    Ctrl+C 로 종료
        pass
    finally:
        node.destroy_node()      # ④ 노드 정리 (타이머도 함께 해제)
        rclpy.try_shutdown()     # ⑤ rclpy 종료 (이미 종료됐으면 건너뜀)


if __name__ == '__main__':
    main()
