import setuptools

setuptools.setup(
    name="chippy",
    version="0.0.1",
    author="Terence Norton",
    author_email="tjtnorton@gmail.com",
    description="A Chip8 / SCHIP emulator implemented in Python.",
    url="https://github.com/tjtnorton/chippy",
    packages=setuptools.find_packages(),
    install_requires=['pygame', 'opencv-python'],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
    ],
)