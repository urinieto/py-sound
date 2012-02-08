# py-sound

This package contains several modules for manipulating sound data in Python.

It depends on several other excellent Python packages, namely [scipy][],
[scikits.audiolab][] (which in turn depends on [libsndfile][]), and
[scikits.samplerate][] (which, likewise, depends on [libsamplerate][]).

[scipy]: http://scipy.org
[scikits.samplerate]: http://www.ar.media.kyoto-u.ac.jp/members/david/softwares/samplerate/sphinx/index.html
[scikits.audiolab]: http://www.ar.media.kyoto-u.ac.jp/members/david/softwares/audiolab/sphinx/fullapi.html
[libsndfile]: http://www.mega-nerd.com/libsndfile/
[libsamplerate]: http://www.mega-nerd.com/SRC/

## Installation

Things will be happiest if you install everything using [pip][] ! Just :

    pip install lmj.sound

and the universe will start to move.

[pip]: http://pip-installer.org

### Dependencies

You should make sure you already have scipy installed, or at least have the
headers to build it. You should also make sure you have libsndfile and
libsamplerate installed on your machine.

If you live on a Mac, use [Homebrew][] to install things :

    brew install libsndfile libsamplerate

If you're an Ubuntu person :

    sudo apt-get install libsndfile-dev libsamplerate-dev

Installing the `lmj.sound` package itself does not require any compilation.

## Interface

### Clip

The primary interface for the library is the `lmj.sound.Clip` class. Clips can
be loaded from and saved to disk (in any format that the sndfile library
supports). Resampling is reasonably smart. You can also encode and decode a clip
using FFT or a [matching pursuit][]

[matching pursuit]: http://github.com/lmjohns3/py-pursuit

### Noise

You can generate white and pink noise with `lmj.noise.white` or
`lmj.noise.pink`, respectively. Did I mention that pink noise is pretty rad ? It
is.

### Repertoire

There's also a sort of silly synthesizer in here that takes a number of `Clip`s
and provides an interface to mix or chain them together randomly.

## License

(The MIT License)

Copyright (c) 2011 Leif Johnson <leif@leifjohnson.net>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the 'Software'), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
