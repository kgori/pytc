from distutils.core import setup

setup(name='pytc',
    version='1.0',
    description='Python wrapper for TreeCollection',
    author='Kevin Gori',
    author_email='kgori@ebi.ac.uk',
    url='',
    packages=['pytc', 
        'pytc.errors', 
        'pytc.readers', 
        'pytc.utils',
        'pytc.wrappers'
    ],
)