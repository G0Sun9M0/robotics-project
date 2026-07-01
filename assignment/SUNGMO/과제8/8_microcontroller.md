# 마이크로컨트롤러(Microcontroller) 조사 보고서

> 로봇을 제어하는 두뇌인 **마이크로컨트롤러(MCU)**와 제어 방식을 조사한 문서.
> ※ 작성 전 각 출처의 신뢰성·정확성을 교차 검증하였다. (근거는 맨 아래 "출처 및 신뢰성" 참조)

## 1. 마이크로컨트롤러(MCU)의 역할

마이크로컨트롤러(MCU)는 **CPU(연산장치) + 메모리(RAM·플래시) + 주변장치(I/O, 타이머, 신호 변환기 등)를 하나의 칩에 통합한 소형 컴퓨터**다. 즉, 별도의 칩 여러 개로 구성하지 않고 단일 집적회로(IC) 안에서 제어에 필요한 거의 모든 요소를 담고 있어, 부품 수·배선·기판 면적을 크게 줄인다.

이 통합 덕분에 MCU는 **임베디드 제어(embedded control)** 에 최적화되어 있다. 자동차 엔진 제어, 가전제품, 리모컨, 전동공구, 의료기기 등 "특정 기능을 반복 수행하는 내장형 장치"의 두뇌 역할을 한다.

**⚠️ 마이크로컨트롤러 vs 마이크로프로세서(MPU)**
- **마이크로컨트롤러**: CPU + 내부 메모리(ROM/RAM) + I/O 주변장치가 한 칩 안에 있음 → 그 자체로 동작 가능, 임베디드 제어용.
- **마이크로프로세서**: 보통 **CPU만** 들어 있어, 메모리와 주변장치를 **외부에 따로 연결**해야 함 → 범용 컴퓨터(PC 등)용.

## 2. 기본 제어 방식과 인터페이스 (PWM / ADC / GPIO)

### 2-1. PWM (Pulse Width Modulation, 펄스 폭 변조)

PWM은 **디지털 신호의 HIGH/LOW 비율을 조절해 아날로그처럼 평균 출력을 제어**하는 방식이다.

- **듀티 사이클(duty cycle)**: 한 주기(period) 안에서 신호가 HIGH(켜짐)로 유지되는 시간의 비율(%). 50%면 HIGH·LOW 시간이 같고, 100%는 항상 ON, 0%는 항상 OFF.
- **원리**: 빠르게 ON/OFF를 반복하면, 부하에 전달되는 **평균 전압(전력)** 이 듀티 사이클에 비례한다. 따라서 디지털 핀만으로 "아날로그처럼 보이는" 출력을 얻는다.
- **용도**: LED 밝기 조절(디밍), 모터 속도 제어, 서보모터 각도 제어.
  - 예) 서보모터는 보통 20ms 주기(50Hz)에서 1~2ms 펄스로 제어하며, 1.5ms 펄스가 90도 중앙.
  - 예) LED 디밍은 약 100Hz 이상이면 깜빡임이 눈에 보이지 않고 부드럽게 조절됨.

> **⚠️ PWM은 진짜 아날로그 전압이 아니다.** 0V와 Vcc(예: 5V) 두 값 사이를 빠르게 스위칭하는 **디지털 사각파**이며, 그 평균값이 중간 전압처럼 동작하는 것이다. 진짜 연속 전압을 내려면 별도의 DAC가 필요하다.

### 2-2. 아날로그 핀(ADC)과 디지털 핀(GPIO)의 차이

| 구분 | 디지털 핀 (GPIO) | 아날로그 핀 (ADC 입력) |
|---|---|---|
| 읽는 값 | HIGH / LOW (2가지, 0V 또는 5V) | 0~5V 사이 연속 전압 |
| 신호 종류 | 이산적(discrete), 사각파 | 연속적(continuous) |
| 해상도 | 1비트(0/1) | 아두이노 Uno 기준 10비트 → 0~1023 (2¹⁰=1024단계) |
| 함수(아두이노) | `digitalRead()` / `digitalWrite()` | `analogRead()` |

- **ADC(Analog-to-Digital Converter)**: 연속적인 아날로그 전압을 MCU가 처리할 수 있는 디지털 숫자로 변환한다. Uno는 10비트 해상도로 0~5V를 0~1023 정수로 매핑하며, 1단계 ≈ 5V ÷ 1024 ≈ 약 4.9mV.
- **GPIO(General Purpose I/O)**: HIGH/LOW 두 상태만 입출력하는 범용 디지털 핀.

> **⚠️ "아날로그 핀 = ADC 입력"** 은 맞지만 주의가 필요하다. 아두이노의 A0~A5 핀은 `analogRead()` 시 ADC로 연결되지만, `pinMode()`로 **일반 디지털 GPIO로도 재사용**할 수 있다. 즉 "아날로그 핀"은 고정된 역할이 아니라 ADC로 연결될 수 있는 능력을 가리킨다.

## 3. 마이크로컨트롤러의 통신 방식 (UART / I2C / SPI)

### 비교 표

| 항목 | **UART** | **I2C** | **SPI** |
|---|---|---|---|
| 동기/비동기 | **비동기** (클럭 선 없음) | **동기** (SCL 클럭) | **동기** (SCLK 클럭) |
| 구조 | 점대점(1:1, 대등) | 마스터-슬레이브 (멀티마스터 가능) | 마스터-슬레이브 |
| 선 수 | **2선** (TX, RX) | **2선** (SDA=데이터, SCL=클럭) | **4선** (MOSI, MISO, SCLK, SS/CS) + 슬레이브당 CS 추가 |
| 다중 장치 | 기본 1:1 | 한 버스에 다수(7비트 주소, 최대 ~112개) | 슬레이브마다 별도 CS 선 필요 |
| 이중성 | 양방향(TX/RX 분리) | 반이중(SDA 단일선 공유) | 전이중(full-duplex) |
| 속도 | 가장 느림(양측 보드레이트 일치 필요) | 중간(보통 100kHz/400kHz) | 가장 빠름(수 MHz~10MHz+) |
| 대표 용도 | PC-MCU 직렬통신, GPS·블루투스 모듈, 디버그 콘솔 | 보드 내 저속 센서·EEPROM·RTC·LCD 다수 연결 | SD카드, TFT 디스플레이, 고속 ADC/DAC, 플래시 메모리 |

### 각 방식 요점
- **UART**: 클럭 선 없이 미리 약속한 속도(baud rate)로 동작. 양쪽 보드레이트가 다르면 데이터가 깨진다. 가장 단순한 1:1 통신.
- **I2C**: SDA(데이터)·SCL(클럭) 2선만으로 여러 장치를 묶는다. 각 장치는 고유 주소로 선택되며, 칩 셀렉트 선이 필요 없다.
- **SPI**: 클럭(SCLK)과 데이터선(MOSI=마스터→슬레이브, MISO=슬레이브→마스터)을 분리해 송수신을 동시에 수행(전이중)하며, 슬레이브를 고를 때 해당 CS선을 LOW로 내린다. 가장 빠르다.

> **⚠️ 용어 변화 주의**: 최신 SparkFun·Arduino 문서는 master/slave 대신 **controller/peripheral**, MOSI/MISO 대신 **COPI/CIPO(또는 PICO/POCI)** 표기를 쓴다. 가리키는 신호는 동일하며, 본 보고서는 학습용으로 전통 용어(MOSI/MISO/SS, 마스터-슬레이브)를 병기했다.

## 4. 실시간 제어와 타이머

### 4-1. 타이머(Timer/Counter)의 개념과 역할

타이머는 **클럭 틱(clock tick)을 세는 하드웨어 카운터** 주변장치다. CPU 프로그램 흐름과 **독립적으로 스스로 카운트**하므로, CPU를 붙잡지 않고도 정밀한 시간 측정·주기적 이벤트 생성·PWM 생성이 가능하다.

- **역할**: `delay()`처럼 CPU가 멍하니 기다리는 방식(busy-waiting) 없이 정확한 타이밍을 만든다 → LED 정밀 점멸, PWM, 일정 주기 센서 샘플링.
- 예) ATmega328P(아두이노 Uno)에는 타이머 3개: Timer0·Timer2는 8비트(최대 255), Timer1은 16비트(최대 65,535).
- **프리스케일러(prescaler)**: 시스템 클럭을 분주(1, 8, 64, 256, 1024)해 타이머를 느리게 동작시켜, 고정 폭 카운터로 더 긴 시간을 측정하게 한다.

### 4-2. 인터럽트(Interrupt)

인터럽트는 **특정 이벤트가 발생하면 CPU가 하던 일을 잠시 멈추고 즉시 처리 함수(ISR, Interrupt Service Routine)로 분기**하는 메커니즘이다.

- **폴링(polling) 대비 장점**: 폴링은 CPU가 계속 플래그를 확인하느라 자원을 100% 소모하지만, 인터럽트는 이벤트 발생 시에만 반응하므로 **효율적이고 응답이 즉각적**이다.
- **타이머 인터럽트 종류**:
  - **오버플로(overflow) 인터럽트**: 타이머가 최대값에서 0으로 넘어갈 때 발생.
  - **컴페어 매치(compare-match) 인터럽트**: 카운터(TCNTn)가 비교 레지스터(OCRnA) 값에 도달할 때 발생. (예: Timer1 → `ISR(TIMER1_COMPA_vect)`)
- **⚠️ ISR은 짧고 결정적으로** 작성해야 하며, 내부에서 `delay()` 등 블로킹 동작을 넣지 않는다.

### 4-3. 타이머 사용 절차 (ATmega328 기준 일반 단계)

1. **전역 인터럽트 비활성화** (`cli()`) — 설정 중 타이머가 잘못 발동하지 않도록.
2. **타이머 선택** (해상도·주기에 맞춰 8비트/16비트).
3. **동작 모드 설정** (TCCRnA/TCCRnB의 WGM 비트) — 주기 인터럽트엔 보통 CTC 모드.
4. **프리스케일러 설정** (TCCRnB의 클럭 선택 비트로 1/8/64/256/1024 중 선택).
5. **비교값/주기 계산·로드**: `OCRn = (클럭 ÷ 프리스케일러 × 원하는 시간) − 1`, 레지스터 폭 안에 들어가야 함.
6. **카운터 초기화** (TCNTn = 0).
7. **타이머 인터럽트 활성화** (TIMSKn의 해당 비트: 컴페어매치 OCIEnA 또는 오버플로 TOIEn).
8. **전역 인터럽트 활성화** (`sei()`).
9. **ISR 작성** (해당 벡터, 예: `ISR(TIMER1_COMPA_vect)`).
10. **타이머 동작** — CTC 모드는 컴페어 매치 시 자동으로 카운터를 0으로 리셋하므로 매 주기 수동 재설정이 불필요.

## 5. 아두이노(Arduino)

### 5-1. 마이크로보드(개발 보드)의 개념

마이크로컨트롤러 개발 보드(breakout board)는 **MCU 칩의 핀을 외부로 끌어내고(breakout), 전원 레귤레이터·USB 연결·표준 간격 헤더 등 주변 회로를 더한 PCB**다. 덕분에 MCU에 전원 공급·프로그래밍·프로토타이핑을 쉽게 할 수 있다.

### 5-2. 아두이노의 개념 (보드 + IDE)

아두이노는 **오픈소스 전자 플랫폼**으로, 두 부분으로 구성된다.
- **하드웨어(보드)**: Atmel 8비트 AVR MCU 기반 단일 보드(예: Uno = **ATmega328P**, 디지털 I/O 14핀 중 6핀 PWM 지원, 아날로그 입력 6핀, 16MHz, USB, 리셋 버튼 등). 하드웨어는 Creative Commons로 공개.
- **소프트웨어(IDE)**: 아두이노 IDE에서 **스케치(sketch, `.ino`)** 를 C/C++로 작성 → "Verify"로 컴파일, "Upload"로 USB를 통해 보드에 업로드.

### 5-3. 아두이노의 인터페이스 및 통신 방식

| 함수/라이브러리 | 역할 | 대응 개념 |
|---|---|---|
| `digitalWrite()` / `digitalRead()` | 디지털 핀 HIGH/LOW 출력·입력 | GPIO |
| `analogRead()` | 아날로그 핀의 전압을 ADC로 읽음 (Uno: 0~1023, 10비트) | ADC |
| `analogWrite()` | **PWM 신호 출력** (0~255 듀티) | **PWM (⚠️ 진짜 아날로그 아님)** |
| `Wire` 라이브러리 | I2C 통신 (7비트 주소) | I2C |
| `SPI` 라이브러리 | SPI 통신 (SCK + 데이터선 + CS) | SPI |
| `Serial` (`Serial.begin(baud)`) | UART 통신 (기본 8-N-1) | UART |

> **⚠️ 가장 흔한 혼동 — `analogWrite()`는 사실 PWM이다.** 아두이노 공식 문서도 "analogWrite()는 아날로그 값(**PWM 파형**)을 쓴다... 출력은 디지털 사각파"라고 명시한다. 또한 공식 문서는 **"analogWrite는 아날로그 핀이나 analogRead와 아무 관련이 없다"** 고 못 박는다. 이름의 "analog" 접두사 때문에 `analogRead`(ADC 입력)와 대칭으로 착각하기 쉽지만, 둘은 완전히 다른 메커니즘이다.
> 단, Due·Zero·MKR·UNO R4 등 **하드웨어 DAC가 있는 보드**의 특정 핀(DAC0 등)에서는 `analogWrite()`가 진짜 아날로그 전압을 출력할 수 있다. 클래식 Uno(ATmega328P)는 DAC가 없어 항상 PWM이다.

---

## 출처 및 신뢰성

| 항목 | 주요 출처(URL) | 등급 | 검증 결과 |
|---|---|---|---|
| MCU = CPU+메모리+I/O 한 칩 / MPU와 차이 | [Wikipedia: Microcontroller](https://en.wikipedia.org/wiki/Microcontroller) · [AWS](https://aws.amazon.com/compare/the-difference-between-microprocessors-microcontrollers/) · [Microchip](https://www.microchipusa.com/industry-news/microcontrollers-vs-microprocessors) | 상 | 3개 출처 일치 |
| PWM 개념·듀티 사이클·평균전력 | [SparkFun PWM](https://learn.sparkfun.com/tutorials/pulse-width-modulation/all) · [Wikipedia: PWM](https://en.wikipedia.org/wiki/Pulse-width_modulation) | 상 | 2개 독립 출처 교차검증 |
| ADC 개념·10비트·0~1023 | [Arduino: analogRead](https://docs.arduino.cc/language-reference/en/functions/analog-io/analogRead/) · [ElectronicWings](https://www.electronicwings.com/arduino/adc-in-arduino) | 상/중 | 2개 출처 교차검증 |
| 아날로그 vs 디지털 신호 | [SparkFun: Analog vs Digital](https://learn.sparkfun.com/tutorials/analog-vs-digital/all) | 상 | 확인 |
| UART 비동기·2선(TX/RX) | [SparkFun: Serial](https://learn.sparkfun.com/tutorials/serial-communication/all) · [Wikipedia: UART](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter) | 상 | 2개 독립 출처 교차검증 |
| I2C 동기·마스터슬레이브·2선 | [SparkFun: I2C](https://learn.sparkfun.com/tutorials/i2c/all) · [Wikipedia: I²C](https://en.wikipedia.org/wiki/I%C2%B2C) | 상 | 2개 독립 출처 교차검증 |
| SPI 동기·4선·전이중 | [SparkFun: SPI](https://learn.sparkfun.com/tutorials/serial-peripheral-interface-spi/all) · [Wikipedia: SPI](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface) | 상 | 2개 독립 출처 교차검증 |
| 타이머/카운터·프리스케일러 | [SparkFun(ATmega timers)](https://news.sparkfun.com/2613) · [Wikipedia: Counter](https://en.wikipedia.org/wiki/Counter_(digital)) · avr-guide | 상/중 | 교차검증 |
| 인터럽트·ISR·폴링 대비 | EmbeddedPrep ISR · TutorialsPoint | 중 | 개념 일치 |
| 아두이노=보드+IDE / Uno=ATmega328P | [Wikipedia: Arduino](https://en.wikipedia.org/wiki/Arduino) · [Arduino Store: Uno](https://store-usa.arduino.cc/products/arduino-uno-rev3) | 상 | 2개 출처 일치 |
| **analogWrite()=PWM (진짜 아날로그 아님)** | [Arduino: analogWrite](https://docs.arduino.cc/language-reference/en/functions/analog-io/analogWrite/) · Adafruit Learn | 상/중 | 공식문서 직접 인용 |
| Wire/SPI/Serial 함수 | [Arduino: Wire](https://docs.arduino.cc/learn/communication/wire) · [SPI](https://docs.arduino.cc/learn/communication/spi) · [UART](https://docs.arduino.cc/learn/communication/uart/) | 상 | 공식문서 |

**검증 메모**
- 핵심 교차검증 대상(UART/I2C/SPI의 동기·마스터슬레이브·선 수, PWM·ADC 개념)은 모두 반도체/하드웨어 벤더(SparkFun)와 Wikipedia 등 독립된 2개 이상 상(上)급 출처로 일치 확인.
- 보드 의존적 예외 ⚠️: ① `analogWrite()`는 DAC 탑재 보드(Due/Zero/MKR/UNO R4)에서만 진짜 아날로그 출력, 클래식 Uno는 항상 PWM. ② ADC 해상도는 Uno 10비트 기본, 일부 보드는 12비트(0~4095). ③ SPI 4선은 슬레이브 1개 기준(추가 시 CS 1선 추가). ④ 용어 master/slave·MOSI/MISO는 현재 controller/peripheral·COPI/CIPO로 표준 표기 변경(동일 신호).
