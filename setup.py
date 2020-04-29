import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="outlier_detector",
    version="0.0.3",
    author="Fabio Veronese",
    author_email="fveronese85@gmail.com",
    description="Minimal tool for outliers detection on small samples set",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/docet85/outlier_detector",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
)
