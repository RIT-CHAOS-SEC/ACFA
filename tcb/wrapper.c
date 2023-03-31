#include <string.h>
#include "hardware.h"

// Watchdog timer
#define WDTCTL_              0x0120    /* Watchdog Timer Control */
#define WDTHOLD             (0x0080)
#define WDTPW               (0x5A00)

// KEY
#define KEY_ADDR 0x6A00
#define KEY_SIZE 32 // in bytes

// METADATA
#define CHAL_BASE       0x180 //180-19f
#define CHAL_SIZE       32 // in bytes
#define METADATA_ADDR   CHAL_BASE+CHAL_SIZE
#define ERMIN_ADDR      METADATA_ADDR //1a0-1
#define ERMAX_ADDR      ERMIN_ADDR+2  //1a2-3
#define CLOGP_ADDR      ERMAX_ADDR+2  //1a4-5
#define METADATA_SIZE   6

// CFLog
#define LOG_BASE        0x1b0 //CHAL_BASE + CHAL_SIZE + METADATA_SIZE+4 //0x1a6
#define LOG_SIZE        256 // in bytes
// #define LOG_SIZE        512 
// #define LOG_SIZE        1024
// #define LOG_SIZE        2048

// Set ER_MIN/MAX based on setting
#define PMEM_MIN  0xE000
#define PMEM_MAX  &acfa_exit

#define ER_MIN  PMEM_MIN
#define ER_MAX  PMEM_MAX

// Timmer settings
#define TIMER_1MS 125 
#define MAX_TIME  0xffff
#define ACFA_TIME MAX_TIME // 50*TIMER_1MS // Time in ms -- note vivado sim is 4x faster

// Communication
#define DELAY     100
#define UART_TIMEOUT   0x167FFE
#define ACK       'a'

// DUMMY DATA TO TEST COMMUNICATION ONLY
#define RESP_ADDR 0xb00
#define KEY_ALT_ADDR 0xb20
#define CHAL_XS 0xb40
#define PRV_AUTH 0xb60
#define VRF_AUTH 0xb80

// Attested Program memory range
#define ATTEST_DATA_ADDR   0xe000
// #define ATTEST_SIZE        0x1fff //8kb
// #define ATTEST_SIZE        0x0fff //4kb
// #define ATTEST_SIZE        0x07ff //2kb
#define ATTEST_SIZE        0x03ff //1kb

// Protocol variables in SData
#define NEW_CHAL_ADDR         0xba4
#define TMP_16_BUFF           0xbc4
#define LOG_BASE_XS   0xca6

// TCB version
#define NOT_SIM   0
#define SIM   1
#define IS_SIM  NOT_SIM
//

/**********     Function Definitions      *********/
__attribute__ ((section (".tcb.lib"))) void my_memset(uint8_t* ptr, int len, uint8_t val);
void my_memcpy(uint8_t* dst, uint8_t* src, int size);
int secure_memcmp(const uint8_t* s1, const uint8_t* s2, int size);
void tcb();
void tcb_attest();
void tcb_wait();
void Hacl_HMAC_SHA2_256_hmac_exit();
void tcb_exit();
void recvBuffer(uint8_t * rx_data, uint16_t size);
void sendCFLog(uint16_t size);
void sendBuffer(uint8_t * tx_data, uint16_t size);
void echo_tx_rx(uint8_t * data, uint16_t size);
void echo_rx_tx(uint8_t * data, uint16_t size);
// EXTERNAL FUNCTIONS
extern void acfa_exit();
#if IS_SIM == NOT_SIM
extern void hmac(uint8_t *mac, uint8_t *key, uint32_t keylen, uint8_t *data, uint32_t datalen);
#else
#define hmac my_hmac
void my_hmac(uint8_t *mac, uint8_t *key, uint32_t keylen, uint8_t *data, uint32_t datalen);
#endif

/**********  CORE TCB    *********/
#pragma vector=FLUSH_VECTOR
__interrupt __attribute__ ((section (".tcb.call")))
void tcb_entry(){
    // __asm__ volatile("push    r11" "\n\t");
    // __asm__ volatile("push    r4" "\n\t");
    // __asm__ volatile("mov    r1,    r4" "\n\t");

    
    // Call TCB Body:
    tcb();

    // Release registers
    // __asm__ volatile("pop    r4" "\n\t");
    __asm__ volatile("pop    r12" "\n\t");
    __asm__ volatile("pop    r13" "\n\t");
    __asm__ volatile("pop    r14" "\n\t");
    __asm__ volatile("pop    r15" "\n\t");

    __asm__ volatile("br #__tcb_leave" "\n\t");
}

__attribute__ ((section (".fini9"), naked)) void acfa_exit(){
    __asm__ volatile("br #__stop_progExec__" "\n\t");
}

__attribute__ ((section (".tcb.body"))) void tcb() {

    /********** SETUP ON ENTRY **********/
    // Switch off the WTD
    uint32_t* wdt = (uint32_t*)(WDTCTL_);
    *wdt = WDTPW | WDTHOLD;

    // Configure Timer A0 for timeout
    CCTL0 = CCIE;                            // CCR0 interrupt enabled
    CCR0  = ACFA_TIME;                     // Set based on time
    TACTL = TASSEL_2 + MC_1 + ID_3;          // SMCLK, contmode

    // Pause Timer
    TACTL &= ~MC_1;
    
    //Clear timer
    TAR = 0x00;

    // Init UART
    UART_BAUD = BAUD;                   
    UART_CTL  = UART_EN;

    P3DIR |= 0xff;

    #if IS_SIM == NOT_SIM
    // // /********** TCB ATTEST **********/
    // Save current value of r5 and r6:
    __asm__ volatile("push    r5" "\n\t");
    __asm__ volatile("push    r6" "\n\t");

    // Save return address
    __asm__ volatile("mov    #0x0012,   r6" "\n\t");
    __asm__ volatile("mov    #0x500,   r5" "\n\t");
    __asm__ volatile("mov    r0,        @(r5)" "\n\t");
    __asm__ volatile("add    r6,        @(r5)" "\n\t");

    // Save the original value of the Stack Pointer (R1):
    __asm__ volatile("mov    r1,    r5" "\n\t");

    // Set the stack pointer to the base of the exclusive stack:
    __asm__ volatile("mov    #0x1704,     r1" "\n\t");

    // tcb_attest(); // monitored by VRASED
    
    tcb_attest();

    // Copy retrieve the original stack pointer value:
    __asm__ volatile("mov    r5,    r1" "\n\t");

    // // Restore original r5,r6 values:
    __asm__ volatile("pop   r6" "\n\t");
    __asm__ volatile("pop   r5" "\n\t");
    #endif

    #if IS_SIM == SIM
    tcb_attest();

    *((uint16_t*)(ERMIN_ADDR)) = ER_MIN;
    P1OUT = *((uint8_t*)(ERMIN_ADDR));
    P1OUT = *((uint8_t*)(ERMIN_ADDR+1));
    *((uint16_t*)(ERMAX_ADDR)) = ER_MAX;
    P1OUT = *((uint8_t*)(ERMAX_ADDR));
    P1OUT = *((uint8_t*)(ERMAX_ADDR+1));
    #endif

    // Resume Timer on exit
    TACTL |= MC_1; 
    
    return;
}

// TCB_ATTEST
__attribute__ ((section (".tcb.attest"))) void tcb_attest()
{
 
    #if IS_SIM == SIM
    uint8_t * cflog = (uint8_t * )(LOG_BASE);
    unsigned int i;
    for(i=0; i<LOG_SIZE; i++){
        P1OUT = cflog[i];
    }

    #else
    // graph sdtata addrs for each obj
    uint8_t * response = (uint8_t*)(RESP_ADDR);
    uint8_t * key = (uint8_t*)(KEY_ADDR);
    uint8_t * metadata = (uint8_t*)(METADATA_ADDR);

    /********** TCB WAIT ************/
    uint8_t readyByte = ACK;

    echo_tx_rx(&readyByte, 1);
    if(readyByte == ACK){
        my_memcpy((uint8_t*)(LOG_BASE_XS), (uint8_t*)(LOG_BASE), LOG_SIZE);

        my_memcpy((uint8_t*)(CHAL_XS), (uint8_t*)(CHAL_BASE), CHAL_SIZE);

        hmac(response, key, (uint32_t) KEY_SIZE, (uint8_t*)(ATTEST_DATA_ADDR), (uint32_t) ATTEST_SIZE);

        hmac(response, response, (uint32_t) KEY_SIZE, (uint8_t*)(CHAL_XS), (uint32_t) CHAL_SIZE);

        hmac(response, response, (uint32_t) KEY_SIZE, metadata, (uint32_t) METADATA_SIZE);

        hmac(response, response, (uint32_t) KEY_SIZE, (uint8_t*)(LOG_BASE_XS), (uint32_t) *((uint16_t*)(CLOGP_ADDR))*2);

        tcb_wait();
    }

    // restore return address
    __asm__ volatile("mov    #0x500,   r6" "\n\t");
    __asm__ volatile("mov    @(r6),     r6" "\n\t");

    // postamble -- check LST, add all insts before "ret"
    __asm__ volatile("incd  r1" "\n\t");
    // __asm__ volatile("pop   r11" "\n\t");
    #endif

    // safe exit
    __asm__ volatile( "br      #__mac_leave" "\n\t");
}

__attribute__ ((section (".do_mac.leave"))) __attribute__((naked)) void Hacl_HMAC_SHA2_256_hmac_exit() 
{
  __asm__ volatile("ret" "\n\t");
}

// TCB WAIT
__attribute__ ((section (".tcb.wait"))) void tcb_wait(){
    uint8_t * response = (uint8_t*)(RESP_ADDR);
    uint8_t * key = (uint8_t*)(KEY_ADDR);
    uint8_t * challenge = (uint8_t*)(CHAL_BASE);
    uint8_t * metadata = (uint8_t*)(METADATA_ADDR);
    uint8_t * cflog = (uint8_t*)(LOG_BASE_XS);

    // receive data
    uint8_t * recv_new_chal = (uint8_t*)(NEW_CHAL_ADDR);
    uint8_t * recv_auth = (uint8_t*)(VRF_AUTH);
    
    uint8_t app = 10;
    uint8_t * buffer_8_to_16 = (uint8_t*)(TMP_16_BUFF);

    unsigned int i;
    
    //// send H, METADATA, CFLog (2)
    // H
    sendBuffer(response, KEY_SIZE);
    P3OUT++;
    // metadata
    sendBuffer(metadata, METADATA_SIZE);
    P3OUT++;
    // cflog
    sendBuffer(cflog, *((uint16_t*)(CLOGP_ADDR))*2);      
    
    P3OUT++;
    //// Receive app, chal', AER_min, AER_max, Auth to Prv (6)
    // app
    echo_rx_tx(&app, 1);

    P3OUT++;
    //chal'
    echo_rx_tx(recv_new_chal, KEY_SIZE);

    P3OUT++;
    // AER_min
    echo_rx_tx(buffer_8_to_16, 2);

    *((uint16_t*)(ERMIN_ADDR)) = (buffer_8_to_16[0] << 8) | buffer_8_to_16[1];
    P3OUT++;

    // AER_max
    echo_rx_tx(buffer_8_to_16, 2);

    *((uint16_t*)(ERMAX_ADDR)) = (buffer_8_to_16[0] << 8) | (buffer_8_to_16[1]);

    //auth
    echo_rx_tx(recv_auth, KEY_SIZE);

    P3OUT++;
    // Authenticate & produce 'out'
    uint8_t out = 0x00;
    for(i=0; i<KEY_SIZE; i++){
        if(recv_new_chal[i] > challenge[i]){
            out = 0x01;
            break;
        } else if(recv_new_chal[i] < challenge[i]){
            out = 0x00;
            break;
        }
    }
    P3OUT++;
    // check auth token
    uint8_t * auth =  (uint8_t*)(PRV_AUTH);

    hmac(auth, key, (uint32_t) KEY_SIZE, recv_new_chal, (uint32_t) KEY_SIZE);

    buffer_8_to_16[0] = (uint8_t) (*((uint16_t*)(ERMIN_ADDR)) >> 8);
    buffer_8_to_16[1] = (uint8_t) (*((uint16_t*)(ERMIN_ADDR)) & 0x00ff);
    P3OUT++;
    hmac(auth, auth, (uint32_t) KEY_SIZE, buffer_8_to_16, (uint32_t) 2);

    buffer_8_to_16[0] = (uint8_t) (*((uint16_t*)(ERMAX_ADDR)) >> 8);
    buffer_8_to_16[1] = (uint8_t) (*((uint16_t*)(ERMAX_ADDR)) & 0x00ff);
    P3OUT++;
    hmac(auth, auth, (uint32_t) KEY_SIZE, buffer_8_to_16, (uint32_t) 2);

    P3OUT++;
    hmac(auth, auth, (uint32_t) KEY_SIZE, &app, (uint32_t) 1);

    sendBuffer(auth, KEY_SIZE);
    recvBuffer(auth, KEY_SIZE);
    P3OUT++;
    
    out ^= secure_memcmp(auth, recv_auth, KEY_SIZE);
    P3OUT++;

    sendBuffer(&out, 1);
    recvBuffer(&out, 1);
    P3OUT++;
    if(out == 0){
        // inauthentic vrf -- re-enter tcb_wait
        P2OUT = 0x55;
    } else {
        P2OUT = 0x0f;
        if(app == 1){
            // vrf approved --> resume exec
           P2OUT |= 0xf0;
        } else {
            // vrf does not approve --> tcb_heal
           P2OUT |= 0x50;
           // "Shut Down"
           _BIS_SR(CPUOFF);

           // "Reset"
           //((void(*)(void))(*(uint16_t*)(0xFFFE)))();
        }
    }
    P3OUT++;

    //DEBUG: print old chal on vrf side
    sendBuffer((uint8_t * )(CHAL_BASE), CHAL_SIZE);

    // Update challenge
    my_memcpy((uint8_t * )(CHAL_BASE), (uint8_t * )(NEW_CHAL_ADDR), CHAL_SIZE);

    //DEBUG: print new chal on vrf side
    sendBuffer((uint8_t * )(CHAL_BASE), CHAL_SIZE);
    // recvBuffer((uint8_t * )(CHAL_BASE), CHAL_SIZE);

    //DEBUG: print first 16 bytes of attested memory
    sendBuffer((uint8_t * )(ATTEST_DATA_ADDR), 16);
}

__attribute__ ((section (".tcb.leave"), naked)) void tcb_exit() {
    __asm__ volatile("reti" "\n\t");
}

 /**********  UTILITY    *********/
#if IS_SIM == SIM
__attribute__ ((section (".tcb.wait"))) void my_hmac(uint8_t *mac, uint8_t *key, uint32_t keylen, uint8_t *data, uint32_t datalen){
    unsigned int i;
    unsigned int j;
    for(i=0; i<keylen; i++){
        mac[i] = key[i] | data[i];
    }
}
#endif

__attribute__ ((section (".tcb.lib"))) void my_memset(uint8_t* ptr, int len, uint8_t val) {
  int i=0;
  for(i=0; i<len; i++) ptr[i] = val;
}

__attribute__ ((section (".tcb.lib"))) void my_memcpy(uint8_t* dst, uint8_t* src, int size) {
  int i=0;
  for(i=0; i<size; i++) dst[i] = src[i];
}

__attribute__ ((section (".tcb.lib"))) int secure_memcmp(const uint8_t* s1, const uint8_t* s2, int size) {
    int res = 0;
    int first = 1;
    for(int i = 0; i < size; i++) {
      if (first == 1 && s1[i] > s2[i]) {
        res = 1;
        first = 0;
      }
      else if (first == 1 && s1[i] < s2[i]) {
        res = 1;
        first = 0;
      }
    }
    return res;
}

/************ UART COMS ************/
__attribute__ ((section (".tcb.wait"))) void recvBuffer(uint8_t * rx_data, uint16_t size){
    P3OUT ^= 0x40;
    unsigned int i=0, j;
    unsigned long time = 0;
    while(i < size && time != UART_TIMEOUT){
        
        #if IS_SIM == NOT_SIM
        // wait while rx buffer is empty         // implementation only
        while((UART_STAT & UART_RX_PND) != UART_RX_PND && time != UART_TIMEOUT){
            time++;
        }
        UART_STAT |= UART_RX_PND;
        #endif

        if(time == UART_TIMEOUT){
            break;
        } else {
            rx_data[i] = UART_RXD;
            
            #if IS_SIM == NOT_SIM
            // implementation only
            for(j=0; j<DELAY; j++)
            {} // wait for buffer to clear before reading next char
            #endif
            
            i++;
        }
    }
    P3OUT ^= 0x40;
}

__attribute__ ((section (".tcb.wait"))) void sendBuffer(uint8_t * tx_data, uint16_t size){

    P3OUT ^= 0x20;
    unsigned int i, j;
    for(i=0; i<size; i++){
        #if IS_SIM == NOT_SIM
        // delay until tx buffer is empty // implementation only
        while(UART_STAT & UART_TX_FULL);
        #endif

        UART_TXD = tx_data[i];
        
        #if IS_SIM == NOT_SIM
        // only implementation
        for(j=0; j<DELAY; j++)
        {} // wait for buffer to clear before sending next char
        #endif

    }
    P3OUT ^= 0x20;
}

__attribute__ ((section (".tcb.wait"))) void echo_rx_tx(uint8_t * data, uint16_t size){

    unsigned int i=0, j;
    unsigned long time = 0;
    uint8_t byte;
    uint8_t cleared = 0;
    // RX ALL BYTES
    while(i < size){
        
        #if IS_SIM == NOT_SIM
        // wait for rx buffer or timeout // only on implementation
        while((UART_STAT & UART_RX_PND) != UART_RX_PND && time != UART_TIMEOUT){
            time++;
        }
        UART_STAT |= UART_RX_PND;
        #endif

        if(time != UART_TIMEOUT)
        {
            // P5OUT = SET_GREEN;
            byte = UART_RXD;
            
            #if IS_SIM == NOT_SIM
            // only for implementation
            for(j=0; j<DELAY; j++)
            {} // wait for buffer to clear before reading next char
            #endif

            if(byte != ACK && cleared != 1){
                cleared = 1; // while data overflowed ACK's, ignore data
            }

            if(cleared){
                data[i] = byte;
            }

            i++;

        } else {
            i = 0;
        }
        time = 0;
    }

    // TX ALL BYTES
    for(i=0; i<size; i++){
        
        #if IS_SIM == NOT_SIM
        // delay until tx buffer is empty // only for implementation
        while(UART_STAT & UART_TX_FULL);
        #endif

        UART_TXD = data[i];

        #if IS_SIM == NOT_SIM
        // only for implementation
        for(j=0; j<DELAY; j++)
        {} // wait for buffer to clear before sending next char
        #endif
    }
}

__attribute__ ((section (".tcb.wait"))) void echo_tx_rx(uint8_t * data, uint16_t size){

    unsigned long i=0, j;
    unsigned long time;
    unsigned char delivered = 0;
    while(!delivered){
        // TX ALL BYTES
        for(i=0; i<size; i++){
            #if IS_SIM == NOT_SIM
            // delay until tx buffer is empty // only for implementation
            while(UART_STAT & UART_TX_FULL);
            #endif

            UART_TXD = data[i];

            #if IS_SIM == NOT_SIM
            // only for implementation
            for(j=0; j<DELAY; j++)
            {} // wait for buffer to clear before sending next char
            #endif
        }

        // RX ALL BYTES
        i = 0;
        time = 0;
        while(i < size){
            #if IS_SIM == NOT_SIM
            // wait for rx buffer or timeout // only for implementation
            while((UART_STAT & UART_RX_PND) != UART_RX_PND && time != UART_TIMEOUT){
                time++;
            }
            UART_STAT |= UART_RX_PND;
            #endif

            if(time != UART_TIMEOUT)
            {
                data[i] = UART_RXD;
                
                #if IS_SIM == NOT_SIM
                // only for implementation
                for(j=0; j<DELAY; j++)
                {} // wait for buffer to clear before sending next char
                #endif

                i++;
                delivered = 1;
            } else {
                delivered = 0;
                break;
            }
        }
    }
}
