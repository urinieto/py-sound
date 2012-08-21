import os
import setuptools

# take description from README.md
here = os.path.dirname(os.path.abspath(__file__))
readme = ''
try:
    readme = file(os.path.join(here, 'README.md')).read()
except (OSError, IOError):
    pass

setuptools.setup(
    name='lmj.sound',
    version='0.1.1',
    install_requires=['scipy', 'scikits.audiolab', 'scikits.samplerate'],
    namespace_packages=['lmj'],
    packages=setuptools.find_packages(),
    author='Leif Johnson',
    author_email='leif@leifjohnson.net',
    description='An assemblage of code for manipulating sound data',
    long_description=readme,
    license='MIT',
    keywords=('sound '
              'fft '
              'noise '
              'encoding '
              'resampling'),
    url='http://github.com/lmjohns3/py-sound/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        ],
    )
