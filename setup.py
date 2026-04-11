from setuptools import setup, find_packages

setup(
    name='nestc',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pycparser',
        'click', # Usaremos click para que sea una CLI profesional
    ],
    entry_points={
        'console_scripts': [
            'nestc=nestc.cli:main', # Esto crea el binario real
        ],
    },
)