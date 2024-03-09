from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
        name="disco-tie",
        version="0.0.1",
        description="A sound reactive light up tie, built using a raspberry pi and individually addressible LEDs",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/RedMoikle/disco-tie/",
        author="Michael Stickler",
        author_email="mgs.tech.art@gmail.com",
        license="GNU GENERAL PUBLIC",
        install_requires=[
            "gpiozero",
            "rpi_ws281x",
        ],
        packages=find_packages(where="src")
)
