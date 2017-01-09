# eyl AUR

A personal Arch Linux User Repository

## Usage

If you would like to use this repository, add the following to `/etc/pacman.conf`:

    [eyl]
    SigLevel = Required
    Server = https://eyl.io/media/aur/$arch

All packages are signed with 0x4D47368BD660A1C7. You'll likely need the
following command:

    pacman-key --lsign-key 4D47368BD660A1C7

There is also a [web interface](https://eyl.io/aur/).
