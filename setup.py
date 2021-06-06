from setuptools import setup

setup(
    name='airquality',
    version='1.0',
    author='Miguel Macarro',
    python_requires='>=3.9',
    packages=setuptools.find_packages(exclude=('test',)),
    install_requires=[
        'flask',
        'webargs',
        'requests'
    ]
)
