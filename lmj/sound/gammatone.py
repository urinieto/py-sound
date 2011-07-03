# Copyright (c) 2011 Leif Johnson <leif@leifjohnson.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''Classes for gammatones and gammachirps.'''

import numpy

TAU = 2 * numpy.pi

def erb(f):
    '''Return the equivalent rectangular bandwidth (ERB) of frequency f.'''
    return 0.1039 * f + 24.7


class Gammatone(object):
    '''A gammatone is a simple sinusoid with a gamma function envelope.'''

    def __init__(self, center_freq, bandwidth=erb, order=2, phase=0.):
        '''Create a gammatone with a fixed frequency, bandwidth, order, and phase.'''
        self.center_freq = center_freq
        self.bandwidth = bandwidth(center_freq) if callable(bandwidth) else bandwidth
        self.order = order
        self.phase = phase

    def __call__(self, t):
        '''Get the response of this tone at a specific point in time.'''
        osc = numpy.cos(TAU * self.center_freq * t + self.phase)
        env = numpy.exp(-TAU * self.bandwidth * t)
        return t ** (self.order - 1) * env * osc

    def itertone(self, resolution=1., scale=1., offset=0.):
        '''Generate gammatone values.

        resolution: Increment the time value by this constant each sample.
        scale: Scale the amplitude of the output by this value.
        offset: Add this offset to the scaled output.
        '''
        t = 0
        while True:
            t += resolution
            yield scale * self(t) + offset


class Gammachirp(Gammatone):
    '''A gammachirp is a type of gammatone with a frequency asymmetry.'''

    def __init__(self, center_freq, bandwidth=erb, order=2, chirp=0.):
        '''Initialize this chirp with a frequency and a chirp "strength".'''
        super(Gammachirp, self).__init__(center_freq, bandwidth, order)
        self.chirp = chirp

    def __call__(self, t):
        '''Get the response of this chirp at a specific point in time.'''
        self.phase = self.chirp * numpy.log(t)
        return super(Gammachirp, self).__call__(t)
