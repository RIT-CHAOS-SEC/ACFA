//----------------------------------------------------------------------------
// Copyright (C) 2001 Authors
//
// This source file may be used and distributed without restriction provided
// that this copyright statement is not removed from the file and that any
// derivative work contains the original copyright notice and the associated
// disclaimer.
//
// This source file is free software; you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation; either version 2.1 of the License, or
// (at your option) any later version.
//
// This source is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
// License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this source; if not, write to the Free Software Foundation,
// Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
//
//----------------------------------------------------------------------------
// 
// *File Name: ram.v
// 
// *Module Description:
//                      Scalable RAM model
//
// *Author(s):
//              - Olivier Girard,    olgirard@gmail.com
//
//----------------------------------------------------------------------------
// $Rev$
// $LastChangedBy$
// $LastChangedDate$
//----------------------------------------------------------------------------

module logger_old (

// OUTPUTs
    ram_dout,                      // RAM data output


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
 
// For LUT measurement
// (* ram_style = "block" *) reg         [15:0] mem [0:1]; 

// For sim & implementation
(* ram_style = "block" *) reg         [15:0] mem [0:(MEM_SIZE/2)-1]; 

reg         [ADDR_MSB:0] ram_addr_reg;

reg        [15:0] mem_val;

integer i;
initial 
    begin
        for(i=0; i<MEM_SIZE; i=i+1)
        begin
            mem[i] <= 0;
        end
        ram_addr_reg <= 0;
        mem_val <=  mem[0];
    end
  
always @(posedge ram_clk)
    begin
        
        if (ram_wen & write_addr<MEM_SIZE/2)
        begin
            mem[write_addr]             <= ram_din1;
            mem[write_addr+1'b1]        <= ram_din2;
        end
    end

assign ram_dout = mem[read_addr] & {16{~ram_cen}};
// assign ram_dout = mem_val;
 

endmodule // logger
