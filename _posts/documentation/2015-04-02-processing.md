---
layout: post
title:  "Configuration: SickRage Post-processing Options"
date:   2015-04-02 21:05:30
categories: documentation configuration
---

The SickRage processing options allow adjusting how the torrent is going to be processed. Open the processing options by going to `Preferences » Sickbeard » Processing`. Follow the instructions on that settings windows. When hovering over an input field, additional information and hints are presented in a small pop-up.

De number of 'Workers' determines the level of parallelization. Don't set this number to high. It may congest your computer, or overload SickRage. It is unsure if SickRage/Sickbeard are safely capable of parallelization. To be really on the safe side, just set '1'; in other words disable any parallelization. Parallelization can be of use when manually bulk processing a lot of completed / failed downloads at once.

**Deluge preferences - Sickbeard Plugin - Processing details**
![Deluge preferences - Sickbeard processing]({{ site.baseurl }}/images/Deluge preferences - Sickbeard processing.png)
