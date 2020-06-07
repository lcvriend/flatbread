import re
from pathlib import Path
from setuptools import setup, find_packages

PATH = Path(__file__).resolve().parent

def get_version(filename, key):
    regex = rf"^__{key}__\s*=\s*['\"]([^'\"]*)['\"]"
    file = PATH / filename
    file_content = file.read_text(encoding='utf8')
    version_match = re.search(regex, file_content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError(f"Unable to find '{key}' string.")

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='flatbread',
    version=get_version('flatbread/version.py', 'version'),
    description='Pivot tables and graphs for pandas',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Utilities',
    ],
    keywords='data pivot tables pandas',
    url='http://github.com/lcvriend/flatbread',
    author=get_version('flatbread/version.py', 'author'),
    author_email=get_version('flatbread/version.py', 'email'),
    license=get_version('flatbread/version.py', 'license'),
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0',
        'matplotlib>=3.0.0',
    ],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
)
