import sys
from setuptools import setup, find_packages

try:
    # Work around a traceback on Python < 2.7.4 and < 3.3.1
    # http://bugs.python.org/issue15881#msg170215
    import multiprocessing  # unused
except ImportError:
    pass

SRC_DIR = 'src'


def get_version():
    sys.path[:0] = [SRC_DIR]
    return __import__('color_ssh').__version__


setup(
    name='color-ssh',
    version=get_version(),
    description='Runs remote commands, colorfully.',
    author='mogproject',
    author_email='mogproj@gmail.com',
    license='Apache 2.0 License',
    url='https://github.com/mogproject/color-ssh',
    install_requires=[
    ],
    tests_require=[
        'six',
        'mog-commons >= 0.2.2',
    ],
    package_dir={'': SRC_DIR},
    packages=find_packages(SRC_DIR),
    include_package_data=True,
    test_suite='tests',
    entry_points="""
    [console_scripts]
    color-ssh = color_ssh.color_ssh:main
    color-cat = color_ssh.color_cat:main
    """,
)
