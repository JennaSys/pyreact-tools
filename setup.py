from setuptools import setup

setup(
    name='jsxtopy',
    version='0.1.2',
    description="Converts a JSX fragment to a Python function equivalent",
    license="MIT",
    python_requires=">=3.8",
    install_requires=[
        'lxml',
        'pyperclip',
    ],
    packages=['jsxtopy'],
    entry_points={
        'console_scripts': [
            'jsxtopy=jsxtopy:main'
        ]
    }
)
