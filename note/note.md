# SNS Router Development Notes

## Framework Survey

I want to use web UI, so that SNSRouter 
can be used on nearly any device. 
In the first step, I launch the HTTP server locally. 
This is for prototyping convenience. 
Later, the codes should be able to move to a 
real dedicated HTTP server with least modification. 

[http://stackoverflow.com/questions/877033/how-can-i-create-an-local-webserver-for-my-python-scripts](http://stackoverflow.com/questions/877033/how-can-i-create-an-local-webserver-for-my-python-scripts)

SimpleHTTPSever and BaseHTTPServer may help. 

[http://docs.python.org/library/wsgiref.html](http://docs.python.org/library/wsgiref.html)

WSGI? Looks more extensible. 

[http://stackoverflow.com/questions/13060853/extensible-local-http-server-with-framework-in-python](http://stackoverflow.com/questions/13060853/extensible-local-http-server-with-framework-in-python)

my questions. 

As pointed out, Bottle and Flask are worth to look at. 
At first sight, the single file aspect of Bottle is attractive for me. 
On the other hand, Flask provides some handy plugins like distributed message queuing. 

[http://www.slideshare.net/r1chardj0n3s/web-microframework-battle](http://www.slideshare.net/r1chardj0n3s/web-microframework-battle)

The survey of Micro-frameworks, Richard Jones. 

[http://www.youtube.com/watch?v=AYjPIMe0BhA](http://www.youtube.com/watch?v=AYjPIMe0BhA)

The survey of Micro-frameworks, Richard Jones. Youtube Video. 

## Serialization

[http://www.youtube.com/watch?v=G-lGCC4KKok](http://www.youtube.com/watch?v=G-lGCC4KKok)

In the talk given by Youtube designer, he shared some experience on 
making Youtube scalable. 
Very interesting. 
One thing about serialization is to not use pickle, 
which is in the standard library and currently used in SNSRouter's queue infrastructure. 
Efficiency is not a major concern in my current project. 
We have at least one upgrade choice: import cPickle as pickle. 

## Preliminary Data (20121108)

```
sqlite> select count(*) from msg;
7404
sqlite> select count(*) from msg where flag="seen";
2994
sqlite> select count(*) from msg_tag;
343
sqlite> select count(*) from log;
4535
sqlite> select count(*) from log where operation like "%forward%";
55
sqlite> select name,count(*) from msg_tag,tag where tag_id = tag.id group by tag_id;
null|2
mark|84
gold|2
silver|16
bronze|10
news|75
interesting|27
shit|26
nonsense|101
```

Line of code (20121108): 5523

## Resources

Google prediction API:

https://developers.google.com/prediction/

Looks strong. 

## Algorithm Framework

### A Rank Preserving Framework

Originally, I want a classification formulation. 
Later I found that it is really hard to tell 
which message should be tagged as what category. 
Step back, I think the system does not have to so accurately. 
Human is natural better filtering system. 
If the system can rank the messages reasonably, 
it is already a significant saving of time. 

For example, I can specify some partial order: 

gold > silver
silver > bronze
bronze > null
mark > news
mark > null
news > null
news > interesting
interesting > null
null > nonsense
nonsense > shit

We want to regress from a set of features to 
get a combined real value so that the real value 
preserves this expected rank of tags. 

I term this as rank preserving regression. 
Are there well known existing techniques?

#### "ordinal regression"? 

From the 
[wikipedia's description](http://en.wikipedia.org/wiki/Ordinal_regression)
, it is not the model I'm pursuing. 

Some references:

   * Peter McCullagh, 1980, Regression Models for Ordinal Data, 
   http://www.jstor.org/stable/10.2307/2984952
   * Yang Liu, Yan Liu, Keith C. C. Chan, 
   Ordinal Regression via Manifold Learning. 
   The search of "ranking preserving regression" on Google 
   hits this paper. 

#### "order preserving regression"?

Reference:

   * Peter H ALL and Hans-Georg M ÜLLER, 
   2003, *Order-Preserving Nonparametric Regression,
   With Applications to Conditional Distribution and
   Quantile Function Estimation*. 

The input is X and y, regress the weights so that 
the output g(X) preserves the order of y. 
However, our tag only has categorical meaning. 

Data types:

   * Nominal
   * Ordinal
   * Interval
   * Ratio

http://changingminds.org/explanations/research/measurement/types_data.htm

> Parametric vs. Non-parametric
> Interval and ratio data are parametric, and are used with parametric tools in which distributions are predictable (and often Normal).  
> Nominal and ordinal data are non-parametric, and do not assume any particular distribution. They are used with non-parametric tools such as the Histogram.

We are dealing with ordinal data. 

#### Metric

I thought to use the number reversed pairs as a metric. 
Kendall's tau turns out to be a normalized version of this metric. 
Anyway, it already has an official definition and wide acceptance.
I'd use Kendall's tau as the measurement. 

[http://en.wikipedia.org/wiki/Kendall_tau_rank_correlation_coefficient](http://en.wikipedia.org/wiki/Kendall_tau_rank_correlation_coefficient)

#### Test Results -- 20121127

Commit: cd18ca368cbb631ba4748b53c4e470f451d00d78

Evaluate the direct sampled output:

```
-0.0152395941749
```

Using the test `autoweight.py` script:

```
0.108986274117
```

Sort by time:

```
-0.0151794217999
```

Well done! I'm half on the way. 

At least, my manual configured weights are meaningful. 
Let's try to train the weights automatically. 

```
{
  "preference": [
    ["gold", "mark"],
    ["silver", "mark"],
    ["bronze", "mark"],
    ["mark", "news"],
    ["mark", "interesting"],
    ["mark", "null"],
    ["news", "null"],
    ["news", "interesting"],
    ["interesting", "null"],
    ["null", "nonsense"],
    ["null", "shit"]
  ]
}
```

#### Test Results -- 20121127 -- modified Kendall

Modifed Kenall. Only count non-equally tagged pairs. 

Commit: 954c97d3985928e08b786993f3309047664ae5c1

   * My manual weight: 0.170852101217
   * Time ordering: -0.0237963989246

#### Test Results -- 20121128

Commit: 8c8d1ea6cf6095a6d6ea64f79f41d2da12aa1ef3

The evaluation process is very slow. 
Major cause is the enumeration of all possible pairs. 
In this commit, all derived ordered pairs are precomputed. 
Then in the evaluation stage, we don't have to 
enumerate all pairs of messages anymore. 
We only enumerate those known relations and check whether 
their order in the ranking list is correct. 


