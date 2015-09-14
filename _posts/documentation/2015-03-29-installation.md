---
layout: post
title:  "Installation Deluge Sickbeard Plugin"
date:   2015-03-29 01:26:30
categories: documentation
---

The installation of this plugin is straight forward. First make sure to check the [requirements][plugin-requirements] page. Then follow the instructions below. Choose between: (Web) *GUI installation*, *Manual installation* or *Client/Server installation*. For more information on installing Deluge plugins, visit the [Deluge Installing Plugins][deluge-install] page. Take note of how to deal with python version differences and take note of the client/server setup instructions if relevant.

As an alternative to the default egg based installation, the plugin can also be installed from source. In that case follow the instructions on [Installation Deluge Sickbeard Plugin from source][plugin-install-from-source]

Next step after installation below: [Configuration Deluge Sickbeard Plugin][plugin-configuration]

## (Web) GUI installation

  1. Download the latest [Deluge SickBeard Plugin egg][egg] to your computer.
  *  Open the Deluge GUI
  *  Then *Preferences* -> *Plugins* -> *Install plugin*
  *  Locate the Deluge SickBeard Plugin egg previously downloaded to your computer
  *  Press install
  *  Restart Deluge
  
     ![]({{ site.baseurl }}/images/Deluge preferences - install plugin.png)  
  
## Manual installation

### Unix/Linux

{% highlight bash %}
$ cd ~/.config/deluge/plugins
$ wget {{ site.egg-base-url }}/{{ site.egg-base-name }}-{{ site.egg-latest-version }}.egg
{% endhighlight %}

After downloading the egg, restart Deluge.

### Windows

  1. Download the latest [Deluge SickBeard Plugin egg][egg] to your computer.
  *  Copy the downloaded Deluge SickBeard Plugin egg to *%APPDATA%\deluge\plugins*
  *  Restart Deluge
   
### Client/Server setup

  Make sure to follow above instructions on both the server and client.

[deluge]: http://deluge-torrent.org/
[deluge-label]: http://dev.deluge-torrent.org/wiki/Plugins
[deluge-web-ui]: http://dev.deluge-torrent.org/wiki/UserGuide/ThinClient#WebUI
[deluge-install]: http://dev.deluge-torrent.org/wiki/Plugins#InstallingPlugins
[srluge]: {{ site.user-url }}
[srluge-sickrage]: https://github.com/srluge/SickRage
[srluge-sickrage-issues]: https://github.com/srluge/SickRage/issues
[sickrage]: https://github.com/SiCKRAGETV/SickRage
[sickbeard]: http://sickbeard.com/
[egg]: {{ site.egg-base-url }}/{{ site.egg-base-name }}-{{ site.egg-latest-version }}.egg
[plugin-requirements]: {{ site.baseurl }}/documentation/requirements
[plugin-configuration]: {{ site.baseurl }}/documentation/configuration
[plugin-install-from-source]: {{ site.baseurl }}/documentation/development
