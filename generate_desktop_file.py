#!/usr/bin/env python3

# -*- coding: utf-8;mode: python -*-

# python stuff
import os
import gettext

HUBIC_L10N_PATH = './po'

def write_key(lnfile, key, value):
    for l18ndir in os.listdir(HUBIC_L10N_PATH):
        if l18ndir == 'hubic-gtk.pot':
            continue

        loc_lang = gettext.translation('hubic-gtk', localedir=HUBIC_L10N_PATH, languages=[l18ndir])
        loc_lang.install()
        lnfile.write("{0}[{1}]={2}\n".format(key, l18ndir, loc_lang.gettext(value)))


with open('./hubic-gtk.desktop', 'w') as lnfile:
    lnfile.write("[Desktop Entry]\n")

    loc_lang = gettext.translation('hubic-gtk', localedir=HUBIC_L10N_PATH, languages=['en_US'])
    loc_lang.install()
    lnfile.write("Name={}\n".format(_('HubicGTK')))
    lnfile.write("GenericName={}\n".format(_('Network Storage')))
    lnfile.write("Comment={}\n".format(_('hubiC is an online storage platform provided by OVH. This is a status icon for it.')))

    write_key(lnfile, 'Name', 'HubicGTK')
    write_key(lnfile, 'GenericName', 'Network Storage')
    write_key(lnfile, 'Comment', 'hubiC is an online storage platform provided by OVH. This is a status icon for it.')

    lnfile.write("""Exec=hubic-gtk
Icon=/usr/share/icons/hicolor/128x128/hubic.png
Terminal=false
Type=Application
Categories=Network;
StartupNotify=false
""")
