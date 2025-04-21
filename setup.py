from setuptools import setup, find_packages

setup(
    name="contribcast",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
          "requests",
          "click",
          "langchain-openai",
          "openai",
          "python-dotenv",
          "seaborn",
          "matplotlib",
          "schedule",
          "slack_sdk",
          "twilio",
    ],
    entry_points={
        'console_scripts': [
            'contribcast = contribcast.cli:main'
        ]
    },
)
