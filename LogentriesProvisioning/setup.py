from distutils.core import setup

setup(
    name='LogentriesProvisioning',
    version='0.1.0',
    author='B Gaudin',
    author_email='benoit@logentries.com',
    packages=['logentriesprovisioning', 'logentriesprovisioning.test'],
    scripts=[],
    url='',
    license='LICENSE.txt',
    description='Logentries Automatic Provioning.',
    long_description=open('README.txt').read(),
    install_requires=[
        "LogentriesSDK",
        "fabric",
        "logentries",
    ],
)
