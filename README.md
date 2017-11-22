# geoclue2-demo

Example for how to use
[GeoClue2](http://www.freedesktop.org/wiki/Software/GeoClue/)
to grab location information and
[libchamplain](https://projects.gnome.org/libchamplain/)
to display the location on a map.


## prereqs

    apt install geoclue-2.0 python-gi gir1.2-gtkclutter-1.0 gir1.2-gtk-3.0 gir1.2-gtkchamplain-0.12


## Examples
command line

    geoclue2client.py

GUI

    geoclue2demo.py


## Notes

`geoclue2client.py` is based on

* [dbus python tutorial](http://dbus.freedesktop.org/doc/dbus-python/doc/tutorial.html)
* [geoclue2demo](https://github.com/parinporecha/GeoClue2-Locator-python)
* [libchamplain](https://projects.gnome.org/libchamplain/)


### TODO

> DBusException: org.freedesktop.DBus.Error.AccessDenied: 'DesktopId' property must be set

Python API needs updating to this new Geocode2 requirement.