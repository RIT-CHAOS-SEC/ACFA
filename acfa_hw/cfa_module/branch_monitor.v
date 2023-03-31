
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
wire call = (inst_so == 8'b00100000)  & (e_state == 4'b1010); // e_state = A

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

assign branch_detect = jmp_or_ret | call | call_irq;

endmodule
