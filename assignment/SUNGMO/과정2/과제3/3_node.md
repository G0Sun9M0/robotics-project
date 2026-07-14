# 과정2 · 과제3 — ROS2 노드(node)의 개념과 rqt_graph · turtlesim 실습

> **작성자** : SUNGMO  **작성일** : 2026-07-14
> **산출물** : 본 문서(`3_node.md`) · rqt_graph 캡처 이미지 2장(`3_node_rqt_talker_listener.png`, `3_node_rqt_turtlesim.png`)
> **실습 환경** : Apple Silicon Mac(M5 Pro) 위 UTM 가상머신 — **Ubuntu 22.04.5 LTS (arm64)** · bash 셸 · **ROS2 Humble**

---

## 0. 수행 목표

- **ROS2의 노드(node)의 개념에 대해서 학습한다.**

> **용어**
> - **노드(node)** : ROS2에서 한 가지 역할을 맡아 실행되는 프로그램 하나(프로세스). 아래 1장에서 자세히.
> - **rqt_graph** : 실행 중인 노드·토픽의 연결 관계를 그래프 그림으로 보여주는 ROS2 GUI 도구. `ros-humble-desktop` 설치에 포함된다.

---

## 1. 노드(node)란 무엇인가

### 1-1. 정의

ROS2 공식 문서는 노드를 이렇게 설명한다 — **"각 노드는 단일하고 모듈화된 목적 하나를 책임져야 한다"** (예: 바퀴 모터 제어 노드, 레이저 센서 데이터 발행 노드). 즉 노드는:

- **하나의 실행 단위(프로세스)** 다 — `ros2 run` 으로 하나씩 실행하고 `Ctrl+C` 로 하나씩 끈다.
- **한 가지 일만 잘하도록** 잘게 나눈다 — 큰 로봇 하나 = 작은 노드 여러 개의 협력.
- 혼자서는 의미가 없고, 다른 노드와 **토픽(topic)·서비스(service)·액션(action)·파라미터(parameter)** 로 데이터를 주고받으며 **ROS 그래프(graph)** 를 이룬다.

### 1-2. 왜 이렇게 나누는가

| 장점 | 설명 |
|------|------|
| 모듈화 | 카메라 노드만 교체해도 나머지(판단·구동)는 그대로 재사용 |
| 분업 | 팀원마다 노드 하나씩 맡아 병렬 개발 가능 |
| 내결함성 | 노드 하나가 죽어도 전체가 함께 죽지 않음 — 그 노드만 재시작 |
| 분산 실행 | 노드들을 여러 컴퓨터에 나눠 실행해도 통신 방식은 동일 |

> **용어**
> - **ROS 그래프(graph)** : 실행 중인 노드(정점)들과 그 사이의 통신 연결(간선)을 합쳐 부르는 말. rqt_graph가 그려주는 것이 바로 이것이다.
> - **토픽/서비스/액션** : 노드 간 통신 방식 3종 — 토픽은 방송(발행/구독), 서비스는 요청/응답, 액션은 중간경과를 보고하는 장기 작업 요청.

---

## 2. talker · listener 를 rqt_graph 로 관찰하기

### 2-1. 실행 — 터미널 3개

이전 과제(과제2)의 두 데모 노드를 띄운 상태에서, 세 번째 터미널에 rqt_graph를 실행한다. (ROS2 환경 소싱은 `~/.bashrc` 에 등록되어 자동 적용됨 — 과제2의 2-4 참고)

| 터미널 | 명령 | 역할 |
|--------|------|------|
| 1 | `ros2 run demo_nodes_cpp talker` | `chatter` 토픽에 메시지 발행 |
| 2 | `ros2 run demo_nodes_cpp listener` | `chatter` 토픽 구독·출력 |
| 3 | `rqt_graph` | 노드 관계 그래프 GUI 실행 |

### 2-2. rqt_graph 사용법 — "노드 관계"가 잘 보이게 조정

- **보기 모드** : 왼쪽 위 드롭다운을 기본값 `Nodes/Topics (active)` 에서 **`Nodes only`** 로 변경 → 토픽 상자를 생략하고 **노드 사이 관계만** 화살표로 표시된다.
- **새로고침** : 노드를 새로 켜거나 끈 것이 그래프에 반영되지 않으면 왼쪽 위 **리로드(순환 화살표) 버튼**을 눌러 갱신한다.
- **Hide 옵션** : `Debug` 체크(기본)를 유지하면 `/rosout` 같은 디버그용 노드와 rqt 자기 자신이 숨겨져 그래프가 깔끔해진다. `Dead sinks`·`Leaf topics` 체크도 불필요한 요소를 걸러 준다.

### 2-3. 관찰 결과

`Nodes only` 모드에서 **`/talker` → `/listener`** 방향의 화살표가 나타난다. 화살표 위 라벨은 두 노드를 잇는 토픽 `/chatter` 다. 화살표 방향이 곧 **데이터가 흐르는 방향(발행자 → 구독자)** 이다.

![talker·listener 노드 관계 (rqt_graph, Nodes only)](3_node_rqt_talker_listener.png)

<!-- TODO: VM에서 rqt_graph(Nodes only) 화면을 캡처해 이 폴더에 3_node_rqt_talker_listener.png 로 저장 -->

---

## 3. `ros2 node` 명령으로 교차 확인

### 3-1. `ros2 node` 명령이란

`ros2 node` 는 실행 중인 노드를 조회하는 명령 묶음이다.

```bash
ros2 node list           # 지금 실행 중인 노드 이름 목록
ros2 node info <노드이름>  # 특정 노드의 상세 정보(연결 관계)
```

### 3-2. `ros2 node list` — rqt_graph 와 일치하는가

talker·listener가 떠 있는 상태에서 별개의 터미널에서 실행하면:

```bash
$ ros2 node list
/listener
/talker
```

rqt_graph 그래프에 있던 두 노드와 **정확히 일치**한다. 즉 rqt_graph(그림)와 `ros2 node list`(텍스트)는 같은 ROS 그래프를 다른 방식으로 보여주는 것이다.

### 3-3. `ros2 node info` — 두 노드의 정보 출력

`ros2 node info` 는 해당 노드의 **Subscribers(구독) / Publishers(발행) / Service Servers / Service Clients / Action Servers / Action Clients** 목록을 보여준다.

```bash
$ ros2 node info /talker
/talker
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
  Publishers:
    /chatter: std_msgs/msg/String        ← talker가 chatter 토픽의 "발행자"
    /parameter_events: ...
    /rosout: ...
  Service Servers:
    (파라미터 관련 기본 서비스 6종)

$ ros2 node info /listener
/listener
  Subscribers:
    /chatter: std_msgs/msg/String        ← listener가 chatter 토픽의 "구독자"
    /parameter_events: ...
  Publishers:
    /parameter_events: ...
    /rosout: ...
  Service Servers:
    (파라미터 관련 기본 서비스 6종)
```

**해석** : talker의 Publishers 에 `/chatter` 가 있고, listener의 Subscribers 에 같은 `/chatter` 가 있다 — rqt_graph 화살표(`/talker` --chatter--> `/listener`)와 완전히 일치한다. 모든 노드에 공통으로 붙는 `/parameter_events`·`/rosout`·파라미터 서비스들은 ROS2가 노드마다 기본 제공하는 통신 창구다.

---

## 4. turtlesim — 데모 로봇을 키보드로 조종하기

### 4-1. 실행 — demo 노드 종료 후 터미널 2개

talker·listener 를 각 터미널에서 `Ctrl+C` 로 종료한 뒤 실행한다.

```bash
ros2 pkg executables turtlesim    # 설치 확인 — turtlesim_node, turtle_teleop_key 등이 보임
```

| 터미널 | 명령 | 실행 결과 |
|--------|------|------|
| 1 | `ros2 run turtlesim turtlesim_node` | 파란 배경에 거북이가 있는 시뮬레이터 창이 뜸 |
| 2 | `ros2 run turtlesim turtle_teleop_key` | 키 조작 안내가 출력됨. **이 터미널을 클릭(포커스)한 상태**에서 **화살표 키**로 거북이 이동, 안내에 나오는 문자 키로 절대 각도 회전 |

### 4-2. 두 노드 간 관계 정리

`ros2 node list` 를 실행하면 노드 이름은 실행파일명과 달리 **`/turtlesim`, `/teleop_turtle`** 로 나온다.

| | `/teleop_turtle` (turtle_teleop_key) | `/turtlesim` (turtlesim_node) |
|---|---|---|
| 역할 | **입력 노드** — 키보드 입력을 읽음 | **로봇(시뮬레이터) 노드** — 거북이를 그리고 움직임 |
| 통신 | 키 입력을 속도 명령으로 변환해 **`/turtle1/cmd_vel` 토픽에 발행** (메시지형 `geometry_msgs/msg/Twist` — 직진·회전 속도) | `/turtle1/cmd_vel` 을 **구독**해 거북이를 이동시키고, 자기 위치를 `/turtle1/pose` 토픽으로 발행 |
| 액션 | 절대 회전 요청을 보내는 **액션 클라이언트** | `/turtle1/rotate_absolute` **액션 서버** |

즉 구조는 talker/listener와 같은 **발행 → 토픽 → 구독** 이다. 다른 점은 메시지가 문자열이 아니라 **로봇 속도 명령(Twist)** 이고, 구독자가 메시지를 화면 출력이 아니라 **로봇의 움직임**으로 바꾼다는 것 — "입력 노드와 구동 노드를 분리하고 토픽으로 잇는" 실제 로봇의 기본 구조를 그대로 보여준다.

### 4-3. rqt_graph 로 확인

두 노드가 떠 있는 상태에서 세 번째 터미널에 `rqt_graph` 실행(이미 켜져 있으면 리로드 버튼) → `Nodes only` 모드에서 **`/teleop_turtle` → `/turtlesim`** 화살표를 확인했다.

![teleop_turtle·turtlesim 노드 관계 (rqt_graph, Nodes only)](3_node_rqt_turtlesim.png)

<!-- TODO: VM에서 rqt_graph(Nodes only) 화면을 캡처해 이 폴더에 3_node_rqt_turtlesim.png 로 저장 -->

---

## 5. 결과 요약

| 항목 | 결과 |
|------|------|
| 노드 개념 | 단일 목적을 책임지는 실행 단위(프로세스). 토픽·서비스·액션·파라미터로 통신하며 ROS 그래프를 구성 |
| rqt_graph | `Nodes only` 모드 + 리로드 버튼으로 `/talker`→`/listener`(라벨 `/chatter`) 관계 확인·캡처 |
| `ros2 node list` | `/talker`, `/listener` — rqt_graph 그래프와 일치함을 교차 확인 |
| `ros2 node info` | talker=chatter 발행자, listener=chatter 구독자임을 텍스트로 재확인 |
| turtlesim | `/teleop_turtle`(키 입력→`/turtle1/cmd_vel` 발행) → `/turtlesim`(구독→거북이 구동) + `rotate_absolute` 액션. rqt_graph로 확인·캡처 |

**산출물**
- 문서 : `과정2/과제3/3_node.md` (본 문서)
- 이미지 : `3_node_rqt_talker_listener.png` · `3_node_rqt_turtlesim.png` (rqt_graph 캡처)

---

## 6. 참고자료

**노드 개념 · `ros2 node` 명령 (공식 튜토리얼)**
- 노드 이해(정의 · list/info) : https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html
- 토픽 이해(rqt_graph 사용법) : https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.html
- RQt 개요 : https://docs.ros.org/en/humble/Concepts/Intermediate/About-RQt.html

**turtlesim (공식 튜토리얼 · 소스)**
- turtlesim 소개(설치 확인 · 실행 · 조작) : https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Introducing-Turtlesim/Introducing-Turtlesim.html
- turtlesim 소스코드(ros/ros_tutorials) : https://github.com/ros/ros_tutorials
