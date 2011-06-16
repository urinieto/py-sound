#!/usr/bin/env python

import os
import sys
import time
import numpy
import logging
import optparse

import sound

FLAGS = optparse.OptionParser()
FLAGS.add_option('-r', '--sample-rate', type=int, default=22050, metavar='N',
                 help='resample audio files to N Hz (22050)')
FLAGS.add_option('-o', '--overlap', type=float, default=0.5, metavar='R',
                 help='overlap successive windows by ratio R (0.5)')
FLAGS.add_option('-w', '--window-msec', type=float, default=30, metavar='N',
                 help='segment audio into blocks of N msec (30)')
FLAGS.add_option('-l', '--log', action='store_true',
                 help='output the log of the result')
FLAGS.add_option('-p', '--power', action='store_true',
                 help='output the absolute value of the result')
FLAGS.add_option('-c', '--cepstrum', action='store_true',
                 help='output the cepstrum coefficients')


def fft_coeffs(clip, window_sec, overlap):
    for _, samples in clip.iter_windows(window_sec, overlap):
        yield numpy.fft.rfft(samples)


def encode(x):
    return x.tostring().encode('base64').replace('\n', '')


def process(opts, filename):
    clip = sound.load_clip(filename, opts.sample_rate)

    window_sec = opts.window_msec / 1000.
    windows = clip.length_sec / window_sec / opts.overlap

    start = time.time()
    count = 0
    for count, coeffs in enumerate(fft_coeffs(clip, window_sec, opts.overlap)):
        if opts.cepstrum:
            coeffs = numpy.fft.rfft(numpy.log(abs(coeffs)))
        if opts.power:
            coeffs = abs(coeffs)
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
        format='%(levelname).1s %(asctime)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    main(*FLAGS.parse_args())
