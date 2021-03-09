import setuptools


def get_version():
    exec(open("privpurge/version.py").read(), locals())
    return locals()["__version__"]


def get_requirements():
    with open("requirements.txt") as f:
        lines = f.read()

    lines = lines.strip().split("\n")
    return lines


name = "privpurge"

version = get_version()

description = "Purging privacy regions from collected data."

python_requires = ">=3.8"

packages = ["privpurge"]

install_requires = get_requirements()

setuptools.setup(
    name=name,
    version=version,
    description=description,
    python_requires=python_requires,
    packages=packages,
    install_requires=install_requires,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "privpurge = privpurge.__main__:main",
        ],
    },
)
