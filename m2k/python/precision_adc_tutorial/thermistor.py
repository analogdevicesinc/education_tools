# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------
# Copyright (c) 2015-2019 Analog Devices, Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Modified versions of the software must be conspicuously marked as such.
# - This software is licensed solely and exclusively for use with
#   processors/products manufactured by or for Analog Devices, Inc.
# - This software may not be combined or merged with other code in any manner
#   that would cause the software to become subject to terms and conditions
#    which differ from those listed here.
# - Neither the name of Analog Devices, Inc. nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
# - The use of this software may or may not infringe the patent rights of one
#   or more patent holders. This license does not release you from the
#   requirement that you obtain separate licenses from these patent holders
#   to use this software.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES, INC. AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# NON-INFRINGEMENT, TITLE, MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ANALOG DEVICES, INC. OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# DAMAGES ARISING OUT OF CLAIMS OF INTELLECTUAL PROPERTY RIGHTS INFRINGEMENT;
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# 2019-01-10-7CBSD SLA
# -----------------------------------------------------------------------


'''
An example of a nonlinear sensor for which one might want to model the impact
of the ADC's noise on the indicated temperature.

'''

import numpy as np
from matplotlib import pyplot as plt


# Steinhart equation solved for temperature.
def temperature(r, Ro=10000.0, To=25.0, beta=3950.0):
    temperature = np.log(r / Ro) / beta # invert later, don't get confused
    temperature += 1.0 / (To + 273.15)
    temperature = (1.0 / temperature) - 273.15
    return temperature

# Calculate resistance of a grounded thermistor with an excitation resistor
# value of rh
def resistance(v, vref=2.50, rh=10000):
    frac = v/vref
    return -(rh*frac/(frac-1))

temps = []
res_vals = []

# Un-comment this line to plot the overall transfer function
voltages = np.linspace(0.1, 2.0, 100, endpoint=True)

# Un-comment this line to plot the resulting noise at various voltages
#voltages = np.random.normal(loc=2.0, scale=0.42e-6, size=100)

# Calculate resistances from voltage readings
for voltage in voltages:
    res_vals.append(resistance(voltage))

# Calculate temperatures
for res in res_vals:
    temps.append(temperature(res))

plt.figure(1)
plt.title('resistance vs. voltage')
plt.ylabel('resistance')
plt.plot(voltages, res_vals)

plt.figure(2)
plt.title('temperature vs. resistance')
plt.ylabel('temperature')
plt.xlabel("resistance")
plt.plot(res_vals, temps)
plt.grid()
plt.show()

