import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class TurtlePose(Node):
    """/turtle1/pose 를 구독해 위치·방향(x·y·theta)이 바뀔 때마다 로그로 기록하는 노드."""

    def __init__(self):
        super().__init__('turtle_pose')
        self.subscription = self.create_subscription(   # 구독자 생성
            Pose,                  # 메시지 유형
            '/turtle1/pose',       # turtlesim_node 가 발행하는 토픽과 같은 이름
            self.pose_callback,    # 메시지가 도착할 때마다 호출될 콜백
            10)                    # 큐 크기
        self.last_pose = None      # 직전에 기록한 (x, y, theta)

    def pose_callback(self, msg):
        # 속도(linear_velocity·angular_velocity)를 제외한 위치·방향만 사용
        current = (round(msg.x, 2), round(msg.y, 2), round(msg.theta, 2))
        if current != self.last_pose:               # 값이 바뀐 경우에만 기록
            self.last_pose = current
            self.get_logger().info(
                f'x: {current[0]}  y: {current[1]}  theta: {current[2]}')


def main(args=None):
    rclpy.init(args=args)        # ① rclpy(통신 계층) 초기화
    node = TurtlePose()          # ② 노드 객체 생성 — 구독자가 이때 등록됨
    try:
        rclpy.spin(node)         # ③ Ctrl+C 까지 계속 구독 — 메시지 도착 시 콜백 호출
    except KeyboardInterrupt:    #    Ctrl+C 로 종료
        pass
    finally:
        node.destroy_node()      # ④ 노드 정리
        rclpy.try_shutdown()     # ⑤ rclpy 종료 (이미 종료됐으면 건너뜀)


if __name__ == '__main__':
    main()
