
`ifdef OMSP_NO_INCLUDE
`else
`include "openMSP430_defines.v"
`endif

module acfa (
    clk,
    pc,
    pc_nxt,
    data_en,
    data_wr,
    data_addr,
    
    dma_addr,
    dma_en,

    ER_min,
    ER_max,
//    LOG_size,
    
    puc,
    
    irq_ta0,
    irq,
    gie,
    
    e_state,
    inst_so,
    
    cflow_hw_wen,
    cflow_log_ptr,
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
input           data_en;
input           data_wr;
input   [15:0]  data_addr;
input   [15:0]  dma_addr;
input           dma_en;
input   [15:0]  ER_min;
input   [15:0]  ER_max;
//input   [15:0]  LOG_size;
input           puc;
input           irq_ta0;
input           irq;
input           gie;
input   [3:0]   e_state;
input   [7:0]   inst_so;
//input           jmp;
//input           call;
//
output          cflow_hw_wen;
output  [15:0]  cflow_log_ptr;
output  [15:0]  cflow_src;
output  [15:0]  cflow_dest;
output          reset;
output          flush;
output         boot;
output         ER_done;
// MACROS ///////////////////////////////////////////
//
parameter META_min = 16'h0140;
parameter META_max = 16'h0140 + 16'h0100 - 16'h0001;
  
//==================================================================
// CFA Module: Uses modules from VRASED and GAROTA
//==================================================================
wire cflow_reset;
cflow #()
cflow_0 (
    
    .clk        (clk),
    .pc         (pc),
    .pc_nxt     (pc_nxt),
    .data_wr    (data_wr),
    .data_addr  (data_addr),
    
    .dma_addr   (dma_addr),
    .dma_en     (dma_en),

    .puc        (puc),

    .ER_min     (ER_min),
    .ER_max     (ER_max),
//    .LOG_size   (LOG_size),
    .irq_ta0    (irq_ta0),
    .irq        (irq),
    .gie        (gie),

    .e_state    (e_state),
    .inst_so    (inst_so),
    
    .cflow_hw_wen (cflow_hw_wen),
    .cflow_log_ptr (cflow_log_ptr),
    
    .cflow_src      (cflow_src),
    .cflow_dest      (cflow_dest),
    
    .reset       (cflow_reset),
    .flush      (flush),
    .boot       (boot),
    .ER_done    (ER_done)
);
  
//==================================================================
// Active RoT Module: Uses modules from VRASED and GAROTA
//==================================================================
wire vrased_reset;// = 0;
vrased #(
) vrased_0 (
   .clk        (clk),
   .pc         (pc),
   .data_en    (data_en),
   .data_wr    (data_wr),
   .data_addr  (data_addr),
    
   .dma_addr   (dma_addr),
   .dma_en     (dma_en),

   .irq        (irq),
    
   .reset      (vrased_reset)
);

wire garota_reset;// = 0;
garota garota_0 (
    .clk        (clk),
    .pc         (pc),

    .data_en    (data_en),
    .data_wr    (data_wr),
    .data_addr  (data_addr),

	.dma_addr   (dma_addr),
    .dma_en     (dma_en),

	.irq		(irq_detect),
	
	.gie               (gie),

    .reset      (garota_reset)
);

assign reset = vrased_reset | garota_reset | cflow_reset;

endmodule
