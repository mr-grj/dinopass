from setuptools import setup, find_packages

setup(
    name='stuff',
    description='Simple CLI Password Manager',
    version='0.1',
    author='Alexandru Grajdeanu',
    author_email='grajdeanu.alex@gmail.com',
    packages=['stuff'],
    package_data={},
    python_requires='>=3.6.0',
    install_requires=['SQLAlchemy', 'psycopg2-binary', 'rich', 'click'],
    entry_points={
        'console_scripts': ['stuff=stuff.cli:start']
    }
)
