#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import signal
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GObject
from threading import Thread
import time
from random import randint
import subprocess
import ssl
import urllib2
from datetime import datetime


APPINDICATOR_ID = 'myappindicator'
CHECK_INTERVAL_SEC = 5 * 60
indicator = None
iplist = [
    ('icmp', '122.201.23.145', 'Unitel',        '#f44336'),
    ('icmp', '10.10.10.1',     'cisco 2800',    '#f44336'),
    ('icmp', '10.10.10.50',    'IPPBX',         '#2196f3'),
    ('icmp', '122.201.23.151', 'Backup server', '#4caf50'),
    ('http', 'https://app.evisa.mn',        'SMSPro',       '#e91e63'),
    ('http', 'https://ajil.it/',            'TeamProgress', '#e91e63'),
    ('http', 'https://evisa.mn',            'eVisa',        '#e91e63'),
    ('http', 'https://immigration.gov.mn',  b'ГИХГ сайт',   '#e91e63'),
]


def build_menu():
    menu = gtk.Menu()
    for protocol, ip, desc, color in iplist:
        menuitem = gtk.MenuItem(protocol + ' - ' + ip + ' - ' + desc)
        menu.append(menuitem)
    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu


def quit(source):
    gtk.main_quit()


def get_svg_bar(offsetx, height, width, border, h, color):
    svg_bar = ""
    svg_bar += """<rect x="%s" y="0" width="%s" height="%s" style="fill:#ccc"/>""" % (offsetx, width, height)
    x = offsetx + border
    y = height - h - border
    w = width - 2 * border
    svg_bar += """<rect x="%s" y="%s" width="%s" height="%s" style="fill:%s"/>""" % (x, y, w, h, color)
    return svg_bar


def log(message):
    with open('/run/shm/check-beep.log', 'w') as f:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write("[%s] %s" % (date_str, message))


def ping_alive(ip):
    try:
        ping_response = subprocess.Popen(
            ["/bin/ping", "-c1", "-w10", ip], stdout=subprocess.PIPE
        ).stdout.read()
    except Exception as e:
        log('Error during ping ' + ip)
        log(e.message)
        return False

    return '1 received' in ping_response


def http_alive(url):
    # TODO quite immature -> ssl._create_unverified_context()
    try:
        rsp = urllib2.urlopen(url, context=ssl._create_unverified_context())
    except urllib2.URLError as e:
        log(e.message)
        return False
    except Exception as e:
        log(e.message)
        return False
    return rsp.getcode() == 200


def action():
    global indicator

    n = 0
    while True:
        filename = '/run/shm/check-beep-icon%s.svg' % (n % 2)
        with open(filename, 'w') as f:
            f.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>""")
            f.write("""<svg width="%s" height="16">""" % (len(iplist) * 9 - 1))
            offset = 0
            for protocol, ip_or_url, desc, color in iplist:
                if protocol == 'http':
                    amount = http_alive(ip_or_url) and 14 or 0
                elif protocol == 'icmp':
                    amount = ping_alive(ip_or_url) and 14 or 0
                else:
                    amount = 0
                f.write(get_svg_bar(offset, 16, 8, 1, amount, color))
                offset += 9
            f.write("""</svg>""")

        GObject.idle_add(
            indicator.set_icon,
            filename,
            priority=GObject.PRIORITY_DEFAULT
        )

        #GObject.idle_add(
        #    indicator.set_label,
        #    '%i seconds left' % num_loop, APPINDICATOR_ID,
        #    priority=GObject.PRIORITY_DEFAULT
        #)

        n += 1
        time.sleep(CHECK_INTERVAL_SEC)


def main():
    global indicator
    indicator = appindicator.Indicator.new(
        APPINDICATOR_ID,
        gtk.STOCK_INFO,
        appindicator.IndicatorCategory.SYSTEM_SERVICES
    )
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())

    action_thread = Thread(target=action)
    action_thread.setDaemon(True)
    action_thread.start()

    gtk.main()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()

