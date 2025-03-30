#include <stdio.h>
#include "hardware.h"

#define ULT_PIN         0x02
#define MAX_DURATION    1000

//
void acfa_exit();
void delay(unsigned int us);
long pulseIn(void);
long getUltrasonicReading(void);
//
long ult_reading;
//

//---------- Gather ultrasonic sensor readings ----------//
void delay(unsigned int us){
    int i;
    for(i=0; i<us; i++);
}

long pulseIn(void){
    unsigned long duration = 0;
    int i = 0;
    while(i < MAX_DURATION){
        duration += (P2IN & ULT_PIN);
        i++;
    }
    return duration;
 }

long getUltrasonicReading(void){
    // Set as output
    P2DIR |= ULT_PIN;

    //Set signal low for 2us
    P2OUT &= ~ULT_PIN;
    delay(2);

    // Set signal high for 5 us
    P2OUT |= ULT_PIN;
    delay(5);

    // Set signal low
    P2OUT &= ~ULT_PIN;
    
    // Set as input
    P2DIR &= ~ULT_PIN;

    unsigned long duration = pulseIn();
    
    return duration;
}

// --------------------- Main ------------------//
int main(void)
{

    P1DIR = 0xff;  // Onboard LED                     
    P2DIR = 0x00;  // Port 2.0-2.7 = Ultrasonic Sensor on P2.2

    ult_reading = getUltrasonicReading();

    // If building CF-Log of entire PMEM, this line is required.
    // Otherwise, comment this line out:
    acfa_exit();

    return 0;
}
