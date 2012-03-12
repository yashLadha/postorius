import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "mailmanweb",
    version = '0.0.1',
    description = "A web user interface for GNU Mailman",
    long_description=open('README.rst').read(),
    maintainer = "The Mailman GSOC Coders",
    maintainer_email = "flo.fuchs@gmail.com",
    license = 'GPLv3',
    keywords = 'email mailman django',
    url = "https://code.launchpad.net/~flo-fuchs/mailmanwebgsoc2011/transition",
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True
)
