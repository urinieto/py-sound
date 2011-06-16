lmj.sound
=========

This package contains several modules for manipulating sound data in Python.

It depends on several other excellent Python packages, namely scipy_,
`scikits.audiolab`_ (which in turn depends on libsndfile_), and
`scikits.samplerate`_ (which, likewise, depends on libsamplerate_).

.. _scipy: http://scipy.org
.. _scikits.samplerate: http://www.ar.media.kyoto-u.ac.jp/members/david/softwares/samplerate/sphinx/index.html
.. _scikits.audiolab: http://www.ar.media.kyoto-u.ac.jp/members/david/softwares/audiolab/sphinx/fullapi.html
.. _libsndfile: http://www.mega-nerd.com/libsndfile/
.. _libsamplerate: http://www.mega-nerd.com/SRC/

Installing
==========

Things will be happiest if you install everything using pip_ ! Just ::

  pip install lmj.sound

and the universe will start to move.

.. _pip: http://pip-installer.org

Dependencies
------------

You should make sure you already have scipy_ installed, or at least have the
headers to build it. You should also make sure you have libsndfile_ and
libsamplerate_ installed on your machine.

If you live on a Mac, use Homebrew_ to install things ::

  brew install libsndfile libsamplerate

If you're an Ubuntu person ::

  sudo aptitude install libsndfile-dev libsamplerate-dev

Installing the lmj.sound package itself does not require any compilation.

.. _scipy: http://scipy.org
.. _libsndfile: http://www.mega-nerd.com/libsndfile/
.. _libsamplerate: http://www.mega-nerd.com/SRC/

Interface
=========

Clip
----

The primary interface for the library is the **lmj.sound.Clip** class. Clips can
be loaded from and saved to disk (in any format that the sndfile library
supports). Resampling is reasonably smart. You can also encode and decode a clip
using FFT or a `matching pursuit`_

.. _matching pursuit: http://github.com/lmjohns3/py-pursuit

Noise
-----

You can generate white and pink noise easily with **lmj.noise.white** or
**lmj.noise.pink**, respectively. Did I mention that pink noise is pretty rad ?
It is.

Repertoire
----------

There's also a sort of silly synthesizer in here that takes a number of Clips
and provides an interface to mix or chain them together randomly.
