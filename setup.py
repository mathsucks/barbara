# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), 'rb') as stream:
    readme = stream.read().decode('utf8')

setup(
    long_description=readme,
    name='barbara',
    version='0.10.2',
    description='Environment variable management',
    python_requires='==3.*,>=3.6.0',
    author='Matthew de Verteuil',
    author_email='onceuponajooks@gmail.com',
    license='GPL-3.0',
    classifiers=[
        'Development Status :: 4 - Beta', 'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS', 'Operating System :: POSIX :: Linux',
        'Operating System :: Unix', 'Topic :: Software Development',
        'Topic :: System', 'Topic :: Terminals'
    ],
    entry_points={
        'console_scripts': [
            'barb = barbara.cli:barbara_develop',
            'barb-deploy = barbara.cli:barbara_deploy'
        ]
    },
    packages=['barbara'],
    package_data={},
    install_requires=[
        'boto3==1.7.48', 'click==7.*,>=7.0.0', 'poetry-version==0.*,>=0.1.3',
        'python-dotenv==0.*,>=0.10.1', 'pyyaml==5.*,>=5.1.0'
    ],
    extras_require={
        'dev': [
            'black==19.3b0', 'dephell==0.*,>=0.5.8',
            'dephell[full]==0.*,>=0.5.8', 'flake8==3.*,>=3.7.0',
            'flake8-bugbear==19.*,>=19.3.0', 'flake8-mypy==17.*,>=17.8.0',
            'flake8-polyfill==1.*,>=1.0.0', 'isort==4.*,>=4.3.0',
            'isort[pyproject]==4.*,>=4.3.0', 'keyring==19.*,>=19.0.0',
            'lockfile==0.*,>=0.12.2', 'poetry-setup==0.*,>=0.3.6',
            'pre-commit==1.*,>=1.15.0', 'pytest==4.*,>=4.4.0',
            'pytest-cov==2.*,>=2.6.0'
        ]
    },
)
