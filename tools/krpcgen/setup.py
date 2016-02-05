from setuptools import setup
import sys
import os

# Dirty hack to make setuptools use file copies instead of hardlinks which do not play well with Bazel
# http://bugs.python.org/issue8876
if os.getenv('BAZEL_BUILD') and hasattr(os, 'link'):
    del os.link

dirpath = os.path.dirname(os.path.realpath(__file__))
if not os.path.exists(os.path.join(dirpath, 'VERSION.txt')):
    dirpath = os.getcwd()

install_requires=['krpc', 'jinja2']
setup(
    name='krpcgen',
    version=open(os.path.join(dirpath, 'VERSION.txt')).read().strip(),
    author='djungelorm',
    author_email='djungelorm@users.noreply.github.com',
    url='https://djungelorm.github.io/krpc/docs',
    license='GNU GPL v3',
    description='Tool for generating service code for kRPC clients',
    long_description=open(os.path.join(dirpath, 'README.txt')).read(),
    packages=['krpcgen'],
    entry_points={'console_scripts': ['krpcgen = krpcgen.main:main']},
    package_data={'': ['*.txt', '*.tmpl', 'bin/*.exe', 'bin/*.dll', 'bin/*.xml']},
    install_requires=install_requires,
    use_2to3=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Topic :: Communications',
        'Topic :: Games/Entertainment :: Simulation',
        'Topic :: Internet'
    ]
)