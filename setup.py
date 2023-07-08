import os

from setuptools import setup
from version import __version__

if os.path.exists("README.md"):
    with open("README.md", "r") as fh:
        long_description = fh.read()

setup(
    name='OpenALPR-Webhook',
    version=__version__,
    platforms='linux',
    include_package_data=True,
    url='https://github.com/mibs510/OpenALPR-Webhook',
    license='MIT',
    author='Connor McMillan',
    author_email='connor@mcmillan.website',
    description='OpenALPR-Webhook is a self-hosted web application that accepts Rekor Scout™ POST data allowinglonger '
                'data retention. It was designed with an emphasis on security to meet organization/business needs.',
    long_description=long_description,
    python_requires=">=3.10",
    install_requires=['certifi~=2021.10.8', 'charset-normalizer~=2.0.9', 'elevate~=0.1.3', 'idna~=3.3',
                      'keyboard~=0.13.5', 'numpy~=1.21.4', 'parse~=1.19.0', 'pexpect==4.8.0', 'psutil~=5.8.0',
                      'pycairo~=1.20.1', 'pydbus~=0.6.0', 'PyGObject~=3.42.0', 'pyserial~=3.5',
                      'python-json-logger~=2.0.2', 'requests~=2.26.0', 'sentry-sdk~=1.5.0', 'urllib3~=1.26.7',
                      'xxhash~=2.0.2', 'Yapsy~=1.12.2'],
    classifiers=['Development Status :: 4 - Beta',
                 'Framework :: Flask',
                 'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 3.10'],
)

if __name__ == "__main__":
    pass
