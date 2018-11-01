#!/usr/bin/env python
#
# Copyright 2014 Jon Eyolfson
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from subprocess import call

if len(sys.argv) == 1:
    print("Arguments required")
    exit(2)

PKG_EXTENSION = '.pkg.tar.xz'
ARCHS = ('i686', 'x86_64', 'armv7h')

def pkg_split(s):
    return s[:-len(PKG_EXTENSION)].rsplit(sep='-', maxsplit=3)

AUR_DIR = os.path.join(os.environ['HOME'], 'aur')
print('Mounting', AUR_DIR)
if not os.path.isdir(AUR_DIR):
    os.mkdir(AUR_DIR)
call(['sshfs', 'eyl.io:/srv/http/eyl/media/aur', AUR_DIR])

for arg in sys.argv[1:]:
    for arch in ARCHS:
        arch_dir = os.path.join(AUR_DIR, arch)
        for filename in os.listdir(arch_dir):
            if not filename.endswith(PKG_EXTENSION):
                continue
            pkg_name, pkg_ver, pkg_rel, pkg_arch = pkg_split(filename)
            if not pkg_name == arg:
                continue
            pkg_path = os.path.join(arch_dir, filename)
            sig_path = os.path.join(arch_dir, '{}.sig'.format(filename))
            if not os.path.exists(sig_path):
                print(arg, 'missing signature')
                continue
            print("Removing", pkg_name, pkg_arch)
            call(['repo-remove', '-s', '-v', 'eyl.db.tar.gz', pkg_name],
                 cwd=arch_dir)
            os.remove(pkg_path)
            os.remove(sig_path)
            call(['ssh', 'site-eyl@eyl.io', 'aursetunavailable', pkg_name, pkg_arch])

call(['fusermount3', '-u', AUR_DIR])
os.rmdir(AUR_DIR)
