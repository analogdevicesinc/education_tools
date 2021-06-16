#
# Copyright (c) 2019 Analog Devices Inc.
#
# (see http://www.github.com/analogdevicesinc/libm2k).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

# This example assumes the following connections:
# W1 -> 100-ohm resistor in series with speaker
# W2 -> open
# 2+ -> Microphone
# GND -> 1-
# GND -> 2-
#
# The application will record a few seconds of audio on scope channel 2, reverse the order of the samples,
# Apply some filtering tricks to remove large DC offsets, then play back. Orignially, Playback was at 75% of
# record speed just due to available sample rates, so a future upgrade would be to do a bit of multirate processing:
# 10ksps upsampled by 3, interpolated, then downsampled by 4 should do the trick :)

# But it turns out there's an easier way - sample MUCH fastser than needed (1Msps), then downsample by 133 (7518.797 sps) giving a 0.2% mismatch
# between effective sample rates. (Audio will be a tiny bit lower in pitch)

import matplotlib
import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.figure as  fg
import libm2k
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import style
import threading
import time

LARGE_FONT = ("Verdana",12)
SMALL_FONT = ("Vedana",10)

style.use("ggplot")

#create figure
fig = fg.Figure(figsize =(10,10))
recording_plot = fig.add_subplot(211)
recording_plot.set_title("Recorded Audio Waveform")
recording_plot.set_xlabel("Samples")
recording_plot.set_ylabel("Audio")
flipped_plot = fig.add_subplot(212)
flipped_plot.set_title("Flipped Audio Waveform")
flipped_plot.set_xlabel("Samples")
flipped_plot.set_ylabel("Flipped Audio")

ctx=libm2k.m2kOpen("ip:192.168.2.1")

if ctx is None:
    print("Failed connection:No device available")
    exit(1)
# Set up
ctx.calibrateADC()
ctx.calibrateDAC()
ain = ctx.getAnalogIn()
aout = ctx.getAnalogOut()
trig = ain.getTrigger()
ps = ctx.getPowerSupply()

def close_app():
    libm2k.contextClose(ctx)
    print("context closed")
    window.destroy()

window = tk.Tk()
window.title("ADALM-2000 Audio Flipper")

window.protocol("WM_DELETE_WINDOW",close_app)

class App():
    def __init__(self,window):

        self.create_gui()
        self.init_m2k()

    def create_gui(self):
        self.add_canvas()
        self.add_widgets()
    def add_canvas(self):
        #create empty canvas
        x_rec=[]
        y_rec=[]
        x_flp=[]
        y_flp=[]
        self.line_rec, = recording_plot.plot(x_rec,y_rec)
        self.line_flp, = flipped_plot.plot(x_flp,y_flp)
        self.canvas = FigureCanvasTkAgg(fig, master = window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side = tk.TOP,fill= tk.BOTH, expand = 1)
        #frame & pack object
        frame = tk.Frame()
        frame.pack()
    def add_widgets(self):
        self.rec_btn = tk.Button(window, text = "Record",foreground = 'red',command = self.record, font = SMALL_FONT)
        self.rec_btn.pack(side=tk.LEFT)
        self.playflipped_btn = tk.Button(window, text = "Play Flipped", foreground = 'green',command =self.play_flipped, font = SMALL_FONT)
        self.playflipped_btn.pack(side=tk.LEFT)
    def init_m2k(self):
        ps.enableChannel(0,True) #Consider using for microphone power,
        ps.pushChannel(0,4.0) # unfortunately DC blocking cap takes forever to charge
        print("waiting 1 second for mic to settle...")
        time.sleep(1.0)

        ain.enableChannel(0,True)
        ain.enableChannel(1,True)
        ain.setSampleRate(1000000)    # 1Msps is REALLY fast for audio, but we're going to filter and downsample for two reasons:
        ain.setOversamplingRatio(133) # First, to reduce noise. Second, to reconcile the difference in available sample rates between
        ain.setRange(1,-1,1)          # input and outputs.

        print("ain sample rate: " + str(ain.getSampleRate()))
        print("ain range: " + str(ain.getRangeLimits(1)))
        print("ain OSR: " + str(ain.getOversamplingRatio()))

        aout.setSampleRate(0, 7500) # This gives us 3.75kHz worth of audio bandwidth...
        aout.setSampleRate(1, 7500) # Note that we don't have a perfect match between input and
        aout.enableChannel(0, True) # output sample rates - see ain sample rate comments.
        aout.enableChannel(1, True)
        print("aout sample rate: " + str(aout.getSampleRate()))

    def record(self):
        print("Recording...")
        time.sleep(0.1)

        self.startime = time.time()

        self.bufflen = 2**16

        data = ain.getSamples(self.bufflen)

        self.captime = time.time() - self.startime
        print("recorded time: " + str(self.captime))

        self.audio_clean = data[1]
        self.audio = []

        self.plot()

    def play_flipped(self):
        print("playing back...wards")
        self.flip()
        self.audio = self.audio * 100.0 # add some gain
        buffer = [self.audio, self.audio]
        aout.setCyclic(False)
        aout.push(buffer)

        self.plot()

    def plot(self):
        recording_plot.plot(range(len(self.audio_clean)),self.audio_clean)
        flipped_plot.plot(range(len(self.audio)),self.audio)
        self.canvas.draw()




    def flip(self):
        print("flipping...")
        dc = np.convolve(self.audio_clean, (np.ones(64)/64.0), mode='same') # Calculate running DC average with a
        #audio = audio - np.average(audio)                                  # really simple boxcar filter
        self.audio = self.audio_clean - dc
        self.audio [0:100] = [0]*100 #get rid of edge effect

        self.audio = np.flip(self.audio) # Here's where the flip happens!!



def main():
    app = App(window)
    window.mainloop()

if __name__=='__main__':
    main()







