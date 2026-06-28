# line_follower_agv (ROS2 패키지)

라인트레이싱 운반 로봇(AGV)의 소프트웨어를 ROS2(노드+토픽) 구조로 구현한 패키지.
요구사항 ①~④를 노드 단위로 분리했다.

## 노드 구성 (요구사항 매핑)
| 노드 | 역할 | 요구 | 구독 | 발행 |
|---|---|---|---|---|
| `sensor_node` | 적외선 어레이·초음파 읽기, 오차 계산 | ① | — | `/line_error`, `/obstacle_distance` |
| `controller_node` | PID 제어 → 주행/조향, 장애물 정지 | ② | `/line_error`, `/obstacle_distance` | `/cmd_vel` |
| `data_logger_node` | 이동 데이터 CSV 저장 | ③ | `/odom`, `/line_error`, `/obstacle_distance`, `/cmd_vel` | (CSV 파일) |
| `mqtt_bridge_node` | 텔레메트리 MQTT 실시간 전송 | ④ | `/odom`, `/line_error`, `/obstacle_distance` | (MQTT 토픽) |

> `/odom`(위치·속도·회전각)과 `/cmd_vel`을 모터로 구동하는 부분은 베이스 드라이버(예: micro-ROS,
> ros2_control, 또는 모터/엔코더 드라이버 노드)가 담당한다. 이 패키지는 그 위의 인식·제어·기록·전송을 다룬다.

## 토픽 흐름
```
sensor_node ──/line_error──────────▶ controller_node ──/cmd_vel──▶ (베이스 드라이버 → 모터)
            └─/obstacle_distance──▶ ┘
(베이스 드라이버) ──/odom──▶ data_logger_node ──▶ CSV (요구③)
                          └─▶ mqtt_bridge_node ──▶ MQTT (요구④)
```

## 빌드 & 실행 (ROS2 Humble 기준)
```bash
# 1) 워크스페이스 루트에서 빌드
cd ros2_ws
colcon build --packages-select line_follower_agv
source install/setup.bash

# 2) 전체 노드 한 번에 실행
ros2 launch line_follower_agv line_follower.launch.py

# (개별 실행 예)
ros2 run line_follower_agv sensor_node
ros2 run line_follower_agv controller_node --ros-args -p kp:=1.0 -p kd:=0.3
```

## 의존성
- ROS2 (Humble 등), `rclpy`, `std_msgs`, `geometry_msgs`, `nav_msgs`
- MQTT 전송용: `pip install paho-mqtt` (미설치 시 전송만 비활성, 나머지는 정상 동작)

## 참고
- 센서 읽기(`read_ir_array`, `read_ultrasonic`)와 베이스 드라이버는 하드웨어 의존부라
  실제 로봇에서는 GPIO/ADC/모터 드라이버 코드로 교체한다. 본 과제에서는 구조 이해용 더미값.
