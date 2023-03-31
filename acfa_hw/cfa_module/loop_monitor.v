
module  loop_monitor (
    clk,    
    pc,
    pc_nxt,
    prev_pc,
    acfa_nmi,
    hw_wr_en,
    branch_detect,
    loop_detect,
//    loop_ctr,
    cflow_src,
    cflow_dest
);

input		    clk;
input   [15:0]  pc;         //dest
input   [15:0]  pc_nxt;
input   [15:0]  prev_pc;    //src
input          acfa_nmi;
input          hw_wr_en;
input          branch_detect;
//
output  [15:0] loop_detect;
//output  [31:0] loop_ctr;

output  [15:0]  cflow_src;
output  [15:0]  cflow_dest;

reg [15:0] loop_detect_bit = 16'h0000;
reg [31:0] ctr = 2;
reg [15:0] loop_src;
reg [15:0] loop_dest;

parameter TCB_BASE = 16'ha000;
parameter TCB_EXIT = 16'hdffe;

wire loop_done = (loop_src == pc && loop_dest != pc_nxt && pc_nxt != pc && pc_nxt != loop_dest+16'h0002);

always @(posedge clk)
begin
    // First instance
    if(hw_wr_en && ctr == 2)
    begin
        loop_src <= prev_pc;
        loop_dest <= pc;
    end
end

always @(posedge clk)
begin
    // Set ctr
//    if(branch_detect && loop_src == pc && (loop_dest == pc_nxt || loop_dest+16'h0002 == pc_nxt))
    if(hw_wr_en && loop_src == prev_pc && loop_dest == pc && !tcb_flag)
        ctr <= ctr + 1;
    else if(loop_done || tcb_flag) // restart counter when loop finish or tcb is triggered
        ctr <= 2; 
    else
        ctr <= ctr;
end

reg tcb_flag = 1'b0;
always @(posedge clk)
begin
    if(acfa_nmi)
        tcb_flag <= 1'b1;
    else if(pc == TCB_EXIT)
        tcb_flag <= 1'b0;
    else
        tcb_flag <= tcb_flag;
end

always @(posedge clk)
begin
    // Set Loop Detect Bits Logic
//    if(loop_src == prev_pc || loop_dest != pc)
//        loop_detect_bit <= 16'h0000;
//    else 
    if(loop_done || tcb_flag)
        loop_detect_bit <= 16'h0000;
    else if(ctr > 2)
        loop_detect_bit <= 16'hffff;
    else
        loop_detect_bit <= 16'h0000;
end

//always @(posedge clk)
//begin
//    if((pc < prev_pc) && hw_wr_en)
//        ctr <= ctr + 1;
//    else if(hw_wr_en)
//        ctr <= 0;
//    else
//        ctr <= ctr;
    
//    if(ctr > 1)
//        loop_detect_bit <= 16'hffff;
//    else
//        loop_detect_bit <= 16'h0000;
//end

assign loop_detect = loop_detect_bit;
//assign loop_ctr = ctr;

assign cflow_src  = (loop_detect_bit & ctr[31:16]) ^ (~loop_detect_bit & prev_pc);
assign cflow_dest = (loop_detect_bit & ctr[15:0]) ^ (~loop_detect_bit & pc);

endmodule