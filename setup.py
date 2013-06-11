import os
import setuptools

setuptools.setup(
    name='lmj.sound',
    version='0.1.4',
    namespace_packages=['lmj'],
    packages=setuptools.find_packages(),
    author='Leif Johnson',
    author_email='leif@leifjohnson.net',
    description='An assemblage of code for manipulating sound data',
    long_description=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')).read(),
    license='MIT',
    url='http://github.com/lmjohns3/py-sound/',
    keywords=('sound '
              'fft '
              'noise '
              'encoding '
              'resampling'),
    install_requires=['scipy', 'scikits.audiolab', 'scikits.samplerate'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        ],
    )
