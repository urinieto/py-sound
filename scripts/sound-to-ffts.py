#!/usr/bin/env python

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

import lmj.sound
import logging
import numpy
import optparse
import os
import sys
import time

FLAGS = optparse.OptionParser()
FLAGS.add_option('-r', '--sample-rate', type=int, default=22050, metavar='N',
                 help='resample audio files to N Hz (22050)')
FLAGS.add_option('-w', '--window-msec', type=int, default=30, metavar='N',
                 help='process audio in frames of N msec (30)')
FLAGS.add_option('-i', '--interval-msec', type=int, default=5, metavar='N',
                 help='space successive frames N msec apart (5)')
FLAGS.add_option('-l', '--log', action='store_true',
                 help='output the log of the result')
FLAGS.add_option('-p', '--power', action='store_true',
                 help='output the absolute value of the result')
FLAGS.add_option('-c', '--cepstrum', action='store_true',
                 help='output the cepstrum coefficients')


def encode(x):
    return x.tostring().encode('base64').replace('\n', '')


def process(opts, filename):
    clip = lmj.sound.load_clip(filename, opts.sample_rate)

    window_sec = opts.window_msec / 1000.
    interval_sec = opts.interval_msec / 1000.
    windows = (clip.length_sec - window_sec) / interval_sec

    fft_coeffs = clip.iter_fft_coeffs(window_sec, interval_sec)

    count = 0
    start = time.time()
    for count, (_, coeffs) in enumerate(fft_coeffs):
        if opts.cepstrum:
            coeffs = numpy.fft.rfft(numpy.log(abs(coeffs) ** 2))
        if opts.power:
            coeffs = abs(coeffs) ** 2
        if opts.log:
            coeffs = numpy.log(coeffs)

        print encode(coeffs)

        if count and not count % 10000:
            logging.debug('%s: %dk of %dk windows processed in %dms',
                          os.path.basename(filename),
                          count / 1000., windows / 1000.,
                          1000 * (time.time() - start))
    return count


def main(opts, filenames):
    for filename in filenames:
        start = time.time()
        windows = process(opts, filename)
        logging.info('%s: %d windows processed in %dms',
                     os.path.basename(filename),
                     windows, 1000 * (time.time() - start))


if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        format='%(levelname).1s %(asctime)s %(message)s')
    main(*FLAGS.parse_args())
