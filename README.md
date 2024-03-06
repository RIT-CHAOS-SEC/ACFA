# Repository for ACFA: Secure Runtime Auditing & Guaranteed Device Healing via Active Control Flow Attestation

## Accepted to ([USENIX Security '23](https://www.usenix.org/conference/usenixsecurity23/presentation/caulfield))
```
@inproceedings {291156,
author = {Adam Caulfield and Norrathep Rattanavipanon and Ivan De Oliveira Nunes},
title = {{ACFA}: Secure Runtime Auditing \& Guaranteed Device Healing via Active Control Flow Attestation},
booktitle = {32nd USENIX Security Symposium (USENIX Security 23)},
year = {2023},
isbn = {978-1-939133-37-3},
address = {Anaheim, CA},
pages = {5827--5844},
url = {https://www.usenix.org/conference/usenixsecurity23/presentation/caulfield},
publisher = {USENIX Association},
month = aug
}
```


### Description folders containing code and data

`acfa_hw` - contains all Verilog files for ACFA hardware. Contains two subdirectories for ACFA's submodules: `active_rot_module` and `cfa_module`

`demo_prv` - contains source and header files for the MCU prover to execute its code for the demo application

`demo_vrf` - contains all Python code to execute the Verifier role of the demo application

`logs` - olds current and previous CF-Log files. It is populated during experiments and demo.

`msp_bin` - contains `*.mem` files used by Vivado to synthesis program memory onto the openMSP430

`openmsp430` - contains all Verilog files for the open source MSP430 (openMSP430) from open-cores

`scripts` - all build scripts for experiments

`syringe_pump`, `ultrasonic_sensor`, `temperature_sensor` - software for example sensor applications

`tcb` - contains all source and header files for ACFA software TCB.

### Requirements / Recommended setup

1- Xilinx Vivado (version 2021.1 or higher)

2- Python 3.6.9 or higher

3- We evaluated ACFA prototype on 64-bit Ubuntu 18.04 OS

4- To evaluate end-to-end demo: Basys3 FPGA Development Board (https://digilent.com/reference/basys3/refmanual) 

### Setup

1- Clone this Repository

2- `cd` into `scripts` and run `sudo make install`

3- Install Xilinx Vivado: https://www.xilinx.com/support/download.html

4- Install pyserial python package using `sudo apt install python3-serial` 

5- Verify required packages from standard distribution: `time, hmac, hashlib, argparse, pickle, dataclasses, os, collections`. 

### Create a Vivado Project for ACFA

1- Start Vivado. On the upper left select: File -> New Project

2- Follow the wizard, select a project name and location. In project type, select RTL Project and click Next.

3- In the "Add Sources" window, select Add Files and add all .v and .mem files contained in the following directories of this reposiroty:

        /acfa_hw
        /msp_bin
        /openmsp430/fpga
        /openmsp430/msp_core
        /openmsp430/msp_memory
        /openmsp430/msp_periph
       
and select Next.

Note that /msp_bin contains the pmem.mem and smem.mem binaries, generated in step [Building ACFA Software].

4- In the "Add Constraints" window, select add files and add the file

        openmsp430/contraints_fpga/Basys-3-Master.xdc

and select Next.

        Note: this file needs to be modified accordingly if you are running ACFA in a different FPGA.

5- In the "Default Part" window select "Boards", search for Basys3, select it, and click Next.

        Note: if you don't see Basys3 as an option you may need to download Basys3 to your Vivado installation.

6- Select "Finish". This will conclude the creation of a Vivado Project for ACFA.

Now we need to configure the project for systhesis.

7- In the PROJECT MANAGER "Sources" window, search for openMSP430_fpga (openMSP430_fpga.v) file, right click it and select "Set as Top".
This will make openMSP430_fpga.v the top module in the project hierarchy. Now its name should appear in bold letters.

8- In the same "Sources" window, search for openMSP430_defines.v file, right click it and select Set File Type and, from the dropdown menu select "Verilog Header".

9- After adding `*.v` and `*.mem` files to the project, open a terminal window and `cd` into `scripts`.

10- Run `make sim` to compile software for the basic test. This will update the `*.mem` files.

### Basic Test

1- Now we are ready to synthesize openmsp430 with ACFA hardware. On the left menu of the PROJECT MANAGER, click "Run Synthesis", and select execution parameters (e.g., number of CPUs used for synthesis) according to your PC's capabilities. This step takes 2-10 minutes.

2- If synthesis succeeds, a window to "Run Implementation" will appear. Do not "Run Implementation" for the basic test, and close this prompt window.

3- In Vivado, click "Add Sources" (Alt-A), then select "Add or create simulation sources", click "Add Files", and select everything inside `openmsp430/simulation`.

4- Open the `tb_openMSP430_fpga.v` file and find lines 193-202. These lines open `*.cflog` files to simulate the transmission of \cflog slices for the basic test. Therefore in lines 193-202, replace `<LOGS_FULL_PATH>` with the full file path of the `logs` subdirectory of the ACFA directory.

5- Now, navigate to the "Sources" window in Vivado. Search for `tb_openMSP430_fpga`, and in the "Simulation Sources" tab, right-click `tb_openMSP430_fpga.v` and set its file type as the top module.

6- Go back to the Vivado window, and in the "Flow Navigator" tab (on the left-most part of Vivado's window), click "Run Simulation," then "Run Behavioral Simulation."

7- On the newly opened simulation window, select 8ms as the time for the simulation to run. Then press "Shift+F2" to run.

8- The simulation waveform will show two ACFA triggers occur during the execution due to the device boot and the program ending. In the `logs` sub-directory of the ACFA directory, two `*.cflog` files were generated. If two `*.cflog` files are generated and match the contents of `logs/expected_cflogs_basic_test/`, the basic test has completed successfully.
