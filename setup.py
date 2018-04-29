import os

from setuptools import setup

from barbara import __version__


_here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_here, 'README.rst')) as f:
    long_description = f.read()


setup(
        name='barbara',
        version=__version__,
        packages=['barbara'],
        url='http://github.com/mverteuil/barbara',
        license='GNU General Public License v3.0',
        author='Matthew de Verteuil',
        author_email='mverteuil@github.com',
        description='Environment variable management',
        long_description=long_description,
        install_requires=[
            'Click',
            'python-dotenv',
            'colorama',
        ],
        entry_points="""
        [console_scripts]
        barb=barbara.cli:barbara
        """,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: MacOS',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Unix',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3 :: Only',
            'Topic :: Software Development',
            'Topic :: System',
            'Topic :: Terminals',
        ]
)
