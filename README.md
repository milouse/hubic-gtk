HubicGTK
========

About
-----

HubicGTK is a system tray icon for [hubiC](https://www.hubic.com),
the online storage service by OVH SAS.

It draws its inspiration from the bundled Dropbox system tray icon.

It is developped in pygtk, thus it depends on python2, gtk2, dbus, xdg
and notify bindings for python. It is released under the terms of the
[WTF Public License](http://www.wtfpl.net/)

Get it
------

The last version is 0.5.3. You can get it [here](https://projects.depar.is/hubic-gtk/raw/archlinux/hubic-gtk-0.5.3.tar.gz?name=a363b835a1)

Usage
-----

The program should run out of the box. Just type the following
commands:

    $ tar xzf hubic-gtk-x.x.x.tar.gz
    $ cd hubic-gtk
    $ ./hubic-gtk.py

If you want to install it system wide, you can use the provided
Makefile:

    $ sudo make

or

    $ make build
    $ su -
    # cd /previous/extracted/path
    # make install

And start it with the `hubic-gtk` command.

You can install it elsewhere if needed, just pass the target root as a
parameter to make. For example:

    $ make build DEST=~/.local
    $ make install DEST=~/.local
    $ .local/bin/hubic-gtk &

or

    $ make build DEST=/opt/hubic-gtk
    $ sudo make install DEST=/opt/hubic-gtk
    $ /opt/hubic-gtk/bin/hubic-gtk &


Configuration
-------------

HubicGTK use a per-user configuration file located in
`$XDG_CONFIG_HOME/hubiC/status_icon.conf`. It is a generic
[configuration file](https://en.wikipedia.org/wiki/Ini_file), which
follows this structure:

    [general]
    notify = True
    hubic_dir = ~/Hubic

    [much_secret_wow_not_see]
    encfs_config = ~/.config/.myhubicsecret.encfs6.xml
    encfs_passfile = ~/.config/.myhubicsecret.encfs.pass
    mount_point = ~/Private/Hubic

The `general` section refers to preferences of the status icon. Any
other section must refer to as many existing encfs containers.

The program does not depend on this per-user configuration file. If no
config file is found for the current user or if a configuration option
is missing in your configuration file, the program follows its default
rules, which are:

    [general]
    notify = False
    show_all_message = False
    file_browser = xdg-open {0}
    prefix_unit = binary

Your default `hubic_dir` is retrieved from dbus at first run.

### General section

- The **`notify`** option specifies if notification bubbles should be
  shown for each hubiC events. The default value is True, but as it
  may generate a lot of noise, you can set it to false to deactivate
  it.
  Please note it is an intended behaviour that the program still
  notify you about encfs events, even if this option is set to False.
  You can also set this option by toggling the `Show notification
  messages` checkbox in the `Last messages` submenu.
- The **`show_all_messages`** restrains the last messages submenu to the
  last 10 messages if it is set to False.
- The **`hubic_dir`** option specifies the path to your synchronized
  folder. This is an attempt to not make a dbus call when the
  programme start to find this path, as this single dbus call will
  consecutively start hubiC. If this option is not set, the first time
  the program ask hubiC to indicates its path, the later is saved for
  future usage and a configuration file is created if needed.
- The **`prefix_unit`** option specifies the file size unit used through
  the application. For now it could be `decimal` or anything else. In
  this last case, the fallback or default mode is [binary
  prefix](https://en.wikipedia.org/wiki/Binary_prefix).
- The **`file_browser`** option overwrite the default use of xdg_open to
  open parent folder of synchronised files appearing in the status
  messages.

### Encfs sections

As we lived in a world where citizen censorship and mass surveillance
is common, it is a good practice to crypt our private data. Many
different systems exist, like [TrueCrypt](http://www.truecrypt.org/)
or [EncFS](http://www.arg0.net/encfs). I chose to add encfs features
to this program as it is, at my sense, the most practical way to crypt
data on such cloud storage services.

By the way, the aim of HubicGTK is NOT to help you create encfs
container, but just to help you mounting these containers. To do so,
just add the correct sections to your configuration file and the
corresponding enfs volume will show up in the hubiC status menu.

The name of the configuration file's section must be the relative path
to your hubiC synchronised folder. Given `~/Hubic` being your hubiC
synchronized folder, if your encfs container is stored
in `~/Hubic/my_private_folder`, the section name must be
`[my_private_folder]`. If it is in `~/Hubic/Documents/very_secret`,
the section name must be `[Documents/very_secret]`.

For each of your encfs containers, the following options are
available:

- **`mount_point`**: the path to a folder, which will be used as a mount
  point. This folder must exist and must be empty.
- **`open_folder_at_mount`**: indicates if the program should open your
  private folder just after having mounted it or not. It uses
  `xdg-open` or the value of the `file_browser` option in the
  `general` section.
- **`encfs_config`**: the path to the encfs config file. It is good
  practice to store it anyway but NOT in a cloud synchronized
  place. If you want to share an encfs folder between two different
  devices, copy this file on an usb stick and put it somewhere in
  your profile directories.
- **`encfs_passphrase`**: the secret phrase to uncrypt your encfs
  container. Obviously this phrase will not be encrypted in the
  HubicGTK config file, so use it with big precaution.
- **`encfs_passfile`**: the path to a file containing only your encfs
  secret pass phrase. The file content must not be encrypted as its
  content is directly passed to the encfs command line. To enforce the
  security on this file, you can do a `chmod 600 mysecretfile` on it
  to prevent any other user of your computer to access its content.
- if neither a encfs_passphrase, nor an encfs_passfile option is
  present in your config file, HubicGTK will prompt you for a
  password each time you will mount an encfs container. It is the
  safer option if you do not want to keep your secret pass phrase
  written somewhere in your computer.

Here is a complete example of an encfs section, regarding a container
staying in `~/Hubic/much_secret_wow_not_see`:

    [much_secret_wow_not_see]
    encfs_config = ~/.config/.myhubicsecret.encfs6.xml
    encfs_passfile = ~/.config/.myhubicsecret.encfs.pass
    mount_point = ~/Private/Hubic


Contributions
-------------

All contributions are welcome. Just clone take the code and do WTF you
want with.

A special attention will be given to any translation help. You can
either:

- [download the main .pot file](http://projects.depar.is/hubic-gtk/raw/po/hubic-gtk.pot?name=tip) or
- ask to become member of [the project on transifex](https://www.transifex.com/projects/p/hubicstatus/) (all demands will be honoured)
