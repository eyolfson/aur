import argparse
import os
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST_DIR = os.path.join(BASE_DIR, 'host')
PERSONAL_DIR = os.path.join(BASE_DIR, 'personal')

ARCHS = ('x86_64', 'armv7h')
PKG_EXTENSION = '.pkg.tar.xz'

def pkg_split(s):
    return s[:-len(PKG_EXTENSION)].rsplit(sep='-', maxsplit=3)

def run_command(args, cwd=None, show_commands=False):
    kwargs = {'check': True}
    if cwd is not None:
        kwargs['cwd'] = cwd
    if show_commands:
        print('\x1b[1m{}\x1b[m'.format(' '.join(args)))
    else:
        kwargs['stderr'] = subprocess.DEVNULL
        kwargs['stdout'] = subprocess.DEVNULL
    return subprocess.run(args, **kwargs)

def host_mount(show_commands=False):
    if os.path.exists(HOST_DIR):
        return False

    os.mkdir(HOST_DIR)
    run_command(['sshfs', 'eyl.io:/srv/http/eyl/media/aur', HOST_DIR],
                show_commands=show_commands)
    return True

def host_umount(show_commands=False):
    if not os.path.exists(HOST_DIR):
        return

    run_command(['fusermount3', '-u', HOST_DIR],
                show_commands=show_commands)
    os.rmdir(HOST_DIR)

def add(package, show_commands=False):
    url = ('https://aur.archlinux.org/cgit/aur.git/snapshot'
           '/{}.tar.gz').format(package)
    wget_args = ['wget', url]
    run_command(wget_args, cwd=PERSONAL_DIR, show_commands=show_commands)

    package_snapshot = os.path.join(PERSONAL_DIR, '{}.tar.gz'.format(package))
    tar_args = ['tar', 'xzvf', package_snapshot]
    run_command(tar_args, cwd=PERSONAL_DIR, show_commands=show_commands)

    rm_args = ['rm', '-f', package_snapshot]
    run_command(rm_args, cwd=PERSONAL_DIR, show_commands=show_commands)

def find_package_files(directory, package=None):
    package_files = []
    for filename in os.listdir(directory):
        if not filename.endswith(PKG_EXTENSION):
            continue
        if package is not None:
            pkg_name = pkg_split(filename)[0]
            if package != pkg_name:
                continue
        pkg_file = os.path.join(directory, filename)
        sig_file = '{}.sig'.format(pkg_file)
        if not os.path.exists(sig_file):
            print('{} missing signature'.format(pkg_file))
            exit(1)
        package_files.append((pkg_file, sig_file))
    if package is not None:
        assert len(package_files) in [0, 1]
    return package_files

def remove(package, repo_remove=True, show_commands=False):
    mounted = host_mount(show_commands=show_commands)

    any_arch_dir = os.path.join(HOST_DIR, 'any')
    package_files = find_package_files(any_arch_dir, package=package)
    has_any_arch = len(package_files) == 1

    for arch in os.listdir(HOST_DIR):
        if arch == 'any':
            continue
        arch_dir = os.path.join(HOST_DIR, arch)
        arch_package_files = find_package_files(arch_dir, package=package)
        if len(arch_package_files) == 0:
            continue
        if repo_remove:
            run_command(['repo-remove', '-s', '-v', 'eyl.db.tar.xz', package],
                        cwd=arch_dir, show_commands=show_commands)
        if repo_remove and not has_any_arch:
            run_command(['ssh', 'site-eyl@eyl.io', 'aursetunavailable',
                         package, arch], show_commands=show_commands)
        package_files.extend(arch_package_files)

    if repo_remove and has_any_arch:
        run_command(['ssh', 'site-eyl@eyl.io', 'aursetunavailable',
                     package, 'any'], show_commands=show_commands)

    for pkg_file, sig_file in package_files:
        os.remove(pkg_file)
        os.remove(sig_file)
    if mounted:
        host_umount(show_commands=show_commands)

def sync(show_commands=False):
    package_files = []
    for pkg_name in os.listdir(PERSONAL_DIR):
        pkg_dir = os.path.join(PERSONAL_DIR, pkg_name)
        for entry in find_package_files(pkg_dir):
            package_files.append(entry)

    mounted = host_mount(show_commands=show_commands)

    for pkg_file, sig_file in package_files:
        pkg_dirname, pkg_basename = os.path.split(pkg_file)
        sig_basename = os.path.basename(sig_file)
        pkg_name, pkg_ver, pkg_rel, pkg_arch = pkg_split(pkg_basename)
        remove(pkg_name, repo_remove=False, show_commands=show_commands)
        pkg_arch_dir = os.path.join(HOST_DIR, pkg_arch)
        run_command(['mv', pkg_file, pkg_arch_dir], show_commands=show_commands)
        run_command(['mv', sig_file, pkg_arch_dir], show_commands=show_commands)
        if pkg_arch != 'any':
            run_command(['repo-add', '-s', '-v', 'eyl.db.tar.xz', pkg_basename],
                        cwd=pkg_arch_dir,
                        show_commands=show_commands)
        else:
            for arch in ARCHS:
                arch_dir = os.path.join(HOST_DIR, arch)
                run_command(['ln', '-s', '../any/{}'.format(pkg_basename),
                             pkg_basename],
                            cwd=arch_dir,
                            show_commands=show_commands)
                run_command(['ln', '-s', '../any/{}'.format(sig_basename),
                             sig_basename],
                            cwd=arch_dir,
                            show_commands=show_commands)
                run_command(['repo-add', '-s', '-v', 'eyl.db.tar.xz', pkg_basename],
                            cwd=arch_dir,
                            show_commands=show_commands)

        run_command(['ssh', 'site-eyl@eyl.io', 'aurcreateupdate', pkg_name,
                     '{}-{}'.format(pkg_ver, pkg_rel), pkg_arch],
                    show_commands=show_commands)
    if mounted:
        host_umount(show_commands=show_commands)

def main(args):
    parser = argparse.ArgumentParser(description='AUR Manager')
    parser.add_argument('--show-commands', action='store_true')
    parser.add_argument('action', choices=['add', 'remove', 'sync'])
    parser.add_argument('packages', nargs=argparse.REMAINDER)
    parsed_args = parser.parse_args()
    if parsed_args.action == 'add':
        for package in parsed_args.packages:
            add(package, show_commands=parsed_args.show_commands)
    elif parsed_args.action == 'remove':
        for package in parsed_args.packages:
            remove(package, repo_remove=True,
                   show_commands=parsed_args.show_commands)
    elif parsed_args.action == 'sync':
        sync(show_commands=parsed_args.show_commands)
