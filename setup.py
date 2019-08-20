from setuptools import setup

setup(
    name='rapyuta_cli',
    version='0.1',
    py_modules=['rapyuta_cli'],
    install_requires=[
        'click', 'requests'
    ],
    entry_points= {
        'console_scripts': [
            'rapyuta = rapyuta_cli:cli'
        ]
    }
)
