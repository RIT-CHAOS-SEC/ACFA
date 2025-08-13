## if the code echoing is annoying, run with:
## source -notrace script.tcl
## https://adaptivesupport.amd.com/s/article/62335?language=en_US

puts "----- ACFA START -----"

# to ensure vivado doesn't nuke your cpu in case of infinite loop for sme reason
set WORST_CASE_TIMEOUT 256 
## so I set that higher as 100 didn't work with me saying we send the full log at once so 128 words (should also have set like this for all others)
set TIMEOUT_INNER 1000 
set i 0 
set STEP 500us

# constants PER APP (rounded times)
## aha_compress 
set WORD_VERIFY_TIME 100us

# baud rate 
# --> 115200 bits per second
# --> 14400 bytes per second
# --> 14.4 bytes per millisecond
# --> 1 bytes per 0.0694 ms
# --> 1 bytes per 69.4 us (call it 70)
set BAUD_BYTE_STEP 70
set BYTE_UART_TIME 70us
## message send from vrf to prv is 65 bytes
## so RX_TIME = 65 * BAUD_BYTE_STEP 
set RX_TIME [expr "$BAUD_BYTE_STEP * 65"]us
## cflog size is constant (128 words aka 256 bytes)
set CFLOG_WORDS 128 
## start with prv waiting for vrf challenge for 0.5 ms
run $STEP

### prv first waits for AER min and max from vrf, so simulate that
### lcdnum --> e12c
###fibcall --> e112
###cover --> e658
### fdct --> e832
### jfdctint --> eaba
### crc_32 --> e210
###libbs --> e10e
## aha-compress --> e584
## libprime --> e28a

## only for caramel 
# add_force {/tb_openMSP430_fpga/dut/acfa_memory_0/vrf_resp_mem/mem[32]} -radix hex {e28a 0ns}

while {[get_value {/tb_openMSP430_fpga/finish}] == 0} {

	### Run until in sendBuffer
	puts "Running until sendBuffer()..."
	set j 0
	while { [get_value {/tb_openMSP430_fpga/in_sendBuffer}] == 0 && [get_value {/tb_openMSP430_fpga/finish}] == 0} {
		# puts "not in sendBuffer()..."
		run $STEP
		if {$j == $TIMEOUT_INNER} {
			break
		} 
		if {[get_value {/tb_openMSP430_fpga/finish}] == 1} {
			break
		}
		incr j
	}

	### Now we are in sendBuffer, so simulate send
	## data size passed via r14
	set tx_size [expr 0x[get_value {/tb_openMSP430_fpga/r14}]]
	# wait 
	puts "Running until $tx_size bytes sent..."
	for {set i 0} {$i < $tx_size} {incr i} {
		run $BYTE_UART_TIME
		# puts "Sending byte $i/$tx_size"
		if {[get_value {/tb_openMSP430_fpga/finish}] == 1} {
			break
		}
	}
	puts "Done"

	### done "sending" so set the p3_din 
	add_force {/tb_openMSP430_fpga/dut/p3_din} -radix hex {ff 0ns}
	
	## keep it set until we exit sendBuffer
	while { [get_value {/tb_openMSP430_fpga/in_sendBuffer}] == 1 && [get_value {/tb_openMSP430_fpga/finish}] == 0} {
		puts "in sendBuffer()..."
		run 5us
		if {[get_value {/tb_openMSP430_fpga/finish}] == 1} {
			break
		}
	}
	#### clear p3_din for the next round
	add_force {/tb_openMSP430_fpga/dut/p3_din} -radix hex {00 0ns}

	set pc [get_value {/tb_openMSP430_fpga/dut/openMSP430_0/pc}]
	# puts "(pc=$pc) Done adding force on p3_din..."

	#### run until in receive buffer
	set j 0
	while { [get_value {/tb_openMSP430_fpga/in_recvBuffer}] == 0 && [get_value {/tb_openMSP430_fpga/finish}] == 0} {
		# puts "not in recvBuffer()..."
		run $STEP
		if {$j == $TIMEOUT_INNER} {
			break
		} 
		if {[get_value {/tb_openMSP430_fpga/finish}] == 1} {
			break
		}
		incr j
	}

	### Now we are in recvBuffer
	## simulate Verifier doing vrf process 
	set log_size [expr 0x[get_value {/tb_openMSP430_fpga/dut/cflow_log_ptr}]]
	puts "Verifier is verifying $log_size entries...."
	for {set i 0} {$i < $log_size} {incr i} {
		run $WORD_VERIFY_TIME
		# puts "Verifying... $i/$log_size"
		if {[get_value {/tb_openMSP430_fpga/finish}] == 1} {
			break
		}
	}
	puts "Done"

	## data size passed via r14
	set rx_size [expr 0x[get_value {/tb_openMSP430_fpga/r14}]]
	# wait 
	puts "Running until $rx_size bytes recieved..."
	for {set i 0} {$i < $rx_size} {incr i} {
		run $BYTE_UART_TIME
		# puts "Receiving byte $i/$rx_size"
		if {[get_value {/tb_openMSP430_fpga/finish}] == 1} {
			break
		}
	}

	### done "receiving" so set the p3_din 
	add_force {/tb_openMSP430_fpga/dut/p3_din} -radix hex {ff 0ns}
	
	## keep it set until we exit recvBuffer
	while { [get_value {/tb_openMSP430_fpga/in_recvBuffer}] == 1 && [get_value {/tb_openMSP430_fpga/finish}] == 0} {
		# puts "in recvBuffer()..."
		run 5us
	}
	#### clear p3_din for the next round
	add_force {/tb_openMSP430_fpga/dut/p3_din} -radix hex {00 0ns}

	set pc [get_value {/tb_openMSP430_fpga/dut/openMSP430_0/pc}]
	# puts "(pc=$pc) Done adding force on p3_din..."
}

run $STEP

##### TODO -- ADD IN the HMAC TIME blub
## done

## returns the time of the sim in micro seconds
## based on above ^ this captures execution + delays for vrf response
set cur_time [current_time] 
regexp {([0-9.]+)} $cur_time -> cur_time_num

set total_hmac1_bytes [get_value {/tb_openMSP430_fpga/total_hmac1_bytes}] 
puts "Total hmac1 bytes: $total_hmac1_bytes"
## per alex spreadsheet (in micro-sec) -- adjust if needed
set hmac1_per_byte_time 24
set hmac1_time [expr "$total_hmac1_bytes * $hmac1_per_byte_time"]
puts "Total hmac1 time: $hmac1_time"

set total_hmac2_bytes [get_value {/tb_openMSP430_fpga/total_hmac2_bytes}]
## per alex spreadsheet (in micro-sec) -- adjust if needed
set hmac2_per_byte_time 427
set hmac2_time [expr "$total_hmac2_bytes * $hmac2_per_byte_time"]
puts "Total hmac2 time: $hmac2_time"

set total_run_time [expr "$hmac2_time + $cur_time_num + $hmac1_time"]
set time_time_sec [expr {$total_run_time / 1000000.0}]
puts "Estimated total run time: $total_run_time micro-sec ($time_time_sec sec)"

# puts "------------------------"