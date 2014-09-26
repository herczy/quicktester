import os
try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup


setup(
    name="quicktester",
    description="For running tests quicker",
    license="BSD",
    version="0.1",
    author="Viktor Hercinger",
    author_email="hercinger.viktor@gmail.com",
    maintainer="Viktor Hercinger",
    maintainer_email="hercinger.viktor@gmail.com",
    packages=['quicktester'],
    entry_points={
        'console_scripts': [
            'quicktester = quicktester.__main__:main'
        ],
    }
)
