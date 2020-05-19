from setuptools import find_packages, setup

setup(
    name='MyStocks',
    version='0.0.1',
    packages=find_packages(),
    install_requires=['flask', 'click'],
    entry_points={
        'console_scripts': [
            'stock=MyStocks.cli:main',
        ],
    },
)
