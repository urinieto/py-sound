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

'''A Python library of sorts for manipulating sound data.'''

import noise
from sound import Clip
from repertoire import Repertoire
from gammatone import Gammatone, Gammachirp


def load_clip(filename, sample_rate=None, normalize=False):
    '''Return a sound clip with some standard preprocessing applied.'''
    clip = Clip(filename)
    if sample_rate is not None and sample_rate != clip.sample_rate:
        if sample_rate < clip.sample_rate:
            clip.lowpass_filter(sample_rate / 2)
        clip.set_sample_rate(sample_rate)
    if normalize:
        clip.normalize()
    return clip


class CachedLoader(dict):
    '''Cache loaded sound clips in memory.

    To use, create an instance of this object and then call it like you would
    call load_clip.
    '''

    def __init__(self, maxlen=256):
        '''Initialize the cache with a maximum clip count.'''
        import collections
        self._maxlen = maxlen
        self._lru = collections.deque(maxlen=maxlen)

    def __call__(self, filename, sample_rate=None):
        '''Retrieve a clip, either from memory or from disk.'''
        if filename in self:
            self._lru.remove(filename)
        else:
            clip = load_clip(filename, sample_rate)
            if len(self._lru) == self._maxlen:
                del self[self._lru[0]]
            self[filename] = clip
        self._lru.append(filename)
        return self[filename]
