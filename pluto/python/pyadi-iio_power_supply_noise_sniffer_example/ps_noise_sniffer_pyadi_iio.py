#File: ps_noise_sniffer_pyadi_iio.py
# Description: Power Supply Noise Sniffer example that uses the pyadi-iio API
# Author: Andreea Pop (andreea.pop@analog.com)
#         Antoniu Miclaus (antoniu.miclaus@analog.com)
#         Mark Thoren (mark.thoren@analog.com)
#
# Copyright 2019(c) Analog Devices, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#  - Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  - Neither the name of Analog Devices, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#  - The use of this software may or may not infringe the patent rights
#    of one or more patent holders.  This license does not release you
#    from the requirement that you obtain separate licenses from these
#    patent holders to use this software.
#  - Use of the software either in source or binary form, must be run
#    on or directly connected to an Analog Devices Inc. component.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT,
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL ANALOG DEVICES BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, INTELLECTUAL PROPERTY RIGHTS, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import time

sys.path.append('C:/apop/Git_Repositories/pyadi-iio') #add own path to pyadi-iio
import adi
try:
    import pandas as pd
except:
    print("Please install pandas")
try:
    import numpy as np
except:
    print("Please install numpy")
try:
    import csv
except:
    print("Please install csv")    
try:
    import tkinter as tk
    from tkinter import filedialog
    import tkinter.scrolledtext as tkscrolled
except:
    print("Please install tkinter")
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
except:
    print("Please install matplotlib")

#Error
ERROR = -1

#Success
SUCCESS = 0

FREQ_BAND = 40000000 #Frequency band  in Hz
TXDAC_FREQ1=500000 #Frequency of test tone 1 in Hz
TXDAC_FREQ2=10000000 #Frequency of test tone 2 in Hz

BUFLEN=2**13 #buffer length

#connect device
try:
    sdr = adi.Pluto('ip:192.168.2.1')
except:
    sdr=ERROR
    
#check device connection
def check_connection(sdr):
    if(sdr== ERROR):
        txt1.config(fg = "red")
        txt1.insert('1.0', "No Device Detected.\n\n")
        return ERROR
    else:
        txt1.config(fg = 'black')
        txt1.insert('1.0', "Device Connected.\n\n")
        return SUCCESS
    
#device setup 
def device_setup(sdr):
    global RX0FS
    sdr.rx_buffer_size=2**13
    sdr.rx_rf_bandwidth =56000000
    sdr.tx_rf_bandwidth=56000000
    sdr.rx_lo = 70000000
    sdr.tx_lo = 70000000
    sdr.tx_cyclic_buffer = False
    sdr.tx_hardwaregain = -30
    sdr.gain_control_mode = 'slow_attack'
    sdr.sample_rate=61440000
    RX0FS=sdr.sample_rate
    sdr.dds_scales=("0.3","0.25","0","0") #scales for DDS Signal generators,  two complex tones can be generated per complex channel
    sdr.dds_enabled=(1, 1, 1, 1) #enable DDS signal generators
    time.sleep(0.1)#delay after setting device parameters
    
#clear plot contents    
def clr_content():
    txt1.delete('1.0', tk.END)
    a.cla()
    canvas.draw()
    
#compute the center frequency for each band
def comp_freq():
    global start_freq
    global stop_freq
    center_freq = np.array([]) #array that holds the center frequencies
    
    #Convert input start/stop frequency values to integers
    try:
        int(start_f.get())
        int(stop_f.get())
    except:
        center_freq = np.append(center_freq, ERROR)
        return center_freq
    
    #Get start/stop frequency values
    start_freq = int(start_f.get())*1e6  #MHz
    stop_freq = int(stop_f.get())*1e6 #MHz
    #Check if start frequency is larger than input frequency
    if (start_freq > stop_freq or start_freq < 70000000 or stop_freq > 6000000000):
        center_freq = np.append(center_freq, ERROR)
    else:
        nr_center_freq = int((stop_freq - start_freq)/FREQ_BAND ) + 1 
        center_freq = np.append(center_freq, start_freq)
    
    #Compute center frequencies for each band
        for i in range(1, nr_center_freq):
            center_freq = np.append(center_freq, center_freq[i-1] + FREQ_BAND )
    return center_freq, start_freq, stop_freq

#Set hardware gain to the smallest value
def set_hw_gain(center_freq):
      
    hw_gain_arr = np.array([])
    for i in range(0, len(center_freq)):
        RXLO = center_freq[i]
        TXLO = RXLO
        sdr.rx_lo= int(RXLO)
        sdr.tx_lo = int(TXLO)
        time.sleep(0.2)
        hw_gain_arr=np.append(hw_gain_arr, sdr.rx_hardwaregain) 
    min_hw_gain = min(hw_gain_arr)

    #set manual hw gain
    min_hw_gain = min(hw_gain_arr)
    sdr.gain_control_mode = 'manual'
    min_hw_gain=float(min_hw_gain.replace(' dB', ""))    
    
    return min_hw_gain
    
def load_gain_calib():
    global gain_freq
    gain_freq = []
    
    with open('gain_calib.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            gain_freq.append(tuple((row['Frequency(MHz):'], row['Magnitude(dB):'])))

def load_filter(sdr):  
    #enable/disable FIR filter for TX and RX 
    if(filter_en.get() == True):
        txt1.insert(tk.END, "FIR Filter enabled.\n\n")
        sdr.filter="LTE20_MHz.ftr" 
    else:
        txt1.insert(tk.END, "FIR Filter disabled.\n\n")
        sdr.filter
        
    root.update_idletasks()
    root.update()
    
#check if the frequency values are in range    
def check_freq(center_freq):
    if(center_freq==ERROR):
        txt1.config(fg = 'red')
        txt1.delete('1.0', tk.END)
        txt1.insert('1.0', "Please insert valid start/stop frequencies.")
        return ERROR
    else:
        txt1.config(fg = "black")
        txt1.insert(tk.END, "Start frequency set to: " + str(start_freq/1e6) + " MHz\n\n")
        txt1.insert(tk.END, "Stop frequency set to: " + str(stop_freq/1e6) + " MHz\n\n")
        return SUCCESS    
    
  
def check_avg_nr():
    try:
        int(avg_nr.get())
        return SUCCESS
    except:
        txt1.config(fg = "red")
        txt1.insert(tk.END, "Please insert valid average number.")
        btn_text.set("Start")
        btn_start.config(bg = "lime green")
        return ERROR
    
#Get and plot data
def get_plot_data(sdr, center_freq, min_hw_gain):
    
    global fft_rxvals_iq_db
    global fftfreq_rxvals_iq
    
    ylim = [0,0]
    window = np.blackman(BUFLEN) 
    avg_step = 0
    fft_rxvals_iq = np.array([])
    fftfreq_rxvals_iq = np.array([])
    avgband = np.array([])
    time.sleep(0.1) # delay before data aqcuisition
    adi.rx_tx.rx.rx_buffer_size=BUFLEN #set the size  of receive buffer in samples
   
    while(True):
        #acquire data 
        for i in range(0, len(center_freq)):
            RXLO = center_freq[i]
            TXLO = RXLO
            sdr.rx_lo= int(RXLO)
            sdr.tx_lo = int(TXLO)
            time.sleep(0.1)
            root.update_idletasks()
            root.update()
            
            #Get gain calibration for specific band
            if(gain_calib_set.get() == True):
                for index_gain in range(0,len(gain_freq)):
                    gain_frequency = float(gain_freq[index_gain][0]) * 1e6
                    if((center_freq[i] - int(FREQ_BAND)/2) <= gain_frequency <= (center_freq[i] + int(FREQ_BAND)/2)):
                        gain_calib = float(gain_freq[index_gain][1])
                        break
            else:
                gain_calib = 0
            
            #generate test tone(s)
            sdr.dds_frequencies=(str(TXDAC_FREQ1),str(TXDAC_FREQ2 ),str(TXDAC_FREQ1),str(TXDAC_FREQ2))
          
            #delay before data acquisition
            time.sleep(0.1)
            
            if(progress_en.get() == False):
                for k in range(0, int(avg_nr.get())+1):
                    for j in range(5):
                        x=sdr.rx()
                        
                    rxvals_i =x.real * window
                    rxvals_q =x.imag * window
                    
                    #construct complex IQ data
                    rxvals_iq = rxvals_i + (1j * rxvals_q)
                    # apply FFT and get amplitude of the IQ data  
                    newband = np.abs(np.fft.fft(rxvals_iq)) 
                    #apply averaging
                    if(k != 0):
                        avgband = (newband) * 1/k + avgband * (k-1) / k;
                    else:
                        avgband = newband
            else:     
                for j in range(5):
                    x = sdr.rx()
                    
                rxvals_i =x.real * window
                rxvals_q =x.imag * window
                
                #construct complex IQ data
                rxvals_iq = rxvals_i + (1j * rxvals_q)
                
                # apply FFT and get amplitude of the IQ data  
                avgband = np.abs(np.fft.fft(rxvals_iq))
                
            txt1.insert(tk.END, "Center Frequency set to: " + str(int(RXLO/1e6)) + ' MHz\n')
            txt1.insert(tk.END, "Min / Max i values: " + str(int(np.min(rxvals_i))) + ", " + str(int(np.max(rxvals_i)))+ "\n")
            txt1.see("end")
                
            #compute cutoff thresholds        
            low_th = int(((int(RX0FS) - int(FREQ_BAND))/(int(RX0FS) * 2)) * int(BUFLEN))
            high_th = int(int(BUFLEN) - (((int(RX0FS) - int(FREQ_BAND))/(int(RX0FS) * 2)) * int(BUFLEN)))
            
            #compute frequency bins
            freq_bins = (np.fft.fftfreq(int(BUFLEN), 1/int(RX0FS)) + (center_freq[0] + int(FREQ_BAND) * i)) /1e6
            
            # Create tuple such that frequencies and corresponding amplitudes can be manipulated together
            tuple1 = zip(freq_bins, avgband)
            
            # Rearrange such that the center frequency is in the middle.
            tuple1 = sorted(tuple1, key=lambda x: x[0])
            
            # Extract the passband of the FIR response
            tuple1 = tuple1[low_th : high_th]
            
            iq = np.array([nr[1] for nr in tuple1]) / (10 ** (gain_calib/10))
            
            if(progress_en.get() == False):
                if(avg_step == 0):
                    # Append amplitudes to collection of bands
                    fft_rxvals_iq = np.append(fft_rxvals_iq, iq)
                    # Append frequency bins to the frequency collection
                    fftfreq_rxvals_iq = np.append(fftfreq_rxvals_iq, [nr[0] for nr in tuple1])
                else:
                    #replace older amplitudes per band with newer amplitudes 
                    fft_rxvals_iq[i * (high_th - low_th) : (i + 1) * (high_th - low_th)] = iq
            else:
                if(avg_step == 0):
                    # Append amplitudes to collection of bands
                    fft_rxvals_iq = np.append(fft_rxvals_iq, iq)
                    fftfreq_rxvals_iq = np.append(fftfreq_rxvals_iq, [nr[0] for nr in tuple1])
                else: 
                    #replace older amplitudes per band with newer amplitudes 
                    iq = iq * 1/avg_step + fft_rxvals_iq[i * (high_th - low_th) : (i + 1) * (high_th - low_th)] * (avg_step - 1) / avg_step;
                    fft_rxvals_iq[i * (high_th - low_th) : (i + 1) * (high_th - low_th)] = iq
            
            # Compute in dB, subtract hardware gain to normalize to absolute analog signal level at input
            fft_rxvals_iq_db = 20* np.log10(fft_rxvals_iq *2 / (2**11 * BUFLEN)) - min_hw_gain
            
            #Perform gain calibration per band
            fft_rxvals_iq_db[i * (high_th - low_th) : (i + 1) * (high_th - low_th)] = fft_rxvals_iq_db[i * (high_th - low_th) : (i + 1) * (high_th - low_th)] - gain_calib
            
            # Plot data
            a.clear()
            a.grid(True)
            a.set_title('Frequency Spectrum')
            a.set_xlabel('Fequency (MHz)')
            a.set_ylabel('Magnitude')

            a.plot(fftfreq_rxvals_iq, fft_rxvals_iq_db)
            if(fixed_axis.get() == True and avg_step != 0):
                a.set_ylim(ylim)
            if(fixed_axis.get() == False or avg_step == 0):
                ylim = a.get_ylim()
            canvas.draw()
            root.update_idletasks()
            root.update()  
                   
            if(btn_text.get() == "Start" and sweep_en.get() == False):
                break
            
        if(btn_text.get() == "Start" or sweep_en.get() == True):
            break       
        avg_step += 1
               
#Sweep button     
def sweep():
     
    sweep_en.set(True)
    
    btn_text.set("Start")
    btn_start.config(bg = "lime green")
    
    btn_export.config(state = tk.DISABLED)
        
    #Clear GUI Content
    clr_content()
  
    #Check connection
    if(check_connection(sdr) == ERROR):
       return
    
    #compute center frequencies
    center_freq, start_freq, stop_freq=comp_freq()
    
    #Check for valid input frequencies
    if(check_freq(center_freq[0]) == ERROR):
       return
    
    #Check for valid average number    
    if(check_avg_nr() == ERROR):
        return
    
    #load FIR filter
    load_filter(sdr)
    time.sleep(0.1)
    
    #setup device
    device_setup(sdr)
    time.sleep(0.1)
    
    load_gain_calib()
    
    #first sweep for getting hardware gain   
    min_hw_gain=set_hw_gain(center_freq)
    txt1.insert(tk.END, "Minimun hardware gain: " + str(min_hw_gain) + ' dB\n')
    get_plot_data(sdr, center_freq, min_hw_gain)
    
    btn_export.config(state = tk.NORMAL)
    
    sweep_en.set(False) 

#Start Button
def start():
    
    if(btn_text.get() == "Stop"):
        btn_text.set("Start")
        btn_start.config(bg = "lime green")
        return
    else:
        btn_text.set("Stop")
        btn_start.config(bg = "red")
        btn_export.config(state = tk.DISABLED)
        
    #Clear GUI Content
    clr_content()
  
    #Check connection
    if(check_connection(sdr) == ERROR):
       btn_text.set("Start")
       btn_start.config(bg = "lime green")
       return

    #compute center frequencies
    center_freq, start_freq, stop_freq=comp_freq()
    
    #Check for valid input frequencies
    if(check_freq(center_freq[0]) == ERROR):
       return
    
    #Check for valid average number    
    if(check_avg_nr() == ERROR):
        return
    
    #load FIR filter
    load_filter(sdr)
    time.sleep(0.1)
    
    #setup device
    device_setup(sdr)
    time.sleep(0.1)
    
    load_gain_calib()
    
    #first sweep for getting hardware gain   
    min_hw_gain=set_hw_gain(center_freq)
    txt1.insert(tk.END, "Minimun hardware gain: " + str(min_hw_gain) + ' dB\n')
    while(btn_text.get() == "Stop"):
        get_plot_data(sdr, center_freq, min_hw_gain)
    
    btn_export.config(state = tk.NORMAL)
    
    btn_text.set("Start")
    btn_start.config(bg = "lime green")
    
#Save data to CSV file
def file_save():
    fdialog = filedialog.asksaveasfile(mode = 'w', initialdir = "/",title = "Select file", defaultextension=".csv", filetypes = (("csv","*.csv"),("all files","*.*")))
    if fdialog is None:
        return
    data = {'Frequency(MHz):': fftfreq_rxvals_iq, 'Magnitude(dB):': fft_rxvals_iq_db }
    df = pd.DataFrame(data)
    df.to_csv(fdialog.name, index = False)        

#Create GUI
def gui():
    
    global root, txt1, start_f, stop_f, filter_en, btn_text, btn_start
    global btn_export, a, canvas, sweep_en, avg_nr, progress_en, fixed_axis
    global tx_on, gain_calib_set
    
    root = tk.Tk()
    root.iconbitmap("favicon.ico")
    root.title("Power Supply Noise Sniffer pyadi-iio (Analog Devices, Inc.)")

    start_f = tk.StringVar()
    stop_f = tk.StringVar()
    avg_nr = tk.StringVar()
    filter_en = tk.BooleanVar()
    sweep_en = tk.BooleanVar()
    progress_en = tk.BooleanVar()
    fixed_axis = tk.BooleanVar()
    btn_text = tk.StringVar()
    tx_on = tk.BooleanVar()
    gain_calib_set = tk.BooleanVar()
    
    avg_nr.set("1")
    sweep_en.set(False)
    filter_en.set(True)
    progress_en.set(False)
    tx_on.set(True)
    gain_calib_set.set(False)
    fixed_axis.set(False)
    btn_text.set("Start")

    fr1 = tk.Frame(root)
    fr1.pack(side = tk.LEFT, anchor = 'n', padx = 10, pady = 10)

    fr2 = tk.Frame(fr1)
    fr2.grid(row = 0, column = 0, pady = 10)

    label1 = tk.Label(fr2, text = "Start frequency (MHz): ")
    label1.grid(row = 0, column = 0)

    entry1 = tk.Entry(fr2, textvariable=start_f)
    entry1.grid(row = 0, column = 1)

    label2 = tk.Label(fr2, text = "Stop frequency (MHz): ")
    label2.grid(row = 1, column = 0, pady = (0,5))

    entry2 = tk.Entry(fr2, textvariable=stop_f)
    entry2.grid(row = 1, column = 1)
    
    label3 = tk.Label(fr2, text = "FIR Filter: ")
    label3.grid(row = 2, column = 0)

    check1 = tk.Checkbutton(fr2, variable=filter_en)
    check1.grid(row = 2, column = 1)
    
    label4 = tk.Label(fr2, text = "Average: ")
    label4.grid(row = 3, column = 0)

    entry3 = tk.Entry(fr2, textvariable=avg_nr)
    entry3.grid(row = 3, column = 1)
    
    label5 = tk.Label(fr2, text = "Progress Avg: ")
    label5.grid(row = 4, column = 0)

    check2 = tk.Checkbutton(fr2, variable=progress_en)
    check2.grid(row = 4, column = 1)
    
    label6 = tk.Label(fr2, text = "Fixed Axis: ")
    label6.grid(row = 5, column = 0)

    check3 = tk.Checkbutton(fr2, variable=fixed_axis)
    check3.grid(row = 5, column = 1)
    
    label7 = tk.Label(fr2, text = "TX On: ")
    label7.grid(row = 6, column = 0)

    check4 = tk.Checkbutton(fr2, variable=tx_on)
    check4.grid(row = 6, column = 1)
    
    label8 = tk.Label(fr2, text = "Gain Calibration: ")
    label8.grid(row = 7, column = 0)

    check5 = tk.Checkbutton(fr2, variable=gain_calib_set)
    check5.grid(row = 7, column = 1)

    btn_start = tk.Button(fr2, textvariable=btn_text, command=start)
    btn_start.config(width = 13, height = 1, bg = "lime green")
    btn_start.grid(row = 8, column = 1, pady = (10,0))
    
    btn_sweep = tk.Button(fr2, text="Single Sweep", command=sweep)
    btn_sweep.config(width = 13, height = 1,  bg = "orange")
    btn_sweep.grid(row = 8, column = 0, pady = (10,0))
 
    btn_export = tk.Button(fr2, text="Export Data", command=file_save)
    btn_export.config(width = 13, height = 1, state = tk.DISABLED)
    btn_export.grid(row = 9, column = 0, pady = (10,0))
    
    fr3 = tk.Frame(fr1)
    fr3.grid(row = 1, column = 0)
        
    label5 = tk.Label(fr3, text = "Message Log: ")
    label5.grid(row = 0, column = 0)
    
    txt1 = tkscrolled.ScrolledText(fr3, width = 40, height = 33.2)
    txt1.grid(row = 1, column = 0)
    
    fig = plt.figure()
    DPI = fig.get_dpi()
    fig.set_size_inches(1024.0/float(DPI), 640.0/float(DPI))   
    a = fig.add_subplot(111)
    a.grid(True)
    a.set_title('Frequency Spectrum')
    a.set_xlabel('Fequency (MHz)')
    a.set_ylabel('Magnitude')
    
    plt.tight_layout()
    plotFrame = tk.Frame(master=root)
    plotFrame.pack(side = tk.LEFT, pady = 10, padx = 10, anchor = 'n')

    toolbarFrame = tk.Frame(master=plotFrame)
    toolbarFrame.pack(anchor = 'w', pady = (0,10))
    
    canvas = FigureCanvasTkAgg(fig, master=plotFrame)
    canvas.get_tk_widget().pack(fill = tk.BOTH)
    canvas.draw()
    root.update_idletasks()

    toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
    toolbar.update()
    
    root.mainloop()

#main function
def main():
    gui()

main()
