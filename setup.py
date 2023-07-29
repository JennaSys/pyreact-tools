from setuptools import setup

setup(
    name='jsxtopy',
    version='0.1.4',
    description="Converts a JSX fragment to a Python function equivalent",
    license="MIT",
    python_requires=">=3.7",
    install_requires=[
        'lxml',
        'pyperclip',
    ],
    packages=["jsxtopy"],
    entry_points={
        'console_scripts': [
            'jsxtopy=jsxtopy:main'
        ]
    }
)
