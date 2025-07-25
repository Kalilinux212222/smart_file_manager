from setuptools import setup

setup(
    name='smart-file-manager',
    version='1.1.0',
    py_modules=['main'],  # this is your .py file (without .py)
    install_requires=[
        'watchdog'
    ],
    entry_points={
        'console_scripts': [
            'smartfm = main:main',  # CLI: smartfm → runs main() in main.py
        ],
    },
)