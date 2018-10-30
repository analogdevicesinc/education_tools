/***************************************************************************//**
 *   @file   buck.js
 *   @brief  Buck Converter Loopback script with Voltmeter
 *   @author Antoniu Miclaus (antoniu.miclaus@analog.com)
********************************************************************************
 * Copyright 2018(c) Analog Devices, Inc.
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *  - Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *  - Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *  - Neither the name of Analog Devices, Inc. nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *  - The use of this software may or may not infringe the patent rights
 *    of one or more patent holders.  This license does not release you
 *    from the requirement that you obtain separate licenses from these
 *    patent holders to use this software.
 *  - Use of the software either in source or binary form, must be run
 *    on or directly connected to an Analog Devices Inc. component.
 *
 * THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES "AS IS" AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT,
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL ANALOG DEVICES BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, INTELLECTUAL PROPERTY RIGHTS, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*******************************************************************************/

//buck converter input amplitude
var input_ampl = 5

//setpoint voltage 			
var setpoint_voltage = 1	

//error range
var accepted_range = 0.3	

//signal initial duty cycle
var duty = 50		

//buck output meanvalue		
var mean_val

//error value				
var error					
	
//Set Signal Generator parameters
function set_signal_generator() {
	
	msleep(100)
	
	//Waveform mode
	siggen.mode[0]=1	
	
	//Square type	
	siggen.waveform_type[0]=1	
	
	//Amplitude (V)	
	siggen.waveform_amplitude[0]=input_ampl	
	
	//Offset (V)
	siggen.waveform_offset[0]=2.5		
	
	//Phase (deg)	
	siggen.waveform_phase[0]=0		
	
	//Frequnecy (Hz)	
	siggen.waveform_frequency[0]=25e3	
	
	//Duty Cycle ()	
	siggen.waveform_duty[0]=duty				
	
}

//main function
function main (){
	
	//set Signal Generator parameters
	set_signal_generator()
	
	msleep(100)
	
	//Run signal generator
	siggen.running=true
	
	msleep(1000)
	
	//Run Voltmeter
	dmm.running=true
	
	msleep(100)
	
	//feeback loop adjusting the oscillator duty cycle
	while(true){
		mean_val = dmm.value_ch1 //read voltmeter channel 1
		// mean_val = osc.channels[0].mean //alternatively read mean value channel 1
		if(mean_val < setpoint_voltage + accepted_range 
			&& mean_val > setpoint_voltage - accepted_range)
			break
		error = mean_val - setpoint_voltage
		duty = duty - 100 * (error/input_ampl)
		siggen.running=false
		siggen.waveform_duty[0]=duty
		siggen.running=true
		msleep(3000)
		
	}
}

main()