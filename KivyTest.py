# Imports the kivy module
import kivy

# From kivy import the classes that will be used in the program
from kivy.app import App

from kivy.uix.tabbedpanel import TabbedPanel

# Ensures correct version of kivy is used
kivy.require('2.3.1')


# Creates a class to store the info of the .kv file
class MainWidget(TabbedPanel):
    pass


# Main class that runs the app inheriting the class app from kivy module
class Controller(App):
    def build(self):
        # returns the main widget as the root widget
        return MainWidget()


if __name__ == "__main__":
    # The app is initialized at runtime
    # And its run method is called
    Controller().run()
