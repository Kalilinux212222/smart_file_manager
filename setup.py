from setuptools import setup

setup(
    name='smart-file-manager',
    version='1.0.0',
    py_modules=['file_manager'],
    install_requires=[
        'watchdog'
    ],
    entry_points={
        'console_scripts': [
            'smartfm = smart_file_manager:main',
        ],
    },
)