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

'''Code for combining a repertoire of sounds to make other sounds.'''

import numpy
import numpy.random as rng

import sound


class Repertoire(list):
    '''A repertoire is a bunch of sound clips that can be mixed into an output.
    '''

    def __init__(self, clips):
        '''Initialize this repertoire with some clips.

        clips: A sequence of sound.Clip objects containing sound data.
        '''
        self.dtype = None
        self.frame_shape = None
        self.sample_rate = None
        self.extend(clips)

    def append(self, clip):
        '''Add a new clip to the repertoire.

        clip: A sound.Clip object to add.
        '''
        if not self:
            self.dtype = clip.dtype
            self.frame_shape = clip.shape[1:]
            self.sample_rate = clip.sample_rate

        # check that we have the same sample rate, etc.
        assert clip.dtype == self.dtype, \
            '%s: dtype %s is not %s' % (
            clip.filename, clip.dtype, self.dtype)
        assert clip.shape[1:] == self.frame_shape, \
            '%s: frame shape %s is not %s' % (
            clip.filename, clip.shape[1:], self.frame_shape)
        assert clip.sample_rate == self.sample_rate, \
            '%s: sample rate %d is not %d' % (
            clip.filename, clip.sample_rate, self.sample_rate)

        super(Repertoire, self).append(clip)

    def extend(self, clips):
        '''Add many new clips to the repertoire.

        clips: A sequence of sound.Clip objects to add.
        '''
        [self.append(clip) for clip in clips]

    def chain(self, overlap=0.25):
        '''Chain together clips from our repertoire.

        overlap: A value in [0, 1] that indicates the proportion of each clip to
          overlap in the resulting stream.
        '''
        active = self[rng.randint(len(self))]
        active_offset = 0
        target = None
        target_offset = None
        while True:
            if active_offset > (1. - overlap) * len(active):
                if target is None:
                    target = self[rng.randint(len(self))]
                    target_offset = 0
                mix = (len(active) - active_offset) / (overlap * len(active))
                yield mix * active[active_offset] + (1 - mix) * target[target_offset]
                target_offset += 1
            else:
                yield active[active_offset]
            active_offset += 1
            if active_offset == len(active):
                active = target
                active_offset = target_offset
                target = None
                target_offset = None

    def itercontrols(self, scale=1., min_coeff=0.):
        '''Generate a sequence of control signals.

        scale: A positive float giving the scale (variance) of the laplace
          distribution that generates control values.
        min_coeff: Only fire control signals with coefficients greater than this
          threshold.

        Generates a sequence of (index, coefficient, sample-offset) tuples.
        '''
        t = 0
        while True:
            t += 1
            frame = []
            for index, coeff in enumerate(rng.exponential(scale, len(self))):
                if coeff > min_coeff:
                    frame.append((index, coeff))
            yield tuple(frame)

    def mix(self, controls, control_rate=1.):
        '''Mix the clips in this repertoire into an output sound.

        controls: A sequence of control frames. Each control frame should
          consist of a tuple (possibly empty) containing (index, coefficient)
          pairs.
        control_rate: The rate (in Hz) at which control frames are generated.

        Returns a sound.Clip object containing the mixed sound.
        '''
        controls = iter(controls)

        # set up a circular buffer (2x the max length of a clip) to hold data
        # for future frames. we rotate the second half of this buffer to the
        # first half whenever s == N, giving amortized O(1) append runtime.
        # http://mail.scipy.org/pipermail/scipy-user/2009-February/020108.html
        N = max(len(w) for w in self)
        staging = numpy.zeros((2 * N, ) + self.frame_shape, self.dtype)
        s = 0

        samples_per_control = float(self.sample_rate) / control_rate
        wait = 0.
        while True:
            if wait <= 0:
                wait += samples_per_control
                for index, coeff in controls.next():
                    w = self[index]
                    staging[s:s + len(w)] += coeff * w
            yield staging[s]
            wait -= 1
            s += 1
            if s == N:
                staging[:N] = staging[N:]
                staging[N:] = 0.
                s = 0


if __name__ == '__main__':
    import sys
    import gzip
    import pickle

    sample_rate = 16000
    control_rate = 3.
    sec = 3.

    rep = Repertoire(sound.load_clip(f, sample_rate) for f in sys.argv[1:])
    print 'loaded', len(rep), 'sounds into repertoire'

    def play(samples):
        sound.Clip(samples=list(samples), sample_rate=sample_rate).play()

    print 'playing sound by chaining'
    frames = rep.chain()
    play(frames.next() for _ in range(sample_rate * 3))

    print 'playing sound by mixing'
    controls = rep.itercontrols(0.02, 0.1)
    play(rep.mix(
        (controls.next() for _ in range(int(control_rate * sec))),
        control_rate=control_rate))
