import rclpy
from rclpy.node import Node


class LoggingNode(Node):
    """생성되면 자신의 이름을 정보(info) 수준 로그로 기록하고 실행 상태를 유지하는 노드."""

    def __init__(self):
        super().__init__('logging_node')                         # 노드 이름 등록
        self.get_logger().info(f'node name: {self.get_name()}')  # 노드 이름을 info 로그로 기록


def main(args=None):
    rclpy.init(args=args)        # ① rclpy(통신 계층) 초기화
    node = LoggingNode()         # ② 노드 객체 생성 — 이때 __init__ 의 로그가 1회 기록됨
    try:
        rclpy.spin(node)         # ③ 종료 신호가 올 때까지 실행 상태 유지
    except KeyboardInterrupt:    #    Ctrl+C 로 종료
        pass
    finally:
        node.destroy_node()      # ④ 노드 정리
        rclpy.try_shutdown()     # ⑤ rclpy 종료 (이미 종료됐으면 건너뜀)


if __name__ == '__main__':
    main()
