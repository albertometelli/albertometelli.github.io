---
title: "Gradient-Aware Model-based Policy Search"
collection: publ_workshops
permalink: /publication/0015-2019-Gradient-Aware-Model-based-Policy-Search
date: 2019-01-01
venue: 'Workshop on Meta-Learning (MetaLearn 2019) @NeurIPS 2019'
pubtype: 'workshops'
authors: ' Pierluca  D&apos;Oro,  Alberto Maria Metelli,  Andrea  Tirinzoni,  Matteo  Papini, and  Marcello  Restelli'
citation: ' Pierluca  D&apos;Oro,  Alberto Maria Metelli,  Andrea  Tirinzoni,  Matteo  Papini, and  Marcello  Restelli&quot;Gradient-Aware Model-based Policy Search.&quot; Workshop on Meta-Learning (MetaLearn 2019) @NeurIPS 2019, 2019.'
bibtexfile: '/files/bibtex/doro2019gradientWorkshop.bib'
---
Abstract
 <br> Traditional MBRL approaches learn a model of the environment dynamics without explicitly considering how it will be used by the agent. In the presence of misspecified model classes, this can lead to poor estimates, as some relevant information is ignored. In this paper, we introduce a model-based policy search approach that, by meta-learning, exploits the knowledge of the current agent policy to learn an approximate transition model, focusing on the portions of the environment that are most relevant for policy improvement. We integrate gradient-aware model learning into a batch policy improvement algorithm, named Gradient-Aware Model-based Policy Search (GAMPS), which iteratively learns a transition model and uses it, together with the collected trajectories, to update the policy. Finally, we empirically validate GAMPS on benchmark domains analyzing and discussing its properties. <br> 
[[BibTeX](/files/bibtex/doro2019gradientWorkshop.bib){:target="_blank"}] 
<pre> @article{doro2019gradientWorkshop,
    author = "D'Oro, Pierluca and Metelli, Alberto Maria and Tirinzoni, Andrea and Papini, Matteo and Restelli, Marcello",
    title = "Gradient-Aware Model-based Policy Search",
    journal = "Workshop on Meta-Learning (MetaLearn 2019) @NeurIPS 2019",
    year = "2019"
} </pre>
