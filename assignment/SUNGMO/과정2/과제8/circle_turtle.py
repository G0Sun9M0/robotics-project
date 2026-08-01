import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CircleTurtle(Node):
    """/turtle1/cmd_vel 토픽에 Twist 메시지를 주기적으로 발행해 거북이가 원을 그리게 하는 노드."""

    def __init__(self):
        super().__init__('circle_turtle')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)  # 게시자 생성
        self.timer = self.create_timer(0.1, self.timer_callback)               # 0.1초(10Hz) 주기 발행

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 2.0       # 전진 속도 (앞 방향)
        msg.angular.z = 1.0      # 좌회전 각속도 → 반지름 = 2.0 / 1.0 = 2.0 의 원
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)        # ① rclpy(통신 계층) 초기화
    node = CircleTurtle()        # ② 노드 객체 생성 — 게시자·타이머가 이때 등록됨
    try:
        rclpy.spin(node)         # ③ 이벤트 루프 — 0.1초마다 콜백이 메시지를 발행
    except KeyboardInterrupt:    #    Ctrl+C 로 종료
        pass
    finally:
        node.destroy_node()      # ④ 노드 정리
        rclpy.try_shutdown()     # ⑤ rclpy 종료 (이미 종료됐으면 건너뜀)


if __name__ == '__main__':
    main()
