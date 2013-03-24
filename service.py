#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2013 Team-XBMC
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#


import sys
import platform
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
try:
    import apt
    from aptdaemon import client
    import aptdaemon.errors
except:
    log('python apt import error')
    sys.exit(0)

__addon__        = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonname__    = __addon__.getAddonInfo('name')
__addonpath__    = __addon__.getAddonInfo('path').decode('utf-8')
__icon__         = __addon__.getAddonInfo('icon')
__localize__    = __addon__.getLocalizedString

def log(txt):
    if isinstance (txt,str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonname__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

class Main:
    def __init__(self):
        if __addon__.getSetting("versioncheck_enable") == 'true':
            if not sys.argv[0]:
                xbmc.executebuiltin('XBMC.AlarmClock(CheckAtBoot,XBMC.RunScript(service.xbmc.versionchecklinux, started),00:00:30,silent)')
                xbmc.executebuiltin('XBMC.AlarmClock(CheckWhileRunning,XBMC.RunScript(service.xbmc.versionchecklinux, started),24:00:00,silent,loop)')
            elif sys.argv[0] and sys.argv[1] == 'started':
                linuxversioncheckApt("xbmc")
            else:
                pass
                
def linuxversioncheckApt(package):

    if (platform.dist()[0] != "Ubuntu" and platform.dist()[0] != "Debian"):
        log("Unsupported platform %s" %platform.dist()[0])
        sys.exit(0)
    
    apt_client = client.AptClient()
    try:
        trans = apt_client.update_cache()
        trans.run(reply_handler=apttransstarted, error_handler=apterrorhandler)
    except errors.NotAuthorizedError:
        log("You are not allowed to update the cache!")
        sys.exit(0)
    
    trans = apt_client.upgrade_packages([package])
    trans.simulate(reply_handler=apttransstarted, error_handler=apterrorhandler)
    pkg = trans.packages[4][0]
    if (pkg == package):
       cache=apt.Cache()
       cache.open(None)
       cache.upgrade()
       #print "Installed version", cache[package].installed.version
       #print "Version available", cache[package].candidate.version
       log("Version installed  %s" %cache[package].installed.version)
       log("Version available  %s" %cache[package].candidate.version)
       oldversion = True
       msg = __localize__(32003)


    if oldversion:
        # Don't show while watching a video
        while(xbmc.Player().isPlayingVideo() and not xbmc.abortRequested):
            xbmc.sleep(500)
        # Detect if it's first run and only show OK dialog + ask to disable on that
        firstrun = __addon__.getSetting("versioncheck_firstrun") != 'false'
        if firstrun and not xbmc.abortRequested:
            xbmcgui.Dialog().ok(__addonname__,
                                msg,
                                __localize__(32001),
                                __localize__(32002))
            # sets check to false which is checked on startup
            if xbmcgui.Dialog().yesno(__addonname__,
                                      __localize__(32009),
                                      __localize__(32010)):
                __addon__.setSetting("versioncheck_enable", 'false')
            # set first run to false to only show a popup next startup / every two days
            __addon__.setSetting("versioncheck_firstrun", 'false')
        # Show notification after firstrun
        elif not xbmc.abortRequested:
            log(__localize__(32001) + '' + __localize__(32002))
            xbmc.executebuiltin("XBMC.Notification(%s, %s, %d, %s)" %(__addonname__,
                                                                      __localize__(32001) + '' + __localize__(32002),
                                                                      15000,
                                                                      __icon__))
        else:
            pass

def apttransstarted():
    pass

def apterrorhandler(error):
    raise error

            
if (__name__ == "__main__"):
    log('Version %s started' % __addonversion__)
    Main()
