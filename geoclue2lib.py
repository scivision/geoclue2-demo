#!/usr/bin/env python

import sys
import dbus
import traceback

from dbus.mainloop.glib import DBusGMainLoop
from collections import namedtuple

class GeoClueLib:
    GEOCLUE2_BUS_NAME = 'org.freedesktop.GeoClue2'
    MANAGER_INTERFACE_NAME = GEOCLUE2_BUS_NAME + '.Manager'
    CLIENT_INTERFACE_NAME = GEOCLUE2_BUS_NAME + '.Client'
    LOCATION_INTERFACE_NAME = GEOCLUE2_BUS_NAME + '.Location'
    PROPERTIES_INTERFACE_NAME = 'org.freedesktop.DBus.Properties'

    # set up a namedtuple which will hold geoclue's location data:
    # latitude, longitude, accuracy, and description info
    LocationStruct = namedtuple('LocationStruct', 
                                'latitude longitude accuracy description')

    def __init__(self):
        '''
        Interfaces with DBus and initializes a client object that will be
        used to interface with GeoClue2
        '''
        try: 
            # setup event loop for asynchronous dbus calls
            dbus_loop = DBusGMainLoop(set_as_default = True)

            # connect to system bus (where GeoClue2 is located)
            self.system_bus = dbus.SystemBus(mainloop = dbus_loop)

            # get GeoClue service manager object, then its interface
            manager_object = self.system_bus.get_object(GeoClueLib.GEOCLUE2_BUS_NAME, 
                                        '/org/freedesktop/GeoClue2/Manager')
            manager = dbus.Interface(manager_object, GeoClueLib.MANAGER_INTERFACE_NAME)

            # call GetClient() to get client object
            client_path = manager.GetClient()
            self.client_object = self.system_bus.get_object(
                    GeoClueLib.GEOCLUE2_BUS_NAME, client_path)

        except dbus.DBusException:
            return (traceback.print_exc())  
    
    def start_client(self, location_updated_user_callback, distance_threshold=1000):
        '''
        Starts GeoClue2 client which signals user's location_updated_callback
        whenever distance between new location and old location is >= to 
        the distance_threshold. by default, threshold is set to 1000 meters
        '''       
        try:
            # set DistanceThreshold, then get client interface
            client_properties = dbus.Interface(self.client_object, 
                                    GeoClueLib.PROPERTIES_INTERFACE_NAME)
            client_properties.Set(GeoClueLib.CLIENT_INTERFACE_NAME,
                         'DistanceThreshold', dbus.UInt32(distance_threshold))
            self.client = dbus.Interface(self.client_object,
                                    GeoClueLib.CLIENT_INTERFACE_NAME)

            # connect location_updated callback to user's callback function
            self.location_updated_callback = location_updated_user_callback
            
            # connect callback function to 'LocationUpdated' signal
            self.client.connect_to_signal('LocationUpdated', self.location_updated)
            
            # start client
            self.client.Start()
        except dbus.DBusException:
            return (traceback.print_exc())
        
    def stop_client(self):
        try:
            self.client.Stop()
        except dbus.DBusException:
            return (traceback.print_exc())
    
    def location_updated(self, previous_location, new_location):
        '''
        When GeoClue2 LocationUpdated signal is emitted, this callback 
        function is trigger and fetchs the new/current location data
        This data is then passed on to the user-defined callback function
        '''
        try:                       
            # get GeoClue2's location object and pull its properties
            location_object = self.system_bus.get_object(
                            GeoClueLib.GEOCLUE2_BUS_NAME, new_location)
            location_properties = dbus.Interface(location_object, 
                            GeoClueLib.PROPERTIES_INTERFACE_NAME)
            latitude = location_properties.Get(
                            GeoClueLib.LOCATION_INTERFACE_NAME, 'Latitude')
            longitude = location_properties.Get(
                            GeoClueLib.LOCATION_INTERFACE_NAME, 'Longitude')
            accuracy = location_properties.Get(
                            GeoClueLib.LOCATION_INTERFACE_NAME, 'Accuracy')
            description = location_properties.Get(
                            GeoClueLib.LOCATION_INTERFACE_NAME, 'Description')
            
            # set data as namedtuple
            current_location = GeoClueLib.LocationStruct(latitude=latitude, 
                    longitude=longitude, accuracy=accuracy, description=description)
            
            # call user's callback function with previous and current location
            self.location_updated_callback(current_location)
        except dbus.DBusException:
            return (traceback.print_exc())

import gobject

loop = None

def main():
    global loop
    locator = GeoClueLib()
    locator.start_client(my_callback)
    loop = gobject.MainLoop()
    loop.run()
    locator.stop_client()
    
def my_callback(current_location):
    print "Latitude = " + str(current_location.latitude)
    print "Longitude = " + str(current_location.longitude)
    print "Accuracy = " + str(current_location.accuracy)
    print "Description = " + str(current_location.description)
    loop.quit()

if  __name__ =='__main__':
    main()
