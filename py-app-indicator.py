import os
import signal
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GObject
from threading import Thread
import time
from random import randint


APPINDICATOR_ID = 'myappindicator'

def build_menu():
    menu = gtk.Menu()
    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu


def quit(source):
    gtk.main_quit()


def action():
    global indicator

    num_loop = 100
    while num_loop > 0:
        time.sleep(0.1)
        num_loop -= 1
        #indicator.set_icon(gtk.STOCK_INFO)
        file = 'icon%s.svg' % (num_loop % 2)
        with open(file, 'w') as f:
            svg =  """<?xml version="1.0" encoding="UTF-8" standalone="no"?>"""
            svg += """<svg width="100" height="4">"""
            svg += """<rect width="%s" height="4" style="fill:rgb(0,0,255);stroke-width:1;stroke:rgb(255,255,0)">""" % num_loop
            svg += """<animate attributeType="XML" attributeName="x" from="0" to="50" dur="2s" repeatCount="indefinite"/>"""
            svg += """</rect>"""
            svg += """</svg>"""
            f.write(svg)

        if num_loop < 20:
            num_loop += randint(0, 40)

        GObject.idle_add(
            indicator.set_icon,
            os.path.abspath(file),
            priority=GObject.PRIORITY_DEFAULT
        )
        break

        #GObject.idle_add(
        #    indicator.set_label,
        #    '%i seconds left' % num_loop, APPINDICATOR_ID,
        #    priority=GObject.PRIORITY_DEFAULT
        #)



indicator = None


def main():
    global indicator
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, gtk.STOCK_INFO, appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())

    action_thread = Thread(target=action)
    action_thread.setDaemon(True)
    action_thread.start()

    gtk.main()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()

