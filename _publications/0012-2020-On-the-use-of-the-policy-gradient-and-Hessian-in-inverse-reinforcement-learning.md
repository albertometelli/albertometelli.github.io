---
title: "On the use of the policy gradient and Hessian in inverse reinforcement learning"
collection: publ_journals
permalink: /publication/0012-2020-On-the-use-of-the-policy-gradient-and-Hessian-in-inverse-reinforcement-learning
date: 2020-01-01
venue: 'Intelligenza Artificiale'
paperurl: 'https://doi.org/10.3233/IA-180011'
pubtype: 'journals'
authors: ' Alberto Maria Metelli,  Matteo  Pirotta, and  Marcello  Restelli'
citation: ' Alberto Maria Metelli,  Matteo  Pirotta, and  Marcello  Restelli&quot;On the use of the policy gradient and Hessian in inverse reinforcement learning.&quot; Intelligenza Artificiale, 2020.'
bibtexfile: '/files/bibtex/metelli2019ongradient.bib'
---
Abstract
 <br> Reinforcement Learning (RL) is an effective approach to solve sequential decision making problems when the environment is equipped with a reward function to evaluate the agent’s actions. However, there are several domains in which a reward function is not available and difficult to estimate. When samples of expert agents are available, Inverse Reinforcement Learning (IRL) allows recovering a reward function that explains the demonstrated behavior. Most of the classic IRL methods, in addition to expert’s demonstrations, require sampling the environment to evaluate each reward function, that, in turn, is built starting from a set of engineered features. This paper is about a novel model-free IRL approach that does not require to specify a function space where to search for the expert’s reward function. Leveraging on the fact that the policy gradient needs to be zero for an optimal policy, the algorithm generates an approximation space for the reward function, in which a reward is singled out employing a second-order criterion. After introducing our approach for finite domains, we extend it to continuous ones. The empirical results, on both finite and continuous domains, show that the reward function recovered by our algorithm allows learning policies that outperform those obtained with the true reward function, in terms of learning speed. <br> 

 [[Paper](https://doi.org/10.3233/IA-180011){:target="_blank"}] [[BibTeX](/files/bibtex/metelli2019ongradient.bib){:target="_blank"}] 
<pre> @article{metelli2019ongradient,
    author = "Metelli, Alberto Maria and Pirotta, Matteo and Restelli, Marcello",
    title = "On the use of the policy gradient and Hessian in inverse reinforcement learning",
    journal = "Intelligenza Artificiale",
    volume = "14",
    number = "1",
    pages = "117--150",
    year = "2020",
    url = "https://doi.org/10.3233/IA-180011",
    doi = "10.3233/IA-180011"
} </pre>
