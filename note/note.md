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

#### Test Results -- 20121128

Sample running, 5 rounds, squared sigmoid objective. 
Gradient descent at least works, but not working very efficient. 
See my manual tuning results after that. 

```
---- init ----
Weights: [30, -100, 1.0, 1.0, 500, 30, 0, 0.01]
total:168095; conc:140498; disc:27597
Kendall's coefficient: 0.672
Round 0
Gradient: [50.097703225965766, 12.72296840254613, 626.92591843424168, 0.0, -1.9642926878747293, 1.6517638283015277, 97253.958146686869, 141394.26337692855]
New objective 21131.913
Weights: [29.999999499022969, -100.00000012722968, 0.99999373074081566, 1.0, 500.00000001964293, 29.999999983482361, -0.00097253958146686871, 0.0085860573662307153]
total:168095; conc:140884; disc:27211
Kendall's coefficient: 0.676
Round 1
Gradient: [50.600670780300923, 12.721790084012731, 698.04614289767972, 0.0, -1.9822536755932665, -0.97802958355932457, 47768.278763320013, 105304.15573375601]
New objective 21022.667
Weights: [29.999998993016263, -100.00000025444758, 0.99998675027938666, 1.0, 500.00000003946548, 29.999999993262659, -0.0014502223691000688, 0.0075330158088931553]
total:168095; conc:141127; disc:26968
Kendall's coefficient: 0.679
Round 2
Gradient: [50.74654751129318, 12.849227152536649, 729.80326066985651, 0.0, -2.0563888974568356, -3.0764096780638512, 9261.9523933536129, 74651.072304447836]
New objective 20974.235
Weights: [29.999998485550787, -100.00000038293986, 0.99997945224677998, 1.0, 500.00000006002938, 30.000000024026754, -0.0015428418930336048, 0.0067865050858486771]
total:168095; conc:141267; disc:26828
Kendall's coefficient: 0.681
Round 3
Gradient: [50.817974540062529, 12.951502712687958, 737.91046734296992, 0.0, -2.1053953055983983, -4.3118715031327435, -12265.579503390305, 55067.395904676116]
New objective 20944.788
Weights: [29.999997977371041, -100.00000051245489, 0.99997207314210657, 1.0, 500.00000008108333, 30.000000067145468, -0.0014201860979997018, 0.006235831126801916]
total:168095; conc:141377; disc:26718
Kendall's coefficient: 0.682
Round 4
Gradient: [50.913644619321779, 13.005147906471326, 736.43859739890172, 0.0, -2.1162167984176552, -4.8957389244655323, -21087.300435644138, 44358.067632875638]
New objective 20921.729
Weights: [29.999997468234596, -100.00000064250636, 0.99996470875613253, 1.0, 500.00000010224551, 30.000000116102857, -0.0012093130936432605, 0.0057922504504731593]
total:168095; conc:141444; disc:26651
Kendall's coefficient: 0.683
```

My manual tuning results:

```
In [1]: aw.w = [30, -299, 1, 1, 600, 30, 0, 0.01]

In [2]: aw.evaluate()
total:168095; conc:142771; disc:25324
Out[2]: 0.6986941907849727
```

See? I just increased the weight for feature `topic_tech`. 

More to do:

   * How to adjust step size?
   * Will step size be easier to adjust if the features are scaled 
   to the same order?
   * How efficient it is to train from all zeros as initial solution. 
   * We found that the step size for each coordinate should be different. 
   How about coordinate descent? 
   * Stochastic Coordinate Descent? 



