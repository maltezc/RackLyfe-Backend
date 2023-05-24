"""Setup file the mnb-backend package."""

from setuptools import setup

setup(
    name='mnb-backend',
    packages=['mnb-backend'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)