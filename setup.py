# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages


setup(
    name='twitch-stream-grabber',
    version='0.0.1',
    author=u'Andreas Bernacca',
    author_email='hello@rinti.se',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/rinti/twitch-screen-grabber',
    license='MIT',
    description='Possibility to get a current screenshot from a Twitch stream.',
    long_description=open('README.md').read(),
    zip_safe=False,
)
