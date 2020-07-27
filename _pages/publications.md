---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

{% if author.googlescholar %}
  You can also find my articles on <u><a href="{{author.googlescholar}}">my Google Scholar profile</a>.</u>
{% endif %}

{% include base_path %}

<h2>International Conferences</h2>
{% for post in site.publications reversed %}
  {% if post.pubtype == 'conferences' %}
      {% include archive-single-pubs.html %}
  {% endif %}
{% endfor %}

<h2>International Journals</h2>
{% for post in site.publications reversed %}
  {% if post.pubtype == 'journals' %}
      {% include archive-single-pubs.html %}
  {% endif %}
{% endfor %}

<h2>International Workshops</h2>
{% for post in site.publications reversed %}
  {% if post.pubtype == 'workshops' %}
      {% include archive-single-pubs.html %}
  {% endif %}
{% endfor %}

<h2>In Preparation or Under Review</h2>
{% for post in site.publications reversed %}
  {% if post.pubtype == 'preparation' %}
      {% include archive-single-pubs.html %}
  {% endif %}
{% endfor %}
