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

'''Code for synthesizing "voice" sounds under the source-filter model.'''

import numpy
import scipy.signal
import numpy.random as rng

from matplotlib import pylab

import sound


class Voice(object):
    '''A voice is a crude source-filter model for speech synthesis.'''

    def __init__(self, fundamental=200., window_msec=30., sample_rate=16000.):
        self.fundamental = fundamental
        self.window_msec = window_msec
        self.sample_rate = sample_rate
        self.samples = 1 + sample_rate * window_msec / 2000.
        self.nyquist = self.sample_rate / 2.

    def source_spectrum(self, bandwidth=10):
        '''Generate a power spectrum for the vocal tract source.'''
        slope = max(0.5, min(1.0, 0.07 * numpy.log(bandwidth) + 0.5))
        f0 = self.fundamental
        f = numpy.linspace(0, self.nyquist, self.samples)
        v = numpy.zeros(self.samples)
        N = 1 + self.nyquist / self.fundamental
        amplitude = 1.
        for i in range(1, int(1 + N)):
            v += amplitude * numpy.exp(-((f - i * f0) / bandwidth) ** 2)
            amplitude *= slope
        return v

    def filter_spectrum(self, formants):
        '''Generate a power spectrum for the vocal tract filter.

        formants: A sequence of (amplitude, center frequency, bandwidth) tuples.
        '''
        f = numpy.linspace(0, self.nyquist, self.samples)
        v = numpy.zeros(self.samples)
        for amplitude, center, bandwidth in formants:
            v += amplitude * numpy.exp(-((f - center) / bandwidth) ** 2)
        return v

    def simulate(self, formants):
        '''Simulate frames of audio, given a sequence of formants.'''
        formants = iter(formants)
        w = scipy.signal.get_window('hanning', 2 * (self.samples - 1))

        def frame(b, f, sw=2., fw=1.):
            ss = sw * self.log_source_spectrum(b)
            fs = fw * self.log_filter_spectrum(f)
            #pylab.clf()
            #x = numpy.linspace(0, self.nyquist, self.samples)
            #pylab.plot(x, ss, x, fs)
            #pylab.plot(x, ss * fs)
            #pylab.show()
            return w * numpy.fft.irfft(ss * fs)

        prev, curr = None, frame(*formants.next())
        for f in formants:
            prev, curr = curr, frame(*f)
            for i in range(len(prev) // 2, len(prev)):
                yield prev[i] + curr[i - len(curr) // 2]

    def generate(self):
        '''Generate some random formants.'''
        bw = 10.
        f1 = rng.uniform(300, 700)
        f2 = rng.uniform(800, 2000)
        f3 = rng.uniform(2000, 2500)
        f4 = rng.uniform(2500, 3500)

        def near(x, t, s):
            return 1. / (1. + numpy.exp((t - x) / s))

        while True:
            if rng.random() < 0.1:
                bw = rng.gamma(5, 5)
                r = near(f1, 500, 100)
                f1 += rng.uniform(-30 * r, 30 * (1 - r))
                r = near(f2, 1500, 300)
                f2 += rng.uniform(-50 * r, 50 * (1 - r))
                r = near(f3, 2200, 500)
                f3 += rng.uniform(-70 * r, 70 * (1 - r))
                r = near(f4, 3000, 700)
                f4 += rng.uniform(-90 * r, 90 * (1 - r))
            yield (bw, ((1., f1, 200),
                        (0.9, f2, 100),
                        (0.8, f3, 100),
                        (0.7, f4, 100)))


if __name__ == '__main__':
    r = 16000
    s = 3 * r

    v = Voice(200)
    f = v.simulate(v.generate())
    sound.Clip(samples=[f.next() for _ in range(s)], sample_rate=r).play()
