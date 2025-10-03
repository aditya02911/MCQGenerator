from setuptools import find_packages, setup

setup(
    name='mcqgenerator',
    version='0.0.1',
    author='aditya',
    author_email='adityaalok2964@gmail.com',
    install_requires=[
        "langchain",
        "google-generativeai",
        "langchain-google-genai",
        "streamlit",
        "python-dotenv",
        "PyPDF2"
    ],
    packages=find_packages()
)
