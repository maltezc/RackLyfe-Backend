"""Setup file the mnb_backend package."""

from setuptools import setup

setup(
    name='mnb_backend',
    packages=['mnb_backend'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)