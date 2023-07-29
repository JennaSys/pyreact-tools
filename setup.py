from setuptools import setup, find_packages

setup(
    name='jsxtopy',
    version='0.1.3',
    description="Converts a JSX fragment to a Python function equivalent",
    license="MIT",
    python_requires=">=3.7",
    install_requires=[
        'lxml',
        'pyperclip',
    ],
    packages=find_packages(include=["jsxtopy"]),
    entry_points={
        'console_scripts': [
            'jsxtopy=jsxtopy:main'
        ]
    }
)
