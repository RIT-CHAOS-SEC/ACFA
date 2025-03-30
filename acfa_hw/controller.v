module  controller (
    mclk,
    cflow_log_ptr,
    read_val,
    boot,
    flush,
    ER_done,

    //
    trigger,
    read_idx,
    continue,
    byte_val,

    t1,
    t2,
    t3
);

input mclk;
input [15:0] cflow_log_ptr;
input [15:0] read_val;
input boot;
input flush;
input ER_done;

output reg trigger;
output reg [15:0] read_idx;
output continue;
output [7:0] byte_val;


//// debug
output reg t1;
output reg t2;
output reg t3;

///
reg counter;
reg [15:0] log_ptr_catch;
reg start;
reg [15:0] trigger_count;

initial
begin
    trigger <= 1'b0;
    //
    t1 <= 1'b0;
    t2 <= 1'b0;
    t3 <= 1'b0;
    read_idx <= 16'h0;
    counter <= 0;
    log_ptr_catch <= 16'h0;
    start <= 1'b0;
    trigger_count <= 16'h0;
end
///

/// here we catch the log_ptr so we know how much of cflog to send
always @(posedge (mclk))
begin
    if(boot)
    begin
        t1 <= 1'b1;
        log_ptr_catch <= cflow_log_ptr;
    end

    if(flush)
    begin
        t2 <= 1'b1;
        log_ptr_catch <= cflow_log_ptr;
    end

    if (ER_done)
    begin
        t3 <= 1'b1;
        log_ptr_catch <= cflow_log_ptr;
    end
end 

/// flag to start transmitting
always @(posedge (mclk))
begin
    if (ER_done)
        start <= 1'b1;
end

/// iterates through cflog entries byte by byte in each entry
// trigger_count is delay between bytes
always @(posedge (mclk))
begin
    if (start == 1'b1)
    begin
        if(trigger == 1'b1)
        begin
            if(counter == 1'b1)
            begin
                read_idx <= read_idx + 16'h1;
                counter <= 1'b0;
            end
            else if(counter == 1'b0)
                counter <= 1'b1;
            trigger <= 1'b0;
        end

        // else if(trigger == 1'b0)
        // begin
        if (trigger_count != 16'hffff)
            trigger_count <= trigger_count + 1;
        else
        begin
            trigger_count <= 16'h0;
            trigger <= 1'b1;
        end
        // end
    end
end 

///// ouptut wires
assign continue = (read_idx <= log_ptr_catch);
assign byte_val = counter ? read_val[15:8] : read_val[7:0];

endmodule