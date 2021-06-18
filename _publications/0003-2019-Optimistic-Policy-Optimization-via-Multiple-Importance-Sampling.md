---
title: "Optimistic Policy Optimization via Multiple Importance Sampling"
collection: publ_conferences
permalink: /publication/0003-2019-Optimistic-Policy-Optimization-via-Multiple-Importance-Sampling
acceptance: 'Acceptance rate: 773/3424 (22.6%)'
date: 2019-01-01
venue: 'Proceedings of the 36th International Conference on Machine Learning, ICML 2019, 9-15 June 2019, Long Beach, California, USA'
paperurl: 'http://proceedings.mlr.press/v97/papini19a.html'
pubtype: 'conferences'
authors: ' Matteo  Papini,  Alberto Maria Metelli,  Lorenzo  Lupo, and  Marcello  Restelli'
citation: ' Matteo  Papini,  Alberto Maria Metelli,  Lorenzo  Lupo, and  Marcello  Restelli&quot;Optimistic Policy Optimization via Multiple Importance Sampling.&quot; Proceedings of the 36th International Conference on Machine Learning, ICML 2019, 9-15 June 2019, Long Beach, California, USA, 2019.'
bibtexfile: '/files/bibtex/papini2019optimistic.bib'
---
Abstract
 <br> Policy Search (PS) is an effective approach to Reinforcement Learning (RL) for solving control tasks with continuous state-action spaces. In this paper, we address the exploration-exploitation trade-off in PS by proposing an approach based on Optimism in the Face of Uncertainty. We cast the PS problem as a suitable Multi Armed Bandit (MAB) problem, defined over the policy parameter space, and we propose a class of algorithms that effectively exploit the problem structure, by leveraging Multiple Importance Sampling to perform an off-policy estimation of the expected return. We show that the regret of the proposed approach is bounded by $\widetilde{\mathcal{O}}(\sqrt{T})$ for both discrete and continuous parameter spaces. Finally, we evaluate our algorithms on tasks of varying difficulty, comparing them with existing MAB and RL algorithms. <br> 

 [[Paper](http://proceedings.mlr.press/v97/papini19a.html){:target="_blank"}] [[Poster](https://t3p.github.io/download/poster_optimist.pdf){:target="_blank"}] [[Slides](https://icml.cc/media/Slides/icml/2019/104(11-14-00)-11-14-25-5158-optimistic_poli.pdf){:target="_blank"}] [[Code](https://github.com/WolfLo/optimist){:target="_blank"}] [[BibTeX](/files/bibtex/papini2019optimistic.bib){:target="_blank"}] 
<pre> @inproceedings{papini2019optimistic,
    author = "Papini, Matteo and Metelli, Alberto Maria and Lupo, Lorenzo and Restelli, Marcello",
    editor = "Chaudhuri, Kamalika and Salakhutdinov, Ruslan",
    title = "Optimistic Policy Optimization via Multiple Importance Sampling",
    booktitle = "Proceedings of the 36th International Conference on Machine Learning, {ICML} 2019, 9-15 June 2019, Long Beach, California, {USA}",
    series = "Proceedings of Machine Learning Research",
    volume = "97",
    pages = "4989--4999",
    publisher = "{PMLR}",
    year = "2019",
    url = "http://proceedings.mlr.press/v97/papini19a.html"
} </pre>
