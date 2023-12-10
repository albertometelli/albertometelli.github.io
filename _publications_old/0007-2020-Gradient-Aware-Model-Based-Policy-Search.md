---
title: "Gradient-Aware Model-Based Policy Search"
collection: publ_conferences
permalink: /publication/0007-2020-Gradient-Aware-Model-Based-Policy-Search
acceptance: 'Acceptance rate: 1591/7737 (20.6%)'
rankCORE: 'CORE 2020: A*'
rankGGS: 'GGS 2018: A++'
date: 2020-01-01
venue: 'The Thirty-Fourth AAAI Conference on Artificial Intelligence (AAAI)'
paperurl: 'https://doi.org/10.1609/aaai.v34i04.5791'
pubtype: 'conferences'
authors: ' Pierluca  D&apos;Oro*,  Alberto Maria Metelli*,  Andrea  Tirinzoni,  Matteo  Papini, and  Marcello  Restelli'
citation: ' Pierluca  D&apos;Oro*,  Alberto Maria Metelli*,  Andrea  Tirinzoni,  Matteo  Papini, and  Marcello  Restelli&quot;Gradient-Aware Model-Based Policy Search.&quot; The Thirty-Fourth AAAI Conference on Artificial Intelligence (AAAI), 2020'
bibtexfile: '/files/bibtex/doro2020gradient.bib'
---
Abstract
 <br> Traditional model-based reinforcement learning approaches learn a model of the environment dynamics without explicitly considering how it will be used by the agent. In the presence of misspecified model classes, this can lead to poor estimates, as some relevant available information is ignored. In this paper, we introduce a novel model-based policy search approach that exploits the knowledge of the current agent policy to learn an approximate transition model, focusing on the portions of the environment that are most relevant for policy improvement. We leverage a weighting scheme, derived from the minimization of the error on the model-based policy gradient estimator, in order to define a suitable objective function that is optimized for learning the approximate transition model. Then, we integrate this procedure into a batch policy improvement algorithm, named Gradient-Aware Model-based Policy Search (GAMPS), which iteratively learns a transition model and uses it, together with the collected trajectories, to compute the new policy parameters. Finally, we empirically validate GAMPS on benchmark domains analyzing and discussing its properties. <br> 

 [[Link](https://doi.org/10.1609/aaai.v34i04.5791){:target="_blank"}] [[Supplementary](https://arxiv.org/abs/1909.04115){:target="_blank"}] [[BibTeX](/files/bibtex/doro2020gradient.bib){:target="_blank"}] 
<pre> @inproceedings{doro2020gradient,
    author = "D'Oro*, Pierluca and Metelli*, Alberto Maria and Tirinzoni, Andrea and Papini, Matteo and Restelli, Marcello",
    title = "Gradient-Aware Model-Based Policy Search",
    booktitle = "The Thirty-Fourth {AAAI} Conference on Artificial Intelligence ({AAAI})",
    pages = "3801--3808",
    year = "2020",
    url = "https://doi.org/10.1609/aaai.v34i04.5791"
} </pre>
