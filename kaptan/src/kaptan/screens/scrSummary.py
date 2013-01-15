# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import QMessageBox
from PyKDE4.kdecore import ki18n, KConfig

import subprocess,os, dbus, time

from kaptan.screen import Screen
from kaptan.screens.ui_scrSummary import Ui_summaryWidget
from PyKDE4 import kdeui

# import other widgets to get the latest configuration
import kaptan.screens.scrWallpaper as wallpaperWidget
import kaptan.screens.scrMouse as mouseWidget
import kaptan.screens.scrStyle as styleWidget
import kaptan.screens.scrMenu as menuWidget
import kaptan.screens.scrAvatar  as avatarWidget
import kaptan.screens.scrServices as servicesWidget
import kaptan.screens.scrSecurity as securityWidget

from kaptan.tools import tools

class Widget(QtGui.QWidget, Screen):
    title = ki18n("Summary")
    desc = ki18n("Save Your Settings")

    def __init__(self, *args):
        QtGui.QWidget.__init__(self,None)
        self.ui = Ui_summaryWidget()
        self.ui.setupUi(self)

    def shown(self):
        self.wallpaperSettings = wallpaperWidget.Widget.screenSettings
        self.mouseSettings = mouseWidget.Widget.screenSettings
        self.menuSettings = menuWidget.Widget.screenSettings
        self.styleSettings = styleWidget.Widget.screenSettings
        self.avatarSettings = avatarWidget.Widget.screenSettings
        self.servicesSettings = servicesWidget.Widget.screenSettings
        self.securitySettings = securityWidget.Widget.screenSettings

        subject = "<p><li><b>%s</b></li><ul>"
        item    = "<li>%s</li>"
        end     = "</ul></p>"
        content = QString("")

        content.append("""<html><body><ul>""")

        # Mouse Settings
        content.append(subject % ki18n("Mouse Settings").toString())

        content.append(item % ki18n("Selected Mouse configuration: <b>%s</b>").toString() % self.mouseSettings["summaryMessage"]["selectedMouse"].toString())
        content.append(item % ki18n("Selected clicking behavior: <b>%s</b>").toString() % self.mouseSettings["summaryMessage"]["clickBehavior"].toString())
        content.append(end)

        # Menu Settings
        content.append(subject % ki18n("Menu Settings").toString())
        content.append(item % ki18n("Selected Menu: <b>%s</b>").toString() % self.menuSettings["summaryMessage"].toString())
        content.append(end)

        # Wallpaper Settings
        content.append(subject % ki18n("Wallpaper Settings").toString())
        if not self.wallpaperSettings["hasChanged"]:
            content.append(item % ki18n("You haven't selected any wallpaper.").toString())
        else:
            content.append(item % ki18n("Selected Wallpaper: <b>%s</b>").toString() % os.path.basename(str(self.wallpaperSettings["selectedWallpaper"])))
        content.append(end)

        # Services Settings
        if self.servicesSettings["hasChanged"]:
            self.daemon = Daemon()
            self.svctext = ki18n("You have: ").toString()
            self.svcissset = False
            content.append(subject % ki18n("Services Settings").toString())

            if self.servicesSettings["enableCups"] and not self.daemon.isEnabled("cups"):
                self.svctext += ki18n("enabled cups; ").toString()
                self.svcisset = True
            elif not self.servicesSettings["enableCups"] and self.daemon.isEnabled("cups"):
                self.svctext += ki18n("disabled cups; ").toString()
                self.svcisset = True
            if self.servicesSettings["enableBluetooth"] and not self.daemon.isEnabled("bluetooth"):
                self.svctext += ki18n("enabled bluetooth; ").toString()
                self.svcisset = True
            elif not self.servicesSettings["enableBluetooth"] and self.daemon.isEnabled("bluetooth"):
                self.svctext += ki18n("disabled bluetooth; ").toString()
                self.svcisset = True

            if not self.svcisset:
                self.svctext = ki18n("You have made no changes.").toString()
                self.servicesSettings["hasChanged"] = False

            content.append(item % ki18n(self.svctext).toString())

            content.append(end)

        # Security Settings
        if self.securitySettings["hasChanged"]:
            self.daemon = Daemon()
            self.sectext = ki18n("You have: ").toString()
            self.secisset = False
            content.append(subject % ki18n("Security Settings").toString())

            if self.securitySettings["enableClam"] and not self.daemon.isEnabled("clamd"):
                self.sectext += ki18n("enabled ClamAV; ").toString()
                self.secisset = True
            elif not self.securitySettings["enableClam"] and self.daemon.isEnabled("clamd"):
                self.sectext += ki18n("disabled ClamAV; ").toString()
                self.secisset = True
            if self.securitySettings["enableFire"] and not self.daemon.isEnabled("ufw"):
                self.sectext += ki18n("enabled the firewall; ").toString()
                self.secisset = True
            elif not self.securitySettings["enableFire"] and self.daemon.isEnabled("ufw"):
                self.sectext += ki18n("disabled the firewall; ").toString()
                self.secisset = True

            if not self.secisset:
                self.sectext = ki18n("You have made no changes.").toString()
                self.securitySettings["hasChanged"] = False

            content.append(item % ki18n(self.sectext).toString())

            content.append(end)

        self.ui.textSummary.setText(content)


    def killPlasma(self):
        try:
            p = subprocess.Popen(["kquitapp", "plasma-desktop"], stdout=subprocess.PIPE)
            out, err = p.communicate()
            time.sleep(1)
            self.startPlasma()

        except:
            QMessageBox.critical(self, ki18n("Error").toString(), ki18n("Cannot restart plasma-desktop. Kaptan will now shut down.").toString())
            from PyKDE4 import kdeui
            kdeui.KApplication.kApplication().quit()

    def startPlasma(self):
        p = subprocess.Popen(["plasma-desktop"], stdout=subprocess.PIPE)


    def execute(self):
        hasChanged = False
        rootActions = ""

        # Wallpaper Settings
        if self.wallpaperSettings["hasChanged"]:
            hasChanged = True
            if self.wallpaperSettings["selectedWallpaper"]:
                config =  KConfig("plasma-desktop-appletsrc")
                group = config.group("Containments")
                for each in list(group.groupList()):
                    subgroup = group.group(each)
                    subcomponent = subgroup.readEntry('plugin')
                    if subcomponent == 'desktop' or subcomponent == 'folderview':
                        subg = subgroup.group('Wallpaper')
                        subg_2 = subg.group('image')
                        subg_2.writeEntry("wallpaper", self.wallpaperSettings["selectedWallpaper"])

        # Menu Settings
        if self.menuSettings["hasChanged"]:
            hasChanged = True
            config = KConfig("plasma-desktop-appletsrc")
            group = config.group("Containments")

            for each in list(group.groupList()):
                subgroup = group.group(each)
                subcomponent = subgroup.readEntry('plugin')
                if subcomponent == 'panel':
                    subg = subgroup.group('Applets')
                    for i in list(subg.groupList()):
                        subg2 = subg.group(i)
                        launcher = subg2.readEntry('plugin')
                        if str(launcher).find('launcher') >= 0:
                            subg2.writeEntry('plugin', self.menuSettings["selectedMenu"] )


        def removeFolderViewWidget():
            config = KConfig("plasma-desktop-appletsrc")

            sub_lvl_0 = config.group("Containments")

            for sub in list(sub_lvl_0.groupList()):
                sub_lvl_1 = sub_lvl_0.group(sub)

                if sub_lvl_1.hasGroup("Applets"):
                    sub_lvl_2 = sub_lvl_1.group("Applets")

                    for sub2 in list(sub_lvl_2.groupList()):
                        sub_lvl_3 = sub_lvl_2.group(sub2)
                        plugin = sub_lvl_3.readEntry('plugin')

                        if plugin == 'folderview':
                            sub_lvl_3.deleteGroup()


        # Desktop Type
        if self.styleSettings["hasChangedDesktopType"]:
            hasChanged = True
            config =  KConfig("plasma-desktop-appletsrc")
            group = config.group("Containments")

            for each in list(group.groupList()):
                subgroup = group.group(each)
                subcomponent = subgroup.readEntry('plugin')
                subcomponent2 = subgroup.readEntry('screen')
                if subcomponent == 'desktop' or subcomponent == 'folderview':
                    if int(subcomponent2) == 0:
                        subgroup.writeEntry('plugin', self.styleSettings["desktopType"])

            # Remove folder widget - normally this would be done over dbus but thanks to improper naming of the plasma interface
            # this is not possible
            # ValueError: Invalid interface or error name 'org.kde.plasma-desktop': contains invalid character '-'
            #
            # Related Bug:
            # Bug 240358 - Invalid D-BUS interface name 'org.kde.plasma-desktop.PlasmaApp' found while parsing introspection
            # https://bugs.kde.org/show_bug.cgi?id=240358

            if self.styleSettings["desktopType"] == "folderview":
                removeFolderViewWidget()

            config.sync()

        # Number of Desktops
        if self.styleSettings["hasChangedDesktopNumber"]:
            hasChanged = True
            config = KConfig("kwinrc")
            group = config.group("Desktops")
            group.writeEntry('Number', self.styleSettings["desktopNumber"])
            group.sync()

            info =  kdeui.NETRootInfo(QtGui.QX11Info.display(), kdeui.NET.NumberOfDesktops | kdeui.NET.DesktopNames)
            info.setNumberOfDesktops(int(self.styleSettings["desktopNumber"]))
            info.activate()

            session = dbus.SessionBus()

            try:
                proxy = session.get_object('org.kde.kwin', '/KWin')
                proxy.reconfigure()
            except dbus.DBusException:
                pass

            config.sync()


        def deleteIconCache():
            try:
                os.remove("/var/tmp/kdecache-%s/icon-cache.kcache" % os.environ.get("USER"))
            except:
                pass

            for i in range(kdeui.KIconLoader.LastGroup):
                kdeui.KGlobalSettings.self().emitChange(kdeui.KGlobalSettings.IconChanged, i)


        # Theme Settings
        if self.styleSettings["hasChanged"]:
            if self.styleSettings["iconChanged"]:
                hasChanged = True
                configKdeGlobals = KConfig("kdeglobals")
                group = configKdeGlobals.group("General")

                groupIconTheme = configKdeGlobals.group("Icons")
                groupIconTheme.writeEntry("Theme", self.styleSettings["iconTheme"])

                configKdeGlobals.sync()

                # Change Icon theme
                kdeui.KIconTheme.reconfigure()
                kdeui.KIconCache.deleteCache()
                deleteIconCache()

            if self.styleSettings["styleChanged"]:
                hasChanged = True
                configKdeGlobals = KConfig("kdeglobals")
                group = configKdeGlobals.group("General")
                group.writeEntry("widgetStyle", self.styleSettings["styleDetails"][unicode(self.styleSettings["styleName"])]["widgetStyle"])

                #groupIconTheme = configKdeGlobals.group("Icons")
                #groupIconTheme.writeEntry("Theme", self.styleSettings["iconTheme"])
                #groupIconTheme.writeEntry("Theme", self.styleSettings["styleDetails"][unicode(self.styleSettings["styleName"])]["iconTheme"])

                configKdeGlobals.sync()

                # Change Icon theme
                kdeui.KIconTheme.reconfigure()
                kdeui.KIconCache.deleteCache()
                deleteIconCache()

                for i in range(kdeui.KIconLoader.LastGroup):
                    kdeui.KGlobalSettings.self().emitChange(kdeui.KGlobalSettings.IconChanged, i)

                # Change widget style & color
                for key, value in self.styleSettings["styleDetails"][unicode(self.styleSettings["styleName"])]["colorScheme"].items():
                    colorGroup = configKdeGlobals.group(key)
                    for key2, value2 in value.items():
                            colorGroup.writeEntry(str(key2), str(value2))

                configKdeGlobals.sync()
                kdeui.KGlobalSettings.self().emitChange(kdeui.KGlobalSettings.StyleChanged)

                configPlasmaRc = KConfig("plasmarc")
                groupDesktopTheme = configPlasmaRc.group("Theme")
                groupDesktopTheme.writeEntry("name", self.styleSettings["styleDetails"][unicode(self.styleSettings["styleName"])]["desktopTheme"])
                configPlasmaRc.sync()

                configPlasmaApplet = KConfig("plasma-desktop-appletsrc")
                group = configPlasmaApplet.group("Containments")
                for each in list(group.groupList()):
                    subgroup = group.group(each)
                    subcomponent = subgroup.readEntry('plugin')
                    if subcomponent == 'panel':
                        #print subcomponent
                        subgroup.writeEntry('location', self.styleSettings["styleDetails"][unicode(self.styleSettings["styleName"])]["panelPosition"])

                configPlasmaApplet.sync()

                configKwinRc = KConfig("kwinrc")
                groupWindowDecoration = configKwinRc.group("Style")
                groupWindowDecoration.writeEntry("PluginLib", self.styleSettings["styleDetails"][unicode(self.styleSettings["styleName"])]["windowDecoration"])
                configKwinRc.sync()

            session = dbus.SessionBus()

            try:
                proxy = session.get_object('org.kde.kwin', '/KWin')
                proxy.reconfigure()
            except dbus.DBusException:
                pass

        # Avatar Settings
        if self.avatarSettings["hasChanged"]:
            hasChanged = True

        # Services Settings
        if self.servicesSettings["hasChanged"]:
            if self.servicesSettings["enableCups"] and not self.daemon.isEnabled("cups"):
                rootActions += "enable_cups "
            elif not self.servicesSettings["enableCups"] and self.daemon.isEnabled("cups"):
                rootActions += "disable_cups "
            if self.servicesSettings["enableBluetooth"] and not self.daemon.isEnabled("bluetooth"):
                rootActions += "enable_blue "
            elif not self.servicesSettings["enableBluetooth"] and self.daemon.isEnabled("bluetooth"):
                rootActions += "disable_blue "

        # Security Settings
        if self.securitySettings["hasChanged"]:
            if self.securitySettings["enableClam"] and not self.daemon.isEnabled("clamd"):
                rootActions += "enable_clam "
            elif not self.securitySettings["enableClam"] and self.daemon.isEnabled("clamd"):
                rootActions += "disable_clam "
            if self.securitySettings["enableFire"] and not self.daemon.isEnabled("ufw"):
                rootActions += "enable_fire "
            elif not self.securitySettings["enableFire"] and self.daemon.isEnabled("ufw"):
                rootActions += "disable_fire "


        if hasChanged:
            self.killPlasma()

        if not rootActions == "":
            os.system("kdesu konsole -e kaptan-rootactions " + rootActions)

        return True
