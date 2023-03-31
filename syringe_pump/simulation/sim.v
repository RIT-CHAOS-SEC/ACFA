
`define NO_TIMEOUT
reg [32:0] total_cycles = 0;
integer outfile1;
initial
   begin
      $display(" ===============================================");
      $display("|                 START SIMULATION              |");
      $display(" ===============================================");
        
      outfile1=$fopen("/home/ac7717/Documents/cflow-vrased/logs/sim.txt","w");

      //$display("pc = %h, r1 = %h, r2 = %h, r3 = %h, r4 = %h, r5 = %h, srom_dout = %h, srom_cen = %h, pmem_cen = %h\n", r0, r1, r2, r3, r4, r5, dut.srom_dout, dut.srom_cen, dut.pmem_cen);

      stimulus_done = 1;
   end

reg [32:0] num_cycles = 0;
reg [32:0] num_non_tcb_cycles = 0;

integer slicefile;
integer i;
integer count = 0;

integer log_ptr = 0;
integer logged_events = 0;

// last instruction of <__stop_progExec__>:
parameter [15:0] PROGRAM_END_INST = 16'he26c; // last instruction of <__stop_progExec__>:

//============================================
// Printing to console and debug file
always @(posedge mclk)
begin
      #1 $fdisplay(outfile1,"pc = %h, hw_wen = %h, catch_log_ptr = %h, logReady = %h, cflog[0] = %h, cflog[1] = %h\n",dut.inst_pc,dut.hdmod_0.cflow_hw_wen,catch_log_ptr,logReady,dut.CFLOW_metadata_0.logs.mem[0],dut.CFLOW_metadata_0.logs.mem[1]);
      num_cycles = num_cycles + 1;

      #1 $fdisplay(outfile1, "entering_TCB = %h, jmp_or_ret = %h, call = %h, call_irq = %h, irq = %h, acfa_nmi = %h\n",dut.hdmod_0.cflow_0.CFLOW_log_monitor_0.entering_TCB,dut.hdmod_0.cflow_0.CFLOW_branch_monitor_0.jmp_or_ret,dut.hdmod_0.cflow_0.CFLOW_branch_monitor_0.call,dut.hdmod_0.cflow_0.CFLOW_branch_monitor_0.call_irq,dut.hdmod_0.cflow_0.CFLOW_branch_monitor_0.irq,dut.hdmod_0.cflow_0.CFLOW_branch_monitor_0.acfa_nmi);

      #1 $display("pc = %h, hw_wen = %h, catch_log_ptr = %h, logReady = %h, cflog[0] = %h, cflog[1] = %h\n",dut.inst_pc,dut.hdmod_0.cflow_hw_wen,catch_log_ptr,logReady,dut.CFLOW_metadata_0.logs.mem[0],dut.CFLOW_metadata_0.logs.mem[1]);
      #1 $display("entering_TCB = %h, jmp_or_ret = %h, call = %h, call_irq = %h, irq = %h, acfa_nmi = %h\n",dut.hdmod_0.cflow_0.CFLOW_log_monitor_0.entering_TCB,dut.hdmod_0.cflow_0.CFLOW_branch_monitor_0.jmp_or_ret,dut.hdmod_0.cflow_0.CFLOW_branch_monitor_0.call,dut.hdmod_0.cflow_0.CFLOW_branch_monitor_0.call_irq,dut.hdmod_0.cflow_0.CFLOW_branch_monitor_0.irq,dut.hdmod_0.cflow_0.CFLOW_branch_monitor_0.acfa_nmi);
      
      // Check if r0 = exit instruction
      if(r0==PROGRAM_END_INST && count > 1)
      begin
            $display("Total time %d cycles", $signed(num_cycles));
            $display("Final state:\n");
            $finish;
      end
end


//=====================================================================
// Capture and write CF-Logs -- ONLY EDIT LOG FILE PATH (lines 68-76)
//=====================================================================
wire catch_log_ptr = (dut.hdmod_0.pc == 16'ha000) && (dut.hdmod_0.pc_nxt != 16'ha000) && (dut.hdmod_0.cflow_0.prev_pc != 16'ha000);

wire logReady = (dut.hdmod_0.cflow_hw_wen == 0) && ~catch_log_ptr && (dut.hdmod_0.pc > 16'ha000 && dut.hdmod_0.pc < 16'hdffe);

always @(posedge catch_log_ptr)
      begin
            $display("Catching log_ptr value (pc=%h)\n", dut.inst_pc);
            log_ptr <= dut.cflow_log_ptr;
            //  logged_events <= ((dut.cflow_log_ptr + 16'h0002) >> 1);// + dut.cflow_log_ptr[0];
            logged_events <= ((dut.cflow_log_ptr) >> 1);// + dut.cflow_log_ptr[0];
      end

always @(posedge logReady)
begin
      $display("Log is ready (pc=%h)\n", dut.inst_pc);

       case(count)
           0: slicefile=$fopen("/home/ac7717/Documents/cflow-vrased/logs/0.cflog","w");
           1: slicefile=$fopen("/home/ac7717/Documents/cflow-vrased/logs/1.cflog","w");
           2: slicefile=$fopen("/home/ac7717/Documents/cflow-vrased/logs/2.cflog","w");
           3: slicefile=$fopen("/home/ac7717/Documents/cflow-vrased/logs/3.cflog","w");
           4: slicefile=$fopen("/home/ac7717/Documents/cflow-vrased/logs/4.cflog","w");
           5: slicefile=$fopen("/home/ac7717/Documents/cflow-vrased/logs/5.cflog","w");
           6: slicefile=$fopen("/home/ac7717/Documents/cflow-vrased/logs/6.cflog","w");
           7: slicefile=$fopen("/home/ac7717/Documents/cflow-vrased/logs/7.cflog","w");
           8: slicefile=$fopen("/home/ac7717/Documents/cflow-vrased/logs/8.cflog","w");
           9: slicefile=$fopen("/home/ac7717/Documents/cflow-vrased/logs/9.cflog","w");
       endcase
       

       for (i = 0; i < log_ptr; i = i +2) begin
          // $fdisplay(slicefile,"%h",dut.CFLOW_metadata_0.logs.logs.ram[i]);  //write as hex 
          $fdisplay(slicefile,"%h%h",dut.CFLOW_metadata_0.logs.mem[i],dut.CFLOW_metadata_0.logs.mem[i+1]);  //write as hex 
           // $fdisplay(slicefile,"%h",dut.dmem_0.mem[16'h1100+i]);  //write as hex
       end
       $fdisplay(slicefile,"%d",log_ptr);  //write log_ptr as last value
       $fdisplay(slicefile,"%d",logged_events);
       
       $fclose(slicefile);

       count = count + 1;
       $display("count = %h\n", count);
end
//============================================