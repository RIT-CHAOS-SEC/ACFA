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
void int_func(int num){
    int i;
    for(i=0; i<num*2; i++);
}

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
int a = 0;
void (*func_ptr)(int);
int main(void)
{

    P1DIR = 0xff;  // Onboard LED                     
    P2DIR = 0x00;  // Port 2.0-2.7 = Ultrasonic Sensor on P2.2
    int c = 0;
    /*ult_reading = getUltrasonicReading();*/
    if (a == 0){
        func_ptr = &delay;
        delay(2);
    } else{
        func_ptr = &int_func;
        delay(2);
    }

    switch(a){
        case 0: c++; break;
        case 1: c++; break;
        case 2: c++; break;
        case 3: c++; break;
        case 4: c++; break;
        case 5: c++; break;
        case 6: c++; break;
        case 7: c++; break;
        case 8: c++; break;
        case 9: c++; break;
    }

    func_ptr(2);

    // If building CF-Log of entire PMEM, this line is required.
    // Otherwise, comment this line out:
    acfa_exit();

    return 0;
}
