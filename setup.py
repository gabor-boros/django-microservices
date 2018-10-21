from distutils.core import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="djangomicroservices",
    version="0.1.2",
    author="Gabor Boros",
    author_email="gabor.brs@gmail.com",
    license='MIT',
    description="Simple django package to easily connect microservices.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/gabor-boros/django-microservices',
    packages=[
        'microservices',
        'microservices.management',
        'microservices.management.commands',
        'microservices.migrations'
    ],
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
