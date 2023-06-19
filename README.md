#### Creating a Vivado Project for ACFA

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