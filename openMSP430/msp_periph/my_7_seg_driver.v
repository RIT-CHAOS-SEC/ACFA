// fpga4student.com: FPGA projects, Verilog projects, VHDL projects
// FPGA tutorial: seven-segment LED display controller on Basys  3 FPGA
module my_7_seg_driver(
    input clock_100Mhz, // 100 Mhz clock source on Basys 3 FPGA
    input [3:0] s0_src,
    input [3:0] s1_src,
    input [3:0] s2_src,
    input [3:0] s3_src,
    input reset, // reset
    output reg [3:0] anode, // anode signals of the 7-segment LED display
    output reg [6:0] LED_out// cathode patterns of the 7-segment LED display
);

reg [3:0] LED_BCD = 0;

reg [3:0] s0_ctr;
reg [3:0] s1_ctr;
reg [3:0] s2_ctr;
reg [3:0] s3_ctr;

reg s0_flag;
reg s1_flag;
reg s2_flag;
reg s3_flag;

initial
begin
    s0_flag <= 1'b0;
    s1_flag <= 1'b0;
    s2_flag <= 1'b0;
    s3_flag <= 1'b0;
    
    s0_ctr <= 4'b0000;
    s1_ctr <= 4'b0000;
    s2_ctr <= 4'b0000;
    s3_ctr <= 4'b0000;
       
    anode <= 4'b0000;
    LED_out <= 7'b0000;
    refresh_counter <= 2'b00;
    LED_BCD <= 4'b0000;
end

always @(posedge clock_100Mhz)
begin
    s0_ctr <= s0_src;
    s1_ctr <= s1_src;
    s2_ctr <= s2_src;
    s3_ctr <= s3_src;
end

//always @(posedge clock_100Mhz)
//begin
//    s0_flag <= reset;
//    s1_flag <= reset;
//    s2_flag <= reset;
//    s3_flag <= reset;
//end

//// seg 0 counter
//always @(posedge s0_flag)
//begin 
//    if(s0_ctr == 4'b1111)
//        s0_ctr <= 1'h0;
//    else
//        s0_ctr <= s0_ctr+1'h1;
//end 

//// seg 1 counter
//always @(posedge s1_flag)
//begin 
//    if(s1_ctr == 4'b1111)
//        s1_ctr <= 1'h0;
//    else
//        s1_ctr <= s1_ctr+1'h1;
//end

//// seg 2 counter
//always @(posedge s2_flag)
//begin 
//    if(s2_ctr == 4'b1111)
//        s2_ctr <= 1'h0;
//    else
//        s2_ctr <= s2_ctr+1'h1;
//end 

//// seg 3 counter
//always @(posedge s3_flag)
//begin 
//    if(s3_ctr == 4'b1111)
//        s3_ctr <= 1'h0;
//    else
//        s3_ctr <= s3_ctr+1'h1;
//end 

reg [15:0] refresh_counter = 4'h0000; 
// the first 18-bit for creating 2.6ms digit period
// the other 2-bit for creating 4 LED-activating signals
wire [1:0] LED_activating_counter; 
// count        0    ->  1  ->  2  ->  3
// activates    LED1    LED2   LED3   LED4
// and repeat
always @(posedge clock_100Mhz)// or posedge reset)
begin 
// if(reset==1)
//  refresh_counter <= 0;
// else
  refresh_counter <= refresh_counter + 1;
end 
assign LED_activating_counter = refresh_counter[15:14];

// anode activating signals for 4 LEDs, digit period of 2.6ms
// decoder to generate anode signals 
always @(*)
begin
    case(LED_activating_counter)
    2'b00: begin
        anode = 4'b0111; 
        // activate LED1 and Deactivate LED2, LED3, LED4
        LED_BCD = s0_ctr;
        // the first digit of the 16-bit number
          end
    2'b01: begin
        anode = 4'b1011; 
        // activate LED2 and Deactivate LED1, LED3, LED4
        LED_BCD = s1_ctr;
        // the second digit of the 16-bit number
          end
    2'b10: begin
        anode = 4'b1101; 
        // activate LED3 and Deactivate LED2, LED1, LED4
        LED_BCD = s2_ctr;
        // the third digit of the 16-bit number
            end
    2'b11: begin
        anode = 4'b1110; 
        // activate LED4 and Deactivate LED2, LED3, LED1
        LED_BCD = s3_ctr;
        // the fourth digit of the 16-bit number    
           end
    endcase
end

// Cathode patterns of the 7-segment LED display 
always @(*)
begin
    case(LED_BCD)
        4'b0000: LED_out = 7'b0000001; // "0"     
        4'b0001: LED_out = 7'b1001111; // "1" 
        4'b0010: LED_out = 7'b0010010; // "2" 
        4'b0011: LED_out = 7'b0000110; // "3" 
        4'b0100: LED_out = 7'b1001100; // "4" 
        4'b0101: LED_out = 7'b0100100; // "5" 
        4'b0110: LED_out = 7'b0100000; // "6" 
        4'b0111: LED_out = 7'b0001111; // "7" 
        4'b1000: LED_out = 7'b0000000; // "8"     
        4'b1001: LED_out = 7'b0000100; // "9" 
        4'b1010: LED_out = 7'b0001000; // "A"
        4'b1011: LED_out = 7'b1100000; // "b"
        4'b1100: LED_out = 7'b0110001; // "C"
        4'b1101: LED_out = 7'b1000010; // "d"
        4'b1110: LED_out = 7'b0110000; // "E"
        4'b1111: LED_out = 7'b0111000; // "F"
        default: LED_out = 7'b0000001; // "0"
    endcase
end
   
 endmodule

