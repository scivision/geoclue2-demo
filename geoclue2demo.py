#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkClutter', '1.0')
gi.require_version('Champlain', '0.12')
gi.require_version('GtkChamplain', '0.12')

from gi.repository import GtkClutter, Clutter
GtkClutter.init([]) # Must be initialized before importing those:
from gi.repository import GObject, Gtk, Champlain, GtkChamplain#, Pango

import geoclue2client

class Geoclue2Demo:

    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_border_width(10)
        self.window.set_title("GeoClue2 + GTK Python Demo")
        self.window.connect("destroy", Gtk.main_quit)

        vbox = Gtk.VBox(False, 10)

        embed = GtkChamplain.Embed()

        self.view = embed.get_view()
        self.view.set_reactive(True)
        self.view.set_property('kinetic-mode', True)
        self.view.set_property('zoom-level', 5)

        scale = Champlain.Scale()
        scale.connect_view(self.view)
        self.view.bin_layout_add(scale, Clutter.BinAlignment.START, Clutter.BinAlignment.END)

        license = self.view.get_license_actor()

        embed.set_size_request(640, 480)

        bbox = Gtk.HBox(False, 10)
        button = Gtk.Button(stock=Gtk.STOCK_ZOOM_IN)
        button.connect("clicked", self.zoom_in)
        bbox.add(button)

        button = Gtk.Button(stock=Gtk.STOCK_ZOOM_OUT)
        button.connect("clicked", self.zoom_out)
        bbox.add(button)

        button = Gtk.ToggleButton(label="Current Location")
        button.set_active(False)
        button.connect("toggled", self.get_location)
        bbox.add(button)

        self.spinbutton = Gtk.SpinButton.new_with_range(0, 20, 1)
        self.spinbutton.connect("changed", self.zoom_changed)
        self.view.connect("notify::zoom-level", self.map_zoom_changed)
        self.spinbutton.set_value(5)
        bbox.add(self.spinbutton)

        button = Gtk.Image()
        self.view.connect("notify::state", self.view_state_changed, button)
        bbox.pack_end(button, False, False, 0)

        vbox.pack_start(bbox, expand=False, fill=False, padding=0)
        vbox.add(embed)

        self.window.add(vbox)

        self.window.show_all()

    def zoom_in(self, widget):
        self.view.zoom_in()

    def zoom_out(self, widget):
        self.view.zoom_out()

    def zoom_changed(self, widget):
        self.view.set_property("zoom-level", self.spinbutton.get_value_as_int())

    def map_zoom_changed(self, widget, value):
        self.spinbutton.set_value(self.view.get_property("zoom-level"))

    def view_state_changed(self, view, paramspec, image):
        state     = view.get_state()
        if state == Champlain.State.LOADING:
            image.set_from_stock(Gtk.STOCK_NETWORK, Gtk.IconSize.BUTTON)
        else:
            image.clear()

    def place_marker(self, latitude, longitude, description):
        orange = Clutter.Color.new(0xf3, 0x94, 0x07, 0xbb)
        layer = Champlain.MarkerLayer()

        markup_string = "";
        lines = description.split(',')
        if (len(lines) > 1):
            markup_string = lines[0] + "\n<span size=\"xx-small\">" + \
                ", ".join(lines[1:]) + "</span>"
        elif (len(lines) == 0):
            markup_string = lines[0].strip()

        marker = Champlain.Label.new_with_text(
            markup_string, "Serif 14", None, orange)
        marker.set_use_markup(True)
        marker.set_color(orange)

        marker.set_location(latitude, longitude)
        layer.add_marker(marker)
        self.view.center_on(latitude, longitude)
        layer.show()
        self.view.add_layer(layer)

    def get_location(self, widget):
        geoclue2client.get_client()
        geoclue2client.start_client(self.my_location_handler)

    def my_location_handler(self, latitude, longitude, accuracy, description):
        print("Latitude = " + str(latitude))
        print("Longitude = " + str(longitude))
        print("Accuracy = " + str(accuracy))
        print("Description = " + str(description))
        geoclue2client.stop_client()
        self.place_marker(latitude, longitude, description)

if __name__ == "__main__":
    GObject.threads_init()
    Geoclue2Demo()
    Gtk.main()
