# 과정2 · 과제4 — ROS2 패키지와 파이썬 빌드 시스템(ament_python) · 워크스페이스 실습

> **작성자** : SUNGMO  **작성일** : 2026-07-17
> **산출물** : 본 문서(`4_ros2_package.md`) · 워크스페이스 소스 디렉토리 압축(`4_src.zip`)
> **실습 환경** : Apple Silicon Mac(M5 Pro) 위 UTM 가상머신 — **Ubuntu 22.04.5 LTS (arm64)** · bash 셸 · **ROS2 Humble**

---

## 0. 수행 목표

- **ROS2의 패키지 및 파이썬 빌드 시스템에 대해서 알아본다.**

> **용어**
> - **패키지(package)** : ROS2 소프트웨어의 배포·설치 단위. 노드 실행파일·라이브러리·설정을 묶은 꾸러미 (과제2의 3장 참고).
> - **빌드 시스템(build system)** : 소스코드를 "실행 가능한 형태로 만들어 정해진 위치에 설치"하는 절차를 자동화하는 도구. C++은 컴파일이 필요하고 파이썬은 복사·등록만 하면 되므로, 언어마다 쓰는 빌드 시스템이 다르다.

---

## 1. 워크스페이스와 src 디렉토리

### 1-1. 워크스페이스란

**워크스페이스(workspace)** 는 ROS2 개발의 작업 공간이 되는 디렉토리다. 앞으로 `~/ros2_ws` 로 표기하며(이름·위치는 자유지만 "워크스페이스 디렉토리"라 하면 이 디렉토리를 뜻한다), 규칙은 두 가지다.

- 내가 만들거나 받은 **패키지 소스는 전부 `src/` (소스 디렉토리)** 아래에 둔다.
- **빌드는 워크스페이스 루트에서** 실행한다 → 결과물이 `build/`·`install/`·`log/` 에 생긴다.

```bash
mkdir -p ~/ros2_ws/src    # 워크스페이스와 소스 디렉토리를 한 번에 생성
cd ~/ros2_ws
```

### 1-2. 왜 이런 구조인가 — 오버레이

`/opt/ros/humble/` 의 시스템 설치본(**언더레이**) 위에, 내 워크스페이스의 `install/` 을 **오버레이**로 겹쳐 쓰는 구조다. 같은 이름의 패키지가 있으면 워크스페이스 쪽이 우선하므로, 시스템을 건드리지 않고 내 패키지를 개발·실험할 수 있다.

> **용어**
> - **언더레이(underlay) / 오버레이(overlay)** : 기반이 되는 ROS2 설치 환경 / 그 위에 겹쳐 소싱하는 내 작업 환경. `source /opt/ros/humble/setup.bash`(언더레이) 후 `source ~/ros2_ws/install/setup.bash`(오버레이) 순으로 읽어 들인다.

---

## 2. colcon — ROS2의 빌드 명령어

### 2-1. colcon이란

**colcon(collective construction)** 은 워크스페이스 안의 **여러 패키지를 의존성 순서에 맞춰 한꺼번에 빌드**해 주는 ROS2 표준 빌드 도구다. 패키지마다 빌드 방식(ament_cmake·ament_python 등)이 달라도 colcon이 각 패키지의 `package.xml` 을 읽어 알맞은 빌드 시스템을 자동으로 호출한다.

| 자주 쓰는 명령 | 설명 |
|------|------|
| `colcon build` | src 아래 전체 패키지 빌드 |
| `colcon build --packages-select <이름>` | 지정한 패키지만 빌드 |
| `colcon build --symlink-install` | 파이썬 소스를 복사 대신 링크로 설치 — 수정이 즉시 반영돼 개발 시 편리 |
| `colcon list` | 워크스페이스의 패키지 목록 |

### 2-2. `colcon: command not found` — 건너뛴 설치 단계 찾기

워크스페이스에서 처음 `colcon build` 를 실행하면 **command not found** 가 난다. 원인을 추적해 보니, ROS2 공식 설치 문서(과제2에서 사용)의 마지막에 **개발 도구 설치** 단계가 별도로 있는데 과제2에서는 `ros-humble-desktop` 까지만 설치하고 이 단계를 건너뛰었기 때문이다. `ros-humble-desktop` 은 데모·RViz 등 **실행 도구** 묶음이고, colcon 같은 **개발 도구**는 `ros-dev-tools` 라는 별도 패키지로 분리되어 있다.

```bash
sudo apt update
sudo apt install ros-dev-tools    # colcon 포함 — 과제2에서 건너뛴 단계 보완
```

### 2-3. 빈 워크스페이스 빌드

패키지가 하나도 없는 상태에서 워크스페이스 루트에서 빌드해 본다.

```bash
cd ~/ros2_ws      # 반드시 워크스페이스 루트에서 (src 안이 아님)
colcon build
```

```
Summary: 0 packages finished [ ... ]
```

빌드할 패키지가 0개여도 colcon은 정상 동작하며, 워크스페이스에 다음 3개 디렉토리를 만든다.

| 디렉토리 | 역할 |
|------|------|
| `build/` | 빌드 중간 산출물 |
| `install/` | 설치 결과 — 이 안의 `setup.bash` 를 소싱하면 내 패키지를 `ros2 run` 으로 실행 가능 |
| `log/` | 빌드 로그 |

---

## 3. 파이썬 빌드 시스템 — ament_python

ROS2에서 패키지를 만들 때 지정하는 **빌드 타입(build type)** 은 대표적으로 두 가지다.

| 빌드 타입 | 대상 언어 | 동작 방식 |
|------|------|------|
| `ament_cmake` | C++ | CMake로 **컴파일**해 실행파일 생성 |
| **`ament_python`** | **Python** | 컴파일 없이 파이썬 표준 배포 도구 **setuptools** 로 소스를 `install/` 에 설치하고 실행 진입점을 등록 |

**ament_python** 은 "파이썬의 표준 패키징 도구(setuptools)를 ROS2 규칙(ament)에 맞게 감싼 것"이다. 그래서 ament_python 패키지의 설치 방법은 파이썬 생태계의 표준 파일인 `setup.py` 에 기술한다(7장).

> **용어**
> - **ament** : ROS2의 빌드 규약·도구 모음의 이름. colcon이 "여러 패키지를 순서대로"를 담당한다면, ament는 "패키지 하나를 어떻게 빌드·설치하는가"의 규칙을 담당한다.
> - **setuptools** : 파이썬 패키지를 설치·배포하는 파이썬 표준 라이브러리. `setup.py` 를 읽어 동작한다.

---

## 4. `ros2 pkg create` — 패키지 생성

### 4-1. 사용법

```bash
ros2 pkg create <패키지이름> [옵션]
```

| 주요 옵션 | 설명 |
|------|------|
| `--build-type <타입>` | 빌드 시스템 지정 (`ament_python` / `ament_cmake`) |
| `--dependencies <패키지...>` | 의존하는 패키지를 `package.xml` 에 미리 등록 |
| `--node-name <이름>` | 예제 노드 소스까지 함께 생성 (이번엔 사용 안 함) |
| `--license <라이선스>` | 라이선스 지정 |

### 4-2. my_robot_controller 패키지 생성

패키지 생성은 **소스 디렉토리(src) 안에서** 실행한다.

```bash
cd ~/ros2_ws/src
ros2 pkg create my_robot_controller --build-type ament_python --dependencies rclpy
```

- `--build-type ament_python` : 파이썬 빌드 시스템 지정 (3장)
- `--dependencies rclpy` : rclpy 의존성을 `package.xml` 에 자동 등록 (4-3)

실행하면 `going to create a new package` 메시지와 함께 패키지 뼈대 파일들이 생성된다. (라이선스를 지정하지 않아 `No license file` 경고가 나오지만 실습 진행에는 지장 없다.)

### 4-3. rclpy란

**rclpy(ROS Client Library for Python)** 는 **파이썬 코드에서 ROS2 기능(노드 생성, 토픽 발행/구독, 서비스, 파라미터 등)을 사용할 수 있게 해 주는 공식 파이썬 클라이언트 라이브러리**다. 파이썬으로 제어 노드를 만들려면 반드시 rclpy를 import 하므로, 패키지 생성 시점에 의존성으로 선언해 둔 것이다.

내부적으로는 계층 구조다 — 파이썬(rclpy)·C++(rclcpp) 클라이언트 라이브러리는 공통 C 라이브러리 **rcl** 의 얇은 언어 바인딩이고, rcl 아래에서 **rmw**(미들웨어 인터페이스)가 DDS 통신(과제2의 1장)을 담당한다. 어떤 언어로 짜도 같은 통신 규칙을 따르는 이유다.

```
 [내 파이썬 코드] → rclpy → rcl → rmw → DDS (실제 통신)
```

---

## 5. tree 로 워크스페이스 구조 확인

### 5-1. tree 설치와 실행

**tree** 는 디렉토리 구조를 나무(tree) 모양으로 출력해 주는 리눅스 프로그램이다. apt로 설치한다.

```bash
sudo apt install tree
cd ~/ros2_ws
tree src          # 소스 디렉토리 구조
tree -L 2 .       # 워크스페이스 전체는 깊이 2로 제한(빌드 산출물이 방대하므로)
```

### 5-2. 실행 결과

패키지 생성 직후 소스 디렉토리 구조는 다음과 같다.

```
src
└── my_robot_controller
    ├── my_robot_controller        ← 패키지와 같은 이름의 파이썬 모듈 폴더 (노드 코드가 들어갈 곳)
    │   └── __init__.py
    ├── package.xml                ← ROS2 패키지 명세서 (6장)
    ├── resource
    │   └── my_robot_controller    ← ROS2가 패키지를 색인하기 위한 표식 파일(빈 파일)
    ├── setup.cfg                  ← 실행파일 설치 경로 설정
    ├── setup.py                   ← 파이썬 설치 스크립트 (7장)
    └── test
        ├── test_copyright.py      ← 자동 생성된 코드 스타일 검사 테스트 3종
        ├── test_flake8.py
        └── test_pep257.py
```

<!-- TODO: VM에서 실제 `tree src` 출력(4_tree_output.txt)으로 위 블록을 교체 -->

빈 빌드(2-3) 후의 워크스페이스 루트는 `build/`·`install/`·`log/`·`src/` 4개 디렉토리로 구성된다.

<!-- TODO: VM에서 `tree -L 2 .` 출력(4_tree_ws.txt)을 여기에 추가 -->

---

## 6. package.xml — ROS2 패키지 명세서

### 6-1. 역할

**package.xml** 은 ROS2 생태계를 향한 **패키지 정보 명세서(매니페스트)** 다. 모든 ROS2 패키지가 빌드 타입과 무관하게 반드시 가져야 하며, 두 가지 일을 한다.

1. **메타데이터 제공** — 이름·버전·설명·관리자·라이선스
2. **의존성 선언** — 이 패키지가 어떤 패키지를 필요로 하는지. **colcon이 이 정보를 읽어 여러 패키지의 빌드 순서를 결정**하고, `rosdep` 같은 도구가 부족한 의존성을 자동 설치할 때도 사용한다.

### 6-2. 생성된 내용과 구조

```xml
<?xml version="1.0"?>
<package format="3">
  <name>my_robot_controller</name>            <!-- 패키지 이름 -->
  <version>0.0.0</version>                    <!-- 버전 -->
  <description>TODO: Package description</description>
  <maintainer email="...">gosungmo</maintainer>
  <license>TODO: License declaration</license>

  <depend>rclpy</depend>                      <!-- --dependencies 옵션으로 등록된 의존성 -->

  <test_depend>ament_copyright</test_depend>  <!-- 테스트에만 필요한 의존성 -->
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>     <!-- colcon에게 알려줄 빌드 타입 -->
  </export>
</package>
```

| 핵심 태그 | 의미 |
|------|------|
| `<name>`·`<version>`·`<description>`·`<maintainer>`·`<license>` | 패키지 메타데이터 (TODO 부분은 개발자가 채움) |
| `<depend>` | 빌드·실행 모두에 필요한 의존성 — `--dependencies rclpy` 가 여기에 들어감 |
| `<test_depend>` | 테스트에만 필요한 의존성 |
| `<export><build_type>` | 이 패키지를 **ament_python** 방식으로 빌드하라고 colcon에 알림 |

---

## 7. setup.py — 파이썬 설치 스크립트

### 7-1. 역할

**setup.py** 는 setuptools가 읽는 **파이썬 설치 스크립트**로, ament_python 패키지에서 "**무엇을 어디에 설치하고, 어떤 실행 명령을 만들 것인가**"를 정의한다. package.xml이 "ROS 세계에 대한 선언"이라면, setup.py는 "파이썬 세계의 실제 설치 방법"이다.

### 7-2. 생성된 내용과 구조

```python
from setuptools import find_packages, setup

package_name = 'my_robot_controller'

setup(
    name=package_name,                        # 패키지 이름 (package.xml과 일치해야 함)
    version='0.0.0',                          # 버전 (package.xml과 일치해야 함)
    packages=find_packages(exclude=['test']), # 설치할 파이썬 모듈 폴더 자동 탐색
    data_files=[                              # 코드 외에 함께 설치할 파일들
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),    #   ← ROS2 패키지 색인 등록용 표식
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gosungmo',
    maintainer_email='...',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # '실행이름 = my_robot_controller.모듈명:main'  ← 노드 등록 자리
        ],
    },
)
```

| 핵심 항목 | 의미 |
|------|------|
| `packages` | 설치할 파이썬 모듈 폴더 (`my_robot_controller/`) |
| `data_files` | package.xml과 색인 표식 파일을 설치 위치에 복사 — ROS2가 패키지를 찾게 하는 장치 |
| **`entry_points` → `console_scripts`** | **가장 중요** — `'이름 = 패키지.모듈:main'` 형식으로 등록하면 빌드 후 `ros2 run my_robot_controller 이름` 으로 실행할 수 있는 **노드 실행파일이 만들어진다**. 다음 과제에서 노드 코드를 작성하면 여기에 등록하게 된다 |

> **참고 — setup.cfg** : 함께 생성되는 `setup.cfg` 는 실행파일을 `lib/<패키지이름>/` 아래에 설치하도록 경로를 지정하는 보조 설정 파일이다. `ros2 run` 이 실행파일을 찾는 위치가 바로 여기다.

### 7-3. 두 파일의 역할 비교 정리

| | **package.xml** | **setup.py** |
|---|---|---|
| 소속 세계 | ROS2 생태계 (모든 빌드 타입 공통) | 파이썬 생태계 (ament_python 전용) |
| 성격 | 패키지 정보 **명세서** — 무엇에 의존하는가 | 설치 **스크립트** — 무엇을 어디에 설치하는가 |
| 주 사용자 | colcon(빌드 순서)·rosdep(의존성 설치) | setuptools(실제 설치 수행) |
| 핵심 내용 | 메타데이터, `<depend>`, `<build_type>` | `packages`, `data_files`, `entry_points(console_scripts)` |

---

## 8. 결과 요약

| 항목 | 결과 |
|------|------|
| 워크스페이스 | `~/ros2_ws` 생성, 소스는 `src/` 아래 — 언더레이(/opt/ros/humble) 위에 오버레이로 동작 |
| colcon | 여러 패키지를 의존성 순서로 빌드하는 ROS2 표준 빌드 도구. `ros-humble-desktop`에 미포함 → 과제2에서 건너뛴 `ros-dev-tools` 설치로 해결 |
| 빈 빌드 | `colcon build` → `Summary: 0 packages finished`, `build/`·`install/`·`log/` 생성 확인 |
| 패키지 생성 | `ros2 pkg create my_robot_controller --build-type ament_python --dependencies rclpy` |
| ament_python | setuptools를 ament 규칙으로 감싼 **파이썬용 빌드 시스템** — 컴파일 없이 설치·진입점 등록 |
| rclpy | 파이썬용 ROS2 **클라이언트 라이브러리** — rclpy → rcl → rmw → DDS 계층으로 동작 |
| tree | 패키지 뼈대 구조(모듈 폴더·package.xml·setup.py·setup.cfg·resource·test) 확인·기록 |
| package.xml vs setup.py | ROS 생태계용 명세서(의존성 선언) vs 파이썬 설치 스크립트(설치 대상·`console_scripts` 실행 등록) |

**산출물**
- 문서 : `과정2/과제4/4_ros2_package.md` (본 문서)
- 압축 : `4_src.zip` — 워크스페이스의 `src/` 디렉토리 압축 (`build/`·`install/`·`log/` 는 빌드 시 재생성되는 산출물이므로 제외)

<!-- TODO: VM에서 만든 4_src.zip 을 이 폴더에 배치 -->

---

## 9. 참고자료

**워크스페이스 · colcon (공식 튜토리얼)**
- colcon으로 패키지 빌드하기 : https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html
- 워크스페이스 만들기(오버레이 개념) : https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-A-Workspace/Creating-A-Workspace.html
- colcon 공식 문서 : https://colcon.readthedocs.io/
- 개발 도구(ros-dev-tools) 설치 단계가 있는 공식 설치 문서 : https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html

**패키지 생성 · 빌드 시스템 · rclpy (공식 문서)**
- 첫 ROS2 패키지 만들기(`ros2 pkg create`, package.xml·setup.py 설명) : https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html
- ROS2 패키지 개발(ament_python 구조) : https://docs.ros.org/en/humble/How-To-Guides/Developing-a-ROS-2-Package.html
- rclpy API 문서 : https://docs.ros2.org/foxy/api/rclpy/index.html
- rclpy 소스코드(ros2/rclpy) : https://github.com/ros2/rclpy
