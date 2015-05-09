---
layout: post
title:  "Requirements Deluge Sickbeard Plugin"
date:   2015-04-01 01:24:30
categories: documentation
---

| **Type** | **Description** |
|:--------|:---------------|
| Required | [Deluge][deluge]. Any recent version of Deluge should do fine. |
| Recommended | [Deluge Label Plugin][deluge-label]. Shipped by default with Deluge. |
| Recommended | [Deluge Web UI][deluge-web-ui]. Shipped by default with Deluge. The Deluge Sickbeard Plugin can be configured using the Web-UI. No configuration support for the Deluge console client or Deluge GTK client. The plugin can be configured manually, without UI, by adjusting the plugin configuration file directly. |
| Required | [srluge/SickRage][srluge-sickrage]. [SickRage][sickrage], a [Sickbeard][sickbeard] fork, provides proper support for Torrent searching and downloading as well as failed download handling. The [srluge/SickRage][srluge-sickrage] fork contains several small **required** post-processing fixes. Once the code matures, the changes in this fork will be offered to the SickRage main project (pull-request). Until then it is recommended to use this fork and not the SickRage main project. The [srluge/SickRage][srluge-sickrage] fork is regularly kept up-to-date with the SickRage main project. File an [issue][srluge-sickrage-issues] in case the fork deviates to much. |
| Recommended | SabNZB or other NZB downloader. Using both NZB and Torrent with SickRage will provide improved coverage. SabNZB, and with this plugin Deluge, both provide automatic (failed) download processing with SickRage. |

[deluge]: http://deluge-torrent.org/
[deluge-label]: http://dev.deluge-torrent.org/wiki/Plugins
[deluge-web-ui]: http://dev.deluge-torrent.org/wiki/UserGuide/ThinClient#WebUI
[srluge]: {{ site.user-url }}
[srluge-sickrage]: https://github.com/srluge/SickRage
[srluge-sickrage-issues]: https://github.com/srluge/SickRage/issues
[sickrage]: https://github.com/SiCKRAGETV/SickRage
[sickbeard]: http://sickbeard.com/
