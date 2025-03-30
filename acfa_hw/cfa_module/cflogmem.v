`include "openMSP430_defines.v"

module cflogmem (

// OUTPUTs
    ram_dout,                      // RAM data output
    read_val,

// INPUTs
    read_addr,                      // RAM address
    write_addr,                      // RAM address
    ram_cen,                       // RAM chip enable (low active)
    ram_clk,                       // RAM clock
    ram_din1,                      // RAM data input
    ram_din2,                      // RAM data input
    ram_wen                        // RAM write enable (low active)
);

// PARAMETERs
//============ 
parameter MEM_SIZE   =  256;       // Memory size in bytes
parameter ADDR_MSB   =  7;         // MSB of the address bus
// ADDR_MSB = LOG_2(MEM_SIZE)-1

// OUTPUTs
//============
output      [15:0] ram_dout;       // RAM data output
output      [15:0] read_val;       // RAM data output

// INPUTs
//============
input [ADDR_MSB:0] read_addr;        // RAM address
input [ADDR_MSB:0] write_addr;       // RAM address
input              ram_cen;          // RAM chip enable (low active)  
input              ram_clk;          // RAM clock
input       [15:0] ram_din1;         // RAM data input
input       [15:0] ram_din2;         // RAM data input
input        [1:0] ram_wen;          // RAM write enable (low active)

// RAM 
//============
 
reg        [15:0] mem_val;

`ifdef ACFA_HW_ONLY
initial 
begin
    mem_val <=  16'h0;
end
`else
(* ram_style = "block" *) reg         [15:0] cflog [0:(MEM_SIZE/2)-1]; 
integer i;
initial 
begin
    for(i=0; i<MEM_SIZE; i=i+1)
    begin
        cflog[i] <= 0;
    end
    mem_val <=  cflog[0];
end
`endif  

always @(posedge ram_clk)
    begin
        
        if (ram_wen & write_addr<MEM_SIZE/2)
        begin
        `ifdef ACFA_HW_ONLY
            mem_val <= ram_din1;
        `else
            cflog[write_addr]             <= ram_din1;
            cflog[write_addr+1'b1]        <= ram_din2;
        `endif
        end
    end

`ifdef ACFA_HW_ONLY
assign ram_dout = mem_val;
`else 
assign ram_dout = cflog[read_addr] & {16{~ram_cen}};
`endif

assign read_val = cflog[read_addr];

endmodule // cflogmem
