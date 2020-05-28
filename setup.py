from setuptools import setup, find_packages

setup(
    name='dinopass',
    description='DinoPass - Simple CLI Password Manager',
    version='0.1',
    author='Alexandru Grajdeanu',
    author_email='grajdeanu.alex@gmail.com',
    packages=['dinopass'],
    package_data={},
    python_requires='>=3.6.0',
    install_requires=['SQLAlchemy', 'psycopg2-binary', 'rich', 'click'],
    entry_points={
        'console_scripts': ['dinopass=dinopass.cli:start']
    }
)
