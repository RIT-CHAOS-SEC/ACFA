module  loop_monitor (
    clk,    
    pc,
    pc_nxt,
    // prev_pc,
    // acfa_nmi,
    // hw_wr_en,
    branch_detect,

    loop_detect,    
    loop_ctr
);

parameter TCB_BASE = 16'ha000;
parameter TCB_EXIT = 16'hdffe;
parameter CTR_MIN = 1;
parameter CTR_SIZE = 32;
 
input           clk;
input   [15:0]  pc;         //dest
input   [15:0]  pc_nxt;    //src
// input   [15:0]  prev_pc;    //src
// input           acfa_nmi; 
// input           hw_wr_en;
input           branch_detect;

output          loop_detect;
output  [CTR_SIZE-1:0]  loop_ctr;
// output  [15:0]  cflow_src;
// output  [15:0]  cflow_dest;

// reg loop_detect_bit = 1'b0;
reg [32:0] ctr = CTR_MIN;
reg [15:0] loop_src;
reg [15:0] loop_dest;

// reg [15:0] next_pc = 0;

// always @(posedge (clk))
// begin
//     if(pc != prev_pc)
//         next_pc <= pc_nxt;
// end

// wire loop_done = (loop_src == pc && loop_dest != pc_nxt && pc_nxt != pc && pc_nxt != loop_dest+16'h0002);
// wire loop_done = (loop_src == pc && ~(loop_dest == pc_nxt || loop_dest == pc_nxt-2));// && pc_nxt != pc && pc_nxt != loop_dest+16'h0002);

always @(posedge clk)
begin
    // First instance
    if(branch_detect && ctr == CTR_MIN)
    begin
        loop_src <= pc;
        loop_dest <= pc_next;
    end
end
wire [15:0] pc_next = pc_nxt-2;
wire loop_done = branch_detect & ((loop_src != pc) | (loop_dest != pc_next));
always @(posedge clk)
begin
    // Set ctr
    // if(hw_wr_en && loop_src == prev_pc && loop_dest == pc)
    if(loop_src == pc && loop_dest == pc_next)
        ctr <= ctr + 1;
    else if(loop_done)
        ctr <= CTR_MIN; 
    else
        ctr <= ctr;
end

// reg tcb_flag = 1'b0;
// always @(posedge clk)
// begin
//     if(acfa_nmi)
//         tcb_flag <= 1'b1;
//     else if(pc == TCB_EXIT)
//         tcb_flag <= 1'b0;
//     else
//         tcb_flag <= tcb_flag;
// end

// always @(posedge clk)
// begin
//     // Set Loop Detect Bits Logic
//     if(loop_done || acfa_nmi)
//         loop_detect_bit <= 1'b0;
//     else if(ctr > CTR_MIN)
//         loop_detect_bit <= 1'b1;
//     else
//         loop_detect_bit <= 1'b0;
// end

assign loop_detect = (ctr > CTR_MIN) & ~loop_done;
assign loop_ctr = ctr;

endmodule //loop_monitor