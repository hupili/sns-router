# Chatting about Horse 

This document is from the appendix of original report. 
The chatting is a metaphor about my design philosophy. 
I realised later that these paragraphs are not user friendly. 
That is why I removed them from the original report. 
Here they are. 
You are not recommended to read them at the first place. 
If you already deployed and tested SNSRouter successfully, 
you can read it according to your interest. 

## Chatting about Horse (Dec 2012)

**A:**
I think the algorithm can not work well 
when there is not enough data. 
Have you considered using advanced machine learning tools 
to deal with this problem? 

**B:** 
If you have a gifted horse but you give him little food, 
do you expect him to run very fast?
[Yu Han](http://baike.baidu.com/view/86583.htm)
says no. 
The right horse eats the right amount of food. 
That is the bottom line. 
In the first month, I spent much time marking training data. 
I mark data after lunch; I mark data during tea break; 
I mark data in the bed using my iPad... 
You see, food is eventually enough and it runs reasonably well. 

**A:**
The system at my side does not work so well as you reported. 
How to improve?

**B:**
There is no best horse or best rider.
When you bet on a "horse", you are actually bet on the "horse+rider". 
Human should not always ask machines to do hard tasks
(that require creative intelligence). 
We should act as one and each component focus on his own job. 
Similarly, I will not ask the system to do everything for me. 
I ask the system to do tedious and repeated tasks like counting the term frequency. 
I do the creative job myself, i.e. find the proper features. 
When I mark data, I do not tag everything just as "good" or "bad". 
I try to do a finer-grained classification {\bf in a consistent manner}. 
Try to think, how about telling your horse:
"Look at my face and what is around. 
Go as I wish using your past memory."
It will not work. 

**A:**
I am machine learning expert but I still can not make your system work well. 

**B:**
That is natural. 
Imagine: the best rider is riding the 2nd best horse;
the 2nd best rider is riding the best horse. 
Now we change their horses. 
What will happen? 
Unless enough training is done, 
the "best rider+best horse" will not outperform 
the "2nd best rider+best horse". 
The important thing is that the "training" is not for horse, 
but for horse and the rider as a whole. 
As a new rider with an ordinary horse, we just cooperate well. 

**A:**
I eventually managed to make RPR-SGD work well for me. 
However, when I migrate it to my friend, 
the performance degrades. 
Can you make another framework which generalizes better?

**B:**
I think many race horses are over trained to a certain race track (standard data set). 
Those horses do not have joy in running. 
In the straight track, horse A outperforms others;
In the bent track, horse B outperforms others. 
The riders keep on arguing whose horse is the best. 
However, the real situation is, it all depends on 
the fraction of straight and bent lines. 
I don't have time to ask my horse to compete with others on a standard track, 
letting alone count how many standard tracks it "generalizes" to. 
All I know is that it runs well along my way, 
where I see mountain, river, grass, marsh, etc. 
When there are fences, I teach him to jump; 
When there are dust wind, I teach him to sit low in the bushes; 
When there is a high wall, I tell him "let's find another way out together". 
I do not blame my horse for his deficiency in running a certain type of road. 
I do not ask my horse to run an imaginary difficult road. 
I also totally agree that it is not the fast even on my road. 
We just saw a fast vehicle running across us. 
Apparently, the highway is not for my horse. 
In the future, I will rent a vehicle when I need to travel on the highway. 
When on the grass, I still ride my horse. 
