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
from subprocess import call

skipped = {'packer', 'oh-my-zsh-git', 'sabnzbd', 'sickbeard-master-git'}
for d in os.listdir('.'):
    if not os.path.isdir(d):
        continue
    if d.startswith('.'):
        continue
    if d in skipped:
        continue
    call(['rm', '-f', '-r', d])
    call(['packer', '-G', d])
    call(['rm', '-f', '{}.tar.gz'.format(d)])
