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
import shutil
from subprocess import call

PKG_EXTENSION = '.pkg.tar.xz'
ARCHS = ('i686', 'x86_64', 'armv7h')

def pkg_split(s):
    return s[:-len(PKG_EXTENSION)].rsplit(sep='-', maxsplit=3)

pkgs_added = []
BASE_DIR = os.path.dirname(__file__)
for pkg_name in os.listdir(BASE_DIR):
    pkg_dir = os.path.join(BASE_DIR, pkg_name)
    if not os.path.isdir(pkg_dir):
        continue
    if pkg_name.startswith('.'):
        continue
    if pkg_name == 'aur.archlinux.org':
        continue
    pkg_filename = None
    for filename in os.listdir(pkg_dir):
        if filename.endswith(PKG_EXTENSION):
            if not pkg_filename:
                pkg_filename = filename
            else:
                print(pkg_name, 'has more than one pkg')
                exit(1)
    if not pkg_filename:
        continue
    if not os.path.exists(os.path.join(pkg_dir, '{}.sig'.format(pkg_filename))):
        print(pkg_name, 'missing signature')
        exit(2)
    pkgs_added.append((pkg_dir, pkg_filename))

AUR_DIR = os.path.join(os.environ['HOME'], 'aur')
print('Syncing', AUR_DIR)
if not os.path.isdir(AUR_DIR):
    os.mkdir(AUR_DIR)
call(['sshfs', 'eyl.io:/srv/http/eyl/media/aur', AUR_DIR])

for pkg_dir, pkg_filename in pkgs_added:
    pkg_name, pkg_ver, pkg_rel, pkg_arch = pkg_split(pkg_filename)
    aur_pkg_dir = os.path.join(AUR_DIR, pkg_arch)
    for filename in os.listdir(aur_pkg_dir):
        if not filename.endswith(PKG_EXTENSION):
            continue
        aur_pkg_name = pkg_split(filename)[0]
        if pkg_name == aur_pkg_name:
            aur_pkg_path = os.path.join(aur_pkg_dir, filename)
            aur_pkg_sig_path = aur_pkg_path + '.sig'
            print('Removing', aur_pkg_path)
            os.remove(aur_pkg_path)
            print('Removing', aur_pkg_sig_path)
            os.remove(aur_pkg_sig_path)
            if pkg_arch == 'any':
                for arch in ARCHS:
                    aur_pkg_path = os.path.join(AUR_DIR, arch, filename)
                    aur_pkg_sig_path = aur_pkg_path + '.sig'
                    print('Removing', aur_pkg_path)
                    os.remove(aur_pkg_path)
                    print('Removing', aur_pkg_sig_path)
                    os.remove(aur_pkg_sig_path)
    pkg_path = os.path.join(pkg_dir, pkg_filename)
    pkg_sig_path = pkg_path + '.sig'
    print('Moving', pkg_path)
    shutil.move(pkg_path, aur_pkg_dir)
    print('Moving', pkg_sig_path)
    shutil.move(pkg_sig_path, aur_pkg_dir)
    if pkg_arch != 'any':
        call(['repo-add', '-s', '-v', 'eyl.db.tar.xz', pkg_filename], cwd=aur_pkg_dir)
    else:
        path = '../any/' + pkg_filename
        sig_path = path + '.sig'
        for arch in ARCHS:
            aur_pkg_dir = os.path.join(AUR_DIR, arch)
            aur_pkg_path = os.path.join(aur_pkg_dir, pkg_filename)
            aur_pkg_sig_path = aur_pkg_path + '.sig'
            print('Symlinking', aur_pkg_path)
            os.symlink(path, aur_pkg_path)
            print('Symlinking', aur_pkg_sig_path)
            os.symlink(sig_path, aur_pkg_sig_path)
            call(['repo-add', '-s', '-v', 'eyl.db.tar.xz', pkg_filename],
                 cwd=aur_pkg_dir)
    call(['ssh', 'site-eyl@eyl.io', 'aurcreateupdate', pkg_name,
          '{}-{}'.format(pkg_ver, pkg_rel), pkg_arch])

call(['fusermount3', '-u', AUR_DIR])
os.rmdir(AUR_DIR)
