#include <isr_compat.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "hardware.h"

#define TEMP_PIN		0x02
#define MAX_READINGS	83
extern void tcb (); 

// Temperature sensor output data
int temp;
int humidity;
uint8_t data[5] = {0,0,0,0,0};
uint8_t valid_reading = 0;
/******** Configurable by vrf **************/

void delay(unsigned int us){
	int i;
	for(i=0; i<us; i++);
}

void read_data(){
	uint8_t counter = 0;
  	uint16_t j = 0, i;

  	/// pull signal high & delay
  	P2OUT |= TEMP_PIN;
  	delay(250);

  	/// pull signal low for 20us
  	P2OUT &= ~TEMP_PIN;
  	delay(20);

  	/// pull signal high for 40us
  	P2OUT &= ~TEMP_PIN;
  	delay(40);

  	//read timings
  	for(i=0; i<MAX_READINGS; i++){
  		counter += (P2IN & TEMP_PIN);

		// ignore first 3 transitions
		if ((i >= 4) && ( (i & 0x01) == 0x00)) {
			// shove each bit into the storage bytes
			data[j >> 3] <<= 1;
			if (counter > 6)
			data[j >> 3] |= 1;
			j++;
		}
  	}

	// check we read 40 bits and that the checksum matches
	if ((j >= 40) && (data[4] == ((data[0] + data[1] + data[2] + data[3]) & 0xFF)) ) {
		valid_reading = 1;
	} else {
		valid_reading = 0;
	}
}

uint16_t get_temperature(){
	read_data();

	uint16_t t = data[2];
	t |= (data[3] << 8);
	return t;
}

uint16_t get_humidity(){
	read_data();

	uint16_t h = data[0];
	h |= (data[1] << 8);
	return h;
}

int main(){ // <5ms on MSP430

	P2DIR = 0x00;                     // Port 2.0-2.7: Temperature Sensor on P2.2

	P5DIR = 0xFF; 				      // Port 1 press controls LED
	P5OUT = 0x00;		

	// Get sensor readings
	temp = get_temperature();
	// humidity = get_humidity();
	
	// If building CF-Log of entire PMEM, this line is required.
	acfa_exit();

	return 0;
}