---
layout: post
title:  "Configuration: configuration file reference"
date:   2015-04-03 23:41:30
categories: documentation configuration
permalink: /documentation/configuration/reference
---

The Deluge Sickbeard configuration file is located *~/config/deluge/sickbeard.conf*. The file is created when the the plugin is enabled for the first time in Deluge. The following options are allowed:

| **Option**        | **Default** | **Description** |
|:------------------|:------------|:----------------|
| ssl               | False       | Connect to SickRage using SSL |
| host              | 'localhost' | SickRage hostname |
| port              | 8081        | SickRage port number |
| username          | ''          | SickRage username |
| password          | ''          | SickRage password |
| method            | 'default'   | SickRage processing method |
| quiet             | True        | SickRage quiet processing output |
| force             | False       | SickRage forced processing |
| priority          | False       | SickRage priority processing |
| workers           | 3           | SickRage Deluge plugin number of workers (parallell connections to SickRage) |
| failed            | False       | Automatic processing enabled |
| failed_interval   | 60          | Check availability torrent every N seconds |
| failed_limit      | 16          | Process as failed if torrent is downloading, but unabailable longer then N hours |
| failed_time       | 24          | Process as failed if torrent is downloading longer then N hours |
| failed_label      | True        | Limit failed detection to torrents with configured label |
| failed_label_name | 'sickrage'  | Label name |
| remove            | False       | Remove processed torrents | 
| remove_data       | False       | Also remove data processed torrents |
