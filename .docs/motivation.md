Motivation
=====

When I am designing and routing PCBs, it is useful for me to have a pinout diagram around.
Atmel provides such diagrams for their AVRs in the manual. Unfortunately STMicroelectronics for their STM32
provides only pin naming diagrams and long list of pins with description, which is not a surprise
since there are so many alternative features on each pin.

I used to create such diagrams on my own in InkScape which was not a big issue when I was working only on
STM32F103, but quickly became tedious when started working with different µC.

So, after quite a few years (and when I found a database of chips in machine-readable format), I started
working on a tool for generating such diagrams.
