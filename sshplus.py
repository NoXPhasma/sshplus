#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# SSHplus
# A remote connect utlity, sshmenu compatible clone, and application starter.
#
# (C) 2011 Anil Gulecha
# Based on sshlist, incorporating changes by Benjamin Heil's simplestarter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Instructions
#
# 1. Copy file sshplus.py (this file) to /usr/local/bin
# 2. Edit file .sshplus in your home directory to add menu entries, each
#    line in the format NAME|COMMAND|ARGS
# 3. Launch sshplus.py
# 4. Or better yet, add it to gnome startup programs list so it's run on login.

import shlex
import sys
import notify2
import os
import gi

gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


_VERSION = "1.0"

_SETTINGS_FILE = os.getenv("HOME") + "/.sshplus"

_ABOUT_TXT = """A simple application starter as appindicator.

To add items to the menu, edit the file <i>.sshplus</i> in your home directory. Each entry must be on a new line in this format:

<tt>NAME|COMMAND|ARGS</tt>

If the item is clicked in the menu, COMMAND with arguments ARGS will be executed. ARGS can be empty. To insert a separator, add a line which only contains "sep". Lines starting with "#" will be ignored. You can set an unclickable label with the prefix "label:". To insert a nested menu, use the prefix "folder:menu name". Subsequent items will be inserted in this menu, until a line containing an empty folder name is found: "folder:". After that, subsequent items get inserted in the parent menu. That means that more than one level of nested menus can be created.

Example file:
<tt><small>
Show top|gnome-terminal|-x top
sep

# this is a comment
label:SSH connections
# create a folder named "Home"
folder:Home
SSH Ex|gnome-terminal|-x ssh user@1.2.3.4
# to mark the end of items inside "Home", specify and empty folder:
folder:
# this item appears in the main menu
SSH Ex|gnome-terminal|-x ssh user@1.2.3.4

label:RDP connections
RDP Ex|rdesktop|-T "RDP-Server" -r sound:local 1.2.3.4

</small></tt>
Copyright 2011 Anil Gulecha
Incorporating changes from simplestarter, Benjamin Heil, http://www.bheil.net

Released under GPL3, http://www.gnu.org/licenses/gpl-3.0.html"""

_EDIT_CONFIG = """To add items to the menu, edit the file <i>.sshplus</i> in your home directory. Each entry must be on a new line in this format:

<tt>NAME|COMMAND|ARGS</tt>

If the item is clicked in the menu, COMMAND with arguments ARGS will be executed. ARGS can be empty. To insert a separator, add a line which only contains "sep". Lines starting with "#" will be ignored. You can set an unclickable label with the prefix "label:". To insert a nested menu, use the prefix "folder:menu name". Subsequent items will be inserted in this menu, until a line containing an empty folder name is found: "folder:". After that, subsequent items get inserted in the parent menu. That means that more than one level of nested menus can be created.

Example file:
<tt><small>
Show top|gnome-terminal|-x top
sep

# this is a comment
label:SSH connections
# create a folder named "Home"
folder:Home
SSH Ex|gnome-terminal|-x ssh user@1.2.3.4
# to mark the end of items inside "Home", specify and empty folder:
folder:
# this item appears in the main menu
SSH Ex|gnome-terminal|-x ssh user@1.2.3.4

label:RDP connections
RDP Ex|rdesktop|-T "RDP-Server" -r sound:local 1.2.3.4

</small></tt>"""


def menuitem_response(w, item):
    if item == "_about":
        show_help_dlg(_ABOUT_TXT)
    elif item == "_edit":
        edit_config_file()
    elif item == "_refresh":
        newmenu = build_menu()
        ind.set_menu(newmenu)
        notify2.init("sshplus")
        notify2.Notification(
            "SSHplus refreshed", '"%s" has been read! Menu list was refreshed!' % _SETTINGS_FILE
        ).show()
    elif item == "_quit":
        sys.exit(0)
    elif item == "folder":
        pass
    else:
        print(item)
        os.spawnvp(os.P_NOWAIT, item["cmd"], [item["cmd"]] + item["args"])
        os.wait3(os.WNOHANG)


def show_help_dlg(msg, error=False):
    if error:
        dlg_icon = Gtk.MessageType.ERROR
        md = Gtk.MessageDialog(
            None, 0, dlg_icon, Gtk.ButtonsType.OK, "This is an INFO MessageDialog"
        )
        edit_config_file()
    else:
        dlg_icon = Gtk.MessageType.INFO
        md = Gtk.MessageDialog(
            None, 0, dlg_icon, Gtk.ButtonsType.OK, "This is an INFO MessageDialog"
        )
    try:
        md.set_markup("<b>SSHplus %s</b>" % _VERSION)
        md.format_secondary_markup(msg)
        md.run()
    finally:
        md.destroy()


def edit_config_file():
    if os.path.isfile(_SETTINGS_FILE) is not True:
        os.mknod(_SETTINGS_FILE)
        show_help_dlg(
            "<b>No <i>.sshplus</i> config file found, we created one for you!\n\nPlease edit the"
            " file and reload the config.</b>\n\n%s"
            % _EDIT_CONFIG,
            error=True,
        )
    os.spawnvp(os.P_NOWAIT, "xdg-open", ["xdg-open", _SETTINGS_FILE])
    os.wait3(os.WNOHANG)


def add_separator(menu):
    separator = Gtk.SeparatorMenuItem()
    separator.show()
    menu.append(separator)


def add_menu_item(menu, caption, item=None):
    menu_item = Gtk.MenuItem.new_with_label(caption)
    if item:
        menu_item.connect("activate", menuitem_response, item)
    else:
        menu_item.set_sensitive(False)
    menu_item.show()
    menu.append(menu_item)
    return menu_item


def get_sshplusconfig():
    if not os.path.exists(_SETTINGS_FILE):
        return []

    app_list = []
    f = open(_SETTINGS_FILE, "r")
    try:
        for line in f.readlines():
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue
            elif line == "sep":
                app_list.append("sep")
            elif line.startswith("label:"):
                app_list.append({"name": "LABEL", "cmd": line[6:], "args": ""})
            elif line.startswith("folder:"):
                app_list.append({"name": "FOLDER", "cmd": line[7:], "args": ""})
            else:
                try:
                    name, cmd, args = line.split("|", 2)
                    app_list.append(
                        {
                            "name": name,
                            "cmd": cmd,
                            "args": [n.replace("\n", "") for n in shlex.split(args)],
                        }
                    )
                except ValueError:
                    print("The following line has errors and will be ignored:\n%s" % line)
    finally:
        f.close()
    return app_list


def build_menu():
    if not os.path.exists(_SETTINGS_FILE):
        show_help_dlg(
            "<b>ERROR: No .sshmenu file found in home directory</b>\n\n%s" % _ABOUT_TXT, error=True
        )
        sys.exit(1)

    app_list = get_sshplusconfig()

    menu = Gtk.Menu()
    menus = [menu]

    for app in app_list:
        if app == "sep":
            add_separator(menus[-1])
        elif app["name"] == "FOLDER" and not app["cmd"]:
            if len(menus) > 1:
                menus.pop()
        elif app["name"] == "FOLDER":
            menu_item = add_menu_item(menus[-1], app["cmd"], "folder")
            menus.append(Gtk.Menu())
            menu_item.set_submenu(menus[-1])
        elif app["name"] == "LABEL":
            add_menu_item(menus[-1], app["cmd"], None)
        else:
            add_menu_item(menus[-1], app["name"], app)

    # Add SSHplus options folder to the end of the Menu
    add_separator(menu)
    menu_item = add_menu_item(menus[-1], "SSHplus Options", "folder")
    menus.append(Gtk.Menu())
    menu_item.set_submenu(menus[-1])
    add_menu_item(menus[-1], "Options", None)
    add_menu_item(menus[-1], "Edit", "_edit")
    add_menu_item(menus[-1], "Refresh", "_refresh")
    add_menu_item(menus[-1], "About", "_about")
    add_separator(menus[-1])
    add_menu_item(menus[-1], "Quit", "_quit")
    menus.pop()
    return menu


if __name__ == "__main__":
    ind = AppIndicator3.Indicator.new(
        "SSHplus", "utilities-terminal", AppIndicator3.IndicatorCategory.APPLICATION_STATUS
    )

    ind.set_label("Launch", "none")
    ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

    if not os.path.exists(_SETTINGS_FILE):
        edit_config_file()

    appmenu = build_menu()
    ind.set_menu(appmenu)
    Gtk.main()
