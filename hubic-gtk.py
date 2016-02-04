#!/usr/bin/env python2
# -*- coding: utf-8;mode: python -*-

# python stuff
import os
import pwd
import time
import shlex
import subprocess
import ConfigParser

# other stuff
import gtk
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import pynotify
from xdg.BaseDirectory import xdg_config_home

HUBIC_ICONS_PATH = os.path.dirname(os.path.realpath(__file__))
HUBIC_STATUS_VERSION = 'dev'
HUBIC_L10N_PATH = './po'

import gettext
gettext.install('hubic-gtk', HUBIC_L10N_PATH)

HUBIC_POSSIBLE_STATUS = {
    'Idle': _('Idle'),
    'Busy': _('Busy'),
    'Paused': _('Paused'),
    'Connecting': _('Connecting'),
    'NotConnected': _('NotConnected'),
    'Synchronized': _('Synchronized'),
    'Unsynchronized': _('Unsynchronized'),
    'NoStatus': _('NoStatus'),
    'Error': _('Error'),
    'Starting': _('Starting'),
    'Killed': _('Killed')
}

def get_bool_conf_option(config, section, option):
    if config.has_option(section, option):
        v = config.get(section, option)
        return str(v).lower() in ('yes', 'true', 't', '1')
    return False


class FileFolderHelper:
    def __init__(self, config, hubic_dir):
        self.config = config
        self.hubic_dir = hubic_dir

        self.folder_opener = 'xdg-open {0}'
        if self.config.has_section('general') and self.config.has_option('general', 'file_browser'):
            self.folder_opener = self.config.get('general', 'file_browser')


    def set_hubic_dir(self, hubic_dir):
        self.hubic_dir = hubic_dir


    def open_folder(self, path):
        raw_argv = shlex.split(self.folder_opener.format(path))
        subprocess.Popen(raw_argv)
        # os.spawnvp(os.P_NOWAIT, raw_argv[0], raw_argv)


    def crunch_path(self, file_path):
        if self.hubic_dir != '' and file_path[:len(self.hubic_dir)] == self.hubic_dir:
            file_path = file_path[len(self.hubic_dir):]

            if file_path[0] != '/':
                file_path = '/' + file_path

            if len(file_path) > 60:
                file_path = file_path[:30] + ' (...) ' + file_path[-30:]

            return '[HubicRoot]' + file_path

        return file_path


    def format_task(self, work, crunch = False):
        workfile = work[1]
        if crunch:
            workfile = self.crunch_path(workfile)
        else:
            workfile = os.path.basename(work[1])

        if work[4] != -1 and work[5] != -1:
            completness = round((work[4] * 100.0) / work[5], 1)
            return '{0} ({1}%)'.format(workfile, completness)

        return workfile


    def file_size(self, file_size):
        # I know that 1byte != 1octet, but here it makes sense... so
        # Number used for conversion come from https://fr.wikipedia.org/wiki/Octet
        # default prefix_unit is 'binary'
        kilo_unit = 1024.0
        kilo_symbol = 'Kio'
        mega_unit = 1048576.0
        mega_symbol = 'Mio'
        giga_unit = 1073741824.0
        giga_symbol = 'Gio'
        tera_unit = 1099511627776.0
        tera_symbol = 'Tio'

        if self.config.has_section('general') and self.config.has_option('general', 'prefix_unit'):
            if self.config.get('general', 'prefix_unit') == 'decimal':
                kilo_unit = float(1e3)
                kilo_symbol = 'Ko'
                mega_unit = float(1e6)
                mega_symbol = 'Mo'
                giga_unit = float(1e9)
                giga_symbol = 'Go'
                tera_unit = float(1e12)
                tera_symbol = 'To'

        if file_size >= tera_unit:
            used_gibi = round(file_size / tera_unit, 2)
            used_unit = tera_symbol
        elif file_size >= giga_unit:
            used_gibi = round(file_size / giga_unit, 2)
            used_unit = giga_symbol
        elif file_size >= mega_unit:
            used_gibi = round(file_size / mega_unit, 2)
            used_unit = mega_symbol
        else:
            used_gibi = round(file_size / kilo_unit, 2)
            used_unit = kilo_symbol

        return (used_gibi, used_unit)



class EncfsMenu:
    def __init__(self, config, hubic_dir):
        self.config = config
        self.hubic_dir = hubic_dir


    def build_menu(self, menu):
        encfs_repos = self.config.sections()
        if len(encfs_repos) > 1:
            encfs_menu = gtk.Menu()

            for sec in self.config.sections():
                if sec != 'general' and self.config.has_option(sec, 'mount_point'):
                    mount_point = os.path.expanduser(self.config.get(sec, 'mount_point'))
                    if subprocess.call(['grep', '-q', mount_point, '/etc/mtab']) == 0:
                        mi_button = gtk.MenuItem(_('Umount {0}').format(mount_point))
                        mi_button.connect('activate', self.encfs_action, 'umount', sec)
                    else:
                        mi_button = gtk.MenuItem(_('Mount {0}').format(mount_point))
                        mi_button.connect('activate', self.encfs_action, 'mount', sec)
                    mi_button.show()
                    encfs_menu.append(mi_button)

            encfs_menu_button = gtk.MenuItem(_('Encrypted repositories'))
            encfs_menu_button.show()
            encfs_menu_button.set_submenu(encfs_menu)
            menu.append(encfs_menu_button)

            sep = gtk.SeparatorMenuItem()
            sep.show()
            menu.append(sep)


    def notify(self, msg, urgency=pynotify.URGENCY_NORMAL):
        pynotify.init(_('HubicGTK Secure Repositories'))
        nota = pynotify.Notification(
            _('HubicGTK Secure Repositories'),
            msg
        )
        nota.set_urgency(urgency)
        nota.show()


    def encfs_action(self, widget, action, section):
        mount_point = os.path.expanduser(self.config.get(section, 'mount_point'))
        origin = os.path.join(self.hubic_dir, section)

        if not self.config.has_option(section, 'encfs_config'):
            self.notify(
                _('No config file path declared for {0}').format(section),
                pynotify.URGENCY_CRITICAL
            )
            return False

        encfs_config_file = os.path.expanduser(self.config.get(section, 'encfs_config'))


        if action == 'mount':
            if os.path.isdir(mount_point) and len(os.listdir(mount_point)) > 0:
                self.notify(
                    _('{0} already exists in your file system but is NOT an empty folder. Please fix it and then retry to mount {1}').format(mount_point, origin),
                    pynotify.URGENCY_CRITICAL
                )
                return False
            elif os.path.exists(mount_point) and not os.path.isdir(mount_point):
                self.notify(
                    _('{0} already exists in your file system but is NOT an empty folder. Please fix it and then retry to mount {1}').format(mount_point, origin),
                    pynotify.URGENCY_CRITICAL
                )
                return False
            elif not os.path.exists(mount_point):
                os.makedirs(mount_point)

            password = ''
            if self.config.has_option(section, 'encfs_passphrase'):
                password = self.config.get(section, 'encfs_passphrase')

            elif self.config.has_option(section, 'encfs_passfile'):
                pass_file = os.path.expanduser(self.config.get(section, 'encfs_passfile'))
                if os.access(pass_file, os.R_OK):
                    with open(pass_file) as fp:
                        password = fp.read()
                        fp.close()

                else:
                    self.notify(
                        _('Error while reading your password from {0}. Please check if everything is OK before retrying.').format(pass_file),
                        pynotify.URGENCY_CRITICAL
                    )
                    return False
            else:
                try:
                    password = subprocess.check_output(['zenity', '--password'])
                except subprocess.CalledProcessError:
                    # Nothing to do, user should have hit cancel button
                    password = ''

            password = password.strip()

            encfs_mount_cmd = 'false'
            if password != '':
                encfs_mount_cmd = 'echo "{0}" | ENCFS6_CONFIG="{1}" encfs -S "{2}" "{3}"'.format(password, encfs_config_file, origin, mount_point)

            if subprocess.call(encfs_mount_cmd, shell=True) == 0:
                self.notify(_('{0} correctly mounted').format(mount_point))
                if get_bool_conf_option(self.config, section, 'open_folder_at_mount'):
                    folder_heler = FileFolderHelper(self.config, self.hubic_dir)
                    folder_helper.open_folder(mount_point)

            else:
                self.notify(
                    _('An error occured while mounting {0}').format(mount_point),
                    pynotify.URGENCY_CRITICAL
                )

        else:
            if subprocess.call(['fusermount', '-u', mount_point]) == 0:
                self.notify(_('{0} successfully umounted').format(mount_point))

            else:
                self.notify(
                    _('An error occured while umounting {0}').format(mount_point),
                    pynotify.URGENCY_CRITICAL
                )



class SystrayIconApp:
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.join(xdg_config_home, 'hubiC', 'status_icon.conf'))

        self.tray = gtk.StatusIcon()
        self.hubic_state = 'Killed'
        self.tray.set_from_file(os.path.join(HUBIC_ICONS_PATH, 'hubic_error.png'))
        self.tray.set_tooltip(HUBIC_POSSIBLE_STATUS[self.hubic_state])
        self.tray.connect('popup-menu', self.on_right_click)
        self.tray.connect('activate', self.on_left_click)

        self.last_messages = []
        self.show_messages = False
        self.hubic_dir = ''

        if self.config.has_section('general'):
            self.show_messages = get_bool_conf_option(self.config, 'general', 'notify')
            self.show_all_messages = get_bool_conf_option(self.config, 'general', 'show_all_messages')

            if self.config.has_option('general', 'hubic_dir'):
                self.hubic_dir = os.path.expanduser(self.config.get('general', 'hubic_dir'))

        self.ff_helper = FileFolderHelper(self.config, self.hubic_dir)

        DBusGMainLoop(set_as_default=True)
        if subprocess.call(['pgrep', '-u' + pwd.getpwuid(os.getuid())[0], '-f', 'mono.*hubiC']) == 0:
            self.initialize_dbus_infos()


    def initialize_dbus_infos(self):
        self.hubic_state = 'Starting'
        self.tray.set_from_file(os.path.join(HUBIC_ICONS_PATH, 'hubic_busy.png'))
        self.tray.set_tooltip(HUBIC_POSSIBLE_STATUS[self.hubic_state])

        dbus.SystemBus().add_signal_receiver(self.on_networking_change, dbus_interface = 'org.freedesktop.NetworkManager', signal_name = 'StateChanged')

        self.session_bus = dbus.SessionBus()
        self.session_bus.add_signal_receiver(self.on_file_change, dbus_interface = 'com.hubic.account', signal_name = 'ItemChanged')
        self.session_bus.add_signal_receiver(self.on_state_change, dbus_interface = 'com.hubic.general', signal_name = 'StateChanged')
        self.session_bus.add_signal_receiver(self.on_message, dbus_interface = 'com.hubic.general', signal_name = 'Messages')

        self.hubic_account_obj = self.session_bus.get_object('com.hubiC', '/com/hubic/Account')
        self.hubic_account_iface = dbus.Interface(self.hubic_account_obj, 'com.hubic.account')
        self.hubic_general_obj = self.session_bus.get_object('com.hubiC', '/com/hubic/General')
        self.hubic_general_iface = dbus.Interface(self.hubic_general_obj, 'com.hubic.general')

        self.ff_helper.set_hubic_dir(self.get_hubic_dir())
        self.on_state_change('Starting', self.hubic_general_obj.Get('com.hubic.general', 'CurrentState'))


    def get_hubic_dir(self):
        if self.hubic_dir == '':
            self.hubic_dir = self.hubic_account_obj.Get('com.hubic.account', 'SynchronizedDir')

            if not self.config.has_section('general'):
                self.config.add_section('general')

            self.config.set('general', 'hubic_dir', self.hubic_dir)

            with open(os.path.join(xdg_config_home, 'hubiC', 'status_icon.conf'), 'wb') as configfile:
                self.config.write(configfile)
                configfile.close()

        return self.hubic_dir


    def on_networking_change(self, state):
        if self.hubic_state != 'Killed' and self.hubic_state != 'Starting':
            if state == 70:
                # Connectivity is up and not only local
                self.last_messages.append((
                    '',
                    _('{0} Resume Hubic as network is up').format(
                        time.strftime("[%d/%m/%Y %H:%M]")
                    )
                ))
                self.hubic_account_iface.SetPauseState(False)
            elif self.hubic_state != 'Paused':
                self.last_messages.append((
                    '',
                    _('{0} Pause Hubic as network connectivity seems to be down').format(
                        time.strftime("[%d/%m/%Y %H:%M]")
                    )
                ))
                self.hubic_account_iface.SetPauseState(True)


    def on_state_change(self, old_state, new_state):
        if new_state == 'NotConnected' and old_state == 'Connecting':
            self.hubic_process(None, 'stop')
            return

        self.hubic_state = new_state
        tray_tooltip = HUBIC_POSSIBLE_STATUS[self.hubic_state]

        if self.hubic_state == 'Busy':
            self.tray.set_from_file(os.path.join(HUBIC_ICONS_PATH, 'hubic_busy.png'))
            current_works = self.hubic_account_obj.Get('com.hubic.account', 'RunningOperations')

            if len(current_works) > 0:
                tray_tooltip = '{0} – {1}'.format(
                    tray_tooltip,
                    self.ff_helper.format_task(current_works[0])
                )

        elif self.hubic_state == 'Connecting':
            self.tray.set_from_file(os.path.join(HUBIC_ICONS_PATH, 'hubic_busy.png'))

        elif self.hubic_state == 'Idle':
            self.tray.set_from_file('/usr/share/icons/hicolor/16x16/hubic.png')

        else:
            self.tray.set_from_file(os.path.join(HUBIC_ICONS_PATH, 'hubic_error.png'))

        self.tray.set_tooltip(tray_tooltip)


    def on_file_change(self, file_path):
        [status, isPublished, canBePublished] = self.hubic_account_iface.GetItemStatus(file_path)
        message = self.ff_helper.crunch_path(file_path) + ': ' + HUBIC_POSSIBLE_STATUS[status]
        self.last_messages.append((file_path, time.strftime("[%d/%m/%Y %H:%M]") + ' ' + message))

        if self.show_messages:
            pynotify.init('HubicGTK')
            nota = pynotify.Notification('HubicGTK', message)
            nota.show()


    def on_message(self, urgency, message, file_path):
        if file_path != '':
            [status, isPublished, canBePublished] = self.hubic_account_iface.GetItemStatus(file_path)
            info_message = message + "\n" + self.ff_helper.crunch_path(file_path) + ': ' + HUBIC_POSSIBLE_STATUS[status]
        else:
            info_message = message

        self.last_messages.append((file_path, time.strftime("[%d/%m/%Y %H:%M]") + ' ' + info_message))

        if self.show_messages or urgency == 2 or urgency == 3:
            pynotify.init('HubicGTK')
            nota = pynotify.Notification('HubicGTK', message)

            if urgency == 1 or urgency == 2:
                nota.set_urgency(pynotify.URGENCY_NORMAL)
            elif urgency == 3:
                nota.set_urgency(pynotify.URGENCY_CRITICAL)
            else:
                nota.set_urgency(pynotify.URGENCY_LOW)

            nota.show()


    def on_right_click(self, icon, event_button, event_time):
        self.make_menu(event_button, event_time)


    def on_left_click(self, event):
        if self.hubic_dir != False:
            self.ff_helper.open_folder(self.get_hubic_dir())


    def on_report_a_bug(self, widget):
        subprocess.Popen(shlex.split('xdg-open https://projects.depar.is/hubic-gtk/ticket'))


    def make_menu(self, event_button, event_time):
        menu = gtk.Menu()

        current_state_info = gtk.MenuItem(HUBIC_POSSIBLE_STATUS[self.hubic_state])
        current_state_info.set_state(gtk.STATE_INSENSITIVE)
        current_state_info.show()
        menu.append(current_state_info)

        if self.hubic_state == 'Busy' or self.hubic_state == 'Idle':
            total = self.hubic_account_obj.Get('com.hubic.account', 'TotalBytes')
            used = self.hubic_account_obj.Get('com.hubic.account', 'UsedBytes')
            used_percent = round((used * 100.0) / total, 1)

            used_size_info = self.ff_helper.file_size(used)
            total_size_info = self.ff_helper.file_size(total)

            current_state_info = gtk.MenuItem(
                _('{0} {1} ({2}%) used on {3} {4} total').format(
                    used_size_info[0],
                    used_size_info[1],
                    used_percent,
                    total_size_info[0],
                    total_size_info[1]
                )
            )
            current_state_info.set_state(gtk.STATE_INSENSITIVE)
            current_state_info.show()
            menu.append(current_state_info)

            if self.hubic_state == 'Busy':
                downspeed = self.ff_helper.file_size(self.hubic_general_obj.Get('com.hubic.general', 'CurrentDownloadSpeed'))
                upspeed = self.ff_helper.file_size(self.hubic_general_obj.Get('com.hubic.general', 'CurrentUploadSpeed'))
                current_state_info = gtk.MenuItem(
                    _('Up: {0} {1}/s – Down: {2} {3}/s').format(
                        upspeed[0],
                        upspeed[1],
                        downspeed[0],
                        downspeed[1]
                    )
                )
                current_state_info.set_state(gtk.STATE_INSENSITIVE)
                current_state_info.show()
                menu.append(current_state_info)

                current_works = self.hubic_account_obj.Get('com.hubic.account', 'RunningOperations')
                if len(current_works) > 0:
                    workmenu = gtk.Menu()

                    for work_tuple in current_works:
                        mi_button = gtk.MenuItem(self.ff_helper.format_task(work_tuple))
                        mi_button.show()
                        workmenu.append(mi_button)

                    queue_status = self.hubic_account_obj.Get('com.hubic.account', 'QueueStatus')
                    total_items = queue_status[0] + queue_status[1] + queue_status[2]
                    up_infos = self.ff_helper.file_size(queue_status[3])
                    down_infos = self.ff_helper.file_size(queue_status[4])
                    mi_button = gtk.MenuItem(
                        _('{0} waiting ({1} {2} up – {3} {4} down)').format(
                            total_items,
                            up_infos[0],
                            up_infos[1],
                            down_infos[0],
                            down_infos[1]
                        )
                    )
                    mi_button.show()
                    workmenu.append(mi_button)

                    messages_info_button = gtk.MenuItem(_('Current transfers'))
                    messages_info_button.show()
                    messages_info_button.set_submenu(workmenu)
                    menu.append(messages_info_button)


        if self.hubic_state == 'Killed':
            start_button = gtk.ImageMenuItem(_('Start Hubic'))
            start_button_icon = gtk.image_new_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_MENU)
            start_button.set_image(start_button_icon)
            start_button.show()
            menu.append(start_button)
            start_button.connect('activate', self.hubic_process, 'start')

        else:
            if self.hubic_state == 'Paused':
                pause_button = gtk.ImageMenuItem(_('Resume synchronization'))
                pause_button_icon = gtk.image_new_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_MENU)
                pause_button.connect('activate', self.hubic_process, 'resume')
            else:
                pause_button = gtk.ImageMenuItem(_('Suspend synchronization'))
                pause_button_icon = gtk.image_new_from_stock(gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_MENU)
                pause_button.connect('activate', self.hubic_process, 'pause')

            pause_button.set_image(pause_button_icon)
            pause_button.show()
            menu.append(pause_button)

            stop_button = gtk.ImageMenuItem(_('Stop Hubic'))
            stop_button_icon = gtk.image_new_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU)
            stop_button.set_image(stop_button_icon)
            stop_button.show()
            menu.append(stop_button)
            stop_button.connect('activate', self.hubic_process, 'stop')

        sep = gtk.SeparatorMenuItem()
        sep.show()
        menu.append(sep)

        messages_info = gtk.Menu()

        mi_button = gtk.CheckMenuItem(_('Show notification messages'))
        mi_button.set_active(self.show_messages)
        mi_button.show()
        messages_info.append(mi_button)
        mi_button.connect('toggled', self.toggle_show_messages)

        sep = gtk.SeparatorMenuItem()
        sep.show()
        messages_info.append(sep)

        messages_to_show = self.last_messages
        if not self.show_all_messages:
            messages_to_show = self.last_messages[-10:]

        for file_path, mi in messages_to_show:
            mi_button = gtk.MenuItem(mi)
            mi_button.show()
            messages_info.append(mi_button)
            if file_path != '':
                mi_button.connect('activate', self.open_parent_dir, file_path)

        messages_info_button = gtk.MenuItem(_('Last messages'))
        messages_info_button.show()
        messages_info_button.set_submenu(messages_info)
        menu.append(messages_info_button)

        sep = gtk.SeparatorMenuItem()
        sep.show()
        menu.append(sep)

        # Encfs submenu
        encfs_menu = EncfsMenu(self.config, self.get_hubic_dir())
        encfs_menu.build_menu(menu)

        # report a bug
        reportbug = gtk.MenuItem(_('Report a bug'))
        reportbug.show()
        menu.append(reportbug)
        reportbug.connect('activate', self.on_report_a_bug)

        # show about dialog
        about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        about.show()
        menu.append(about)
        about.connect('activate', self.show_about_dialog)

        # add quit item
        quit_button = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit_button.show()
        menu.append(quit_button)
        quit_button.connect('activate', self.kthxbye)

        menu.popup(None, None, gtk.status_icon_position_menu,
                   event_button, event_time, self.tray)


    def toggle_show_messages(self, widget):
        self.show_messages = widget.get_active()
        if not self.config.has_section('general'):
            self.config.add_section('general')

        self.config.set('general', 'notify', self.show_messages)

        with open(os.path.join(xdg_config_home, 'hubiC', 'status_icon.conf'), 'wb') as configfile:
            self.config.write(configfile)
            configfile.close()


    def open_parent_dir(self, widget, file_path):
        dir_open = self.get_hubic_dir()
        if os.path.isdir(file_path):
            dir_open = file_path

        elif os.path.isfile(file_path):
            dir_open = os.path.dirname(file_path)

        else:
            file_path = os.path.dirname(file_path)
            if os.path.isdir(file_path):
                dir_open = file_path

        self.ff_helper.open_folder(dir_open)


    def hubic_process(self, widget, action):
        if self.hubic_state == 'Killed':
            if action == 'start':
                subprocess.call(['hubic', 'start'])
                self.initialize_dbus_infos()
            else:
                print 'Dafuq did I just read?'

        else:
            if action == 'stop':
                self.hubic_general_iface.Stop()
                self.hubic_state = 'Killed'
                self.tray.set_tooltip(HUBIC_POSSIBLE_STATUS[self.hubic_state])
                self.tray.set_from_file(os.path.join(HUBIC_ICONS_PATH, 'hubic_error.png'))

            elif action == 'pause':
                self.hubic_account_iface.SetPauseState(True)

            elif action == 'resume':
                self.hubic_account_iface.SetPauseState(False)

            else:
                print 'Dafuq did I just read?'


    def  show_about_dialog(self, widget):
        about_dialog = gtk.AboutDialog()
        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_icon_name ("HubicGTK")
        about_dialog.set_name('HubicGTK')
        about_dialog.set_website('https://projects.depar.is/hubic-gtk')
        about_dialog.set_comments(_("A status icon for hubiC on Gnu/Linux, providing an easy way to manage your encfs synchronised folders too."))
        about_dialog.set_logo(gtk.gdk.pixbuf_new_from_file('/usr/share/icons/hicolor/128x128/hubic.png'))
        about_dialog.set_version(HUBIC_STATUS_VERSION)
        hubic_version = "\n\n" + subprocess.check_output('hubic help | head -n2', shell=True) + subprocess.check_output('mono -V | head -n2', shell=True)
        about_dialog.set_copyright(_("HubicGTK is released under the WTF public license\nStatus icons use famfamfam silk icons, released under CC By 2.5 license") + hubic_version)
        about_dialog.set_authors(['Étienne Deparis <etienne@depar.is>'])
        about_dialog.run()
        about_dialog.destroy()


    def kthxbye(self, widget):
        gtk.main_quit()


if __name__ == "__main__":
    SystrayIconApp()
    gtk.main()
