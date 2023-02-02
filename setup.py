from setuptools import setup, find_packages

with open("./README.md", "r") as f:
    long_description = f.read()

# Version
# Info: https://packaging.python.org/guides/single-sourcing-package-version/
# Example: https://github.com/pypa/warehouse/blob/64ca42e42d5613c8339b3ec5e1cb7765c6b23083/warehouse/__about__.py
meta_package = {}
with open("./twitterexplorer/__version__.py") as f:
    exec(f.read(), meta_package)

setup(
    name="twitterexplorer",
    version=meta_package["__version__"],
    description="A Python tool for interactive network visualizations of Twitter data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/pournaki/twitter-explorer",
    license="GPLv3",
    author="Armin Pournaki",
    keywords="networks, social media",
    python_requires=">=3.7",
    packages=find_packages(exclude=[]),
    package_data={'twitterexplorer':['html/*','languages.json']},
    install_requires=[
        "streamlit>=1.7.0,<2",
        "tweepy>=4.6.0",        
        "pandas>=1.3.4,<2",        
        "python-igraph>=0.9.8,<1",
        "twitwi>=0.15.0,<0.16",
        "twarc>=2.9.4,<3",
        "louvain>=0.8.0",
    ],
    entry_points={"console_scripts": ["twitterexplorer=twitterexplorer.launcher:main"]},
    zip_safe=True,
)