---
layout: post
title:  "Installation Deluge Sickbeard Plugin from source"
date:   2015-09-14 21:35:00
categories: documentation
---

_Note 1: these instructions are written for a Debian system. Procedures for other operating systems should be similar._

_Note 2: for default installation instuctions see [Installation Deluge Sickbeard Plugin][plugin-installation]_

In order to install the plugin from source, follow the steps below. For the Deluge plugin location on your platform see: [Deluge Manual install section][deluge-manual-install].

   * SRC_DIR: work directory (full path)
   * PLUGIN_DIR: Deluge plugin directory

### Download source to work directory
{% highlight bash %}
$ cd SRC_DIR
$ git clone https://github.com/srluge/DelugeSickbeardPlugin.git
{% endhighlight %}

### Build the plugin
{% highlight bash %}
cd SRC_DIR/DelugeSickbeardPlugin
$ python setup.py bdist_egg
{% endhighlight %}

### Create an egg link
{% highlight bash %}
$ cd PLUGIN_DIR
{% endhighlight %}

and create a file Sickbeard.egg-link with the following contents and make sure to substitue SRC_DIR for the actual path:
{% highlight bash %}
SRC_DIR/DelugeSickbeardPlugin
.
{% endhighlight %}

_ Note: the second line with the dot '.'_

### Restart deluge
The plugin should be available in the Deluge Web Interface after restarting Deluge. The plugin should behave exactly as if it was normally installed via the egg install. Don't forget to first enable the plugin in the configuration section of the web interface. To see if the plugin is recognized, see Deluge log files. Shortly after starting Deluge, it logs which plugins it found.

{% highlight bash %}
/etc/init.d/deluged restart
{% endhighlight %}

[deluge-manual-install]: http://dev.deluge-torrent.org/wiki/Plugins#ManualInstall
[plugin-installation]: {{ site.baseurl }}/documentation/installation
