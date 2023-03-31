#include <stdio.h>
#include "hardware.h"
/* -- Constants -- */
/* -- Constants -- */
#define SYRINGE_VOLUME_ML 30.0
#define SYRINGE_BARREL_LENGTH_MM 8.0

#define THREADED_ROD_PITCH 1.25
#define STEPS_PER_REVOLUTION 4.0
#define MICROSTEPS_PER_STEP 16.0

#define SPEED_MICROSECONDS_DELAY 100 //longer delay = lower speed

#define false  0
#define true   1

#define LED_OUT_PIN 0
/* -- Enums and constants -- */
//syringe movement direction
enum{PUSH,PULL};
extern void VRASED (uint8_t *challenge, uint8_t *response, uint8_t operation);

extern void my_memset(uint8_t* ptr, int len, uint8_t val);

extern void my_memcpy(uint8_t* dst, uint8_t* src, int size);

void delayMicroseconds(unsigned int delay)
{
    volatile unsigned int j = 0;
    for (; j < delay; j++);
}

char getserialinput(uint8_t inputserialpointer)
{
    uint8_t maxinputpointer = 2;
    char input[2] = "+\n";
    if (inputserialpointer < maxinputpointer)
    {
        return input[inputserialpointer];
    }
    return 0;
}
// INSTRUMENTER: entry
int syringepump()
{
    /* -- Global variables -- */
    // Input related variables
    volatile uint8_t inputserialpointer = -1;
    uint16_t inputStrLen = 0;
    char inputStr[10]; //input string storage

    // Bolus size
    uint16_t mLBolus =  5;

    // Steps per ml
    int ustepsPerML = (MICROSTEPS_PER_STEP * STEPS_PER_REVOLUTION * SYRINGE_BARREL_LENGTH_MM) / (SYRINGE_VOLUME_ML * THREADED_ROD_PITCH );
    
    //int ustepsPerML = 10;
    int inner = 0;
    int outer = 0;
    int steps = 0;

    while(outer < 1)
       {
           char c = getserialinput(++inputserialpointer);
           // hex to char reader
           while (inner < 10)
           {
               if(c == '\n') // Custom EOF
               {
                   break;
               }
               if(c == 0)
               {
                   outer = 10;
                   break;
               }
               inputStr[inputStrLen++] = c;
               c = getserialinput(++inputserialpointer);
               inner += 1;
           }
           inputStr[inputStrLen++] = '\0';
           steps = mLBolus * ustepsPerML;
           if(inputStr[0] == '+' || inputStr[0] == '-')
           {
               for(int i=0; i < steps; i++)
               {
                    P3OUT = 0xff;
                    delayMicroseconds(SPEED_MICROSECONDS_DELAY);
                    P3OUT = 0x0;
                    delayMicroseconds(SPEED_MICROSECONDS_DELAY);
                }
            }
            inputStrLen = 0;
            outer += 1;
        }
        return steps;
    }


int main(){ 
	P2DIR = 0x00;                     // Port 2.0-2.7 = Ultrasonic Sensor on P2.2
    P5DIR = 0xFF;                     // Port 1 press controls LED
    P3OUT = 0x00;       
    // Run Syringe Pump
    syringepump(); 
    // If building CF-Log of entire PMEM, this line is required.
    acfa_exit();
	return 0;
}