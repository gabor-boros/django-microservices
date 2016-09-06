from distutils.core import setup

setup(
    name='djangomicroservices',
    version='0.1.0',
    url='https://github.com/gabor-boros/django-microservices',
    download_url='https://github.com/gabor-boros/django-microservices',
    license='MIT',
    author='Boros Gabor',
    author_email='gabor.brs@gmail.com',
    description='',
    packages=[
        'microservices',
        'microservices.management',
        'microservices.management.commands',
        'microservices.migrations'
    ],
)
