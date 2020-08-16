# eyl.io AUR

A personal Arch Linux User Repository

## Description

Most packages match the ones in the offical AUR. Some are stripped down
versions for my own use (`sabnzbd`). I have a few official AUR packages
including:

- `dynamorio`
- `emacs-async`
- `emacs-evil`
- `emacs-helm`
- `emacs-helm-ls-git`
- `emacs-rust-mode`
- `emacs-undo-tree`
- `emacs-yasnippet`
- `pin`
- `python-pluginloader`

## Usage

If you would like to use this repository, add the following to `/etc/pacman.conf`:

    [eyl]
    SigLevel = Required
    Server = https://eyl.io/media/aur/$arch

All packages are signed with `3245467889B6B0C31B668D764D47368BD660A1C7`. You'll
likely need the following commands:

    sudo pacman-key -r 3245467889B6B0C31B668D764D47368BD660A1C7
    sudo pacman-key --lsign-key 3245467889B6B0C31B668D764D47368BD660A1C7

There is also a [web interface](https://eyl.io/aur/) with the latest updates.

## Manager

    python -m aur_manager -h
