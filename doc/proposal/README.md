# Proposal 

This is the proposal submitted to CSCI5070 course in Sept, 2012. 

## Final Review

### General 

   * Prototyping works well (in my environment).
   * All factors listed in objective are hit (with somewhat degraded outcome). 
   * Formulation shifted twice during the process but 
   became more applicable at last. 

### Algorithm Framework

   * At first, the aggresive objective is to do **auto forwarding**. 
   * In the middle, we found forwarding decision is hard. 
   Human's forwarding decision is based on more factors than quality.
   One consideration is to not bother message recipients. 
   * A **classfication** problem is proposed in the middle. 
   We can predict the tags and it help human to make final decisions. 
   * Later we find classification is still too aggressive. 
   What's more important, classification is not needed. 
   Human processes messages sequentially. 
   If human review is deemed to exist, 
   there is no point to classify those messages. 
   Reasonable ordering of the messages is already good enough to save time. 
   * Luckily, we have collected many tags. 
   One can prioritize those tags! 
   Then I get many partial ordering and derive more partial ordering. 
   **Rank Preserving Regression** is my first thought. 
   * To solve RPR, one can invoke Quadratic Programming routines. 
   One can also relax the objective to L1 norm and solve it by 
   Linear Programming routines. 
   * I just felt there are too many variables if we do first version of RPR
   (all y's are variables; This is different from ordinary regression
   where y's are known data).
   Next trial is to enforce `y=Xw` and put number of violated constraints 
   in the objective.
   With Sigmoid approximation, gradient is tractable. 
   * Plain Gradient Descent is very slow and the step size setup is tricky. 

### Remark

   * There are more engineering problems than my expectation. 
   SNSAPI is also frequently revisited during the time. 
   * Original objective is ambitious but tractable. 
   * Feature extraction is also a fun part to play with. 
   I don't have enough time now. 

   
