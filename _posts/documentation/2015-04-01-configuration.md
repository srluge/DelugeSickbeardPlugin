---
layout: post
title:  "Configuration Deluge Sickbeard Plugin"
date:   2015-04-01 11:09:30
categories: documentation
---

Directly after installing the plugin a new preferences category, Sickbeard, will be available in Deluge. See screenshot below. To locate the Deluge Sickbeard plugin settings in the Deluge web user interface(no support for the GTK UI), go to Perferences and select the category Sickbeard. For manual configuration, for example when only using the GTK interface, see the [Configuration file reference documentation][config-reference].

Minimal recommended configuration steps:

   1. [Create a connection with SickRage][config-connecting]
   *  [Enable automatic (failed) processing][config-auto]
   *  [Enable usage of labels in Deluge and SickRage][config-auto]
   
## Preferences sections

  * [Connecting to SickRage preferences][config-connecting]
  * [Processing preferences][config-processing]
  * [Automatic processing preferences][config-auto]
  * [Configuration file reference / Manual configuration][config-reference]

## Deluge preferences - Plugin Preferences Screenshot

![Deluge preferences - plugin settings]({{ site.baseurl }}/images/Deluge preferences - Sickbeard settings.png)


[config-connecting]: {{ site.baseurl }}/documentation/configuration/connecting
[config-processing]: {{ site.baseurl }}/documentation/configuration/processing
[config-auto]: {{ site.baseurl }}/documentation/configuration/processing/automatic
[config-reference]: {{ site.baseurl }}/documentation/configuration/reference

