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
        ],
        entry_points = '''
        [console_scripts]
        barb=barbara:barbara
        ''',
)
