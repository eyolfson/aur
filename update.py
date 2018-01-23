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

skipped = {'sabnzbd', 'eyl-launcher', 'teensy-tools', 'emacs-async'}

vcs_package = {'oh-my-zsh', 'emacs-rust-mode', 'packer', 'firefox-pentadactyl', 'emacs-color-theme-solarized'}

for arg in sys.argv[1:]:
    skipped.add(arg)
for d in os.listdir('.'):
    if not os.path.isdir(d):
        continue
    if d.startswith('.'):
        continue
    if d == 'aur.archlinux.org':
        continue
    if d in skipped:
        continue
    print(d)
    if d.endswith('-git') or d.endswith('-hg') or d in vcs_package:
        call(['makepkg', '-o', '-d'], cwd=d)
        rc = call(['git', 'diff', '--exit-code'])
        if rc != 0:
            break
    else:
        call(['rm', '-f', '-r', d])
        call(['packer', '-G', d])
        call(['rm', '-f', '{}.tar.gz'.format(d)])
        call(['rm', '-f', '{}/.AURINFO'.format(d)])
        call(['rm', '-f', '{}/.SRCINFO'.format(d)])
        call(['rm', '-f', '{}/MKPKG'.format(d)])
        rc = call(['git', 'diff', '--exit-code'])
        if rc != 0:
            exit(0)
