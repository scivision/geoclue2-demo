#!/usr/bin/env python

import dbus
import traceback

from dbus.mainloop.glib import DBusGMainLoop

GEOCLUE2_BUS_NAME = 'org.freedesktop.GeoClue2'
MANAGER_INTERFACE_NAME = GEOCLUE2_BUS_NAME + '.Manager'
CLIENT_INTERFACE_NAME = GEOCLUE2_BUS_NAME + '.Client'
LOCATION_INTERFACE_NAME = GEOCLUE2_BUS_NAME + '.Location'
DBUS_PROPERTIES_INTERFACE_NAME = 'org.freedesktop.DBus.Properties'

def get_client():
    '''
    Interfaces with DBus and initializes a client object that will be
    used to obtain GeoClue2 client object
    '''
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


def set_distance_threshold(threshold):
    '''
    Sets a distance threshold for GeoClue2 client. Whenever the distance
    between the new location and old location is >= to the threshold, a
    LocationUpdated signal is emitted by GeoClue2.
    '''
    client_props = dbus.Interface(client_object, DBUS_PROPERTIES_INTERFACE_NAME)
    client_props.Set(CLIENT_INTERFACE_NAME,
                        'DistanceThreshold', dbus.UInt32(threshold))

def start_client(signal_handler, threshold=1000):
    '''
    Starts GeoClue2 client with a default distance threshold of 1000 meters
    '''
    global location_updated_user_handler, iclient

    # set threshold for updating location (and triggering callback)
    set_distance_threshold(threshold);

    # set user-defined handler for getting location updates
    location_updated_user_handler = signal_handler

    # connect handler to GeoClue's LocationUpdated signal
    system_bus.add_signal_receiver(location_updated_handler,
            dbus_interface = CLIENT_INTERFACE_NAME,
            signal_name = "LocationUpdated")

    # use client object to get client interface & start client
    iclient = dbus.Interface(client_object, dbus_interface=CLIENT_INTERFACE_NAME)
    iclient.Start()


def stop_client():
    '''
    Stops GeoClue2 client
    '''
    iclient.Stop()


def location_updated_handler(previous_location, new_location):
    '''
    Handler for when GeoClue2 LocationUpdated signal is emitted. It fetchs
    the new/current location and passes it to the user-defined handler
    '''

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


# below is example code for how to interface with the GeoClue2 client
# the handler simply prints out the location information once & quits
def my_location_handler(latitude, longitude, accuracy, description):
    print("Latitude = " + str(latitude))
    print("Longitude = " + str(longitude))
    print("Accuracy = " + str(accuracy))
    print("Description = " + str(description))
    stop_client()
    loop.quit()

if  __name__ =='__main__':
    import gobject
    global loop
    get_client()
    start_client(my_location_handler)
    loop = gobject.MainLoop()
    loop.run()
