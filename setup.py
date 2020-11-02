import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="assr-tools", # Replace with your own username
    version="1.0",
    author="Dominik Welke",
    author_email="dominik.welke@web.de",
    description="Frequency tagged auditory stimuli for ASSR experiments in PsychPy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dominikwelke/assr-tools",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'psychopy>=3',
        'arabic-reshaper'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)