import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="projet-python-twitter",
    version="0.0.1",
    author=(
        "Gabriel Watkinson <gabriel.watkinson@ensae.fr>, "
        "Mathias Vigouroux <mathias.vigouroux@ensae.fr>, "
        "Wilfried Yapi <wilfied.yapi@ensae.fr>"
    ),
    description="Projet avec l'API de Twitter pour l'ENSAE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gwatkinson/projet-python-twitter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
