from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

install_requires = parse_requirements("requirements.in")

setup(
    name="Anwill Back Catalog & Platform",
    version='0.1.0',
    description="Дмитрий Иванюк | Backend Developer & DevOps",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="dmitrij-el",
    author_email="dmitrijelectro@gmail.com",
    url="https://github.com/dmitrij-el",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    license="",
    classifiers=[
    ],
    python_requires=">=3.12",
)
