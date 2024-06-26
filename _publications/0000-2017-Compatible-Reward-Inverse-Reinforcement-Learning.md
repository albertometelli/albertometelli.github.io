---
title: "Compatible Reward Inverse Reinforcement Learning"
collection: publ_conferences
permalink: /publication/0000-2017-Compatible-Reward-Inverse-Reinforcement-Learning
acceptance: 'Acceptance rate: 678/3240 (20.9%)'
rankCORE: 'CORE 2017: A*'
rankGGS: 'GGS 2017: A++'
date: 2017-01-01
venue: 'Advances in Neural Information Processing Systems (NIPS)'
paperurl: 'http://papers.nips.cc/paper/6800-compatible-reward-inverse-reinforcement-learning'
pubtype: 'conferences'
authors: ' Alberto Maria Metelli,  Matteo  Pirotta, and  Marcello  Restelli'
citation: ' Alberto Maria Metelli,  Matteo  Pirotta, and  Marcello  Restelli&quot;Compatible Reward Inverse Reinforcement Learning.&quot; Advances in Neural Information Processing Systems (NIPS), 2017'
bibtexfile: '/files/bibtex/metelli2017compatible.bib'
---
Abstract
 <br> Inverse Reinforcement Learning (IRL) is an effective approach to recover a reward function that explains the behavior of an expert by observing a set of demonstrations. This paper is about a novel model-free IRL approach that, differently from most of the existing IRL algorithms, does not require to specify a function space where to search for the expert&apos;s reward function. Leveraging on the fact that the policy gradient needs to be zero for any optimal policy, the algorithm generates a set of basis functions that span the subspace of reward functions that make the policy gradient vanish. Within this subspace, using a second-order criterion, we search for the reward function that penalizes the most a deviation from the expert&apos;s policy. After introducing our approach for finite domains, we extend it to continuous ones. The proposed approach is empirically compared to other IRL methods both in the (finite) Taxi domain and in the (continuous) Linear Quadratic Gaussian (LQG) and Car on the Hill environments. <br> 

 [[Link](http://papers.nips.cc/paper/6800-compatible-reward-inverse-reinforcement-learning){:target="_blank"}] [[Poster](https://albertometelli.github.io/files/poster_nips2017.pdf){:target="_blank"}] [[Code](https://github.com/albertometelli/crirl){:target="_blank"}] [[BibTeX](/files/bibtex/metelli2017compatible.bib){:target="_blank"}] 
<pre> @incollection{metelli2017compatible,
    author = "Metelli, Alberto Maria and Pirotta, Matteo and Restelli, Marcello",
    title = "Compatible Reward Inverse Reinforcement Learning",
    booktitle = "Advances in Neural Information Processing Systems ({NIPS})",
    pages = "2047--2056",
    year = "2017",
    url = "http://papers.nips.cc/paper/6800-compatible-reward-inverse-reinforcement-learning"
} </pre>
