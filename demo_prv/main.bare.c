#include <msp430fr2476.h>
#include <stdint.h>

#define KEY_SIZE 32
#define SET_GREEN   BIT0
#define SET_RED   BIT1
#define SET_BLUE  BIT7
#define SET_OFF   0x00
#define DELAY     100
#define TIMEOUT   1000
#define ACK       'a'

//uint8_t key[KEY_SIZE] = {35,1,103,69,171,137,239,205,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
uint8_t key[KEY_SIZE] = {0,0,0,0,0,0,0,0,
                         0,0,0,0,0,0,0,0,
                         0,0,0,0,0,0,0,0,
                         0,0,0,0,0,0,0,0};
// data
uint8_t challenge[KEY_SIZE];
uint8_t response[KEY_SIZE];
uint16_t aermin = 0;// = 0xe000;
uint16_t aermax = 0;// = 0xfffe;

// buffer to read 16bit number
uint8_t buffer_8_to_16[2] = {0,0};

//

// metadata: [ermin, ermax, log_ptr]
#define METADATA_SIZE   6
uint8_t metadata[METADATA_SIZE] = {0xe0, 0x00, 0xff, 0xfe, 0x00, 0x02};
#define METADATA_ADDR   &metadata[0]
//
// model cflog
#define LOG_SIZE   4
uint8_t cflog[LOG_SIZE] = {0xe0, 0x40, 0xdf, 0xfe};
#define LOG_BASE   &cflog[0]
//
// model attested program memory
#define ATTEST_SIZE   4
uint8_t pmem[LOG_SIZE] = {0xab, 0xcd, 0x12, 0x34};
#define ATTEST_DATA_ADDR   &pmem[0]
//
uint8_t readyByte;
uint8_t ackByte = 'a';
uint8_t acfa_nmi = 0;
volatile uint8_t wipeBuffer;
//
void setup();
void tcb_wait();
void my_hmac(uint8_t *mac, uint8_t *key, uint32_t keylen, uint8_t *data, uint32_t datalen);
void recvBuffer(uint8_t * rx_data, uint8_t size);
void sendBuffer(uint8_t * tx_data, uint8_t size);
//

// Attest & return response (H)
void tcb_attest(){
    my_hmac(response, key, (uint32_t) KEY_SIZE, (uint8_t*) ATTEST_DATA_ADDR, (uint32_t) ATTEST_SIZE);

    my_hmac(response, response, (uint32_t) KEY_SIZE, challenge, (uint32_t) KEY_SIZE);

    my_hmac(response, response, (uint32_t) KEY_SIZE, (uint8_t*) METADATA_ADDR, (uint32_t) METADATA_SIZE);

    my_hmac(response, response, (uint32_t) KEY_SIZE, (uint8_t*) LOG_BASE, (uint32_t) LOG_SIZE);
}

void main(void)
{
    setup();

    while(1);
}

void tcb_wait(){
    uint8_t recv_new_chal[KEY_SIZE];
    uint8_t auth[KEY_SIZE];
    uint8_t recv_auth[KEY_SIZE];
    uint8_t app = 10;
    unsigned int i;

    // produce HMAC, store in mac (mimic tcb_attest)  (1)
    tcb_attest();
    //my_hmac(mac, key, KEY_SIZE, challenge, KEY_SIZE);

    //// send H, METADATA, CFLog (2)
    // H
    sendBuffer(response, KEY_SIZE);
    // metadata
    sendBuffer((uint8_t *) METADATA_ADDR, METADATA_SIZE);
    // cflog
    sendBuffer((uint8_t *) LOG_BASE, LOG_SIZE);

    //// Receive app, chal', AER_min, AER_max, Auth to Prv (6)
    // app
    recvBuffer(&app, 1);
    sendBuffer(&app, 1);

    //chal'
    recvBuffer(recv_new_chal, KEY_SIZE);
    sendBuffer(recv_new_chal, KEY_SIZE);

    // AER_min
    recvBuffer(buffer_8_to_16, 2);
    aermin = (buffer_8_to_16[0] << 8) | buffer_8_to_16[1];
    sendBuffer(buffer_8_to_16, 2);

    // AER_max
    recvBuffer(buffer_8_to_16, 2);
    aermax = (buffer_8_to_16[0] << 8) | (buffer_8_to_16[1]);
    sendBuffer(buffer_8_to_16, 2);

    //auth
    recvBuffer(recv_auth, KEY_SIZE);
    sendBuffer(recv_auth, KEY_SIZE);

    // Authenticate & produce out
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
    // check auth token
    my_hmac(auth, key, (uint32_t) KEY_SIZE, recv_new_chal, (uint32_t) KEY_SIZE);
    buffer_8_to_16[0] = (uint8_t) (aermin >> 8);
    buffer_8_to_16[1] = (uint8_t) (aermin & 0x00ff);
    my_hmac(auth, auth, (uint32_t) KEY_SIZE, buffer_8_to_16, (uint32_t) 2);
    buffer_8_to_16[0] = (uint8_t) (aermax >> 8);
    buffer_8_to_16[1] = (uint8_t) (aermax & 0x00ff);
    my_hmac(auth, auth, (uint32_t) KEY_SIZE, buffer_8_to_16, (uint32_t) 2);
    my_hmac(auth, auth, (uint32_t) KEY_SIZE, &app, (uint32_t) 1);

    sendBuffer(auth, KEY_SIZE);
    for(i=0; i<KEY_SIZE; i++){
        if(auth[i] != recv_auth[i]){
            out = 0x00;
            break;
        }
    }

    sendBuffer(&out, 1);

    if(out == 0){
        // inauthentic vrf -- re-enter tcb_wait
        P5OUT = SET_GREEN | SET_RED;
    } else {
        if(app == 1){
            // vrf approved --> resume exec
            P5OUT = SET_GREEN;
        } else {
            // vrf does not approve --> tcb_heal
            P5OUT = SET_RED;
        }
    }

}

void my_hmac(uint8_t *mac, uint8_t *key, uint32_t keylen, uint8_t *data, uint32_t datalen){
    uint32_t i;
    uint32_t j = 0;
    for(i=0; i<datalen; i++){
        mac[j] = (data[i] | key[j]);
        j++;
        if(j == keylen){
            j = 0;
        }
    }
}

void setup(){
    WDTCTL = WDTPW | WDTHOLD;   // stop watchdog timer

    PM5CTL0 &= ~LOCKLPM5;       // Disable the GPIO power-on default high-impedance mode
                                // to activate previously configured port settings

    // Setup UART A1
    UCA0CTLW0 |= UCSWRST;  // put A1 into SW RESET

    UCA0CTLW0 |= UCSSEL__SMCLK; // Choose SMCLK for UART A1
    UCA0BRW = 8; // Divide SMCLK by 8 (1Mhz / 8)
    UCA0MCTLW |= 0xD600; // Modulation and Low Power setting

    // Select UART Ports
    // Pass UART A0 RX over P1.5
    P1SEL1 &= ~BIT5;
    P1SEL0 |= BIT5;

    // Pass UART A0 TX over P1.4
    P1SEL1 &= ~BIT4;
    P1SEL0 |= BIT4;

    // LED1 is Port 1 Pin 0
    P1OUT &= 0x00; // Shut down pins on P1
    P1DIR = 0x00; // Set P1 pins as input (= 0)

    P5DIR |= BIT0;
    P5DIR |= BIT1;
    P5OUT &= 0x00;

    UCA0CTLW0 &= ~UCSWRST;  // TAKE A1 OUT OF SW RESET

    // Blue Pin is Port 4 Pin 7
    P4OUT &= 0x00; // Shut down pins on P5
    P4DIR = BIT7; // P5.0 pin set as output (1) (RGB LED) the rest are input (0)
    //BTN1 is Port 4 pin 0
    P4REN |= BIT0; // Enable internal pull-up resistors for Port 4 pin 1 (BTN1)
    P4OUT |= BIT0; // Select pull-up mode for Port 4 pin 1 (BTN1)
    P4IE |= BIT0;  // signal on this pin triggers interrupt
    P4IES |= BIT0; // high to low edge
    P4IFG &= ~BIT0; // clear interrupt flag on P4.1

//    UCA0IE |= UCRXIE;   // Enable receive interrupt

    __enable_interrupt();
    UCA0STATW = 0x00;

    unsigned int i;
    for(i=0; i<25; i++){
        challenge[i] = 0x62+i;
    }

    for(i=0; i<7; i++){
        challenge[25+i] = 0x30+i;
    }
}

#pragma vector=PORT4_VECTOR
__interrupt void tcb_entry(void){
    acfa_nmi = 1;
    while(acfa_nmi){
        sendBuffer(&ackByte, 1);
        recvBuffer(&readyByte, 1);
        if(readyByte == ACK){
            P4OUT &= ~(SET_BLUE);
            tcb_wait();
            readyByte = 0;
        }
        acfa_nmi = 0;
        P4IFG &= ~BIT0;
    }
}

/**************** Helper Functions ****************/
void recvBuffer(uint8_t * rx_data, uint8_t size){
    P4OUT ^= SET_BLUE;
    unsigned int i=0, j;
    unsigned long timeout = 0x8ffff;
    unsigned long time = 0;
    while(i < size && time != timeout){
        // wait while rx buffer is empty
        while((UCA0IFG & UCRXIFG) != UCRXIFG && time != timeout){
            time++;
        }
        if(time == timeout){
            break;
        } else {
            rx_data[i] = UCA0RXBUF;
            for(j=0; j<DELAY; j++)
            {} // wait for buffer to clear before sending next char
            i++;
        }
    }
}

void sendBuffer(uint8_t * tx_data, uint8_t size){
//    P5OUT ^= SET_GREEN;
//    P4OUT ^= SET_BLUE;
    unsigned int i, j;
    for(i=0; i<size; i++){
        // delay until tx buffer is empty
        while((UCA0IFG & UCTXIFG) != UCTXIFG);

        UCA0TXBUF = tx_data[i];
        for(j=0; j<DELAY; j++)
        {} // wait for buffer to clear before sending next char
    }
//    P5OUT = SET_OFF;
//    P4OUT = SET_OFF;
}
