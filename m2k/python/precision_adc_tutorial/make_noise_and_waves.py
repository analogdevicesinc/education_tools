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
Super simple script to generate some stuff that's interesting to plot

'''

import numpy as np
from matplotlib import pyplot as plt

data = np.ndarray(1024, dtype=float)

for t in range(1024):
    data[t] = 1.0*np.cos(2.0*np.pi*10*(t/1024))

offset = 0.000
#rmsnoise = 0.42e-6 # AD7124 noise, refer to datasheet modes
rmsnoise = 0.1 # Visible relative to cosine w/ amplitude 1.0

noise = np.random.normal(loc=offset, scale=rmsnoise, size=1024)
measured_noise = np.std(noise)
print("Measured Noise: ", measured_noise)

plt.figure(1)

plt.title('A sinewave and some noise')
plt.ylabel('Value')
plt.xlabel("Sample Number")
plt.plot(data)
plt.plot(noise)
plt.grid()
plt.show()

