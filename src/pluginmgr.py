"""Plugin manager for Aranduka, using Yapsy"""

from PyQt4 import QtCore

import logging
#logging.basicConfig(level=logging.DEBUG)

import os
from yapsy.PluginManager import PluginManager
from yapsy.IPlugin import IPlugin

# These classes define our plugin categories
class ShelveView(QtCore.QObject):
    title = "base ShelveView"
    def __init__(self):
        print "INIT: ", self.title
        self.widget = None
        QtCore.QObject.__init__(self)
    
class BookStore(object): pass
class Converter(object): pass

manager = PluginManager(
    categories_filter={
        "ShelveView": ShelveView,
        "BookStore": BookStore,
        "Converter": Converter,
    })

plugindir = os.path.join(
            os.path.abspath(
            os.path.dirname(__file__)),'plugins')

manager.setPluginPlaces([plugindir])

