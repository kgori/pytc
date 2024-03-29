#!/usr/bin/env python

__all__ = [
    'basename',
    'can_locate',
    'can_open',
    'delete',
    'gpickle',
    'gunpickle',
    'join_path',
    'locate_by_dir',
    'locate_by_env',
    'locate_file',
    'path_to',
    'subprocess',
    'syscall',
    'verify',
    ]

import bz2
import cPickle
import glob
import gzip
import os
from subprocess import Popen, PIPE
from ..errors.errors import filecheck, directorycheck


def basename(filename, strip_ext=False):
    fname = os.path.basename(filename)
    if strip_ext:
        fname = os.path.splitext(fname)[0]
    return fname


def can_locate(filename):
    return (os.path.isfile(filename) if filename else False)


def can_open(directory):
    return (os.path.isdir(directory) if directory else False)


def delete(filename):
    return os.remove(filecheck(filename))


def freader(filename, gz=False, bz=False):
    """ Returns a filereader object that can handle gzipped input """

    filecheck(filename)
    if filename.endswith('gz'):
        gz = True
    elif filename.endswith('bz2'):
        bz = True

    if gz:
        return gzip.open(filename, 'rb')
    elif bz:
        return bz2.BZ2File(filename, 'r')
    else:
        return open(filename, 'r')


def fwriter(filename, gz=False, bz=False):
    """ Returns a filewriter object that can write plain or gzipped output"""

    if filename.endswith('gz'):
        gz = True
    elif filename.endswith('bz2'):
        bz = True
    if gz:
        return gzip.open(filename, 'wb')
    elif bz:
        return bz2.BZ2File(filename, 'w')
    else:
        return open(filename, 'w')


def glob_by_extensions(directory, extensions):
    """ Returns files matched by all extensions in the extensions list """
    directorycheck(directory)
    files = []
    xt = files.extend
    for ex in extensions:
        xt(glob.glob('{0}/*.{1}'.format(directory, ex)))
    return files


def gpickle(obj, filename):

    if not filename.endswith('.gz'):
        filename += '.gz'
    cPickle.dump(obj, file=gzip.open(filename, 'wb'), protocol=-1)


def gunpickle(filename):

    return cPickle.load(gzip.open(filename, 'rb'))


def head(filename, n=10):
    """ prints the top `n` lines of a file """
    with freader(filename) as fr:
        for _ in range(n):
            print fr.readline().strip()
            

def join_path(*elements):
    return os.path.join(*elements)


def locate_by_env(filename, path=None):
    path = os.getenv(path) or os.getenv('PATH', os.defpath)
    for directory in path.split(os.pathsep):
        if verify(filename, directory):
            print directory
            return os.path.abspath(directory)
        f = locate_by_dir(filename, directory)
        if f:
            return os.path.abspath(f)


def locate_by_dir(filename, directory=None):
    f = os.path.join(directory, filename)
    return (os.path.abspath(f) if can_locate(f) else None)


def locate_file(filename, env_var='', directory=''):
    f = locate_by_env(filename, env_var) or locate_by_dir(filename, directory)
    return (os.path.abspath(f) if can_locate(f) else None)


def path_to(filename):
    return os.path.dirname(filename)


def subprocess(cmd):
    process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    return process.communicate()


def syscall(cmd):
    return os.system(cmd)


def verify(filename, path):
    return can_locate(path) and os.path.basename(path) == filename
