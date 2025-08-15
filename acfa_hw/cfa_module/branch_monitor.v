
module  branch_monitor (
    clk,    
    pc,     
    ER_min,
    ER_max,
//    LOG_size,
    acfa_nmi,
    irq,
    gie,
    
    e_state,
    inst_so,
    inst_type,
    inst_ad,
    inst_as,
    inst_jmp,

    branch_detect
);

input		    clk;
input   [15:0]  pc;
input   [15:0]  ER_min;
input   [15:0]  ER_max;
//input   [15:0]  LOG_size;
input           acfa_nmi;
input           irq;
input           gie;
input   [3:0]   e_state;
input   [7:0]   inst_so;
input   [2:0]   inst_type;
input   [7:0]   inst_as;
input   [7:0]   inst_ad;
input   [7:0]   inst_jmp;
output          branch_detect;


//MACROS //
parameter LOG_SIZE = 16'h0000; // overwritten by parent module
parameter TCB_BASE = 16'ha000;

reg irq_pend;
reg call_irq;
reg acfa_nmi_pnd = 0;
initial
begin
        irq_pend = 0;
        call_irq = 0;
end

//////////////// BRANCH DETECTION /////////////////
wire jmp_or_ret = (e_state == 4'b1100);
//
wire call = (inst_so == 8'b00100000)  & (e_state == 4'b1010); 
//
wire indr_call = call & (inst_ad == 8'h0) & (inst_as == 8'h1); 
//
wire ret = (e_state == 4'b1100) & (inst_type == 3'h4) & (inst_ad == 8'h1) & (inst_as == 8'h8);
//
wire cond_jmp = (e_state == 4'b1100) & (inst_jmp != 8'b10000000) & (inst_type == 3'h2);
//
wire dir_br = (e_state == 4'b1100) & (inst_ad == 8'h1) & (inst_as == 8'h20);
//
wire indr_br = (e_state == 4'b1100) & (inst_ad == 8'h1) & (inst_as == 8'h1);
//
wire dir_jmp = (e_state == 4'b1100) & ~ret & ~dir_br & ~indr_br & ~cond_jmp;

always @(posedge clk)
if(irq && gie) // Wait --> Pend 
    irq_pend <= 1;
else if(call_irq) irq_pend <= 0; //Acc --> Wait

always @(posedge clk)
if(irq && acfa_nmi) // Wait --> Pend 
    acfa_nmi_pnd <= 1;
else if(call_irq) acfa_nmi_pnd <= 0; //Acc --> Wait
    
always @(posedge clk)
if((~gie && pc >= ER_min && pc<=ER_max && irq_pend && (e_state == 4'b0100)) || (~acfa_nmi && acfa_nmi_pnd && (e_state == 4'b0100))) // Pend --> Acc
    call_irq <= 1;
else call_irq <= 0; // Wait or Pend

// old --> detect everything
// assign branch_detect = jmp_or_ret | call | call_irq;

// new --> detect only indirect jumps/calls, returns, cond jumps, and irqs 
assign branch_detect = indr_br | indr_call | ret | cond_jmp | call_irq;

endmodule
