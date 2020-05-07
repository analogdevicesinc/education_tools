# ADALM1000 Accessory Boards

[Analog Devices Inc.](https://www.analog.com/en/index.html)

Design Resource files for accessory PC boards for use with Active Learning Module [ADALM1000](https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-boards-kits/adalm1000.html), [ADALP2000](https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-boards-kits/EVAL-ADALP2000.html) Parts Kit.

The PC Board design files were generated using EAGLE (Easily Applicable Graphical Layout Editor) Version 7.7.0 for Windows (64 bit) Standard Edition.

The board files can generally be downloaded and used directly on many prototyping and rapid PC board manufacturer web sites. [Oshpark](https://oshpark.com/):

General background on the M1K accessory boards.

The idea is that the M1K analog input path is bare bones simple (for cost savings) and this ecosystem of accessory boards is a set of signal chain building blocks to daisy chain together more complex input and output signal chains. To that end there are generally pass through connections from one side of the boards to the other. Let's consider the 8 pin female analog connector on the M1K as connector "analog1". The connector pads on the accessory boards named ADALM1000 would be populated with matching male connectors. The connector pads on the accessory boards named analog2 would be populated with a female connector replicating the female connector on the M1K but with whatever signal processing a given board does inserted. The simple model is that various boards would be daisy chained in series (the ADALM1000 male connector plugged into the analog2 female connector etc.) building up a new signal chain. The order the boards are connected in series would of course matter and provides additional flexibility. What is not yet there in the initial release is what we are calling a "riser" board which allows the signal chain to split vertically and have a second parallel path as it were.

- Applications:
  - Analog Input Multiplexer using CD4052 dual 4:1
  - Input Buffer amplifier using dual op-ampa such as AD822 and AD8542
  - Input resistor voltage divider
  - BNC / Scope probe adapter
  - +/- 5 V supply generator
    - Notice that the M1K connector has two ground pins. The -5 generator hijacks one of these pins for its -5 V rail. On all the accessory boards these two "ground" pins are never shorted together. If a given board (other than the -5 generator) is plugged into the M1K directly, the two pins will be connected together inside the M1K.

