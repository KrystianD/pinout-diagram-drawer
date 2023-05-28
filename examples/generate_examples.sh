#!/bin/bash
cd $(dirname "$0")/..

python pinout-drawer -c examples/config1.yaml -o examples/output1.png
python pinout-drawer -c examples/config2.yaml -o examples/output2.png
python pinout-drawer -c examples/config3.yaml -o examples/output3.png
