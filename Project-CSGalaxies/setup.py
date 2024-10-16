from setuptools import setup, find_packages

setup(
    name="project_csgalaxies",
    version="0.1.0",
    description="Análise de dados do MaNGA com API Marvin",
    author="Gregory Peruzzo Fiel, Marina Trevisan",
    author_email="gregory.fiel@ufrgs.br",
    url="https://github.com/gregoryfiel/Extragalactic-Astrophysics",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "numpy",
        "marvin"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
