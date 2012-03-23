import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "mailmanweb",
    version = '1.0.0a1',
    description = "A web user interface for GNU Mailman",
    long_description=open('README.rst').read(),
    maintainer = "The Mailman GSOC Coders",
    license = 'GPLv3',
    keywords = 'email mailman django',
    url = "https://launchpad.net/mailmanweb",
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True
)
