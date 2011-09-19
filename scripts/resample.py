#!/usr/bin/env python
#
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

'''Resample a set of sounds, and save them back to disk.'''

import os
import sys
import logging
import optparse
import multiprocessing

import lmj.sound

FLAGS = optparse.OptionParser()
FLAGS.add_option('-r', '--sample-rate', default=22050, type=float, metavar='N',
                 help='resample all sounds to N Hz before processing (22050)')
FLAGS.add_option('-o', '--output', metavar='DIR',
                 help='save resampled sounds to DIR (resampled-N)')


SAMPLE_RATE = None
OUTPUT = None

def resample(filename):
    lmj.sound.load_clip(filename, SAMPLE_RATE).save(
        os.path.join(OUTPUT, os.path.basename(filename)))


if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format='%(levelname).1s %(asctime)s [%(module)s:%(lineno)d] %(message)s')
    opts, args = FLAGS.parse_args()
    SAMPLE_RATE = opts.sample_rate
    OUTPUT = opts.output or 'resampled-%d' % opts.sample_rate
    if not os.path.isdir(OUTPUT):
        os.makedirs(OUTPUT)
    multiprocessing.Pool().map(resample, args)
