---
title: "Policy Optimization via Optimal Policy Evaluation"
collection: publ_workshops
permalink: /publication/0208-2021-Policy-Optimization-via-Optimal-Policy-Evaluation
date: 2021-01-01
venue: 'Deep Reinforcement Learning Workshop - NeurIPS 2021'
paperurl: 'https://openreview.net/forum?id=iseuu3iLqn'
pubtype: 'workshops'
authors: ' Alberto Maria Metelli,  Samuele  Meta, and  Marcello  Restelli'
citation: ' Alberto Maria Metelli,  Samuele  Meta, and  Marcello  Restelli&quot;Policy Optimization via Optimal Policy Evaluation.&quot; Deep Reinforcement Learning Workshop - NeurIPS 2021, 2021'
bibtexfile: '/files/bibtex/metelli2021optimalis.bib'
---
Abstract
 <br> Off-policy methods are the basis of a large number of effective Policy Optimization (PO) algorithms. In this setting, Importance Sampling (IS) is typically employed as a what-if analysis tool, with the goal of estimating the performance of a target policy, given samples collected with a different behavioral policy. However, in Monte Carlo simulation, IS represents a variance minimization approach. In this field, a suitable behavioral distribution is employed for sampling, allowing diminishing the variance of the estimator below the one achievable when sampling from the target distribution. In this paper, we analyze IS in these two guises, showing the connections between the two objectives. We illustrate that variance minimization can be used as a performance improvement tool, with the advantage, compared with direct off-policy learning, of implicitly enforcing a trust region. We make use of these theoretical findings to build a PO algorithm, Policy Optimization via Optimal Policy Evaluation (PO2PE), that employs variance minimization as an inner loop. Finally, we present empirical evaluations on continuous RL benchmarks, with a particular focus on the robustness to small batch sizes. <br> 

 [[Link](https://openreview.net/forum?id=iseuu3iLqn){:target="_blank"}] [[BibTeX](/files/bibtex/metelli2021optimalis.bib){:target="_blank"}] 
<pre> @article{metelli2021optimalis,
    author = "Metelli, Alberto Maria and Meta, Samuele and Restelli, Marcello",
    title = "Policy Optimization via Optimal Policy Evaluation",
    journal = "Deep Reinforcement Learning Workshop - NeurIPS 2021",
    year = "2021",
    url = "https://openreview.net/forum?id=iseuu3iLqn"
} </pre>
