import codecs
import os
import io
import sys
import re
import setuptools
from distutils.version import LooseVersion
import argparse
import pprint
import jinja2


LIB_PARENT_DIR = os.path.join('..', 'src')
HERE = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, LIB_PARENT_DIR)

parser = argparse.ArgumentParser(description='Deployment script')

def module_type(value):
    module = __import__(value)

    # Verify lib exists in ../src directory
    if not os.path.exists(os.path.join(LIB_PARENT_DIR, value)):
        raise argparse.ArgumentTypeError(
            "library '{lib}' cannot be found in folder '{parent}'".format(
                lib=value, parent=LIB_PARENT_DIR,
            )
        )

    # Verify imported module is that in ../src/{module name} (even if referenced by symlink)
    module_filename = module.__file__
    local_filename = os.path.join(
        LIB_PARENT_DIR, value, os.path.basename(module_filename)
    )
    if os.stat(module_filename).st_ino != os.stat(local_filename).st_ino:
        raise argparse.ArgumentTypeError(
            "imported '{lib}' lib is not local".format(module.__name__)
        )

    # Verify __name__ is equal to the containing folder's name
    if module.__name__ != value:
        raise argparse.ArgumentTypeError(
            "imported {lib!r} but the __name__ of '{name}' is invalid, expecting {expected}".format(
                lib=module, name=module.__name__, expected=value,
            )
        )

    # Verify module is ready for release
    if getattr(module, '__release_ready__', True) != True:
        raise argparse.ArgumentTypeError(
            "library '{lib}' is not ready for release".format(lib=value)
        )

    return module

parser.add_argument(
    '--lib', dest='lib', type=module_type, default=module_type('cqparts'),
    help='library being deployed',
)

args = parser.parse_args()


PACKAGES = setuptools.find_packages(
    where=LIB_PARENT_DIR,
    include=(args.lib.__name__, args.lib.__name__ + '.*'),
)
CLASSIFIERS = [
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
    #"Development Status :: ???"  added later
]

# pre-requisite packages, get from library's requirements.txt file
INSTALL_REQUIRES = []
requirements_filename = os.path.join(LIB_PARENT_DIR, args.lib.__name__, 'requirements.txt')
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
    return codecs.open(os.path.join(HERE, *parts), "rb", "utf-8").read()


# Development Status Classifier
VERSION_CLASSIFIER_MAP = [
    (LooseVersion('0.1'), "Development Status :: 2 - Pre-Alpha"),
    (LooseVersion('0.2'), "Development Status :: 3 - Alpha"),
    (LooseVersion('0.3'), "Development Status :: 4 - Beta"),
    (LooseVersion('1.0'), "Development Status :: 5 - Production/Stable"),
]

def version_classifier(version_str):
    """
    Verify version consistency:
    version number must correspond to the correct "Development Status" classifier
    :raises: ValueError if error found, but ideally this function does nothing
    """
    # cast version
    version = LooseVersion(version_str)

    for (test_ver, classifier) in reversed(sorted(VERSION_CLASSIFIER_MAP, key=lambda x: x[0])):
        if version >= test_ver:
            return classifier

    raise ValueError("could not find valid 'Development Status' classifier for v{}".format(version_str))

CLASSIFIERS.append(version_classifier(args.lib.__version__))


# ------- Mainline --------

def setup_standin(**kwargs):
    # Used instead of `setuptools.setup`;
    # Write a clean `setup.py` file to execute or building & installation.
    #
    # "Why on earth are you doing this?" I hear you ask:
    # "That's a fair question" I reply...
    #
    #   originally this *was* the `setup.py` file used to *build* the distrubution files.
    #   However, I have since learnt is that the `setup.py` file itself is
    #   distributed with the build module(s). It is used to *install* the library on
    #   each end-user's system.
    #
    #   I think you'll agree that the above code has no place on an end-user's
    #   system; it's highly reliant on it being executed from inside this repository.
    #
    #   Therefore, I've chosen to serialize the kwargs designed for `setuptools.setup`
    #   and write them to a very simple `setup.py` file.
    #   Normally I abhor unnecessarily generating code to execute, but I believe,
    #   in this case, it's necessary to keep deployment clean.

    params_str = pprint.PrettyPrinter(indent=2).pformat(kwargs)
    with open('setup.py.jinja', 'r') as tmp, open(os.path.join(LIB_PARENT_DIR, 'setup.py'), 'w') as output:
        template = jinja2.Template(tmp.read())
        output.write(template.render(params=params_str))


#setuptools.setup(
setup_standin(
    name=args.lib.__name__,
    description=args.lib.__description__,
    license=args.lib.__license__,
    url=args.lib.__url__,
    version=args.lib.__version__,
    author=args.lib.__author__,
    author_email=args.lib.__email__,
    maintainer=args.lib.__author__,
    maintainer_email=args.lib.__email__,
    keywords=args.lib.__keywords__,
    long_description=io.open(
        os.path.join(LIB_PARENT_DIR, args.lib.__name__, 'README.rst'),
        encoding='utf-8',
    ).read(),
    packages=PACKAGES,
    #package_dir={'': LIB_PARENT_DIR},
    package_data={'': ['LICENSE']},
    zip_safe=False,
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    scripts=SCRIPTS,
)
