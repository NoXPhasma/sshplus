sshplus
======

GTK+3/Python3 fork of sshplus based on the original sshplus from Anil Gulecha.

Changes :

- Updated to Gtk+3 and Python3
- Removed sshmenu support
- Added option menu

Configuration:
Create a file .sshplus in your home directory (touch ~/.sshplus).
Edit the file and add the entries in the format
NAME|COMMAND|arguments

For Example

```
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

sep
label:RDP connections
RDP Ex|rdesktop|-T "RDP-Server" -r sound:local 1.2.3.4
```

Install and Run:
- git clone https://github.com/NoXPhasma/sshplus.git
- cd sshplus
- chmod a+rx sshplus.py
- sudo cp sshplus.py /usr/local/bin

To run:
/usr/local/bin/sshplus.py

Add this to the startup program list so that it runs when the user logs in.
