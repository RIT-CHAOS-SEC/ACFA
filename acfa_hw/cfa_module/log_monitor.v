
module  log_monitor (
    clk,
    //
    pc,
    pc_nxt,
    //
    ER_min,
    ER_max,
    //
    irq,
    reset,

    loop_detect,
    branch_detect,

    flush,
    hw_wr_en,
    cflow_log_ptr,
    cflow_log_prev_ptr
);

input		clk;
input   [15:0]  pc;
input   [15:0]  pc_nxt;
//
input   [15:0]  ER_min;
input   [15:0]  ER_max;
//
input       irq;
input		reset;
//
input           loop_detect;
input           branch_detect;

output          flush;
output          hw_wr_en;
output  [15:0]  cflow_log_ptr;
output  [15:0]  cflow_log_prev_ptr;

// Logging States //////////////////////////////////////////////////////////
parameter notX = 2'b00;
parameter Wait = 2'b01;
parameter inX = 2'b10;
parameter Write = 2'b11;

parameter TCB_min = 16'ha000;
parameter TCB_max = 16'hdffe;

// Trigger States
parameter EXEC  = 1'b0, ABORT = 1'b1;

parameter LOG_SIZE = 16'h0000; // overwritten by parent module

//-------------Internal Variables---------------------------
reg             state;
reg             flush_log;
reg             attest_pend;
reg     [1:0]   pc_state;
reg     [15:0]  log_ptr_reg;
wire     [15:0]  log_ptr_next;
reg     [15:0]  log_ptr_prev;
reg             wr_en;
//

initial
    begin
        pc_state = notX;
        log_ptr_reg = 16'b0;
        wr_en = 0;
        state = ABORT;
        flush_log = 1'b0;
        attest_pend = 1'b0;
//        entering_ER = 1'b0;
        cf_ctr = 16'h0000;
    end

wire is_fst_ER = pc == ER_min;
wire log_full = log_ptr_reg+2 >= LOG_SIZE;

always @(posedge clk)
if( state == EXEC && (reset || log_full))
    state <= ABORT;
else if (state == ABORT && !reset && !log_full)
    state <= EXEC;
else state <= state;

always @(posedge clk)
if (state == EXEC && (log_full || reset))
    flush_log <= 1'b1;
else if (state == ABORT && !reset && !log_full)
    flush_log <= 1'b0;
else if (attest_pend) //Pend --> Acc
    flush_log <= 0;

always @(posedge clk)
if(log_full && irq) // Abort --> Pend
    attest_pend <= 1;
else
    attest_pend <= 0;
    
assign flush = flush_log;

always @(posedge clk)
begin
    begin
    case (pc_state)
        notX:
            if(pc >= ER_min && pc <= ER_max)
                pc_state <= inX;
            else
                pc_state <= pc_state;
                
        Wait:
            if(branch_detect && !log_full)
                pc_state <= Write;
            else if(pc > ER_max || pc < ER_min)
                pc_state <= notX;
            else
                pc_state <= pc_state;
                
        inX:
            if(branch_detect && !log_full)
                pc_state <= Write;
            else if(!branch_detect || log_full)
                pc_state <= Wait;
            else 
                pc_state <= pc_state;
                
        Write:
            if(!branch_detect || log_full)
                pc_state <= Wait;
            else if(pc > ER_max || pc < ER_min)
                pc_state <= notX;
            else
                pc_state <= pc_state;
     endcase 
     end
     
end 

////////////// OUTPUT LOGIC //////////////////////////////////////
//wire dest_in_ER = (pc_nxt <= ER_max) && (pc_nxt >= ER_min);
//wire src_out_ER = ((pc > ER_max) || (pc < ER_min));// && (prev_pc == pc);
wire entering_ER = (pc == TCB_max) && ((pc_nxt >= ER_min) && (pc_nxt <= ER_max));

wire pc_next_in_TCB = (pc_nxt >= TCB_min) && (pc_nxt <= TCB_max); 
wire pc_out_TCB = (pc <= TCB_min) || (pc >= TCB_max);  
wire entering_TCB = pc_out_TCB && pc_next_in_TCB;

always @(posedge clk)
begin
//    if(entering_ER)
//        wr_en <= 1'b1;
//    else 
    if(pc_state == notX && entering_ER && branch_detect && (log_ptr_reg+2 < LOG_SIZE))
        wr_en <= 1'b1;
    else if(entering_TCB && branch_detect) //notX
        wr_en <= 1'b1;
    else if(pc > TCB_min && pc < TCB_max)
         wr_en <= 1'b0; 
    else if((pc_state == inX || pc_state == Wait) && branch_detect && (log_ptr_reg+2 < LOG_SIZE))
        wr_en <= 1'b1;
    else //if(pc_state == Wait or notX) 
        wr_en <= 1'b0;
end

always @(posedge clk)
begin
    if(pc_state == notX && entering_ER && branch_detect && (log_ptr_reg+2 < LOG_SIZE))
        log_ptr_reg <= log_ptr_next+16'b10;
    else if(entering_TCB && branch_detect) //notX
        log_ptr_reg <= log_ptr_next+16'b10;
    else if(pc > TCB_min && pc < TCB_max)
        log_ptr_reg <= log_ptr_next; 
    else if((pc_state == inX || pc_state == Wait) && branch_detect && (log_ptr_reg+2 < LOG_SIZE) && !loop_detect)
        log_ptr_reg <= log_ptr_next+16'b10;
    else if(pc == TCB_max)
        log_ptr_reg <= 16'b0;
    else //if(pc_state == Wait) 
        log_ptr_reg <= log_ptr_next;
end

reg [15:0] cf_ctr;
always @(posedge clk)
begin
    if(pc_state == notX && entering_ER && branch_detect)
        cf_ctr <= cf_ctr+16'b01;
    else if((pc_state == inX || pc_state == Wait || entering_ER) && branch_detect && !loop_detect)
        cf_ctr <= cf_ctr+16'b01;
    else //if(pc_state == Wait) 
        cf_ctr <= cf_ctr;
end

/////////////////// OUTPUT //////////////////////
assign cflow_log_prev_ptr = log_ptr_next;
assign hw_wr_en = wr_en;
assign cflow_log_ptr = log_ptr_reg;
assign log_ptr_next = log_ptr_reg;

endmodule
