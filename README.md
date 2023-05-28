pinout-diagram-drawer
=====

A tool for creating pinout diagrams useful when designing PCBs with microcontrollers.

currently supports:
- STM32 - using data files from STM32CubeIDE - https://github.com/LibrePCB/stm-db

supported packages:
- LQFP

### Features

* Filtering signals
* Rotating dies

### Motivation

See [Motivation](.docs/motivation.md)

### Usage

```shell
python pinout-drawer -c config.yaml -o output.png
```

### Examples

`config.yaml`

```yaml
pinout: stm-db/data/STM32F103C8Tx.json
rotate: 0
drawing:
  image_size_w: 700
  image_size_h: 800
  die_size: 6
  die_margin: 20
filters:
  - or: [SWDIO, SWCLK]
  - and:
      - or: [USART, UART]
      - or: [TX, RX]
  - and: [I2C, {or: [SCL, SDA]}]
  - or: [USB_OTG_FS_DM, USB_OTG_FS_DP]
  - and: [TIM, CH]
```

#### Result

<a href="./examples/output1.png"><img src="./examples/output1.png" height="200"/></a>

#### Other examples

<a href="./examples/output2.png"><img src="./examples/output2.png" height="200"/></a>
<a href="./examples/output3.png"><img src="./examples/output3.png" height="200"/></a>

### Alternative software

* STM32CubeIDE 
