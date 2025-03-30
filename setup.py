from setuptools import setup, find_packages

setup(
    name="ai_news",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests',
        'feedparser',
        'beautifulsoup4',
        'newspaper3k',
        'pytz'
    ],
) 