from setuptools import setup

setup(
    name='smart-file-manager',
    version='1.0.0',
    py_modules=['smart_file_manager'],  # this is your .py file (without .py)
    install_requires=[
        'watchdog'
    ],
    entry_points={
        'console_scripts': [
            'smartfm = smart_file_manager:main',  # CLI: smartfm → runs main() in smart_file_manager.py
        ],
    },
)