---
layout: post
title:  "Configuration: SickRage Automatic (failed) Processing Options"
date:   2015-04-03 22:15:30
categories: documentation configuration
permalink: /documentation/configuration/processing/automatic
---

One of the most important features of the plugin is to automatically process **completed** or **failed** downloads. To configure automatic processing go to `Preferences » Sickbeard » Failed`. To *enable* automatic **failed** AND **completed** downloads processing, check the  `Enabled` checkbox. 

The remainer of the screen contains *failed* detection settings. See below for more information about **Automatic detection** and the *highly adviced* **Label plugin** integration.

**Deluge preferences - Sickbeard Plugin - Failed processing details**
![Deluge preferences - Sickbeard failed]({{ site.baseurl }}/images/Deluge preferences - Sickbeard failed.png)

## Automatic Detection

Every `Check Interval` seconds the plugin inspects each torrent which is active / downloading. Succesfully downloaded torrents are automatically processed as 'success' with SickRage. If a download is unavailable longer then N configured hours (soft limit) or downloading for more then N configured hours (hard limit), the download is considered failed and offered to SickRage as a 'failed' download. Which gives SickRage the opportunity to search for a different release, NZB or Torrent , of the requested content.

<p class="warning">Only active / downloading torrents are inspected. Paused or previously completed torrents, or torrents in an error state are ignored.</p>

### Availability Based  (Soft Limit)

If a torrent is *unavailable* for longer then N hours, it will be automatically processed to SickRage as a failed download. A download is considered *unavailable* if less then *1 full copy* is available within the connected torrent network. Enable the Deluge *Availability* column in the Torrent Grid to monitor the actual availability value per torrent. The major number (*10* for an availability of 10.998) is used by the Deluge SickRage plugin to identify the number of available copies. If this number is 0, then *no* full copies of this torrent are available and as a result the torrent is considered *unavailable*.

For more information on the availability metric see [here][vuze-availability]

### Time Based  (Hard Limit)

Regardless whether a torrent is considered available or not, after N hours, acitve/downloading torrents are automatically processed to SickRage as failed downloads. This hard limits ensures that a torrent is never longer active then N hours.

## Label Plugin

Without the use of the Deluge Label plugin, all torrents, also those which should not be processed by SickRage like music, movies or other content torrent, may be offered to SickRage for post processing automatically. To process only torrents valid for SickRage (TV Shows), it is adviced to use the Deluge Label plugin. SickRage schedules each torrent with a specific Deluge label set(*sickrage*) whilst the Deluge SickRage in its turn will **only** automatically process torrents which have this label set. 

To configure this, both SickRage and the Deluge will require matching settings.

<p class="warning">BY DEFAULT NO TORRENTS WILL BE AUTOMATICALLY PROCESSED IF THE LABEL PLUGIN IS NOT ENABLED</p>

### Deluge Settings

#### Enable Label Plugin

Deluge plugins can be enabled via `Preferences » Plugins`. Enable the 'Label' plugin.

#### Deluge SickBeard Plugin

On the `Failed` preferences tab, check *Process only torrents with label* and specify the *Label name*. This name should match the SickRage label setting set in *Add label to torrent*. See below.

### SickRage Settings

This can be done via `Sickbeard » Search Settings » Torrent Search`. See screenshot below.

**Sickbeard - Search Settings - Torrent Search - Deluge**
![Sickbeard - Search Settings - Torrent Search - Deluge]({{ site.baseurl }}/images/Sickbeard - Search Settings - Torrent Search - Deluge.png)

[vuze-availability]: https://wiki.vuze.com/w/Availability
