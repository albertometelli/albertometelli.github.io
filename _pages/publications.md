---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---
{% include base_path %}


{% if page.author and site.data.authors[page.author] %}
  {% assign author = site.data.authors[page.author] %}{% else %}{% assign author = site.author %}
{% endif %}

<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/jpswalsh/academicons@1/css/academicons.min.css">

[<i class="ai ai-google-scholar ai-1x fa-align-center"></i>]({{ author.googlescholar }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp;[Google Scholar]({{ author.googlescholar }}){:target="_blank"}{:rel="noopener noreferrer"}
&emsp;[<i class="ai ai-researchgate ai-1x"></i>]({{ author.researchgate }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp; [ResearchGate]({{ author.researchgate }}){:target="_blank"}{:rel="noopener noreferrer"}
&emsp;[<i class="ai ai-orcid ai-1x"></i>]({{ author.orcid }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp;[ORCID]({{ author.orcid }}){:target="_blank"}{:rel="noopener noreferrer"}
&emsp;[<i class="ai ai-dblp ai-1x"></i>]({{ author.dblp }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp;[dblp]({{ author.dblp }}){:target="_blank"}{:rel="noopener noreferrer"}
&emsp;[<i class="ai ai-scopus ai-1x"></i>]({{ author.scopus }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp;[Scopus]({{ author.scopus }}){:target="_blank"}{:rel="noopener noreferrer"}
&emsp;[<i class="ai ai-semantic-scholar ai-1x"></i>]({{ author.semantic-scholar }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp;[Semantic Scholar]({{ author.semantic-scholar }}){:target="_blank"}{:rel="noopener noreferrer"}
&emsp;[<i class="ai ai-publons ai-1x"></i>]({{ author.publons }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp;[Publons]({{ author.publons }}){:target="_blank"}{:rel="noopener noreferrer"}


* <b>Scientific Productivity</b> (updated December 2023): 41 publications, 51 co-authors according to Scopus
* <b>Publication Impact</b> (updated December 2023): 713 citations and  h-index 15 according to Google Scholar

<!--
<p style="background-color:blue;">
* <b>Scientific Productivity</b> (updated December 2023): 41 publications, 51 co-authors according to Scopus
* <b>Publication Impact</b> (updated December 2023): 713 citations and  h-index 15 according to Google Scholar
</p>
-->

<h2>Books</h2>
<ol>
{% for post in site.publications reversed %}
{% if post.pubtype == 'book' %}
<li>
{% include archive-single-pubs.html %}
</li>
{% endif %}
{% endfor %}
</ol> 

<h2>Book Chapters</h2>
<ol>
{% for post in site.publications reversed %}
{% if post.pubtype == 'bookchapter' %}
<li>
{% include archive-single-pubs.html %}
</li>
{% endif %}
{% endfor %}
</ol> 

<h2>International Journal Articles</h2>
<ol>
{% for post in site.publications reversed %}
{% if post.pubtype == 'journals' %}
<li>
{% include archive-single-pubs.html %}
</li>
{% endif %}
{% endfor %}
</ol> 

<h2>International Conference Papers</h2>
<ol>
{% for post in site.publications reversed %}
{% if post.pubtype == 'conferences' %}
<li>
{% include archive-single-pubs.html %}
</li>
{% endif %}
{% endfor %}
</ol> 

<h2>International Workshop Papers</h2>
<ol>
{% for post in site.publications reversed %}
{% if post.pubtype == 'workshops' %}
<li>
{% include archive-single-pubs.html %}
</li>
{% endif %}
{% endfor %}
</ol> 

<h2>International Conference Abstracts</h2>
<ol>
{% for post in site.publications reversed %}
{% if post.pubtype == 'abstract' %}
<li>
{% include archive-single-pubs.html %}
</li>
{% endif %}
{% endfor %}
</ol> 

<h2>Theses</h2>
<ol>
{% for post in site.publications reversed %}
{% if post.pubtype == 'thesis' %}
<li>
{% include archive-single-pubs.html %}
</li>
{% endif %}
{% endfor %}
</ol> 

