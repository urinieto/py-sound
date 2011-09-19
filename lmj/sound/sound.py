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

'''Utility classes and methods for processing sound data.'''

import os
import sys
import numpy
import logging
import scipy.signal

from scikits.audiolab import Format, Sndfile, play
from scikits.samplerate import resample


class Clip(object):
    '''A clip is a single piece of sound that's loaded from a file on disk.

    Clips are all forced to be mono (1 channel) by averaging each frame across
    all channels that are encountered in the file.
    '''

    def __init__(self, filename='', samples=None, sample_rate=0.):
        '''Initialize this signal by loading sound data from a file.

        filename: The name of the file to load sound data from, if any.
        samples: If given, a numpy array containing sound data.
        sample_rate: If samples is not None, this must also be given.
        '''
        self.samples = numpy.zeros(1.)
        self.sample_rate = 44100.
        self.length_sec = 0.

        self.filename = filename
        if filename:
            self.load(filename)
        elif samples is not None:
            assert 0 < sample_rate
            self.samples = numpy.asarray(samples)
            self.sample_rate = sample_rate
            self.length_sec = len(self.samples) / self.sample_rate

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

    def load(self, filename):
        '''Load sound data from a file on disk.

        filename: The name of the file to load sound data from.
        '''
        snd = Sndfile(filename)
        self.samples = snd.read_frames(snd.nframes)
        while len(self.shape) > 1:
            self.samples = self.samples.mean(axis=-1)

        self.filename = filename
        self.sample_rate = snd.samplerate
        self.length_sec = len(self.samples) / self.sample_rate

        logging.info('%s: read %d frames at %d Hz (%.2f sec)',
                     os.path.basename(self.filename),
                     len(self.samples),
                     self.sample_rate,
                     self.length_sec)

    def normalize(self):
        '''Normalize the samples in this clip.

        Normalizing here means subtracting out the mean and dividing by the
        standard deviation of all samples.
        '''
        self.samples -= self.samples.mean()
        self.samples /= self.samples.std()
        logging.info('%s: normalized %d samples',
                     os.path.basename(self.filename),
                     len(self.samples))

    def lowpass_filter(self, pass_freq, attenuate_freq=None, pass_db=3, attenuate_db=90):
        '''Lowpass filter the clip to eliminate high frequencies.

        pass_freq: Maintain at most pass_db attenuation for frequencies lower
          than this.
        attenuate_freq: Maintain at least attenuate_db attenuation for
          frequencies higher than this. Defaults to 10% higher than pass_freq.
        pass_db: Allow this much attenuation in the passband.
        attenuate_db: Enforce this much attenuation in the stopband.
        '''
        nyquist = self.sample_rate / 2.0
        attenuate_freq = attenuate_freq or pass_freq * 1.1
        assert 0 < pass_freq < attenuate_freq < nyquist
        order, width = scipy.signal.buttord(
            pass_freq / nyquist,
            attenuate_freq / nyquist,
            pass_db,
            attenuate_db)
        assert order < 32, '%d: implausible butterworth filter order !' % order
        b, a = scipy.signal.butter(order, width)
        self.samples = numpy.asarray(
            scipy.signal.lfilter(b, a, self.samples),
            self.dtype)
        logging.info('%s: lowpass filter %.2fHz/%.2fdB -> %.2f/%.2fdB = %d, %.3f',
                     os.path.basename(self.filename),
                     pass_freq, pass_db, attenuate_freq, attenuate_db,
                     order, width)

    def set_sample_rate(self, sample_rate):
        '''Set the sample rate for this clip.

        sample_rate: The desired sample rate for the clip.
        '''
        resample_ratio = float(sample_rate) / self.sample_rate
        if resample_ratio != 1.0:
            self.samples = numpy.asarray(
                resample(self.samples, resample_ratio, 'sinc_best'),
                self.dtype)
            r = self.sample_rate = sample_rate
            n = len(self.samples)
            logging.info('%s: resampled %d frames at %d Hz (%.2f sec)',
                         os.path.basename(self.filename), n, r, n / r)

    def get_window(self, offset_sec, window_sec, window_type='hanning'):
        '''Get a slice of samples from this clip as a numpy array.

        offset_sec: The number of seconds from the start of the sound.
        window_sec: The number of seconds of samples to retrieve.
        window_type: A string or tuple describing the type of window to use. See
          the documentation for scipy.signal.get_window for details.
        '''
        n = int(self.sample_rate * window_sec)
        window = scipy.signal.get_window(window_type, n)
        offset = int(self.sample_rate * offset_sec)
        if offset + n < len(self.samples):
            return window * self.samples[offset:offset + n]
        return None

    def iter_windows(self, window_sec, overlap=0.5, window_type='hanning'):
        '''Iterate over consecutive windows of samples in this clip.

        window_sec: The number of seconds of samples to return in each window.
        overlap: The proportion (in [0, 1]) of overlap in successive windows.
        window_type: A string or tuple describing the type of window to use. See
          the documentation for scipy.signal.get_window for details.
        '''
        n = int(self.sample_rate * window_sec)
        o = int(n * (1. - overlap))
        window = scipy.signal.get_window(window_type, n)
        offset = 0
        while offset + n < len(self.samples):
            yield offset, window * self.samples[offset:offset + n]
            offset += o

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

    def reconstruct_with_fft(self, window_sec=0.1, overlap=0.5, min_coeff=0.1, d_phase=0.):
        '''Reconstruct the sound in this clip using threshold-filtered FFT data.

        window_sec: Process sound in windows of this length.
        overlap: Overlap successive windows by this fraction.
        min_coeff: Set all FFT coefficients less than this magnitude to 0.
        phase_distort: Distort the phase of each coefficient uniformly in the
          interval [-phase_distort, phase_distort].

        Returns a new clip with the reconstructed sound.
        '''
        pd = phase_distort
        samples = numpy.zeros(self.shape, self.dtype)
        for o, w in self.iter_windows(window_sec, overlap):
            coeffs = numpy.fft.rfft(w)
            for i, c in enumerate(coeffs):
                if abs(c) < min_coeff:
                    coeffs[i] = 0
                else:
                    t = numpy.angle(c) + numpy.random.uniform(-pd, pd)
                    coeffs[i] = abs(c) * (numpy.cos(t) + numpy.sin(t) * 1j)
            samples[o:o+len(w)] += numpy.fft.irfft(coeffs)
        return Clip(samples=samples, sample_rate=self.sample_rate)

    def reconstruct_with_codebook(self, codebook,
                                  min_coeff=0., max_num_coeffs=-1,
                                  window_sec=None, overlap=0.5):
        '''Reconstruct the sound in this clip using a matching pursuit object.

        codebook: An lmj.pursuit.TemporalCodebook instance to do the encoding
          and decoding.
        min_coeff: Stop encoding when coefficients fall below this threshold.
        max_num_coeffs: Stop encoding when this many coefficients have been
          processed (per window).

        Returns a new clip with the reconstructed sound.
        '''
        samples = codebook.decode(
            codebook.encode(self.samples.copy(), min_coeff, max_num_coeffs),
            self.shape)
        return Clip(samples=samples, sample_rate=self.sample_rate)
