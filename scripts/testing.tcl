while {[get_value {/tb_openMSP430_fpga/finish}] == 0} {
    run 500us
}