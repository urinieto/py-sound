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


def Gammachirp(center_freq, bandwidth=erb, chirp=0., order=4, phase=0.):
    '''A gammachirp is a of gammatone with a frequency asymmetry.

    center_freq: The primary frequency of the gammatone, in Hz.
    bandwidth: The "duration" of the impulse response of the gammatone.
    chirp: The degree of frequency asymmetry in the chirp.
    order: The slope of the impulse response envelope.
    phase: The relative offset of the sinusoid within the envelope.

    The gammatones we generate have amplitude 1. Rescale the output manually to
    use a different amplitude.
    '''
    bandwidth = bandwidth(center_freq) if callable(bandwidth) else bandwidth
    def tone(t):
        '''Get the response of this tone at a specific point in time.'''
        bend = 0.
        if chirp > 0:
            bend = chirp * numpy.log(t)
        osc = numpy.cos(TAU * center_freq * t + phase + bend)
        env = numpy.exp(-TAU * bandwidth * t)
        return t ** (order - 1) * env * osc
    return tone


def Gammatone(center_freq, bandwidth=erb, order=4, phase=0.):
    '''A gammatone is a simple sinusoid with a gamma function envelope.

    center_freq: The primary frequency of the gammatone, in Hz.
    bandwidth: The "duration" of the impulse response of the gammatone.
    order: The slope of the impulse response envelope.
    phase: The relative offset of the sinusoid within the envelope.

    The gammatones we generate have amplitude 1. Rescale the output manually to
    use a different amplitude.
    '''
    return Gammachirp(center_freq, bandwidth, order=order, phase=phase)
