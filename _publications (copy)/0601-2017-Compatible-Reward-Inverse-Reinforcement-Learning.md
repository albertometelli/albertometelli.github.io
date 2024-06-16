---
title: "Compatible Reward Inverse Reinforcement Learning"
collection: publ_preparation
permalink: /publication/0601-2017-Compatible-Reward-Inverse-Reinforcement-Learning
date: 2017-07-01
venue: 'Politecnico di Milano'
paperurl: 'http://hdl.handle.net/10589/135141'
pubtype: 'thesis'
authors: ' Alberto Maria Metelli'
citation: ' Alberto Maria Metelli&quot;Compatible Reward Inverse Reinforcement Learning.&quot; Politecnico di Milano, 2017'
bibtexfile: '/files/bibtex/mastersthesis.bib'
---
Abstract
 <br> Sequential decision making problems arise in a variety of areas in Artificial Intelligence. Reinforcement Learning proposes a number of algorithms able to learn an optimal behavior by interacting with the environment. The major assumption is that the learning agent receives a reward as soon as an action is performed. However, there are several application domains in which a reward function is not available and difficult to estimate, but samples of expert agents playing an optimal policy are simple to generate. Inverse Reinforcement Learning (IRL) is an effective approach to recover a reward function that explains the behavior of an expert by observing a set of demonstrations. Most of the classic IRL methods, in addition to expert&apos;s demonstrations, require sampling the environment in order to compute the optimal policy for each candidate reward function. Furthermore, in most of the cases, it is necessary to specify a priori a set of engineered features that the algorithms combine to single out the reward function. This thesis is about a novel model-free IRL approach that, differently from most of the existing IRL algorithms, does not require to specify a function space where to search for the expert&apos;s reward function. Leveraging on the fact that the policy gradient needs to be zero for any optimal policy, the algorithm generates a set of basis functions that span the subspace of reward functions that make the policy gradient vanish. Within this subspace, using a second-order criterion, we search for the reward function that penalizes the most a deviation from the expert&apos;s policy. After introducing our approach for finite domains, we extend it to continuous ones. The proposed approach is compared to state-of-the-art IRL methods both in the (finite) Taxi domain and in the (continuous) Linear Quadratic Gaussian Regulator and Car on the Hill environments. The empirical results show that the reward function recovered by our algorithm allows learning policies that outperform both behavioral cloning and those obtained with the true reward function, in terms of learning speed. <br> 

 [[Link](http://hdl.handle.net/10589/135141){:target="_blank"}] [[Slides](https://albertometelli.github.io/files/slides_msc_thesis.pdf){:target="_blank"}] [[BibTeX](/files/bibtex/mastersthesis.bib){:target="_blank"}] 
<pre> @mastersthesis{mastersthesis,
    author = "Metelli, Alberto Maria",
    title = "Compatible Reward Inverse Reinforcement Learning",
    school = "Politecnico di Milano",
    year = "2017",
    month = "July",
    doi = "http://hdl.handle.net/10589/135141",
    keywords = "Reinforcement Learning, Inverse Reinforcement Learning, Policy Gradient, Feature Extraction",
    supervisor = "Prof. Marcello Restelli (Politecnico di Milano, Italy)",
    url = "http://hdl.handle.net/10589/135141"
} </pre>
