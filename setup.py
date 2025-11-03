from setuptools import setup, find_packages

setup(
    name="pqctls",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'liboqs-python>=0.14.1',
        'scapy>=2.5.0',
        'cryptography>=41.0.0',
        'pyOpenSSL>=23.0.0',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'matplotlib>=3.7.0',
        'pyyaml>=6.0',
        'requests>=2.31.0',
        'aiohttp>=3.8.0',
    ],
)