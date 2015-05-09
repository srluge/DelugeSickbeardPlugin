---
layout: default
title: Deluge Sickbeard Plugin Documentation
permalink: /documentation/
---

<div id="home">
  <h1>Documentation</h1>
  <ul class="posts">
    {% for post in site.posts %}
      <li><a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a></li>
    {% endfor %}
  </ul>
</div>
