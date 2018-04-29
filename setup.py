from setuptools import setup

setup(
        name='barbara',
        version='0.1',
        packages=['barbara'],
        url='http://github.com/mverteuil/barbara',
        license='GNU General Public License v3.0',
        author='Matthew de Verteuil',
        author_email='mverteuil@github.com',
        description='Environment variable management',
        install_requires=[
            'Click',
            'python-dotenv',
            'colorama',
        ],
        entry_points="""
        [console_scripts]
        barb=barbara:barbara
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
