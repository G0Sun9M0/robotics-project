# 과정2 · 과제6 — 콜백 함수와 ROS2 타이머 · 주기 동작 노드 실습

> **작성자** : SUNGMO  **작성일** : 2026-08-01
> **산출물** : 본 문서(`6_callback.md`) · 노드 소스(`timer_test.py`) · 소스 디렉토리 압축(`6_src.zip`)
> **실습 환경** : Apple Silicon Mac(M5 Pro) 위 UTM 가상머신 — **Ubuntu 22.04.5 LTS (arm64)** · bash 셸 · **ROS2 Humble** · 과제4~5의 워크스페이스와 `my_robot_controller` 패키지를 이어서 사용

---

## 0. 수행 목표

- **ROS2의 타이머와 콜백 사용법을 학습한다.**

과제5의 노드는 시작할 때 로그 한 줄을 남기고는 가만히 있기만 했다. 실제 로봇은 센서를 읽고 모터를 갱신하는 일을 **일정 주기로 반복**해야 한다. 이번 과제에서는 그 반복을 만드는 두 가지 재료 — **콜백 함수**와 **ROS2 타이머** — 를 배우고, 주기적으로 로그를 남기는 `timer_node` 를 만든다.

---

## 1. 콜백(callback) 함수란

### 1-1. 개념

**콜백 함수**는 내 코드가 직접 호출하는 함수가 아니라, **"이런 일이 생기면 이 함수를 불러 달라"고 시스템에 등록해 두는 함수**다. 이름 그대로 시스템이 나중에 "다시 불러주는(call back)" 함수다.

- 일반 함수 : 호출 시점을 **내 코드**가 결정 — `f()`
- 콜백 함수 : 호출 시점을 **시스템(프레임워크)** 이 결정 — 등록만 해 두면 조건(시간 도달, 데이터 수신, 버튼 클릭 등)이 충족될 때 시스템이 호출

이렇게 "호출의 주도권"이 내 코드에서 시스템으로 넘어가는 구조를 **제어의 역전(Inversion of Control)** 이라 부르며, GUI·네트워크·로봇처럼 **언제 일이 생길지 모르는 이벤트 중심 프로그램**의 기본 설계 방식이다.

### 1-2. 파이썬에서 콜백이 가능한 이유 — 함수는 1급 객체

파이썬의 함수는 **1급 객체(first-class object)** — 값처럼 변수에 담거나 **다른 함수의 인자로 전달**할 수 있다. 그래서 함수 "이름"을 그대로 넘겨 등록할 수 있다.

```python
def greet():
    print('hello')

f = greet      # 함수 자체를 변수에 담음 (호출 아님)
f()            # → hello  : 담아 둔 함수를 나중에 호출
```

> **주의 — 괄호 함정** : 등록할 때는 **괄호 없이 함수 이름만** 넘겨야 한다. `create_timer(2.0, self.callback)` 은 "나중에 불러 달라"는 등록이지만, `create_timer(2.0, self.callback())` 처럼 괄호를 붙이면 **그 자리에서 즉시 호출**되어 버려서 콜백의 반환값(None)이 등록되는 오류가 된다.

---

## 2. ROS2 타이머

### 2-1. 개념

**타이머(timer)** 는 **정해진 주기마다 등록된 콜백 함수를 호출해 주는 ROS2의 장치**다. "2초마다 이 함수를 실행해 줘"라고 등록해 두면, 노드가 살아 있는 동안 시스템이 그 주기를 지켜 콜백을 반복 호출한다. 지속적으로 동작하는 로봇 — 주기적인 센서 읽기, 제어 명령 발행, 상태 보고 — 의 뼈대가 되는 기능이다.

### 2-2. 생성과 사용 — `create_timer()`

타이머는 `Node` 클래스가 제공하는 `create_timer()` 메서드로 만든다 (그래서 노드 클래스의 `__init__` 안에서 만드는 것이 일반적이다).

```python
self.타이머변수 = self.create_timer(주기_초, 콜백함수)
```

| 인자 | 의미 |
|------|------|
| 주기(초) | 콜백을 호출할 간격. `float` 초 단위 (`2.0` = 2초) |
| 콜백함수 | 주기마다 호출될 함수 — **괄호 없이** 이름만 (1-2의 주의) |

반환되는 **Timer 객체**를 속성에 담아 두면 실행 중에 `cancel()`(일시 중지), `reset()`(재개) 으로 제어할 수도 있다.

### 2-3. spin과 타이머의 관계

과제5에서 `rclpy.spin(node)` 은 "노드를 실행 상태로 유지하는 블로킹 함수"였다. 정확히는 **이벤트 루프** — spin이 돌면서 "만기된 타이머가 있나? 도착한 데이터가 있나?"를 계속 살피다가, 조건이 충족된 콜백을 하나씩 꺼내 실행한다.

```
rclpy.spin(node)  ──  이벤트 루프
   │  2초 경과?  → timer_2s_callback() 실행
   │  3초 경과?  → timer_3s_callback() 실행
   └  (반복)
```

- **spin이 없으면 타이머도 없다** — 타이머를 만들어도 spin을 호출하지 않으면 콜백은 영원히 실행되지 않는다.
- 기본 설정에서 콜백은 **한 번에 하나씩 순차 실행**된다. 두 타이머가 같은 순간에 만기되어도(4-3) 콜백이 겹쳐 실행되며 값이 꼬이는 일은 없다.

> **용어**
> - **이벤트 루프(event loop)** : "기다리다 → 생긴 일(이벤트)에 맞는 콜백 실행 → 다시 기다림"을 반복하는 무한 루프. spin의 정체다.

---

## 3. 1차 — 2초 타이머 하나로 시작

### 3-1. 코드 (`timer_test.py` 1차 버전)

파일 위치는 과제5와 같은 파이썬 모듈 폴더다 — `~/ros2_ws/src/my_robot_controller/my_robot_controller/timer_test.py`

```python
import rclpy
from rclpy.node import Node


class TimerNode(Node):
    """2초마다 로그를 남기는 노드 — 타이머·콜백 첫 실습."""

    def __init__(self):
        super().__init__('timer_node')
        self.timer = self.create_timer(2.0, self.timer_callback)   # 2초 주기로 콜백 등록

    def timer_callback(self):
        self.get_logger().info('2 seconds passed')


def main(args=None):
    rclpy.init(args=args)
    node = TimerNode()
    try:
        rclpy.spin(node)         # 이벤트 루프 — 2초마다 timer_callback 을 호출
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
```

과제5의 `logging.py` 와 뼈대는 같고, 달라진 것은 두 가지뿐이다 — `__init__` 에서 **타이머를 등록**하고, 로그 기록이 생성 시 1회가 아니라 **콜백 안에서 주기적으로** 일어난다.

### 3-2. 실행 결과

setup.py 등록(5장)과 빌드(6장)를 마친 뒤 실행하면, 2초 간격으로 같은 로그가 반복된다.

```
[INFO] [1754...] [timer_node]: 2 seconds passed
[INFO] [1754...] [timer_node]: 2 seconds passed
[INFO] [1754...] [timer_node]: 2 seconds passed
```

<!-- TODO: VM에서 1차 실행 캡처(6_run1.png)를 이 폴더에 배치하고 이 주석을 이미지 링크로 교체 -->

타이머가 기대대로 동작하는 것을 확인했으면 **Ctrl+C** 로 종료하고 2차 확장으로 넘어간다.

---

## 4. 2차 — counter 속성과 타이머 두 개

### 4-1. 만들 동작

- 클래스 속성 `counter` 를 초기값 0으로 생성
- **2초 타이머** 콜백 : counter 를 **+1** 하고 값을 로그로 출력
- **3초 타이머** 콜백 : counter 를 **−1** 하고 값을 로그로 출력

### 4-2. 코드 (`timer_test.py` 최종본)

```python
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
```

- 타이머는 몇 개든 만들 수 있고, 각 타이머가 자기 주기대로 독립적으로 콜백을 호출한다.
- 두 콜백 모두 `self.counter` 라는 **같은 속성을 공유**한다 — 값을 먼저 바꾼 뒤 바뀐 값을 출력한다.

### 4-3. 실행 로그 해석

```
[INFO] [...] [timer_node]: 2 seconds passed : 1     ← 2초: 0+1=1
[INFO] [...] [timer_node]: 3 seconds passed : 0     ← 3초: 1−1=0
[INFO] [...] [timer_node]: 2 seconds passed : 1     ← 4초: 0+1=1
[INFO] [...] [timer_node]: 2 seconds passed : 2     ← 6초: 1+1=2   ┐ 같은 순간
[INFO] [...] [timer_node]: 3 seconds passed : 1     ← 6초: 2−1=1   ┘ 연달아 실행
[INFO] [...] [timer_node]: 2 seconds passed : 2     ← 8초: 1+1=2
```

- **6초마다(2와 3의 최소공배수)** 두 타이머가 같은 순간에 만기된다. 이때도 spin은 콜백을 **하나씩 순차 실행**(2-3)하므로 로그 두 줄이 연달아 찍히고 counter 값은 꼬이지 않는다.
- 6초 동안 +1이 3번, −1이 2번이므로 **counter 는 6초마다 순증가 +1** — 로그를 길게 보면 값이 계단식으로 올라간다.

<!-- TODO: VM에서 2차 실행 캡처(6_run2.png)를 이 폴더에 배치하고 이 주석을 이미지 링크로 교체 -->

---

## 5. setup.py 등록 — 두 번째 진입점

과제5에서 등록한 `logging_node` 아래에 `timer_node` 를 **추가**한다 (기존 줄은 그대로 둔다).

```python
    entry_points={
        'console_scripts': [
            'logging_node = my_robot_controller.logging:main',
            'timer_node = my_robot_controller.timer_test:main',
        ],
    },
```

이로써 한 패키지가 실행파일 두 개(`logging_node`·`timer_node`)를 제공하게 된다 — 로봇 하나가 여러 노드로 구성되는 ROS2 구조 그대로다.

---

## 6. 빌드와 실행 — 언제 재빌드가 필요한가

```bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 run my_robot_controller timer_node
```

과제5에서 배운 `--symlink-install` 의 효과를 이번 과제에서 정확히 체감할 수 있다.

| 상황 | 재빌드 필요? | 이유 |
|------|------|------|
| **새 진입점 등록** (setup.py 수정, timer_node 추가) | **필요** | 실행파일은 빌드 때 만들어지므로 |
| **코드 내용 수정** (1차 → 2차 확장) | **불필요** | 소스가 심볼릭 링크로 설치되어 수정이 즉시 반영 — Ctrl+C 후 `ros2 run` 만 다시 하면 됨 |

---

## 7. 결과 요약

| 항목 | 결과 |
|------|------|
| 콜백 함수 | 시스템에 등록해 두면 조건 충족 시 시스템이 호출하는 함수 — 파이썬 함수가 1급 객체라 이름만(괄호 없이) 넘겨 등록 |
| 타이머 | `self.create_timer(주기초, 콜백)` — 주기마다 콜백 호출, `cancel()`/`reset()` 제어 가능 |
| spin과의 관계 | spin = 이벤트 루프. 만기된 타이머의 콜백을 하나씩 순차 실행 — spin 없이는 콜백도 없음 |
| 1차 실습 | 2초 타이머 1개 → `2 seconds passed` 반복 기록 확인 후 Ctrl+C |
| 2차 실습 | `counter`(초기 0) + 2초 +1 / 3초 −1 타이머 2개, 콜백마다 값 출력 — 6초마다 순증가 +1 패턴 확인 |
| setup.py | `'timer_node = my_robot_controller.timer_test:main'` 추가 — 한 패키지에 실행파일 2개 |
| 재빌드 기준 | 진입점 추가 = 재빌드 필요 / 코드 수정 = symlink 덕에 불필요 |

**산출물**
- 문서 : `과정2/과제6/6_callback.md` (본 문서)
- 소스 : `과정2/과제6/timer_test.py` — VM의 `~/ros2_ws/src/my_robot_controller/my_robot_controller/timer_test.py` 와 동일본(최종본)
- 압축 : `6_src.zip` — 워크스페이스의 **src 디렉토리** 압축 (빌드 산출물·파이썬 캐시 제외)

```bash
cd ~/ros2_ws
zip -r 6_src.zip src -x "*__pycache__*"
```

<!-- TODO: VM에서 만든 6_src.zip 을 이 폴더에 배치 -->

---

## 8. 참고자료

**타이머 · 콜백 (공식 튜토리얼 · API)**
- 파이썬 노드에서 create_timer 로 콜백 등록(퍼블리셔 예제) : https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html
- rclpy 타이머 API 문서 : https://docs.ros2.org/foxy/api/rclpy/api/timers.html
- 콜백을 실행하는 실행기(Executor) 개념 : https://docs.ros.org/en/humble/Concepts/Intermediate/About-Executors.html
- 파이썬 공식 용어집의 callback 정의 : https://docs.python.org/3/glossary.html
- rclpy 소스코드(ros2/rclpy) : https://github.com/ros2/rclpy

**빌드 · 실행 (공식 튜토리얼)**
- colcon 으로 패키지 빌드하기(--symlink-install) : https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html
- 첫 ROS2 패키지 만들기(빌드 후 소싱·ros2 run) : https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html
