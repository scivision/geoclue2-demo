#!/usr/bin/env python

import sys
import dbus
import traceback

from dbus.mainloop.glib import DBusGMainLoop
from collections import namedtuple

GEOCLUE2_BUS_NAME = 'org.freedesktop.GeoClue2'
MANAGER_INTERFACE_NAME = GEOCLUE2_BUS_NAME + '.Manager'
CLIENT_INTERFACE_NAME = GEOCLUE2_BUS_NAME + '.Client'
LOCATION_INTERFACE_NAME = GEOCLUE2_BUS_NAME + '.Location'
DBUS_PROPERTIES_INTERFACE_NAME = 'org.freedesktop.DBus.Properties'


def get_client():
    '''
    Interfaces with DBus and initializes a client object that will be
    used to interface with GeoClue2
    '''
    try: 
        global system_bus, client_object
        # connect to dbus system (not session) bus
        DBusGMainLoop(set_as_default = True)
        system_bus = dbus.SystemBus()

        # get GeoClue2 manager object from system (not session) bus
        manager_object = system_bus.get_object(GEOCLUE2_BUS_NAME,
                            "/org/freedesktop/GeoClue2/Manager")
        imanager = dbus.Interface(manager_object, MANAGER_INTERFACE_NAME)

        # get GeoClue2 client interface by getting client path -> 
        # client object -> client interface
        client_path = imanager.GetClient()
        client_object = system_bus.get_object(GEOCLUE2_BUS_NAME, client_path)

    except dbus.DBusException:
        return (traceback.print_exc())  

def set_distance_threshold(threshold):
    client_props = dbus.Interface(client_object, DBUS_PROPERTIES_INTERFACE_NAME)
    client_props.Set(CLIENT_INTERFACE_NAME,
                        'DistanceThreshold', dbus.UInt32(threshold))

def start_client(signal_handler, threshold=1000):
    '''
    Starts GeoClue2 client which signals user's location_updated_callback
    whenever distance between new location and old location is >= to 
    the distance_threshold. by default, threshold is set to 1000 meters
    '''
    global location_updated_user_handler, iclient
    try:
        # set threshold for updating location (and triggering callback)
        set_distance_threshold(threshold);

        # connect location_updated callback to user's 
        location_updated_user_handler = signal_handler
        
        # connect callback function to 'LocationUpdated' signal
        system_bus.add_signal_receiver(location_updated_handler, 
                dbus_interface = CLIENT_INTERFACE_NAME, 
                signal_name = "LocationUpdated")
        
        # start client
        iclient = dbus.Interface(client_object, dbus_interface=CLIENT_INTERFACE_NAME)
        iclient.Start()
    except dbus.DBusException:
        return (traceback.print_exc())
    
def stop_client():
    try:
        iclient.Stop()
    except dbus.DBusException:
        return (traceback.print_exc())

def location_updated_handler(previous_location, new_location):
    '''
    When GeoClue2 LocationUpdated signal is emitted, this callback 
    function is trigger and fetchs the new/current location data
    This data is then passed on to the user-defined callback function
    '''
    try:                       
        # get GeoClue2's location object and pull its properties
        location_object = system_bus.get_object(
                        GEOCLUE2_BUS_NAME, new_location)
        location_properties = dbus.Interface(location_object, 
                        DBUS_PROPERTIES_INTERFACE_NAME)
        latitude = location_properties.Get(
                        LOCATION_INTERFACE_NAME, 'Latitude')
        longitude = location_properties.Get(
                        LOCATION_INTERFACE_NAME, 'Longitude')
        accuracy = location_properties.Get(
                        LOCATION_INTERFACE_NAME, 'Accuracy')
        description = location_properties.Get(
                        LOCATION_INTERFACE_NAME, 'Description')
        
        # call user's callback function with previous and current location
        location_updated_user_handler(latitude, longitude, accuracy, description)

    except dbus.DBusException:
        return (traceback.print_exc())

def my_location_handler(latitude, longitude, accuracy, description):
    print "Latitude = " + str(latitude)
    print "Longitude = " + str(longitude)
    print "Accuracy = " + str(accuracy)
    print "Description = " + str(description)
    stop_client()
    loop.quit()

if  __name__ =='__main__':
    import gobject
    global loop
    get_client()
    start_client(my_location_handler)
    loop = gobject.MainLoop()
    loop.run()
