// `include "VAPE_immutability.v"
// `include "VAPE_atomicity.v"
// `include "VAPE_output_protection.v"
// `include "VAPE_EXEC_flag.v"
// `include "VAPE_boundary.v"
// `include "VAPE_reset.v"
// `include "VAPE_irq_dma.v"

`include "log_monitor.v"
`include "branch_monitor.v"
`include "boundary_monitor.v"
`include "loop_monitor.v"
`include "logger.v"

`ifdef OMSP_NO_INCLUDE
`else
`include "openMSP430_defines.v"
`endif

module cflow (
    clk,
    pc,
    pc_nxt,
    
    data_wr,
    data_addr,
    
    dma_addr,
    dma_en,
    
    puc,

    ER_min,
    ER_max,

    irq_ta0,
    irq,
    gie,
    
    e_state,
    inst_so,
    inst_type,
    
    cflow_hw_wen,
    cflow_log_ptr,
    // cflow_log_ptr_prev,
    cflow_src,
    cflow_dest,
    
    reset,
    flush,
    boot,
    ER_done
);
input           clk;
input   [15:0]  pc;
input   [15:0]  pc_nxt;
input           data_wr;
input   [15:0]  data_addr;
input   [15:0]  dma_addr;
input           dma_en;
input   [15:0]  ER_min;
input   [15:0]  ER_max;
input           puc;
input           irq_ta0;
input           irq;
input           gie;
input   [3:0]   e_state;
input   [7:0]   inst_so;
input   [2:0]   inst_type;

// 
output          cflow_hw_wen;
output  [15:0]  cflow_log_ptr;
// output  [15:0]  cflow_log_ptr_prev;
output  [15:0]  cflow_src;
output  [15:0]  cflow_dest; 
output          reset;
output          flush;
output          boot;
output          ER_done;

parameter LOG_SIZE = 16'h0100; // # of 2-byte words
parameter TCB_max = 16'hdffe; 
parameter RESET_addr = 16'he000;
parameter PMEM_min = 16'he03e;

reg tcb_boot_done = 0;
reg [15:0] prev_pc;
// wire [15:0] cflow_log_prev_ptr;
wire [31:0] loop_ctr;
wire loop_detect_out;
wire acfa_nmi = irq_ta0 | flush | ER_done | boot;
// wire pc_TCB_exit = (pc == TCB_max);

boundary_monitor #() 
boundary_monitor_0 ( // Boundary Protection
    .clk        (clk),
    .pc         (pc),
    .data_addr  (data_addr),
    .data_en    (data_wr),
    .dma_addr   (dma_addr),
    .dma_en     (dma_en),
    .ER_min     (ER_min),
    .ER_max     (ER_max),
    .reset      (reset) 
);

log_monitor #(
    .LOG_SIZE (LOG_SIZE)
) 
log_monitor_0 (
    .clk        (clk),
    .pc         (pc),
    .pc_nxt     (pc_nxt),
    
    .ER_min     (ER_min),
    .ER_max     (ER_max),
 
    .irq        (irq),
    .reset      (puc),
    .loop_detect    (loop_detect_out),
    .branch_detect  (branch_detect),

    .flush      (flush),
    .hw_wr_en       (cflow_hw_wen),
    .cflow_log_ptr  (cflow_log_ptr)
    // .cflow_log_ptr_prev (cflow_log_ptr_prev)
);

branch_monitor #(
    .LOG_SIZE (LOG_SIZE)
)
branch_monitor_0( //Branch Monitor
    
    .clk            (clk),    
    .pc             (pc),     
    .ER_min         (ER_min),
    .ER_max         (ER_max),
    .acfa_nmi   (acfa_nmi),
    .irq        (irq),
    .gie        (gie),

    .e_state    (e_state),
    .inst_so    (inst_so),
    .inst_type  (inst_type),
    
    .branch_detect (branch_detect)
);

always @(posedge clk)
begin
    prev_pc <= pc;  
end

loop_monitor loop_monitor_0(
    .clk            (clk),    
    .pc             (pc),
    .pc_nxt         (pc_nxt),
    // .prev_pc        (prev_pc),
    
    // .acfa_nmi       (acfa_nmi),
    // .hw_wr_en       (cflow_hw_wen),
    .branch_detect  (branch_detect),
    
    .loop_detect    (loop_detect_out),
    .loop_ctr       (loop_ctr)
);

logger logger_0(
    // .clk            (clk),
    .pc             (pc),
    .prev_pc        (prev_pc),
    
    .loop_detect    (loop_detect_out),
    .loop_ctr       (loop_ctr),
    .cflow_src      (cflow_src),
    .cflow_dest     (cflow_dest)
);

always @(posedge clk) 
begin
   if(pc == TCB_max)
      tcb_boot_done <= 1'b1;
   else if(reset)
      tcb_boot_done <= 1'b0;
   else
      tcb_boot_done <= tcb_boot_done;
end

assign ER_done = (pc == ER_max) & tcb_boot_done;
assign boot = (pc == PMEM_min);

endmodule //cflow
