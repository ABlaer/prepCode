from setuptools import setup, find_packages

setup(
    name='prepCode',
    version='1.2',
    install_requires=['numpy', 'obspy', 'pandas', 'glob', 'matplotlib'],
    url='www.github.com/ABlaer',
    license='MIT',
    author='almogblaer',
    author_email='blaer@post.bgu.ac.il',
    description='Preparation code for synthetic seismic data, that mimics real ones',
    python_requires='>3'
)

