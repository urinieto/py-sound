#!/usr/bin/env python

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

'''A glumpy-based FFT viewer.'''

import sys
import math
import time
import numpy
import glumpy
import optparse
import lmj.sound
import multiprocessing

FLAGS = optparse.OptionParser()
FLAGS.add_option('', '--sample-rate', type=int, default=22050, metavar='N',
                 help='resample audio files to N Hz (22050)')
FLAGS.add_option('', '--window-msec', type=float, default=30, metavar='N',
                 help='segment audio into blocks of N msec (30)')
FLAGS.add_option('', '--latency-msec', type=float, default=0.5, metavar='N',
                 help='adjust playback of sound by N msec (0.5)')
FLAGS.add_option('', '--history', type=int, default=800, metavar='N',
                 help='display the most recent N frames (800)')
FLAGS.add_option('', '--min-power', type=float, default=1e-7, metavar='N',
                 help='set the bottom of the dynamic range to N (1e-7)')
FLAGS.add_option('', '--range', type=float, default=10, metavar='N',
                 help='set the dynamic range to N (10)')
FLAGS.add_option('', '--silent', action='store_true',
                 help='do not play the sound while displaying it')
FLAGS.add_option('', '--phase', action='store_true',
                 help='default to the phase spectrum view')
FLAGS.add_option('', '--cepstrum', action='store_true',
                 help='default to the cepstrum view')


if __name__ == '__main__':
    opts, args = FLAGS.parse_args()

    start = time.time()

    clip = lmj.sound.load_clip(args[0], opts.sample_rate)
    samples = int(1 + clip.sample_rate * opts.window_msec / 2000.0)

    phase = numpy.zeros((opts.history, samples), 'f')
    spectrum = numpy.zeros((opts.history, samples), 'f')
    cepstrum = numpy.zeros((opts.history, samples / 2 + 1), 'f')

    index = 0

    window = glumpy.Figure()
    player = None

    @window.timer(1000.0 / opts.window_msec)
    def update(dt):
        global index, phase, spectrum, cepstrum, player

        now = time.time()

        signal = clip.get_window(now - start + opts.latency_msec / 1000.0,
                                 opts.window_msec / 1000.0)

        if signal is None:
            if player:
                player.terminate()
            sys.exit()

        def idx(offset):
            return (index + offset) % len(phase)

        index = idx(1)

        def power(scale=1):
            m = opts.min_power + scale
            return numpy.clip(abs(coeffs), m, m + opts.range) - m

        coeffs = numpy.fft.rfft(signal)
        spectrum[index, ::-1] = numpy.log(1 + power()) / numpy.log(opts.range)
        spectrum[idx(1), :] = spectrum[idx(2), :] = 0

        angles = numpy.array([math.atan2(c.imag, c.real) for c in coeffs])
        phase[index, ::-1] = (angles + numpy.pi) / (2 * numpy.pi)
        phase[idx(1), :] = phase[idx(2), :] = 0

        coeffs = numpy.fft.rfft(numpy.log(abs(coeffs)))
        cepstrum[index, ::-1] = numpy.log(1 + power(10)) / numpy.log(opts.range)
        cepstrum[idx(1), :] = cepstrum[idx(2), :] = 0

    kwargs = dict(interpolation='bicubic',
                  colormap=glumpy.colormap.IceAndFire,
                  vmin=0,
                  vmax=1)

    P = glumpy.Image(phase.T, **kwargs)
    S = glumpy.Image(spectrum.T, **kwargs)
    C = glumpy.Image(cepstrum.T, **kwargs)

    I = S
    if opts.phase:
        I = P
    if opts.cepstrum:
        I = C

    @window.event
    def on_draw():
        window.clear()
        I.draw(x=window.x, y=window.y, z=0, width=window.width, height=window.height)

    @window.event
    def on_key_press(key, modifiers):
        global I, player
        if key in (glumpy.window.key.ESCAPE, glumpy.window.key.Q):
            if player:
                player.terminate()
            sys.exit()
        if key == glumpy.window.key._1:
            I = S
        if key == glumpy.window.key._2:
            I = P
        if key == glumpy.window.key._3:
            I = C

    @window.event
    def on_idle(dt):
        I.update()
        window.redraw()

    if not opts.silent:
        player = multiprocessing.Process(target=clip.play)
        player.start()

    start = time.time()

    glumpy.show()
