/**
 * Adam Caulfield
 * 
 * Demo software for the Prover
 * 
 * main.c
 * 
 * Prv compares a buffer (which simulates user input) to constant password
 * After receiving a correct password, Prv gathers six ultrasonic sensor readings
 * 
 * Since Prv software is vulnerable, an adversary can cause a buffer overflow to skip the password check
 * and can gather the sensor readings without a correct password
 * 
 * To execute the benign version with a correct password, define user_input based on line 35 (and comment out line 38)
 * 
 * To execute the attack version with a incorrect password and buffer overflow, define user_input based on line 38 (and comment out line 35)
 * 
*/

#include <stdio.h>
#include "hardware.h"

// Password defines
#define size            4
#define user_size       5
#define attack_size   9 
#define cr              '\r'

// Ultrasonic sensor 
#define HIGH            0xffff
#define LOW             0x0000
#define ULT_PIN         0x02
#define MAX_DURATION    1000
#define TOTAL_READINGS  6

// TARGET ADDRESS OF ATTACK: location of "access granted" -- 0xe06c
#define TARGET_UPPER    0xe0
#define TARGET_LOWER    0x6c

// functions
void acfa_exit();
int my_memcmp(const char* s1, const char* s2, int length);
char waitForPassword();
void read_data(char * entry);
void delay(unsigned int us);
long pulseIn(void);
long getUltrasonicReading(void);
//

// Password
char pass[4] = {'a', 'b', 'c', 'd'};

// Simulate non-attack input
char user_input[5] = {'a', 'b', 'c', 'd', '\r'};

// Simulate Buffer overflow attack
// Since the code waits for '\r', the return address can be overwritten to skip the password check
// This input includes an incorrect password jump to 'grant access' after the return from waitForPassword
// char user_input[attack_size] = {0x01, 0x02, 0x03, 0x04, 0x00, 0x04, TARGET_LOWER, TARGET_UPPER, '\r'};

// Output data
long ult_readings[TOTAL_READINGS] = {0,0,0,0,0,0};


//---------- Check "password" code (vulnerable to buffer-overflow) ----------//
char waitForPassword(){
    char entry[4] = {0,0,0,0};

    read_data(entry);

    char total = 0;
    unsigned int i;
    for(i=0; i<4; i++){
        total |= (pass[i] ^ entry[i]);
    }

    return total;
}

void read_data(char * entry){
    // simulate uart receive
    int  i = 0;
    while(user_input[i] != cr){
        // save read value
        entry[i] = user_input[i];
        i++;
    }
}
//---------- Gather ultrasonic sensor readings ----------//
// delay microseconds
void delay(unsigned int us){
    int i;
    for(i=0; i<us; i++);
}
// measures total duration of pulse(s) over a max duration
long pulseIn(void){
    unsigned long duration = 0;
    int i = 0;
    while(i < MAX_DURATION){
        duration += (P2IN & ULT_PIN);
        i++;
    }
    return duration;
 }
// get reading from ultrasonic sensor, connected to PORT2
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

    // Enable GPIO
    P1DIR = 0xff;  // Onboard LED                     
    P2DIR = 0x00;  // Port 2.0-2.7 = Ultrasonic Sensor on P2.2
    
    // Call wait for password, 'total' determines validity of password
    char total = waitForPassword();

    if(total != 0){
        // Deny access
        P1OUT = 0x00;
    }
    else { 
        // Grant access
        P1OUT = 0x01;
        unsigned char i = 0;
        // After granting access, collect readings from sensor
        while(i < TOTAL_READINGS){
            ult_readings[i] = getUltrasonicReading();
            i++;
        }
    }

    // If building CF-Log of entire PMEM, this line is required.
    // Otherwise, comment this line out:
    acfa_exit();

    return 0;
}
