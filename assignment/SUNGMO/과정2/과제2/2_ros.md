# 과정2 · 과제2 — ROS2(Humble) 설치와 `ros2 run` 실습

> **작성자** : SUNGMO  **작성일** : 2026-07-14
> **산출물** : 본 문서(`2_ros.md`) · 데모 실행 캡처 이미지(`2_ros_talker_listener.png`)
> **실습 환경** : Apple Silicon Mac(M5 Pro) 위 UTM 가상머신 — **Ubuntu 22.04.5 LTS (arm64)** · bash 셸 · **ROS2 Humble**

---

## 0. 수행 목표

- **ROS2에 대해서 조사**하고, **ROS2 활용 실습 환경을 구성**한다.
- **`ros2 run` 명령의 사용법을 학습**한다.

> **용어**
> - **ROS2 (Robot Operating System 2)** : 로봇 소프트웨어를 여러 개의 작은 프로그램(노드)으로 나눠 서로 메시지를 주고받게 하는 로봇 소프트웨어 프레임워크. 이름에 OS가 들어가지만 윈도우·리눅스 같은 진짜 운영체제는 아니다(아래 1장).
> - **Humble (Humble Hawksbill)** : ROS2의 배포본(버전) 이름 중 하나. Ubuntu 22.04와 짝을 이루는 LTS(장기지원) 배포본이다.

---

## 1. 로봇 운영체제의 개념

### 1-1. "로봇 운영체제"란 무엇인가

ROS는 이름과 달리 **컴퓨터 운영체제(윈도우·리눅스)를 대체하는 것이 아니라, 운영체제 위에서 동작하는 미들웨어(소프트웨어 프레임워크)** 다. 리눅스가 CPU·메모리·파일을 관리해 준다면, ROS는 그 위에서 **로봇 개발에 공통으로 필요한 기능**을 표준화해 제공한다.

| ROS가 제공하는 것 | 설명 |
|------|------|
| **하드웨어 추상화** | 모터·센서 제조사가 달라도 같은 방식(토픽·메시지)으로 다루게 함 |
| **프로세스 간 통신** | 노드끼리 메시지를 주고받는 발행/구독(pub/sub) 통신 — ROS2는 산업 표준 **DDS** 기반 |
| **패키지 생태계** | 남이 만든 주행·비전·SLAM 패키지를 `apt`로 받아 조립하듯 재사용 |
| **개발 도구** | 시각화(RViz)·시뮬레이션(Gazebo)·로그·디버깅 도구 일체 |

> **용어**
> - **미들웨어(middleware)** : 운영체제와 응용 프로그램 사이(middle)에서 공통 기능을 제공하는 소프트웨어 계층.
> - **DDS (Data Distribution Service)** : 데이터를 발행/구독 방식으로 실시간 분배하는 산업 표준 통신 규격. ROS2가 노드 간 통신에 사용한다.

### 1-2. 운영체제를 사용하는 로봇 vs 사용하지 않는 로봇

| 구분 | OS(ROS) 없이 동작하는 로봇 | OS(리눅스+ROS) 위에서 동작하는 로봇 |
|------|------|------|
| 구조 | 마이크로컨트롤러(MCU)에 **펌웨어 하나**를 구워 넣음(베어메탈) | 리눅스 컴퓨터 위에서 **여러 노드(프로그램)** 가 동시에 협력 |
| 예시 | 라인트레이서 키트, 로봇청소기 하위 제어보드, 아두이노 로봇 | 자율주행차, 물류로봇(AGV/AMR), 연구용 로봇팔 |
| 장점 | 단순·저렴·부팅 즉시 동작·**정밀한 실시간 제어**에 유리 | 모듈화·재사용·팀 분업·시뮬레이션 연동·복잡한 판단(비전·SLAM) 가능 |
| 단점 | 기능이 커지면 코드가 뒤엉키고 재사용 어려움 | 컴퓨터급 하드웨어 필요, OS 스케줄링 때문에 마이크로초 단위 실시간성은 별도 보강 필요 |
| 개발 방식 | 센서 읽기~모터 출력까지 한 덩어리 코드 | 센서 노드·판단 노드·구동 노드로 분리, 메시지로 연결 |

실제 제품은 두 방식을 **함께** 쓰는 경우가 많다 — 밀리초가 급한 모터 제어는 MCU 펌웨어가 맡고, 경로 계획·인식 같은 상위 판단은 리눅스+ROS가 맡아 서로 통신하는 구조다.

---

## 2. 우분투에 ROS2(Humble) 설치하기

### 2-1. 배포본 선택 — 왜 Humble + Ubuntu 22.04인가

ROS2는 매년 새 배포본이 나오고, **각 배포본은 특정 우분투 버전과 짝**을 이룬다(REP 2000 문서에 명시). **Humble ↔ Ubuntu 22.04(jammy)** 가 그 짝이며, Humble은 LTS라 자료가 가장 풍부하다. 내 환경(Ubuntu 22.04.5 **arm64**)도 Humble의 **Tier-1 공식 지원 플랫폼**이라 그대로 설치 가능하다.

### 2-2. 설치 방법 조사

| 방법 | 설명 | 선택 |
|------|------|------|
| **deb 패키지 설치(apt)** | 공식 저장소를 등록하고 `apt install` — 공식 권장, 업데이트 쉬움 | ✅ 선택 |
| 소스 빌드 | 소스코드를 직접 컴파일 — ROS2 자체를 수정할 때만 필요 | ✗ |

> **참고 — 설치 방식 변경(2025년~)** : 예전 자료는 GPG 키를 `curl`로 받아 수동 등록하는 방법을 안내하지만, 현재 공식 문서는 키·저장소 등록을 한 번에 처리하는 **`ros2-apt-source.deb` 패키지 설치 방식**으로 바뀌었다. 아래는 현재 공식 문서의 방법이다.

### 2-3. 실제 설치 명령 (Ubuntu 22.04 터미널에서 순서대로)

**① 로케일이 UTF-8인지 확인·설정**

```bash
locale   # LANG 값에 UTF-8 이 보이면 ②로 건너뜀

sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

**② universe 저장소 활성화**

```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
```

**③ ROS2 apt 저장소 등록 (`ros2-apt-source.deb`)**

```bash
sudo apt update && sudo apt install curl -y
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
```

**④ ROS2 Humble 설치 (데스크톱 풀 구성 — 데모·RViz 포함)**

```bash
sudo apt update
sudo apt upgrade
sudo apt install ros-humble-desktop
```

**⑤ 설치 확인**

```bash
source /opt/ros/humble/setup.bash
ros2 --help                          # ros2 명령이 인식되는지
ros2 pkg list | grep demo_nodes      # 데모 패키지가 설치됐는지
```

`demo_nodes_cpp`, `demo_nodes_py` 가 목록에 보이면 설치 완료다.

> **왜 파이썬을 따로 안 깔았나** : ROS2 Humble은 우분투 **기본 시스템 파이썬(3.10)** 에 맞춰 배포된다. Homebrew·pyenv 파이썬을 끼우면 `rclpy` 등이 깨지므로 기본 파이썬을 그대로 쓴다(과제1에서 정리).

### 2-4. 환경 설정 — `source` 로 ROS2 환경 불러오기

설치가 끝나도 새 터미널에서 바로 `ros2` 를 치면 **command not found** 가 난다. ROS2는 `/opt/ros/humble/` 아래에 설치될 뿐, 셸이 그 위치를 알게 하려면 **터미널마다** 환경 설정 스크립트를 읽어 들여야 한다.

```bash
source /opt/ros/humble/setup.bash
```

이 한 줄이 `PATH`, `AMENT_PREFIX_PATH`, `PYTHONPATH` 등 환경변수를 현재 셸에 등록해 `ros2` 명령과 패키지들을 찾을 수 있게 한다. 매번 치기 번거로우면 bash 시작 파일에 등록해 자동화한다.

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc   # 새 터미널마다 자동 적용
```

---

## 3. 패키지와 노드의 관계

| 개념 | 정의 | 비유 |
|------|------|------|
| **패키지(package)** | ROS2 소프트웨어의 **배포·설치 단위**. 노드 실행파일·라이브러리·설정을 묶은 꾸러미 | 스마트폰의 "앱 하나" (설치 단위) |
| **노드(node)** | 패키지 안에 들어 있는 **실행 단위**. 한 가지 일을 맡는 하나의 프로그램(프로세스) | 앱 안의 "기능 하나" (실행 단위) |

- 관계는 **1(패키지) : N(노드)** — 한 패키지 안에 여러 노드가 들어 있다.
- 이번 실습의 `demo_nodes_cpp` 패키지 안에는 `talker`, `listener` 를 비롯한 여러 데모 노드가 들어 있다.
- 실행 중인 각 노드는 독립된 프로세스로 돌고, 서로 **토픽(topic)** 등으로 메시지를 주고받는다.

```bash
ros2 pkg list                            # 설치된 패키지 전체 목록
ros2 pkg executables demo_nodes_cpp     # 이 패키지 안의 실행파일(노드) 목록
```

---

## 4. `ros2 run` 명령 사용법

`ros2 run` 은 **패키지 이름과 실행파일 이름을 지정해 노드 하나를 실행**하는 명령이다.

```bash
ros2 run <패키지이름> <실행파일이름>
```

- 셸이 아니라 **ROS2가 패키지 색인에서 실행파일을 찾아** 실행하므로, 실행파일이 어느 경로에 설치돼 있는지 몰라도 된다.
- 실행파일 이름은 `ros2 pkg executables <패키지이름>` 으로 미리 확인할 수 있다.
- 종료는 해당 터미널에서 `Ctrl + C`.

```bash
# 예시
ros2 run demo_nodes_cpp talker      # demo_nodes_cpp 패키지의 talker 노드 실행
ros2 run demo_nodes_cpp listener    # 같은 패키지의 listener 노드 실행
```

---

## 5. talker · listener 데모 동시 실행

### 5-1. 필요한 "환경 설정 추가 작업"이 무엇인가

두 노드를 **서로 다른 터미널**에서 실행해야 하므로, **두 터미널 모두에서** ROS2 환경 스크립트를 먼저 소싱해야 한다. 이것이 이 실습에 필요한 추가 작업이다(2-4 참고 — `~/.bashrc` 에 등록해 두면 자동).

```bash
source /opt/ros/humble/setup.bash    # 터미널 1, 터미널 2 각각에서 실행
```

> **참고** : 같은 컴퓨터에서 같은 `ROS_DOMAIN_ID`(기본값 0)를 쓰는 노드들은 별도 설정 없이 DDS가 서로를 자동 발견한다. 그래서 소싱 외의 네트워크 설정은 필요 없다.

### 5-2. 실행 절차

| | 터미널 1 (talker) | 터미널 2 (listener) |
|---|---|---|
| ① | `source /opt/ros/humble/setup.bash` | `source /opt/ros/humble/setup.bash` |
| ② | `ros2 run demo_nodes_cpp talker` | `ros2 run demo_nodes_cpp listener` |

### 5-3. 실행 결과 — 두 노드의 상호작용

`talker` 는 1초마다 `chatter` 라는 토픽에 `Hello World: N` 메시지를 **발행(publish)** 하고, `listener` 는 같은 토픽을 **구독(subscribe)** 해 받은 내용을 출력한다.

```
[터미널 1 — talker]
[INFO] [...] [talker]: Publishing: 'Hello World: 1'
[INFO] [...] [talker]: Publishing: 'Hello World: 2'
[INFO] [...] [talker]: Publishing: 'Hello World: 3'

[터미널 2 — listener]
[INFO] [...] [listener]: I heard: [Hello World: 1]
[INFO] [...] [listener]: I heard: [Hello World: 2]
[INFO] [...] [listener]: I heard: [Hello World: 3]
```

**같은 번호가 두 터미널에서 짝을 이루며 실시간으로 올라가는 것**으로, 두 노드가 동시에 실행되어 상호작용(발행 ↔ 구독)하고 있음을 확인할 수 있다.

```
 [talker 노드] --- "Hello World: N" ---> (chatter 토픽) ---> [listener 노드]
    발행(publish)                                              구독(subscribe)
```

두 노드가 떠 있는 상태에서 세 번째 터미널로 아래를 실행하면 구조를 한 번 더 검증할 수 있다.

```bash
ros2 node list          # → /talker, /listener
ros2 topic list         # → /chatter 가 보임
ros2 topic echo /chatter    # 토픽에 흐르는 메시지를 직접 엿보기
```

### 5-4. 실행 화면 캡처

아래는 두 터미널에서 talker와 listener가 동시에 실행되어 같은 번호의 메시지를 주고받는 장면이다.

![talker와 listener 동시 실행 캡처](2_ros_talker_listener.png)

<!-- TODO: VM에서 두 터미널을 나란히 띄운 화면을 캡처해 이 폴더에 2_ros_talker_listener.png 로 저장하면 위 이미지가 표시됩니다. -->

---

## 6. 결과 요약

| 항목 | 결과 |
|------|------|
| 로봇 운영체제 개념 | ROS = OS가 아닌 **미들웨어** — 하드웨어 추상화·통신·패키지·도구 제공. 베어메탈 펌웨어 로봇과의 차이 정리 |
| 실습 환경 | UTM VM · Ubuntu 22.04.5 LTS (arm64) 위에 **ROS2 Humble** apt 설치 (`ros-humble-desktop`) |
| 패키지 ↔ 노드 | 패키지 = 배포·설치 단위, 노드 = 실행 단위. 1 : N 관계 (`demo_nodes_cpp` ⊃ `talker`·`listener`) |
| `ros2 run` | `ros2 run <패키지> <실행파일>` 로 노드 실행 |
| 환경 설정 추가 작업 | **각 터미널에서 `source /opt/ros/humble/setup.bash`** (`~/.bashrc` 등록으로 자동화) |
| 데모 실행 | talker(발행) ↔ listener(구독)가 `chatter` 토픽으로 같은 번호의 메시지를 실시간 교환함을 확인·캡처 |

**산출물**
- 문서 : `과정2/과제2/2_ros.md` (본 문서)
- 이미지 : `과정2/과제2/2_ros_talker_listener.png` (동시 실행·상호작용 캡처)

---

## 7. 참고자료

**ROS2 개념 · 설치 (공식 문서)**
- ROS2 Humble 공식 문서 : https://docs.ros.org/en/humble/
- Ubuntu deb 패키지 설치 가이드 : https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
- ROS2 apt 저장소 패키지(ros2-apt-source) : https://github.com/ros-infrastructure/ros-apt-source
- ROS2 배포본-우분투 짝·지원 플랫폼(REP 2000) : https://www.ros.org/reps/rep-2000.html

**환경 설정 · 노드 · `ros2 run` (공식 튜토리얼)**
- 환경 설정(setup.bash 소싱) : https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Configuring-ROS2-Environment.html
- 노드 이해(talker·listener, `ros2 run`) : https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html
- 토픽 이해(chatter 발행·구독) : https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.html
- 데모 노드 소스코드(demo_nodes_cpp) : https://github.com/ros2/demos
