from setuptools import setup, find_packages
setup(
    name = "pythonMoodleScraper",
    version = "0.0.5",
    packages = find_packages(),
    scripts = ['pythonMoodleScraper.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['docutils>=0.3', 'beautifulsoup4>=4.3.2', 'requests'],

)