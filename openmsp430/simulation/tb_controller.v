module tb_controller;

// Testbench signals
reg clk;
reg puc_rst;
reg acfa_nmi;
reg [15:0] read_val;
wire tx_triggered;
wire txfer_done;
wire controller_en;
wire [7:0] byte_val;

// Instantiate the controller module
controller ctrl_0 (
    .clk             (clk),
    .puc_rst         (puc_rst),
    .acfa_nmi        (acfa_nmi),
    .read_val        (read_val),
    .tx_triggered    (tx_triggered),
    .txfer_done      (txfer_done),
    .data_tx_wr      (controller_en),
    .tx_byte         (byte_val)
);

/// instantiate uart
wire             irq_uart_rx;     // UART receive interrupt
wire             irq_uart_tx;     // UART transmit interrupt
wire      [15:0] per_dout;        // Peripheral data output
wire             uart_txd;        // UART Data Transmit (TXD)
wire      [7:0] ctrl_out;        // UART_CTL
wire      [7:0] stat_out;         // UART_STAT
///
omsp_uart #(.BASE_ADDR(15'h0080)) uart_0 (

// OUTPUTs
    .irq_uart_rx  (irq_uart_rx),   // UART receive interrupt
    .irq_uart_tx  (irq_uart_tx),   // UART transmit interrupt
    .per_dout     (per_dout_uart), // Peripheral data output
    .uart_txd     (hw_uart_txd),   // UART Data Transmit (TXD)
    .ctrl_out     (ctrl_out),
    .stat_out     (stat_out),
    .tx_triggered (tx_triggered),
    .tx_done      (txfer_done),

// INPUTs
    .mclk         (clk),          // Main system clock
    .per_addr     (0),      // Peripheral address
    .per_din      (0),       // Peripheral data input
    .per_en       (0),        // Peripheral enable (high active)
    .per_we       (0),        // Peripheral write enable (high active)
    .puc_rst      (puc_rst),       // Main system reset
    .smclk_en     (1),      // SMCLK enable (from CPU)
    .uart_rxd     (0),    // UART Data Receive (RXD)
    .irq_rx_acc  (0),    // Interrupt request RX accepted
    .irq_tx_acc  (0),    // Interrupt request TX accepted
    .controller_en    (controller_en),
    .cflog_val  (byte_val)
    // .acfa_nmi   (acfa_nmi)
);



// Clock generation
always #5 clk = ~clk; // 10ns period (100MHz)

initial begin
    // Initialize signals
    clk = 0;
    puc_rst = 1;
    acfa_nmi = 0;
    read_val = 16'hABCD;  // Example test value
    // tx_triggered = 0;
    // txfer_done = 0;

    // Reset the controller
    #20 puc_rst  = 0;
    
    // Trigger UART transmission
    #10 acfa_nmi = 1;  
    #10 acfa_nmi = 0; // Simulate a pulse

    #20 //wait

    // Finish simulation
    #50;
    $finish;
end


endmodule