---
title: "Policy Optimization via Importance Sampling"
collection: publ_conferences
permalink: /publication/0002-2018-Policy-Optimization-via-Importance-Sampling
acceptance: 'Acceptance rate: 1011/4856 (20.8%), Oral: 30/4856 (0.62%)'
rankCORE: 'CORE 2018: A*'
rankGGS: 'GGS 2018: A++'
date: 2018-01-01
venue: 'Advances in Neural Information Processing Systems (NeurIPS)'
paperurl: 'http://papers.nips.cc/paper/7789-policy-optimization-via-importance-sampling'
pubtype: 'conferences'
authors: ' Alberto Maria Metelli,  Matteo  Papini,  Francesco  Faccio, and  Marcello  Restelli'
citation: ' Alberto Maria Metelli,  Matteo  Papini,  Francesco  Faccio, and  Marcello  Restelli&quot;Policy Optimization via Importance Sampling.&quot; Advances in Neural Information Processing Systems (NeurIPS), 2018'
bibtexfile: '/files/bibtex/metelli2018policy.bib'
---
Abstract
 <br> Policy optimization is an effective reinforcement learning approach to solve continuous control tasks. Recent achievements have shown that alternating online and offline optimization is a successful choice for efficient trajectory reuse. However, deciding when to stop optimizing and collect new trajectories is non-trivial, as it requires to account for the variance of the objective function estimate. In this paper, we propose a novel, model-free, policy search algorithm, POIS, applicable in both action-based and parameter-based settings. We first derive a high-confidence bound for importance sampling estimation; then we define a surrogate objective function, which is optimized offline whenever a new batch of trajectories is collected. Finally, the algorithm is tested on a selection of continuous control tasks, with both linear and deep policies, and compared with state-of-the-art policy optimization methods. <br> 

 [[Link](http://papers.nips.cc/paper/7789-policy-optimization-via-importance-sampling){:target="_blank"}] [[Poster](https://albertometelli.github.io/files/poster_nips2018.pdf){:target="_blank"}] [[Slides](https://albertometelli.github.io/files/talk_nips2018.pdf){:target="_blank"}] [[Code](https://github.com/T3p/pois){:target="_blank"}] [[BibTeX](/files/bibtex/metelli2018policy.bib){:target="_blank"}] 
<pre> @incollection{metelli2018policy,
    author = "Metelli, Alberto Maria and Papini, Matteo and Faccio, Francesco and Restelli, Marcello",
    title = "Policy Optimization via Importance Sampling",
    booktitle = "Advances in Neural Information Processing Systems ({NeurIPS})",
    pages = "5447--5459",
    year = "2018",
    url = "http://papers.nips.cc/paper/7789-policy-optimization-via-importance-sampling"
} </pre>
