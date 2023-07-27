from setuptools import setup, find_packages

setup(
    name='Ibp2py',
    version='1.0.0',
    author='Pedro Rastha',
    author_email='pedrorastha@gmail.com',
    description='SAP Data Retrieval and Processing Library for IBP',
    long_description='A Python library to fetch and process data from SAP IBP.',
    long_description_content_type='text/markdown',
    url='https://github.com/pedrorastha/ibpy',
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.1',
        'pandas>=1.5.2',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
