---
layout: default
title: Deluge Sickbeard Plugin
css: table
---

# Deluge Sickbeard Plugin <img src="{{ site.baseurl }}/images/deluge.png" height="64px" width="64px" style="float: right; margin: 0 1 1 0;"/>
**Automatically** or manually process **completed** or **failed** Deluge *torrent* downloads with SickRage. Provides full *torrent* integration of [Deluge][deluge] with [SickRage][sickrage], a fork of [Sickbeard][sickbeard].

* Complete integration with SickRage *failed download handling*
* **Automatically** process **completed** Torrents with SickRage
* **Automatically** process **failed** Torrents with SickRage
* Manually (bulk) process Torrents with SickRage
* 'Download *processing* status' visible per Torrent in Deluge UI
* 'Download *failed* status' visible per Torrent in Deluge UI
* Easy configuration

Quick installation guide [here][quick-install]. For user documentation visit the [documentation][documentation] section. Issues can be filed using the [GitHub Issues][github-issues] tracker. For an impression see the various screenshots below or consult the user documentation.


# SickRage versus Sickbeard
In honor of all the excellent work done by the Sickbeard developer(s) and community, this plugin is called the Deluge **Sickbeard** Plugin. Unfortunately Sickbeard is not up-to-speed on torrent integration, failed download handling and seems slow in accepting new features or other improvements. SickRage development on the other hand seems more alive, active, open, and includes failed download support.

# User Interface

| **Description**   | **Screenshot**    |
|:------------- |:------------- |
| Deluge torrent grid - processing status. Additional status columns are added to the Deluge Torrent grid. Click on the *'info'* icon in the *Processing Status* column to open the SickRage post-processing status and output dialog. See next screenshot. | ![Deluge torrent grid - processing statusg]({{ site.baseurl }}/images/Deluge torrent grid - processing status.png) [Deluge torrent grid - processing status]({{ site.baseurl }}/images/Deluge torrent grid - processing status.png)  |
| Deluge torrent grid - post processing log. Display per-torrent SickRage post-processing status and output log. | ![Deluge torrent grid - post processing log]({{ site.baseurl }}/images/Deluge torrent grid - post processing log.png) [Deluge torrent grid - post processing dialog]({{ site.baseurl }}/images/Deluge torrent grid - post processing log.png) |
| Deluge torrent grid - context menu. **Manually** process a **completed** or **failed** torrent with SickRage.  | ![Deluge torrent grid - context menu]({{ site.baseurl }}/images/Deluge torrent grid - context menu.png)  |

[deluge]: http://deluge-torrent.org/
[sickrage]: https://github.com/SiCKRAGETV/SickRage
[sickbeard]: http://sickbeard.com/
[quick-install]: {{ site.baseurl }}/documentation/installation
[documentation]: {{ site.baseurl }}/documentation/index
[github-issues]: {{ site.project-url }}/issues

