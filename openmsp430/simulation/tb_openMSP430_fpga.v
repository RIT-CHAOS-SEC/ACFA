//----------------------------------------------------------------------------
// Copyright (C) 2001 Authors
//
// This source file may be used and distributed without restriction provided
// that this copyright statement is not removed from the file and that any
// derivative work contains the original copyright notice and the associated
// disclaimer.
//
// This source file is free software; you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation; either version 2.1 of the License, or
// (at your option) any later version.
//
// This source is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
// License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this source; if not, write to the Free Software Foundation,
// Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
//
//----------------------------------------------------------------------------
// 
// *File Name: tb_openMSP430_fpga.v
// 
// *Module Description:
//                      openMSP430 FPGA testbench
//
// *Author(s):
//              - Olivier Girard,    olgirard@gmail.com
//
//----------------------------------------------------------------------------
// $Rev$
// $LastChangedBy$
// $LastChangedDate$
//----------------------------------------------------------------------------
`include "timescale.v"
`ifdef OMSP_NO_INCLUDE
`else
`include "openMSP430_defines.v"
`endif

module  tb_openMSP430_fpga;

wire         [7:0] p3_dout = dut.p3_dout;
wire         [7:0] p1_dout = dut.p1_dout;
wire       [15:0] pc    = dut.openMSP430_0.inst_pc;

//
// Wire & Register definition
//------------------------------
 
//
// Include files
//------------------------------

// CPU & Memory registers
//`include "registers.v"

// GPIO
//wire         [7:0] p3_din = dut.p3_din;
//wire         [7:0] p3_dout = dut.p3_dout;
//wire         [7:0] p3_dout_en = dut.p3_dout_en;

//wire         [7:0] p1_din = dut.p1_din;
//wire         [7:0] p1_dout = dut.p1_dout;
//wire         [7:0] p1_dout_en = dut.p1_dout_en;

// // debug in seven seg -- freeze on pc before reset
// wire  [3:0] s0_src = dut.driver_7segment_0.s0_src;
// wire  [3:0] s1_src = dut.driver_7segment_0.s1_src;
// wire  [3:0] s2_src = dut.driver_7segment_0.s2_src;
// wire  [3:0] s3_src = dut.driver_7segment_0.s3_src;
// wire        rst_d  = dut.rst_d;
// wire [15:0] pc_d   = dut.pc_d;
// wire [15:0] pc_out = dut.pc_out;
// wire  [1:0] ctr    = dut.ctr;

// debug
wire [15:0] data_addr = dut.openMSP430_0.acfa_0.data_addr;
wire data_en = dut.openMSP430_0.acfa_0.data_en;
wire data_wr = dut.openMSP430_0.acfa_0.data_wr;

// acfa triggers
wire       acfa_nmi = dut.openMSP430_0.acfa_0.cflow_0.acfa_nmi;
wire       boot = dut.boot;
wire       flush = dut.flush;
wire       irq_ta0 = dut.irq_ta0;
wire       ER_done = dut.ER_done;

wire       puc_rst = dut.openMSP430_0.puc_rst;
wire       acfa_reset = dut.openMSP430_0.acfa_0.cflow_reset;
wire       vrased_reset = dut.openMSP430_0.acfa_0.vrased_reset;
wire       garota_reset = dut.openMSP430_0.acfa_0.garota_reset;

parameter TCB_att_min = 16'ha100;
parameter TCB_att_max = 16'hbffe;
parameter TCB_wait_min = 16'ha14a;
parameter TCB_wait_max = 16'ha1ea; 
parameter TCB_min = 16'ha000;
parameter TCB_max = 16'hdffe;

wire       in_TCB_attest = (dut.openMSP430_0.pc >= TCB_att_min) & (dut.openMSP430_0.pc <= TCB_att_max);
wire       in_TCB_wait = (dut.openMSP430_0.pc >= TCB_wait_min) & (dut.openMSP430_0.pc <= TCB_wait_max);
wire       in_TCB = (dut.openMSP430_0.pc >= TCB_min) & (dut.openMSP430_0.pc <= TCB_max);
wire       in_ER = (dut.openMSP430_0.pc >= dut.ER_min) & (dut.openMSP430_0.pc <= dut.ER_max);

wire              per_en   = dut.per_en;

// wire       [15:0] read_addr_reg = dut.acfa_memory_0.logs.logs.read_addr_reg;
// wire       [15:0] read_addr = dut.acfa_memory_0.logs.logs.read_addr;
// wire       [15:0] dout_16bit = dut.acfa_memory_0.logs.dout_16bit;
// wire       [15:0] read_addr_32bit = dut.acfa_memory_0.logs.read_addr_32bit;
// wire       [15:0] read_addr_16bit = dut.acfa_memory_0.logs.read_addr_16bit;
// wire              cflow_cen   = dut.acfa_memory_0.cflow_cen;
// wire              cflow_hw_wen = dut.acfa_memory_0.cflow_hw_wen;
// wire       [15:0] cflow_logs_ptr = dut.acfa_memory_0.cflow_logs_ptr;
// wire       [14:0] write_addr = dut.acfa_memory_0.logs.logs.write_addr;
// wire       [15:0] cflow_addr_reg = dut.acfa_memory_0.cflow_addr_reg;
// wire       [15:0] cflow_ermin = dut.acfa_memory_0.ermin;
// wire       [15:0] cflow_ermax = dut.acfa_memory_0.ermax;
// CPU registers
//====================== 

//wire       [15:0] pc    = dut.openMSP430_0.inst_pc;
wire       [15:0] r0    = dut.openMSP430_0.execution_unit_0.register_file_0.r0;
wire       [15:0] r1    = dut.openMSP430_0.execution_unit_0.register_file_0.r1;
wire       [15:0] r2    = dut.openMSP430_0.execution_unit_0.register_file_0.r2;
wire       [15:0] r3    = dut.openMSP430_0.execution_unit_0.register_file_0.r3;
wire       [15:0] r4    = dut.openMSP430_0.execution_unit_0.register_file_0.r4;
wire       [15:0] r5    = dut.openMSP430_0.execution_unit_0.register_file_0.r5;
wire       [15:0] r6    = dut.openMSP430_0.execution_unit_0.register_file_0.r6;
wire       [15:0] r7    = dut.openMSP430_0.execution_unit_0.register_file_0.r7;
wire       [15:0] r8    = dut.openMSP430_0.execution_unit_0.register_file_0.r8;
wire       [15:0] r9    = dut.openMSP430_0.execution_unit_0.register_file_0.r9;
wire       [15:0] r10   = dut.openMSP430_0.execution_unit_0.register_file_0.r10;
wire       [15:0] r11   = dut.openMSP430_0.execution_unit_0.register_file_0.r11;
wire       [15:0] r12   = dut.openMSP430_0.execution_unit_0.register_file_0.r12;
wire       [15:0] r13   = dut.openMSP430_0.execution_unit_0.register_file_0.r13;
wire       [15:0] r14   = dut.openMSP430_0.execution_unit_0.register_file_0.r14;
wire       [15:0] r15   = dut.openMSP430_0.execution_unit_0.register_file_0.r15;


// RAM cells
//======================

//wire       [15:0] srom_cen = dut.openMSP430_0.srom_cen;
// Verilog stimulus
//`include "stimulus.v"

//
// Initialize Program Memory
//------------------------------

////
//// Initialize ROM
////------------------------------
////integer tb_idx;
//initial
//  begin
//     // Initialize data memory
////     for (tb_idx=0; tb_idx < `DMEM_SIZE/2; tb_idx=tb_idx+1)
////        dmem_0.mem[tb_idx] = 16'h0000;

//     // Initialize program memory
//     //$readmemh("smem.mem", dut.openMSP430_0.srom_0.mem);
//     //
//     $readmemh("pmem.mem", dut.openMSP430_0.srom_0.mem);
//  end
  
integer slicefile;
integer i;
integer count = 0;

integer log_ptr = 0;
integer logged_events = 0;

wire catch_log_ptr = (dut.openMSP430_0.acfa_0.pc == 16'ha000) && (dut.openMSP430_0.acfa_0.pc_nxt != 16'ha000) && (dut.openMSP430_0.acfa_0.cflow_0.prev_pc != 16'ha000);
always @(posedge catch_log_ptr)
begin
    log_ptr <= dut.cflow_log_ptr;
//  logged_events <= ((dut.cflow_log_ptr + 16'h0002) >> 1);// + dut.cflow_log_ptr[0];
    logged_events <= ((dut.cflow_log_ptr) >> 1);// + dut.cflow_log_ptr[0];
end

wire logReady = (dut.openMSP430_0.acfa_0.cflow_hw_wen == 0) && ~catch_log_ptr && (dut.openMSP430_0.acfa_0.pc == 16'ha000);
// generate log slices as files
always @(posedge logReady)
begin 

    case(count)
        0: slicefile=$fopen("<LOGS_FULL_PATH>/0.cflog","w");
        1: slicefile=$fopen("<LOGS_FULL_PATH>/1.cflog","w");
        2: slicefile=$fopen("<LOGS_FULL_PATH>/2.cflog","w");
        3: slicefile=$fopen("<LOGS_FULL_PATH>/3.cflog","w");
        4: slicefile=$fopen("<LOGS_FULL_PATH>/4.cflog","w");
        5: slicefile=$fopen("<LOGS_FULL_PATH>/5.cflog","w");
        6: slicefile=$fopen("<LOGS_FULL_PATH>/6.cflog","w");
        7: slicefile=$fopen("<LOGS_FULL_PATH>/7.cflog","w");
        8: slicefile=$fopen("<LOGS_FULL_PATH>/8.cflog","w");
        9: slicefile=$fopen("<LOGS_FULL_PATH>/9.cflog","w");
    endcase
    
    for (i = 0; i < log_ptr; i = i +2) begin
       // $fdisplay(slicefile,"%h",dut.acfa_memory_0.logs.logs.ram[i]);  //write as hex 
       $fdisplay(slicefile,"%h%h",dut.acfa_memory_0.cflog.cflog[i],dut.acfa_memory_0.cflog.cflog[i+1]);  //write as hex 
        // $fdisplay(slicefile,"%h",dut.dmem_0.mem[16'h1100+i]);  //write as hex
    end
    $fdisplay(slicefile,"%d",log_ptr);  //write log_ptr as last value
    $fdisplay(slicefile,"%d",logged_events);
    
    $fclose(slicefile);
    
    count = count + 1;
end

// Clock & Reset
reg               CLK_100MHz;
reg               RESET;

// Slide Switches
reg               SW7;
reg               SW6;
reg               SW5;
reg               SW4;
reg               SW3;
reg               SW2;
reg               SW1;
reg               SW0;

// Push Button Switches
reg               BTN2;
reg               BTN1;
reg               BTN0;

// LEDs

wire              LED7;
wire              LED6;
wire              LED5;
wire              LED4;
wire              LED3;
wire              LED2;
wire              LED1;
wire              LED0;

// Four-Sigit, Seven-Segment LED Display
wire              SEG_A;
wire              SEG_B;
wire              SEG_C;
wire              SEG_D;
wire              SEG_E;
wire              SEG_F;
wire              SEG_G;
wire              SEG_DP;
wire              SEG_AN0;
wire              SEG_AN1;
wire              SEG_AN2;
wire              SEG_AN3;

// UART
reg               UART_RXD;
wire              UART_TXD;

// JB-C
wire              JB1;
wire              JC1;
wire              JC2;
wire              JC7;

// Core debug signals
//wire   [8*32-1:0] i_state;
//wire   [8*32-1:0] e_state;
//wire       [31:0] inst_cycle;
//wire   [8*32-1:0] inst_full;
//wire       [31:0] inst_number;
wire       [15:0] inst_pc;
//wire   [8*32-1:0] inst_short;

//// Testbench variables
//integer           i;
integer           error;
reg               stimulus_done;


//
// Generate Clock & Reset
//------------------------------
initial
  begin
     CLK_100MHz = 1'b0;
      forever #10 CLK_100MHz <= ~CLK_100MHz; // 100 MHz
//     forever #40 CLK_100MHz <= ~CLK_100MHz; // 25 MHz (accurate to MSP430)
  end

initial
  begin
     RESET         = 1'b0;
     #100 RESET    = 1'b1;
     #600 RESET    = 1'b0;
  end

//
// Global initialization
//------------------------------
initial
  begin
     error         = 0;
     stimulus_done = 1;
     SW7           = 1'b0;  // Slide Switches
     SW6           = 1'b0;
     SW5           = 1'b0;
     SW4           = 1'b0;
     SW3           = 1'b0;
     SW2           = 1'b0;
     SW1           = 1'b0;
     SW0           = 1'b0;
     BTN2          = 1'b0;  // Push Button Switches
     BTN1          = 1'b1;  
     BTN0          = 1'b0;
     UART_RXD      = 1'b0;  // UART
     
     forever #137 BTN2 <= ~BTN2; 
  end

//
// openMSP430 FPGA Instance
//----------------------------------

openMSP430_fpga dut (

// Clock Sources
    .CLK_100MHz    (CLK_100MHz),
    //.CLK_SOCKET   (1'b0),

// Slide Switches
    .SW7          (SW7),
    .SW6          (SW6),
    .SW5          (SW5),
    .SW4          (SW4),
    .SW3          (SW3),
    .SW2          (SW2),
    .SW1          (SW1),
    .SW0          (SW0),

// Push Button Switches
    .BTN3         (RESET),
    .BTN2         (BTN2),
    .BTN1         (BTN1),
    .BTN0         (BTN0),
    
// RS-232 Port
    .UART_RXD     (UART_RXD),
    .UART_TXD     (UART_TXD),  

// LEDs
    .LED8         (LED8),
    .LED7         (LED7),
    .LED6         (LED6),
    .LED5         (LED5),
    .LED4         (LED4),
    .LED3         (LED3),
    .LED2         (LED2),
    .LED1         (LED1),
    .LED0         (LED0),
    
    
    // JB-C
    .JB1          (JB1),
    .JC1          (JC1),
    .JC2          (JC2),
    .JC7          (JC7),

// Four-Sigit, Seven-Segment LED Display
    .SEG_A        (SEG_A),
    .SEG_B        (SEG_B),
    .SEG_C        (SEG_C),
    .SEG_D        (SEG_D),
    .SEG_E        (SEG_E),
    .SEG_F        (SEG_F),
    .SEG_G        (SEG_G),
    .SEG_DP       (SEG_DP),
    .SEG_AN0      (SEG_AN0),
    .SEG_AN1      (SEG_AN1),
    .SEG_AN2      (SEG_AN2),
    .SEG_AN3      (SEG_AN3)
    );

   
//
// Debug utility signals
//----------------------------------------
/*
msp_debug msp_debug_0 (

// OUTPUTs
    .e_state      (e_state),       // Execution state
    .i_state      (i_state),       // Instruction fetch state
    .inst_cycle   (inst_cycle),    // Cycle number within current instruction
    .inst_full    (inst_full),     // Currently executed instruction (full version)
    .inst_number  (inst_number),   // Instruction number since last system reset
    .inst_pc      (inst_pc),       // Instruction Program counter
    .inst_short   (inst_short),    // Currently executed instruction (short version)

// INPUTs
    .mclk         (mclk),          // Main system clock
    .puc_rst      (puc_rst)        // Main system reset
);
*/
//
// Generate Waveform
//----------------------------------------
initial
  begin
   `ifdef VPD_FILE
     $vcdplusfile("tb_openMSP430_fpga.vpd");
     $vcdpluson();
   `else
     `ifdef TRN_FILE
        $recordfile ("tb_openMSP430_fpga.trn");
        $recordvars;
     `else
        $dumpfile("tb_openMSP430_fpga.vcd");
        $dumpvars(0, tb_openMSP430_fpga);
     `endif
   `endif
  end

//
// End of simulation
//----------------------------------------
/*
initial // Timeout
  begin
   `ifdef NO_TIMEOUT
   `else
     `ifdef VERY_LONG_TIMEOUT
       #500000000;
     `else     
     `ifdef LONG_TIMEOUT
       #5000000;
     `else     
       #500000;
     `endif
     `endif
       $display(" ===============================================");
       $display("|               SIMULATION FAILED               |");
       $display("|              (simulation Timeout)             |");
       $display(" ===============================================");
       $finish;
   `endif
  end
*/
initial // Normal end of test
  begin
     @(inst_pc===16'hffff)
     $display(" ===============================================");
     if (error!=0)
       begin
	  $display("|               SIMULATION FAILED               |");
	  $display("|     (some verilog stimulus checks failed)     |");
       end
     else if (~stimulus_done)
       begin
	  $display("|               SIMULATION FAILED               |");
	  $display("|     (the verilog stimulus didn't complete)    |");
       end
     else 
       begin
	  $display("|               SIMULATION PASSED               |");
       end
     $display(" ===============================================");
     $finish;
  end

//
// Tasks Definition
//------------------------------

   task tb_error;
      input [65*8:0] error_string;
      begin
	 $display("ERROR: %s %t", error_string, $time);
	 error = error+1;
      end
   endtask


endmodule
