# setup.py
from setuptools import setup, find_packages

setup(
    name='summarizer',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'nltk>=3.5',
    ],
    entry_points={
        'console_scripts': [
            'summarize = summarizer.summarize:summarize_text',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple one-sentence summarizer library based on NLTK.",
    keywords="summarizer nltk text",
)
