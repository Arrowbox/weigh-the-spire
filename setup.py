from setuptools import setup
from setuptools import find_packages

pkg_name = 'weigh-the-spire'

setup(
    name=pkg_name,
    version='0.0.1',
    description='Stats for Slay the Spire',
    url='https://github.com/Arrowbox/weigh-the-spire',
    author='Jayson Messenger',
    author_email='jayson.messenger@gmail.com',
    license='MIT',
    packages=find_packages('src'),
    entry_points={
        'console_scripts': ['weigh-the-spire=weigh_the_spire.__main__:main']
    }
)
