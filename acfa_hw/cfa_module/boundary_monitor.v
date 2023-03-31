module  boundary_monitor (
    clk,
    //
    pc,
    //
    data_addr,
    data_en,
    //
    dma_addr,
    dma_en,
    //
    ER_min,
    ER_max,
    //
    reset
);

input		clk;
input   [15:0]  pc;
input   [15:0]  data_addr;
input           data_en;
input   [15:0]  dma_addr;
input           dma_en;
input   [15:0]  ER_min;
input   [15:0]  ER_max; 
output          reset;

// State codes
parameter RUN  = 1'b0, KILL = 1'b1; 
//-------------Internal Variables---------------------------
reg             state;
reg             reset_reg;
// 

initial
    begin
        state = KILL;
        reset_reg = 1'b0;
    end

parameter META_min = 16'h0180;
parameter META_max = META_min + 16'h0026 - 16'h0001;

parameter LOG_SIZE = 16'h0080; // # of 2-byte words
parameter LOG_min = 16'h01b0;
parameter LOG_max = LOG_min + LOG_SIZE+16'h0002;

parameter TCB_BASE = 16'hA000; 
parameter TCB_SIZE = 16'h4000;

parameter RESET_HANDLER = 16'h0000;

// PC compared to TCB
wire outside_TCB = (pc < TCB_BASE) || (pc >= TCB_BASE + TCB_SIZE);
wire inside_TCB =  ~outside_TCB;

// detect write to METADATA by cpu or dma
wire is_write_META = data_en && (data_addr >= META_min && data_addr <= META_max) && outside_TCB;
wire is_write_DMA_META = dma_en && (dma_addr >= META_min && dma_addr <= META_max);
wire META_change = is_write_META || is_write_DMA_META;

// detect write to ER by cpu or dma
wire is_write_ER = data_en && (data_addr >= ER_min && data_addr <= ER_max) && outside_TCB;
wire is_write_DMA_ER = dma_en && (dma_addr >= ER_min && dma_addr <= ER_max);
wire ER_change = is_write_ER || is_write_DMA_ER;

// detect write to LOG by cpu or dma
wire is_write_LOG = data_en && (data_addr >= LOG_min && data_addr <= LOG_max) && outside_TCB;
wire is_write_DMA_LOG = dma_en && (dma_addr >= LOG_min && dma_addr <= LOG_max);
wire LOG_change = is_write_LOG || is_write_DMA_LOG;

always @(posedge clk)
if( state == RUN && (META_change || ER_change || LOG_change)) 
    state <= KILL;
else if (state == KILL && (pc==RESET_HANDLER) && !META_change && !ER_change && !LOG_change)
    state <= RUN;
else state <= state;

always @(posedge clk)
if (state == RUN && (META_change || ER_change || LOG_change)) 
    reset_reg <= 1'b1;
else if (state == KILL && (pc==RESET_HANDLER) && !META_change && !ER_change && !LOG_change)
    reset_reg <= 1'b0;
else if (state == KILL)
    reset_reg <= 1'b1;
else if (state == RUN)
    reset_reg <= 1'b0;
else reset_reg <= 1'b0;

assign reset = reset_reg;

endmodule
