---
layout: post
title:  "Configuration: Connecting SickRage"
date:   2015-04-02 20:54:30
categories: documentation configuration
---

In most cases SickRage will run on the same computer as the Deluge download software. If that is the case, specify 'localhost'. The default port is '8081'. Note that plugin does not use the Sickbeard API, but used the 'normal' web method. Hence there is no need to setting the SickRage API key, but are you required to set the username/password. This can be left empty in case no username/password is required  by SickRage. See screenshost below.

Press *'Test connection'* to test the connection with SickRage. In case of errors, a short error line will be displayed. Check all settings and / or enable SickRage debugging and watch SickRage log files for any activity.

The plugin will be immediately active once the connection has been established.

**Deluge preferences - Sickbeard Plugin - Connection details**
![Deluge preferences - plugin settings]({{ site.baseurl }}/images/Deluge preferences - Sickbeard settings.png)

**Screenshot SickRage General Configuration - Interface - Web Interface:**
![SickRage General Configuration - Interface - Web Interface]({{ site.baseurl }}/images/SickRage General Configuration - Interface - Web Interface.png)

