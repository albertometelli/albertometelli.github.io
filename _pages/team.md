---
title: "Team"
permalink: /team/
author_profile: true
---

{% assign categories = "Faculty and Postdocs|PhD students|Research assistants" | split: "|" %}

{% for cat in categories %}
## {{ cat }}

{% assign members = site.data.team | where: "category", cat | sort: "order" %}

<div class="team-grid">
  {% for m in members %}
    <div class="team-card">
      <img class="team-photo" src="{{ m.photo | relative_url }}" alt="{{ m.name }}">
      
      <div class="team-meta">
        <div class="team-name">{{ m.name }}</div>
        {% if m.role %}<div class="team-role">{{ m.role }}</div>{% endif %}
        {% if m.qualification %}<div class="team-qual">{{ m.qualification }}</div>{% endif %}
        
        {% if m.links %}
          <div class="team-links">
            {% for l in m.links %}
              <a href="{{ l.url }}" target="_blank" rel="noopener">{{ l.label }}</a>
            {% endfor %}
          </div>
        {% endif %}
      </div>
    </div>
  {% endfor %}
</div>

{% endfor %}
