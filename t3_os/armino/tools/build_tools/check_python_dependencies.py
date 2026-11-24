#!/usr/bin/env python

import argparse
import os
import re
import sys

try:
    from importlib import metadata as importlib_metadata
except ImportError:
    importlib_metadata = None

try:
    import pkg_resources
except Exception:
    pkg_resources = None

try:
    from packaging.requirements import Requirement as PackagingRequirement
    from packaging.version import Version as PackagingVersion
except Exception:
    PackagingRequirement = None
    PackagingVersion = None

if importlib_metadata is None and pkg_resources is None:
    print('Neither importlib.metadata nor pkg_resources can be imported. '
          'Please refer to the Get Started section of the BEKEN-ARMINO Programming Guide for '
          'setting up the required packages.')
    sys.exit(1)


def _version_tuple(version_str):
    parts = [int(p) for p in re.findall(r'\d+', version_str)]
    return tuple(parts) if parts else (0,)


def _check_specifier(installed, spec_str):
    for part in spec_str.split(','):
        part = part.strip()
        if not part:
            continue
        match = re.match(r'^(==|!=|>=|<=|~=|>|<)\s*(.+)$', part)
        if not match:
            continue
        op, target = match.group(1), match.group(2).strip()
        lhs, rhs = _version_tuple(installed), _version_tuple(target)
        width = max(len(lhs), len(rhs))
        lhs += (0,) * (width - len(lhs))
        rhs += (0,) * (width - len(rhs))
        if op == '==' and lhs != rhs:
            return False
        if op == '!=' and lhs == rhs:
            return False
        if op == '>=' and lhs < rhs:
            return False
        if op == '<=' and lhs > rhs:
            return False
        if op == '>' and lhs <= rhs:
            return False
        if op == '<' and lhs >= rhs:
            return False
        if op == '~=':
            prefix = _version_tuple(target)[:-1]
            if lhs < rhs or lhs[:len(prefix)] != prefix:
                return False
    return True


def _require_line(line):
    if importlib_metadata is not None:
        if PackagingRequirement is not None:
            req = PackagingRequirement(line)
            if req.marker is not None and not req.marker.evaluate():
                return
            installed = importlib_metadata.version(req.name)
            if req.specifier and not req.specifier.contains(PackagingVersion(installed), prereleases=True):
                raise ValueError('Version mismatch')
            return
        base = line.split(';', 1)[0].strip()
        match = re.match(r'^([A-Za-z0-9_.-]+)(?:\[[^\]]*\])?\s*(.*)$', base)
        if not match:
            raise ValueError('Invalid requirement')
        name, spec = match.group(1), match.group(2).strip()
        installed = importlib_metadata.version(name)
        if spec and not _check_specifier(installed, spec):
            raise ValueError('Version mismatch')
        return
    pkg_resources.require(line)


def escape_backslash(path):
    if sys.platform == "win32":
        # escaped backslashes are necessary in order to be able to copy-paste the printed path
        return path.replace("\\", "\\\\")
    else:
        return path


if __name__ == "__main__":
    armino_path = os.getenv("ARMINO_PATH")

    default_requirements_path = os.path.join(armino_path, 'requirements.txt')

    parser = argparse.ArgumentParser(description='BEKEN-ARMINO Python package dependency checker')
    parser.add_argument('--requirements', '-r',
                        help='Path to the requirements file',
                        default=default_requirements_path)
    args = parser.parse_args()

    not_satisfied = []
    with open(args.requirements) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('file://'):
                line = os.path.basename(line)
            if line.startswith('-e') and '#egg=' in line:  # version control URLs, take the egg= part at the end only
                line = re.search(r'#egg=([^\s]+)', line).group(1)
            elif line.startswith('-'):
                continue
            try:
                _require_line(line)
            except Exception:
                not_satisfied.append(line)

    if len(not_satisfied) > 0:
        print('The following Python requirements are not satisfied:')
        for requirement in not_satisfied:
            print(requirement)
        if os.path.realpath(args.requirements) != os.path.realpath(default_requirements_path):
            # we're using this script to check non-default requirements.txt, so tell the user to run pip
            print('Please check the documentation for the feature you are using, or run "%s -m pip install -r %s"' % (sys.executable, args.requirements))
        elif os.environ.get('ARMINO_PYTHON_ENV_PATH'):
            # We are running inside a private virtual environment under ARMINO_TOOLS_PATH,
            # ask the user to run install.bat again.
            if sys.platform == "win32" and not os.environ.get("MSYSTEM"):
                install_script = 'install.bat'
            else:
                install_script = 'install.sh'
            print('To install the missing packages, please run "%s"' % os.path.join(armino_path, install_script))
        elif sys.platform == "win32" and os.environ.get("MSYSTEM", None) == "MINGW32" and "/mingw32/bin/python" in sys.executable:
            print("The recommended way to install a packages is via \"pacman\". Please run \"pacman -Ss <package_name>\" for"
                  " searching the package database and if found then "
                  "\"pacman -S mingw-w64-i686-python-<package_name>\" for installing it.")
            print("NOTE: You may need to run \"pacman -Syu\" if your package database is older and run twice if the "
                  "previous run updated \"pacman\" itself.")
            print("Please read https://github.com/msys2/msys2/wiki/Using-packages for further information about using "
                  "\"pacman\"")
            # Special case for MINGW32 Python, needs some packages
            # via MSYS2 not via pip or system breaks...
            for requirement in not_satisfied:
                if requirement.startswith('cryptography'):
                    print("WARNING: The cryptography package have dependencies on system packages so please make sure "
                          "you run \"pacman -Syu\" followed by \"pacman -S mingw-w64-i686-python{}-cryptography\"."
                          "".format(sys.version_info[0],))
                    continue
                elif requirement.startswith('setuptools'):
                    print("Please run the following command to install MSYS2's MINGW Python setuptools package:")
                    print("pacman -S mingw-w64-i686-python-setuptools")
                    continue
        else:
            print('Please follow the instructions found in the "Set up the tools" section of '
                  'BEKEN-ARMINO Getting Started Guide')

        print('Diagnostic information:')
        armino_python_env_path = os.environ.get('ARMINO_PYTHON_ENV_PATH')
        print('    ARMINO_PYTHON_ENV_PATH: {}'.format(armino_python_env_path or '(not set)'))
        print('    Python interpreter used: {}'.format(sys.executable))
        if not armino_python_env_path or armino_python_env_path not in sys.executable:
            print('    Warning: python interpreter not running from ARMINO_PYTHON_ENV_PATH')
            print('    PATH: {}'.format(os.getenv('PATH')))
        sys.exit(1)

    print('Python requirements from {} are satisfied.'.format(args.requirements))
