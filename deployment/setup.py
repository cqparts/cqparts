import codecs
import os
import re
import setuptools
from distutils.version import LooseVersion
import argparse

LIB_PARENT_DIR = os.path.join('..', 'src')
HERE = os.path.abspath(os.path.dirname(__file__))

parser = argparse.ArgumentParser(description='Deployment script')

def lib_type(value):
    if not os.path.exists(os.path.join(LIB_PARENT_DIR, value)):
        raise argparse.ArgumentTypeError(
            "library '{lib}' cannot be found in folder '{parent}'".format(
                lib=value, parent=LIB_PARENT_DIR,
            )
        )

parser.add_argument(
    '--lib', dest='lib', type=lib_type, default=lib_type('cqparts'),
    help='library being deployed',
)

parser.add_argument(
    'script_args', metavar='arg', nargs='*',
    help='setuptools.setup sysv arguments',
)

args = parser.parse_args()


# Setup template thanks to: Hynek Schlawack
#   https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
###################################################################

PACKAGES = setuptools.find_packages(
    where=os.path.join('..', 'src'),
    include=(args.lib, args.lib + '.*'),
)
META_PATH = os.path.join('..', 'src', args.lib, '__init__.py')
CLASSIFIERS = [
    "Development Status :: 2 - Pre-Alpha",
    #"Development Status :: 3 - Alpha",  # see src/pygcode/__init__.py
    "Intended Audience :: Developers",
    "Intended Audience :: Manufacturing",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Natural Language :: English",
    "Operating System :: MacOS",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering",
    "Topic :: Multimedia :: Graphics :: 3D Modeling",
    "Topic :: Multimedia :: Graphics :: 3D Rendering",
]

# pre-requisite packages, get from library's requirements.txt file
INSTALL_REQUIRES = []
requirements_filename = os.path.join('..', 'src', args.lib, 'requirements.txt')
if os.path.exists(requirements_filename):
    with open(requirements_filename, 'r') as fh:
        INSTALL_REQUIRES = [
            l.rstrip('\n')
            for l in fh.readlines()
            if not re.search(r'^(.*#|\s*$)', l)  # invalid: contains #, or is a blank line
        ]

SCRIPTS = [
    # scripts callable from a standard shell upon package installation by end-user
    # (none)
]


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


META_FILE_CONTENT = read(META_PATH)

def find_meta(meta):
    match = re.search(
        r"""^__{meta}__\s*=\s*(?P<value>.*)$""".format(meta=meta),
        META_FILE_CONTENT,
        flags=re.MULTILINE,
    )
    if not match:
        raise RuntimeError("Unable to find __{name}__ string in '{file}'.".format(
            name=meta, file=META_PATH,
        ))
    return eval(match.group('value'))


def assert_version_classifier(version_str):
    """
    Verify version consistency:
    version number must correspond to the correct "Development Status" classifier
    :raises: ValueError if error found, but ideally this function does nothing
    """
    V = lambda v: LooseVersion(v)
    # cast version
    version = V(version_str)

    # get "Development  Status" classifier
    dev_status_list = [x for x in CLASSIFIERS if x.startswith("Development Status ::")]
    if len(dev_status_list) != 1:
        raise ValueError("must be 1 'Development Status' in CLASSIFIERS")
    classifier = dev_status_list.pop()

    version_map = [
        (V('0.1'), "Development Status :: 2 - Pre-Alpha"),
        (V('0.2'), "Development Status :: 3 - Alpha"),
        (V('0.3'), "Development Status :: 4 - Beta"),
        (V('1.0'), "Development Status :: 5 - Production/Stable"),
    ]

    for (test_ver, test_classifier) in reversed(sorted(version_map, key=lambda x: x[0])):
        if version >= test_ver:
            if classifier == test_classifier:
                return  # all good, now forget any of this ever happened
            else:
                raise ValueError("for version {ver} classifier should be \n'{good}'\nnot\n'{bad}'".format(
                    ver=str(version), good=test_classifier, bad=classifier
                ))


if __name__ == "__main__":

    version = find_meta("version")
    assert_version_classifier(version)

    setuptools.setup(
        name=args.lib,
        description=find_meta('description'),
        license=find_meta('license'),
        url=find_meta('url'),
        version=version,
        author=find_meta('author'),
        author_email=find_meta('email'),
        maintainer=find_meta('author'),
        maintainer_email=find_meta('email'),
        keywords=find_meta('keywords'),
        long_description=read('..', 'README.rst'),
        packages=PACKAGES,
        package_dir={'': LIB_PARENT_DIR},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        scripts=SCRIPTS,

        # argv's referenced by setuptools.setup
        script_name=os.path.basename(sys.argv[0]),  # sys.argv[0]
        script_args=args.script_args,  # sys.argv[:1]
    )
