---
title: "Policy Optimization as Online Learning with Mediator Feedback"
collection: publ_conferences
permalink: /publication/0010-2021-Policy-Optimization-as-Online-Learning-with-Mediator-Feedback
acceptance: 'Acceptance rate: 1692/7911 (21.4%)'
rankCORE: 'CORE 2021: A*'
rankGGS: 'GGS 2021: A++'
date: 2021-01-01
venue: 'The Thirty-Fifth AAAI Conference on Artificial Intelligence (AAAI)'
paperurl: 'https://ojs.aaai.org/index.php/AAAI/article/view/17083'
pubtype: 'conferences'
authors: ' Alberto Maria Metelli*,  Matteo  Papini*,  Pierluca  D&apos;Oro, and  Marcello  Restelli'
citation: ' Alberto Maria Metelli*,  Matteo  Papini*,  Pierluca  D&apos;Oro, and  Marcello  Restelli&quot;Policy Optimization as Online Learning with Mediator Feedback.&quot; The Thirty-Fifth AAAI Conference on Artificial Intelligence (AAAI), 2021'
bibtexfile: '/files/bibtex/metelli2021policy.bib'
---
Abstract
 <br> Policy Optimization (PO) is a widely used approach to address continuous control tasks. In this paper, we introduce the notion of mediator feedback that frames PO as an online learning problem over the policy space. The additional available information, compared to the standard bandit feedback, allows reusing samples generated by one policy to estimate the performance of other policies. Based on this observation, we propose an algorithm, RANDomized-exploration policy Optimization via Multiple Importance Sampling with Truncation (RANDOMIST), for regret minimization in PO, that employs a randomized exploration strategy, differently from the existing optimistic approaches. When the policy space is finite, we show that under certain circumstances, it is possible to achieve constant regret, while always enjoying logarithmic regret. We also derive problem-dependent regret lower bounds. Then, we extend RANDOMIST to compact policy spaces. Finally, we provide numerical simulations on finite and compact policy spaces, in comparison with PO and bandit baselines. <br> 

 [[Link](https://ojs.aaai.org/index.php/AAAI/article/view/17083){:target="_blank"}] [[Poster](https://albertometelli.github.io/files/poster_aaai2021.pdf){:target="_blank"}] [[Slides](https://albertometelli.github.io/files/slides_aaai2021.pdf){:target="_blank"}] [[Code](https://github.com/proceduralia/randomist){:target="_blank"}] [[Talk](https://slideslive.com/38949290){:target="_blank"}] [[Supplementary](https://arxiv.org/abs/2012.08225){:target="_blank"}] [[BibTeX](/files/bibtex/metelli2021policy.bib){:target="_blank"}] 
<pre> @incollection{metelli2021policy,
    author = "Metelli*, Alberto Maria and Papini*, Matteo and D'Oro, Pierluca and Restelli, Marcello",
    title = "Policy Optimization as Online Learning with Mediator Feedback",
    booktitle = "The Thirty-Fifth {AAAI} Conference on Artificial Intelligence ({AAAI})",
    publisher = "{AAAI} Press",
    year = "2021",
    pages = "8958--8966",
    url = "https://ojs.aaai.org/index.php/AAAI/article/view/17083"
} </pre>