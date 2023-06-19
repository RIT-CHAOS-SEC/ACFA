module logger (
    pc,
    prev_pc,
    loop_detect,
    loop_ctr,

    cflow_src,
    cflow_dest
);

input [15:0] pc;
input [15:0] prev_pc;    //src
input        loop_detect;
input [31:0] loop_ctr;
//output  [31:0] loop_loop_ctr;

output  [15:0] cflow_src;
output  [15:0] cflow_dest;

// assign cflow_src  = ({16{loop_detect}} & loop_ctr[31:16]) ^ ({16{~loop_detect}} & prev_pc);
// assign cflow_dest = ({16{loop_detect}} & loop_ctr[15:0]) ^ ({16{~loop_detect}} & pc);

assign cflow_src  = loop_detect ? loop_ctr[31:16] : prev_pc;
assign cflow_dest  = loop_detect ? loop_ctr[15:0] : pc;

endmodule