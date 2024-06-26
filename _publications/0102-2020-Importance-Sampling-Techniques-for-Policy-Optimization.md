---
title: "Importance Sampling Techniques for Policy Optimization"
collection: publ_journals
permalink: /publication/0102-2020-Importance-Sampling-Techniques-for-Policy-Optimization
rankCORE: 'CORE 2020: A*'
rankSJR: 'SJR 2020: Q1'
date: 2020-01-01
venue: 'Journal of Machine Learning Research'
paperurl: 'http://jmlr.org/papers/v21/20-124.html'
pubtype: 'journals'
authors: ' Alberto Maria Metelli,  Matteo  Papini,  Nico  Montali, and  Marcello  Restelli'
citation: ' Alberto Maria Metelli,  Matteo  Papini,  Nico  Montali, and  Marcello  Restelli&quot;Importance Sampling Techniques for Policy Optimization.&quot; Journal of Machine Learning Research, 2020'
bibtexfile: '/files/bibtex/metelli2020importance.bib'
---
Abstract
 <br> How can we effectively exploit the collected samples when solving a continuous control task with Reinforcement Learning? Recent results have empirically demonstrated that multiple policy optimization steps can be performed with the same batch by using off-distribution techniques based on importance sampling. However, when dealing with off-distribution optimization, it is essential to take into account the uncertainty introduced by the importance sampling process. In this paper, we propose and analyze a class of model-free, policy search algorithms that extend the recent Policy Optimization via Importance Sampling (Metelli et al., 2018) by incorporating two advanced variance reduction techniques: per-decision and multiple importance sampling. For both of them, we derive a high-probability bound, of independent interest, and then we show how to employ it to define a suitable surrogate objective function that can be used for both action-based and parameter-based settings. The resulting algorithms are finally evaluated on a set of continuous control tasks, using both linear and deep policies, and compared with modern policy optimization methods. <br> 

 [[Link](http://jmlr.org/papers/v21/20-124.html){:target="_blank"}] [[BibTeX](/files/bibtex/metelli2020importance.bib){:target="_blank"}] 
<pre> @article{metelli2020importance,
    author = "Metelli, Alberto Maria and Papini, Matteo and Montali, Nico and Restelli, Marcello",
    title = "Importance Sampling Techniques for Policy Optimization",
    journal = "Journal of Machine Learning Research",
    year = "2020",
    volume = "21",
    number = "141",
    pages = "1-75",
    url = "http://jmlr.org/papers/v21/20-124.html"
} </pre>
