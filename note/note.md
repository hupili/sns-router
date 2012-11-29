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

#### Test Results -- 20121129

Use step size of fixed `1e-7`. 
Sigmoid performs 
better than SqureSigmoid,  
although both of them jumps out of my initial region. 

```
---- init ----
Weights: [30, -100, 1.0, 1.0, 500, 30, 0, 0.01]
total:168095; conc:140498; disc:27597
Kendall's coefficient: 0.672
Round 0
Gradient: [36.590422025295361, 30.680791112673223, -518.0392812064074, 0.0, -15.55948437261711, -10.310456096851693, -260281.98141021063, -162125.56471230232]
New objective 37373.669
Weights: [29.999996340957797, -100.00000306807911, 1.0000518039281205, 1.0, 500.00000155594842, 30.00000103104561, 0.026028198141021062, 0.026212556471230233]
total:168095; conc:132358; disc:35737
Kendall's coefficient: 0.575
Round 1
Gradient: [27.131253460628741, 30.643742219467374, -580.11798629489215, 0.0, -9.6438081792770323, 3.6953282357037334, 116568.09967354899, 53491.438822090364]
New objective 35687.460
Weights: [29.999993627832449, -100.00000613245334, 1.0001098157267501, 1.0, 500.00000252032925, 30.000000661512786, 0.014371388173666164, 0.020863412589021198]
total:168095; conc:135152; disc:32943
Kendall's coefficient: 0.608
Round 2
Gradient: [32.481530516586162, 32.545041852062987, -482.64600631637535, 0.0, -10.767161795397975, 3.0059769589092427, 107403.31056273941, 65790.167283797258]
New objective 34883.029
Weights: [29.999990379679396, -100.00000938695752, 1.0001580803273817, 1.0, 500.00000359704541, 30.000000360915092, 0.0036310571173922227, 0.014284395860641473]
total:168095; conc:138956; disc:29139
Kendall's coefficient: 0.653
Round 3
Gradient: [37.14612421194132, 30.721692842982623, -360.42172031973399, 0.0, -13.203682229823864, -2.4706948071665766, -56704.665025549344, -19322.451107832738]
New objective 34967.582
Weights: [29.999986665066974, -100.00001245912679, 1.0001941224994138, 1.0, 500.00000491741361, 30.000000607984571, 0.0093015236199471569, 0.016216640971424747]
total:168095; conc:137307; disc:30788
Kendall's coefficient: 0.634
Round 4
Gradient: [35.583317591783754, 32.588149170573949, -417.21536317804362, 0.0, -11.780884101841854, 1.3005224830188036, 60698.947138248041, 42595.812176410182]
New objective 35000.302
Weights: [29.999983106735215, -100.00001571794171, 1.0002358440357315, 1.0, 500.00000609550199, 30.000000477932321, 0.0032316289061223528, 0.011957059753783729]
total:168095; conc:139578; disc:28517
Kendall's coefficient: 0.661
```

The Sigmoid one is easier for line search along gradient. 

#### Test Results -- 20121129

Initialize from all zero's, step size is fixed `1e-7`. 
Seems to converge to Kendall's value about `0.416`. 

Some observations:

   * Two text length features out-weight others. 
   * I think rescaling the feature is an urgent task. 
   Given domain knowledge, I can manual configure weights of different order of magnitude. 
   However, the program can not (or find it hard) to do so. 
   One term in the gradient is xi(k) - x(k). 
   So the text length dimension is very large. 
   * "test" feature (every message is 1) is zero, as expected. 

```
---- init ----
Weights: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
total:168095; conc:83147; disc:84948
Kendall's coefficient: -0.011
Round 0
Gradient: [23.119906478186667, 199.8664421654631, -9157.5, 0.0, -143.21701066608628, -87.468982890868219, -2140342.75, -1606245.5]
New objective 49237.381
Weights: [-2.3119906478186668e-06, -1.9986644216546311e-05, 0.00091575000000000001, 0.0, 1.4321701066608628e-05, 8.746898289086821e-06, 0.214034275, 0.16062455]
total:168095; conc:118970; disc:49125
Kendall's coefficient: 0.416
Round 1
Gradient: [6.9461667309910018, 10.962703754149443, -223.53594797010197, 0.0, -5.3298095978539637, -1.5470264322897449, 2344.6822311679393, -3955.4264722461257]
New objective 49235.264
Weights: [-3.006607320917767e-06, -2.1082914591961253e-05, 0.00093810359479701017, 0.0, 1.4854682026394024e-05, 8.9016009323157951e-06, 0.21379980677688321, 0.16102009264722461]
total:168095; conc:118971; disc:49124
Kendall's coefficient: 0.416
Round 2
Gradient: [6.9475493113310804, 10.970743863034102, -223.71778228464476, 0.0, -5.3318665367381817, -1.5550314442269118, 2343.2211462432429, -3942.1840298176853]
New objective 49233.159
Weights: [-3.701362252050875e-06, -2.2179988978264665e-05, 0.00096047537302547468, 0.0, 1.538786868006784e-05, 9.0571040767384857e-06, 0.21356548466225889, 0.16141431105020637]
total:168095; conc:118982; disc:49113
Kendall's coefficient: 0.416
Round 3
Gradient: [6.9489699498619641, 10.978626228123256, -223.90029339447582, 0.0, -5.3339293069028217, -1.5630000260225958, 2341.4597394170519, -3928.6269797544046]
New objective 49231.065
Weights: [-4.3962592470370711e-06, -2.3277851601076991e-05, 0.00098286540236492228, 0.0, 1.5921261610758121e-05, 9.2134040793407459e-06, 0.21333133868831719, 0.16180717374818182]
total:168095; conc:118983; disc:49112
Kendall's coefficient: 0.416
Round 4
Gradient: [6.9504325164706611, 10.986348468077763, -224.08347492810566, 0.0, -5.335999159117903, -1.5709060863221507, 2339.4162988333555, -3914.7813982846947]
New objective 49228.983
Weights: [-5.0913024986841369e-06, -2.4376486447884766e-05, 0.0010052737498577329, 0.0, 1.6454861526669912e-05, 9.3704946879729615e-06, 0.21309739705843386, 0.1621986518880103]
total:168095; conc:118983; disc:49112
Kendall's coefficient: 0.416
```


