import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rtcwlog-donkz",
    version="1.0.0",
    author="rtcw-na-donkz",
    author_email="donkanator@hotmail.com",
    description="Process RTCW game logs. Get html reports and fancy datasets!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/donkz/RTCW-stats-py-sci",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)