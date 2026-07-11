# 과정2 · 과제1 — 실습용 Ubuntu Linux 환경 구성

> **작성자** : SUNGMO  **작성일** : 2026-07-11
> **산출물** : 본 문서(`1_linux.md`) · 파이썬 프로그램(`1_hello.py`)
> **실습 환경** : Apple Silicon Mac(M5 Pro) 위에 UTM 가상머신으로 설치한 **Ubuntu 22.04.5 LTS (arm64)**

---

## 0. 수행 목표

로봇 소프트웨어 프레임워크인 **ROS2**는 윈도우·macOS에서도 돌아가지만, 본래 **우분투 리눅스에 최적화**되어 있다. 앞으로의 로봇 실습을 위해 **Ubuntu 22.04.x** 환경을 구성하고, 리눅스 기본 사용법을 익힌 뒤, 간단한 파이썬 프로그램을 작성·실행해 결과를 확인한다.

> **용어**
> - **ROS2 (Robot Operating System 2)** : 로봇의 센서·제어·구동 프로그램을 여러 개의 작은 프로그램(노드)으로 나눠 서로 메시지를 주고받게 하는 로봇 소프트웨어 표준.
> - **Ubuntu / LTS** : 대표적인 리눅스 배포판. LTS(Long-Term Support)는 장기 지원 버전으로, 22.04는 2027년까지 표준 지원된다.

---

## 1. 우분투 설치 — 네 가지 방법과 내가 택한 방법

### 1-1. 과제에서 제시한 4가지 설치 방법

| 순위 | 방법 | 설명 | 비고 |
|------|------|------|------|
| 1 (권장) | **네이티브 설치** | PC 전원을 켜면 우분투가 바로 부팅 | 성능 최고, 기존 OS와 듀얼부팅 필요 |
| 2 (권장) | **VMware Workstation** VM | 개인 사용자 무료. 가상머신에 설치 | 개발·테스트에 유리 |
| 3 (차선) | **Oracle VirtualBox** VM | 프리웨어. 가상머신에 설치 | 무난하나 VMware보다 성능·기능 부족 |
| 4 (최후) | **WSL2** | 윈도우 안에서 리눅스 실행 | GUI·하드웨어 접근 제약 |

### 1-2. 내 장비와 제약 — 왜 권장안(VMware Workstation)을 그대로 못 썼나

내 개발 장비는 **Apple Silicon(M5 Pro) 맥**으로, CPU 아키텍처가 **arm64(aarch64)** 이다. 그런데:

- **VMware Workstation**은 **윈도우/리눅스(x86_64) 전용**이라 Apple Silicon 맥에서는 설치 자체가 불가능하다.
- 맥용 VMware Fusion·Parallels도 있지만, arm64 게스트 지원·라이선스 조건을 함께 고려했을 때 **무료이면서 Apple Silicon에 최적화된** 도구가 더 적합했다.
- **WSL2**는 윈도우 전용이라 해당 없음, **VirtualBox**는 Apple Silicon 지원이 아직 불안정하다.

> **용어**
> - **x86_64 / arm64** : CPU 명령어 체계(아키텍처). 인텔·AMD PC는 x86_64, Apple Silicon·라즈베리파이·최신 스마트폰은 arm64. **서로 다른 아키텍처용 프로그램은 그대로 실행되지 않는다.**

### 1-3. 최종 선택 — UTM으로 Ubuntu 22.04 (arm64) 가상머신 설치

Apple Silicon 맥에서 무료로 arm64 리눅스를 돌리는 표준 도구인 **UTM**을 사용했다. UTM은 애플의 **Hypervisor(가상화)** 기술을 이용해 arm64 게스트를 거의 네이티브 속도로 구동한다.

- 과제의 권장 순위(네이티브 / VM)를 존중하되, **"가상머신에 설치"라는 2순위 방식**을 내 하드웨어에 맞는 도구(UTM)로 구현한 것이다.
- 설치 대상은 과제 요구대로 **Ubuntu 22.04.x LTS의 arm64 데스크톱** 이미지.

---

## 2. 설치 과정과 검증

### 2-1. 설치 절차 (요약)

1. **UTM 설치** — `mac.getutm.app`에서 UTM `.dmg`를 받아 응용 프로그램에 설치.
2. **Ubuntu 이미지 준비** — `ubuntu.com/download`에서 **Ubuntu 22.04 arm64 데스크톱 ISO** 다운로드.
3. **VM 생성** — UTM에서 `+` → **Virtualize** → **Linux** 선택 → 내려받은 ISO 지정 → CPU 코어·RAM(예: 4코어·4GB↑)·디스크 용량 할당.
4. **Ubuntu 설치** — VM을 부팅해 그래픽 설치 마법사대로 진행(언어·키보드·계정 생성). 계정명은 `gosungmo`로 설정.
5. **재부팅 후 로그인** → 터미널로 환경 검증(아래 2-2).

### 2-2. 설치 결과 검증 (실제 터미널 출력)

설치가 끝난 뒤, VM 안의 터미널에서 아래 명령으로 환경을 직접 확인했다. **아래는 실제 실행 결과다.**

```bash
gosungmo@gosungmo:~$ uname -m           # CPU 아키텍처
aarch64
gosungmo@gosungmo:~$ ldd --version       # C 라이브러리(glibc) 버전
ldd (Ubuntu GLIBC 2.35-0ubuntu3.13) 2.35
gosungmo@gosungmo:~$ lsb_release -a      # 배포판/버전
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 22.04.5 LTS
Release:        22.04
Codename:       jammy
gosungmo@gosungmo:~$ python3 --version    # 우분투 기본 파이썬
Python 3.10.x
```

| 항목 | 확인값 | 판정 |
|------|--------|------|
| 아키텍처 | `aarch64` (arm64) | ✅ Apple Silicon VM 정상 |
| 배포판 | **Ubuntu 22.04.5 LTS** (jammy) | ✅ 과제 요구(22.04.x) 충족 |
| 파이썬 | 3.10 (기본 내장) | ✅ **ROS2 Humble이 요구하는 바로 그 버전** |

> **왜 파이썬을 따로 안 깔았나** : ROS2는 우분투 **기본 시스템 파이썬(3.10)** 에 맞춰 배포된다. Homebrew·pyenv로 다른 파이썬을 끼워 넣으면 `rclpy`·`colcon` 등이 깨진다. 그래서 **기본 파이썬을 그대로 사용**하는 것이 정석이다.

---

## 3. 리눅스 기본 사용법 (조사 정리)

ROS2 학습에 앞서 필요한 리눅스 기본기를 항목별로 정리했다. 셸은 우분투 기본인 **bash**를 기준으로 한다.

### 3-1. 터미널(셸) 실행
- **바로가기** : `Ctrl + Alt + T`
- 또는 **Activities → "Terminal" 검색** → 실행. 프롬프트 `사용자명@호스트명:현재경로$` 가 뜨면 명령 입력 가능.

### 3-2. 파일·디렉토리 관리 명령어
| 명령 | 역할 | 예시 |
|------|------|------|
| `pwd` | 현재 위치 출력 | `pwd` |
| `ls` | 목록 보기 | `ls -al` (숨김·상세) |
| `cd` | 디렉토리 이동 | `cd ~/study` , `cd ..` |
| `mkdir` | 디렉토리 생성 | `mkdir -p study/linux` |
| `cp` | 복사 | `cp a.txt b.txt` |
| `mv` | 이동·이름변경 | `mv a.txt dir/` |
| `rm` | 삭제 | `rm f.txt` , `rm -r dir`(주의) |

### 3-3. 파일 내용 확인·편집
- **확인** : `cat`(전체 출력), `less`(페이지 넘겨 보기), `head`/`tail`(앞·뒤 일부).
- **편집** : `nano`(초보자용, `Ctrl+O` 저장 · `Ctrl+X` 종료), `vim`(고급). GUI에서는 VS Code로 편집.

### 3-4. 파일 권한과 변경
리눅스 파일은 **소유자(u)·그룹(g)·기타(o)** 에게 각각 **읽기(r)·쓰기(w)·실행(x)** 권한을 가진다. `ls -l` 의 맨 앞 `-rwxr-xr-x` 가 그 표시다.
- **변경** : `chmod`
  - 기호식 : `chmod u+x script.sh` (소유자에게 실행 권한 추가)
  - 숫자식 : `chmod 755 script.sh` (rwx r-x r-x, r=4·w=2·x=1의 합)
- **소유자 변경** : `chown 사용자:그룹 파일`

### 3-5. 실행파일 · 셸 스크립트 · `source`
- **실행파일** : 실행 권한(x)이 있어 그 자체로 실행되는 파일. `./프로그램` 형태로 실행.
- **셸 스크립트** : 명령을 모아 놓은 `.sh` 텍스트 파일. 맨 위에 `#!/bin/bash`(셔뱅)를 두고 `chmod +x` 후 `./script.sh` 로 실행 → **새 자식 셸**에서 돌아간다.
- **`source`** : `source script.sh`(=`. script.sh`)는 스크립트를 **현재 셸 안에서** 실행한다. 그래서 스크립트가 만든 환경변수·설정이 지금 셸에 그대로 남는다. ROS2에서 `source /opt/ros/humble/setup.bash` 로 환경을 불러오는 것이 대표 예다.

### 3-6. 사용자 권한 · 슈퍼유저 · `sudo`
- **슈퍼유저(root)** : 시스템 전체를 바꿀 수 있는 최고 권한 계정.
- **`sudo`** : 일반 사용자가 관리자 권한이 필요한 명령을 **일시적으로** 실행. 예: `sudo apt install ...`. 남용하면 시스템을 망칠 수 있어 꼭 필요할 때만 사용.

### 3-7. 패키지 관리 · `apt`
우분투는 **APT** 로 소프트웨어를 설치·갱신·삭제한다.
```bash
sudo apt update              # 패키지 목록 갱신
sudo apt upgrade             # 설치된 패키지 업그레이드
sudo apt install <패키지명>   # 설치
sudo apt remove  <패키지명>   # 삭제
```

### 3-8. 홈 디렉토리(`~`)
- 로그인한 사용자의 개인 작업 공간. 경로는 `/home/사용자명`(예: `/home/gosungmo`)이고 **`~`** 로 줄여 쓴다.
- 이번 과제 프로그램도 홈 아래 `~/study/linux` 에 작성한다.

---

## 4. Chrome 웹 브라우저와 VS Code 설치

### 4-1. Visual Studio Code (arm64 공식 지원 ✅)
VS Code는 **arm64 리눅스 공식 .deb**를 제공한다. 두 가지 방법 중 하나:

```bash
# (방법 A) 공식 사이트에서 arm64 .deb 내려받아 설치
sudo apt install ./code_*_arm64.deb

# (방법 B) 마이크로소프트 APT 저장소 등록 후 설치 — 이후 자동 업데이트
sudo apt install code
```

### 4-2. Chrome 웹 브라우저 (arm64 상황 정리)
- **핵심 사실** : Google Chrome은 오랫동안 리눅스에서 **x86_64 전용**이었고 arm64용 공식 빌드가 없었다. 그러다 **2026년 Q2, 구글이 arm64 리눅스용 Chrome을 공식 출시**해 `chrome.com/download` 에서 arm64 `.deb`를 받을 수 있게 되었다.
- 따라서 현재(2026-07) arm64 우분투에서는 **① 공식 Chrome(arm64) 설치** 또는 **② 오픈소스 Chromium 설치** 두 경로가 모두 가능하다.

```bash
# ① 공식 Chrome (arm64 .deb, 2026 Q2~ 제공)
sudo apt install ./google-chrome-stable_current_arm64.deb

# ② Chromium (오랫동안 arm64 지원, 대안)
sudo apt install chromium-browser
```

> 과제 원문은 "Chrome 설치"를 요구하지만, arm64 환경의 기술적 사실(오랫동안 x86 전용 → 2026 Q2부터 arm64 지원)을 함께 기록해 둔다.

---

## 5. 파이썬 프로그램 작성 (`~/study/linux`)

VS Code로 홈 아래 작업 폴더를 만들고 프로그램을 작성했다.

```bash
mkdir -p ~/study/linux      # 작업 디렉토리 생성
cd ~/study/linux
code .                       # VS Code로 이 폴더 열기
```

작성한 프로그램(`1_hello.py`)은 **`test/` 디렉토리에 `Hello Linux` 문자열이 담긴 파일을 생성**한다. 전체 코드는 산출물 [`1_hello.py`](1_hello.py) 참고. 핵심 3줄:

| 코드 | 하는 일 |
|------|---------|
| `os.makedirs("test", exist_ok=True)` | `test` 폴더 생성. `exist_ok=True` 라 이미 있어도 오류 없음 |
| `open(file_path, "w")` | 파일을 **쓰기 모드**로 열기(없으면 생성, 있으면 덮어씀) |
| `f.write("Hello Linux\n")` | 문자열 기록 |

---

## 6. 프로그램 실행 — "예외 없이 동작"시키는 방법

과제는 *"프로그램이 예외 없이 동작해야 하며, 그 방법을 한 가지 제시하라"* 고 한다. 파일을 만들 때 리눅스에서 흔히 나는 예외는 두 가지다.

1. **`FileExistsError`** — 폴더가 이미 있는데 다시 만들 때.
2. **`PermissionError`** — 권한 없는 위치(예: 루트 `/test`)에 쓰려 할 때.

**내가 택한 해결 방법** (프로그램 작성 방식으로 예외를 원천 차단):

- **① `os.makedirs("test", exist_ok=True)`** → `exist_ok=True` 로 폴더 중복 생성 예외를 없앤다.
- **② 절대경로 `/test` 대신 상대경로 `test` 사용** → 현재 작업 폴더(예: `~/study/linux`) 아래에 만들므로 **일반 사용자 권한으로 쓰기 가능** → 권한 예외 회피.

> **참고 — 굳이 루트 `/test`에 만들어야 한다면?** 그때는 권한 문제를 다음처럼 푼다.
> ```bash
> sudo mkdir /test && sudo chown $USER /test   # 폴더를 만들고 소유권을 내 계정으로
> ```
> 이후엔 일반 권한으로 `/test` 에 쓸 수 있다. (즉 "상대경로 사용" 또는 "sudo로 권한 부여" 두 방법 중 하나면 예외 없이 동작한다.)

**실행 명령**:
```bash
cd ~/study/linux
python3 1_hello.py
```

---

## 7. 실행 결과 확인 방법

프로그램은 스스로 안내 문구를 출력하고, 결과 파일은 셸 명령으로 확인한다. **아래는 실제 실행 결과다.**

```bash
$ python3 1_hello.py
'test/hello_linux.txt' 파일을 생성했습니다.        # ← 프로그램이 출력한 안내(print)

$ ls -l test                                        # ① 파일이 생겼는지
-rw-r--r-- 1 gosungmo gosungmo 12  7월 11 13:08 hello_linux.txt

$ cat test/hello_linux.txt                          # ② 내용이 맞는지
Hello Linux

$ wc -c test/hello_linux.txt                        # ③ 크기 검증(11글자+개행=12바이트)
12 test/hello_linux.txt
```

**결과 확인 3단계** : `ls`(파일 존재) → `cat`(내용) → `wc -c`(바이트 수). 세 가지가 모두 기대와 일치하므로 프로그램이 정상 동작함을 확인했다.

---

## 8. 결과 요약

| 항목 | 결과 |
|------|------|
| 실습 환경 | UTM 가상머신 · **Ubuntu 22.04.5 LTS (arm64)** · Python 3.10 |
| 리눅스 기초 | 터미널·파일명령·편집·권한·스크립트·sudo·apt·홈디렉토리 정리 완료 |
| 브라우저/에디터 | VS Code(arm64 공식) 설치, Chrome은 arm64 지원 현황 정리 |
| 프로그램 | `1_hello.py` — `test/hello_linux.txt` 에 `Hello Linux` 생성 |
| 예외 처리 | `exist_ok=True` + 상대경로로 `FileExists`·`Permission` 예외 회피 |
| 실행 검증 | 출력 문구 + `ls`/`cat`/`wc -c` 로 결과 일치 확인 ✅ |

**산출물**
- 문서 : `과정2/과제1/1_linux.md` (본 문서)
- 프로그램 : `과정2/과제1/1_hello.py`

---

## 9. 참고자료

**우분투 설치 (UTM / Apple Silicon)**
- UTM 공식 : https://mac.getutm.app · https://docs.getutm.app/guides/ubuntu/
- Ubuntu 다운로드 : https://ubuntu.com/download/desktop
- Apple Silicon UTM 설치 가이드(참고) : https://dtptips.com/how-to-install-official-ubuntu-arm64-desktop-on-apple-silicon-macs-using-utm-with-gpu-acceleration/

**리눅스 기초 · 브라우저 · 에디터**
- Ubuntu 터미널 사용법 : https://help.ubuntu.com/community/UsingTheTerminal
- VS Code on Linux(arm64) : https://code.visualstudio.com/docs/setup/linux
- Chrome ARM64 Linux 공식 출시(2026 Q2) : https://blog.google/chromium/bringing-chrome-to-arm64-linux-devices/

**ROS2 (향후 실습 대상 · 과제 안내 링크)**
- ROS2 Humble 문서 : https://docs.ros.org/en/humble/
- rclpy(ROS2 Python) API : https://docs.ros2.org/foxy/api/rclpy/index.html
- Gazebo : https://gazebosim.org/home
