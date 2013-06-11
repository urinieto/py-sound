# Copyright (c) 2011-2012 Leif Johnson <leif@leifjohnson.net>
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

'''Utility classes and methods for processing sound data.'''

import logging
import numpy
import os
import scipy.signal
import sys

from scikits.audiolab import Format, Sndfile, play
from scikits.samplerate import resample


class Clip(object):
    '''A clip is a single piece of sound that's loaded from a file on disk.

    Clips are all forced to be mono (1 channel) by averaging each frame across
    all channels that are encountered in the file.
    '''

    def __init__(self, filename='', samples=None, sample_rate=None):
        '''Initialize this signal by loading sound data from a file.

        filename: The name of the file to load sound data from, if any.
        samples: If given, a numpy array containing sound data.
        sample_rate: If samples is not None, this must also be given.
        '''
        self.samples = numpy.zeros(1.)
        self.sample_rate = sample_rate

        self.filename = filename
        if filename:
            self.load(filename)
        elif samples is not None:
            assert sample_rate > 0
            self.samples = numpy.asarray(samples)
            self.sample_rate = sample_rate

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, slice):
        return self.samples[slice]

    @property
    def shape(self):
        return self.samples.shape

    @property
    def dtype(self):
        return self.samples.dtype

    @property
    def nyquist(self):
        return self.sample_rate / 2.

    def load(self, filename):
        '''Load sound data from a file on disk.

        filename: The name of the file to load sound data from.
        '''
        snd = Sndfile(filename)
        self.samples = snd.read_frames(snd.nframes)
        while len(self.shape) > 1:
            self.samples = self.samples.mean(axis=-1)

        self.filename = filename
        r = self.sample_rate = snd.samplerate
        n = len(self.samples)
        logging.info('%s: read %d frames at %d Hz (%.2f sec)',
                     os.path.basename(self.filename), n, r, float(n) / r)

    def normalize(self):
        '''Normalize the samples in this clip.

        Normalizing here means subtracting out the mean and dividing by the
        standard deviation of all samples.
        '''
        self.samples -= self.samples.mean()
        self.samples /= self.samples.std()
        logging.info('%s: normalized %d samples',
                     os.path.basename(self.filename), len(self.samples))

    def lowpass_filter(self, freq, order=31):
        '''Lowpass filter the clip to eliminate high frequencies.

        freq: Construct a lowpass filter with this cutoff frequency.
        order: Build a filter of this order.
        '''
        b, a = scipy.signal.butter(order, freq / self.nyquist)
        z = scipy.signal.filtfilt(b, a, self.samples)
        self.samples = numpy.asarray(z, self.dtype)
        logging.info('%s: lowpass filter at %.2fHz',
                     os.path.basename(self.filename), freq)

    def set_sample_rate(self, sample_rate, method='sinc_best'):
        '''Set the sample rate for this clip.

        sample_rate: The desired sample rate for the clip.
        method: One of 'linear', 'sinc_fastest', 'sinc_medium', 'sinc_best'.
        '''
        resample_ratio = float(sample_rate) / self.sample_rate
        if resample_ratio != 1.:
            self.samples = numpy.asarray(
                resample(self.samples, resample_ratio, method),
                self.dtype)
            r = self.sample_rate = sample_rate
            n = len(self.samples)
            logging.info('%s: resampled to %d frames at %d Hz (%.2f sec)',
                         os.path.basename(self.filename), n, r, float(n) / r)

    def get_window(self, width, offset=0, window_type='hanning'):
        '''Get a slice of samples from this clip as a numpy array.

        width: The number of samples to include in the window.
        offset: Offset the window this many samples from the start of the sound.
        window_type: A string or tuple describing the type of window to use. See
          the documentation for scipy.signal.get_window for details.
        '''
        window = scipy.signal.get_window(window_type, width)
        if offset + n < len(self.samples):
            return window * self.samples[offset:offset + n]
        return None

    def iter_windows(self, width, offset=0, interval=0.5, window_type='hanning'):
        '''Iterate over consecutive windows of samples in this clip.

        Generates a sequence of (sample offset, samples) tuples.

        width: The number of samples to return in each window.
        offset: Offset the first window from the start of the sound.
        interval: The proportion of the window width to skip between the start
          of each successive window. Defaults to half the window width.
        window_type: A string or tuple describing the type of window to use. See
          the documentation for scipy.signal.get_window for details.
        '''
        window = scipy.signal.get_window(window_type, width)
        interval = width * interval
        while offset + width < len(self.samples):
            o = int(offset)
            yield o, window * self.samples[o:o + width]
            offset += interval

    def iter_fft_coeffs(self, width, offset=0, interval=0.5, window_type='hanning'):
        '''Iterate over consecutive windows of FFT coefficients in this clip.

        Generates a sequence of (sample offset, coefficients) tuples.

        width: The number of samples to return in each window.
        offset: Offset the first window from the start of the sound.
        interval: The proportion of the window width to skip between the start
          of each successive window. Defaults to half the window width.
        window_type: A string or tuple describing the type of window to use. See
          the documentation for scipy.signal.get_window for details.
        '''
        for o, samples in self.iter_windows(width, offset, interval, window_type):
            yield o, numpy.fft.rfft(samples)

    def play(self):
        '''Play this clip.'''
        if 'darwin' == sys.platform.lower() and self.sample_rate != 48000:
            c = Clip(samples=self.samples, sample_rate=self.sample_rate)
            c.set_sample_rate(48000)
            c.play()
        else:
            n = abs(self.samples).max()
            play(self.samples / (n if n > 1 else 1), self.sample_rate)

    def specgram(self, *args, **kwargs):
        '''Generate a spectrogram of this clip using matplotlib.'''
        from matplotlib import pyplot
        pyplot.specgram(self.samples, *args, **kwargs)

    def save(self, filename):
        '''Write the data for this clip to a WAV file on disk.'''
        snd = Sndfile(filename, 'w', Format('wav'), 1, self.sample_rate)
        snd.write_frames(self.samples)
        snd.close()

    def rms_error(self, other):
        '''Calculate the RMS error from another clip of the same length.

        other: A second clip to compare with this one.
        '''
        if (not isinstance(other, Clip) or
            len(other) != len(self) or
            other.sample_rate != self.sample_rate):
            raise NotImplemented
        return (numpy.linalg.norm(self.samples - other.samples) /
                numpy.sqrt(len(self)))

    def reconstruct_with_fft(self, width, interval=0.5, min_coeff=0.1, phase_distort=0.):
        '''Reconstruct the sound in this clip using threshold-filtered FFT data.

        Returns a new clip with the reconstructed sound.

        width: Process sound in windows of this length.
        interval: The proportion of the window width to skip between the
          start of each successive window. Defaults to half the window width.
        min_coeff: Set all FFT coefficients less than this magnitude to 0.
        phase_distort: Distort the phase of each coefficient uniformly in the
          interval [-phase_distort, phase_distort].
        '''
        pd = phase_distort
        samples = numpy.zeros(self.shape, self.dtype)
        for o, coeffs in self.iter_fft_coeffs(width, interval):
            for i, c in enumerate(coeffs):
                if abs(c) < min_coeff:
                    coeffs[i] = 0
                else:
                    t = numpy.angle(c) + numpy.random.uniform(-pd, pd)
                    coeffs[i] = abs(c) * (numpy.cos(t) + numpy.sin(t) * 1j)
            samples[o:o+w] += numpy.fft.irfft(coeffs)
        return Clip(samples=samples, sample_rate=self.sample_rate)
