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


<div style="background-color: #8FB4E6; overflow: hidden;">
<ul style="background-color:#8FB4E6;">
<li><b>Scientific Productivity</b> (updated June 2024): 61 publications, 63 co-authors according to Scopus</li>
<ul>
	<li>
		<u>Peer-reviewed International Journal articles</u>: <b>13 publications</b> (4 as main contributor, 1 single-author), including <b>JMLR</b> (<b>2</b>), <b>Machine Learning</b> (<b>3</b>), <b>RAS</b> (<b>1</b>), <b>ESWA</b> (<b>1</b>), <b>IEEE TNNLS</b> (<b>1</b>), <b>IEEE T-ITS</b> (<b>1</b>), and <b>DMKD</b> (<b>1</b>)
	</li>
	<li>
		<u>Peer-reviewed Intenrational Conference papers</u>: <b>48 publications</b> (11 as main contributor), including <b>ICML</b> (<b>16</b>), <b>NeurIPS</b> (<b>8</b>), <b>AAAI</b> (<b>7</b>), <b>IJCAI</b> (<b>1</b>), <b>AISTATS</b> (<b>4</b>), <b>COLT</b> (<b>2</b>), and <b>UAI</b> (<b>1</b>)
	</li>
</ul>
<li><b>Publication Impact</b> (updated June 2024): 891 citations and  h-index 17 according to Google Scholar</li>
</ul>
</div>


[<i class="ai ai-google-scholar ai-1x fa-align-center"></i>]({{ author.googlescholar }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp;[Google Scholar]({{ author.googlescholar }}){:target="_blank"}{:rel="noopener noreferrer"}
&emsp;[<i class="ai ai-researchgate ai-1x"></i>]({{ author.researchgate }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp; [ResearchGate]({{ author.researchgate }}){:target="_blank"}{:rel="noopener noreferrer"}
&emsp;[<i class="ai ai-orcid ai-1x"></i>]({{ author.orcid }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp;[ORCID]({{ author.orcid }}){:target="_blank"}{:rel="noopener noreferrer"}
&emsp;[<i class="ai ai-dblp ai-1x"></i>]({{ author.dblp }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp;[dblp]({{ author.dblp }}){:target="_blank"}{:rel="noopener noreferrer"}
&emsp;[<i class="ai ai-scopus ai-1x"></i>]({{ author.scopus }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp;[Scopus]({{ author.scopus }}){:target="_blank"}{:rel="noopener noreferrer"}
&emsp;[<i class="ai ai-semantic-scholar ai-1x"></i>]({{ author.semantic-scholar }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp;[Semantic Scholar]({{ author.semantic-scholar }}){:target="_blank"}{:rel="noopener noreferrer"}
&emsp;[<i class="ai ai-publons ai-1x"></i>]({{ author.publons }}){:target="_blank"}{:rel="noopener noreferrer"}&nbsp;[Publons]({{ author.publons }}){:target="_blank"}{:rel="noopener noreferrer"}



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

