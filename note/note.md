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

#### Test Results -- 20121128 -- improve evaluation stage

Commit: 8c8d1ea6cf6095a6d6ea64f79f41d2da12aa1ef3

The evaluation process is very slow. 
Major cause is the enumeration of all possible pairs. 
In this commit, all derived ordered pairs are precomputed. 
Then in the evaluation stage, we don't have to 
enumerate all pairs of messages anymore. 
We only enumerate those known relations and check whether 
their order in the ranking list is correct. 

#### Test Results -- 20121128 -- Squared Sigmoid Objective

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

#### Test Results -- 20121129 -- Sigmoid Objective

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

#### Test Results -- 20121129 -- 0 init weights

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

#### Test Result -- 20121129 -- test single feature Kendall

I tried different step size and start from all zero or all one's. 
I also tried to normalize the weight every step.  
There does not seem to be a reasonable result. 
It seems a slight deviation from all zero can result in about `0.44` Kendall's score. 
However, further gradient descent does not help too much. 

One thought is to test the Kendall's coefficient of single feature first!
It looks they are informative!

```
In [4]: evaluate_kendall(sorted(aw.samples, key = lambda m: aw.samples[m].feature['topic_tech'], reverse = True), order)
total:168095; conc:140038; disc:28057
Out[4]: 0.6661768642731789

In [5]: evaluate_kendall(sorted(aw.samples, key = lambda m: aw.samples[m].feature['topic_news'], reverse = True), order)
total:168095; conc:109511; disc:58584
Out[5]: 0.30296558493708914

In [6]: evaluate_kendall(sorted(aw.samples, key = lambda m: aw.samples[m].feature['topic_interesting'], reverse = True), order)
total:168095; conc:101805; disc:66290
Out[6]: 0.21127933608971117

In [7]: evaluate_kendall(sorted(aw.samples, key = lambda m: aw.samples[m].feature['topic_nonsense'], reverse = True), order)
total:168095; conc:47570; disc:120525
Out[7]: -0.4340105297599572

In [9]: evaluate_kendall(sorted(aw.samples, key = lambda m: aw.samples[m].feature['text_len'], reverse = True), order)
total:168095; conc:118163; disc:49932
Out[9]: 0.40590737380647846

In [10]: evaluate_kendall(sorted(aw.samples, key = lambda m: aw.samples[m].feature['text_orig_len'], reverse = True), order)
total:168095; conc:118692; disc:49403
Out[10]: 0.41220143371307894

In [11]: evaluate_kendall(sorted(aw.samples, key = lambda m: aw.samples[m].feature['contain_link'], reverse = True), order)
total:168095; conc:100960; disc:67135
Out[11]: 0.20122549748654034

In [12]: evaluate_kendall(sorted(aw.samples, key = lambda m: aw.samples[m].feature['test'], reverse = True), order)
total:168095; conc:83147; disc:84948
Out[12]: -0.010714179481840625
```

So let's try to initialize the weights using single feature Kendall's score. 

```
---- init ----
Weights: [0.19758879924347028, -0.40586213285278738, 0.18813345909670323, -0.010017098590780859, 0.62284550332671451, 0.28330980062110195, 0.37949841973768395, 0.38538297848784842]
total:168095; conc:128318; disc:39777
Kendall's coefficient: 0.527
Round 0
Gradient: [0.023595681932085697, 0.064325781504381077, -0.70953836462429964, 0.0, -0.25831647137155006, -0.017775352939474236, -0.41651307309586683, -0.50133246866779968]
New objective 77372.319
New weights: [0.15322004167010889, -0.31560109361580396, 0.15157101895696337, -0.0077770365232156463, 0.48556790670834138, 0.22009297827362451, 0.29786723346891114, 0.30309438215082857]
total:168095; conc:128226; disc:39869
Kendall's coefficient: 0.526
Round 1
Gradient: [0.022412073880935541, 0.063414438210569149, -0.71060725435866912, 0.0, -0.25652243654572138, -0.017947849363759108, -0.41657016931549856, -0.50085631303992362]
New objective 78079.109
New weights: [0.13386734363164007, -0.27669738523623055, 0.13883821611107908, -0.0068046991995074852, 0.42710344954089863, 0.19273251524064799, 0.26427074965984682, 0.26958184635787069]
total:168095; conc:128105; disc:39990
Kendall's coefficient: 0.524
Round 2
Gradient: [0.022006944682225377, 0.063114714450163326, -0.71089612801191371, 0.0, -0.25596832751649728, -0.01801105484678581, -0.41663628810633435, -0.50072841244329769]
New objective 78384.410
New weights: [0.12403155007826666, -0.25737515382876774, 0.135446493404311, -0.0063151111362294505, 0.39874950461738951, 0.17903284711369558, 0.24912345852217496, 0.2548328478534167]
total:168095; conc:127965; disc:40130
Kendall's coefficient: 0.523
Round 3
Gradient: [0.021839790890864592, 0.063004951399853432, -0.71093848507329982, 0.0, -0.25579584558311502, -0.018040407982776258, -0.41670977145239063, -0.50071535378192411]
New objective 78513.576
New weights: [0.11828262444823587, -0.24648053973248094, 0.13618814411142083, -0.0060330256179388676, 0.38338172569934476, 0.17120809312790466, 0.24197648807656205, 0.24823338040169055]
total:168095; conc:127837; disc:40258
Kendall's coefficient: 0.521
Round 4
Gradient: [0.021763993345352343, 0.06296954253477241, -0.71087998811781583, 0.0, -0.25577382150619787, -0.01805687169648279, -0.41678972793026126, -0.50075026920483057]
New objective 78561.028
New weights: [0.11440899303975011, -0.2394582381085501, 0.13885962154862305, -0.0058462073981382801, 0.37398849135680717, 0.16608145336813801, 0.23852229673927386, 0.24539904485926706]
total:168095; conc:127713; disc:40382
Kendall's coefficient: 0.520
```

The starting point is better in objective. 
With step size `10e-2` and gradient normalized, this does not improve further...

#### Test Result -- 20121129 -- Sigmoid coefficient

New findings!

When I was about to write a line search algorithm for alpha (step size), 
I found the Kendall's coefficient does not agree with objective
(gradient is normalized; weights are not normalized). 

Then I changed the coefficient of Sigmoid function, 
making it more stringent. 
The test result show that the Kendall's coefficient now agrees with Sigmoid objective. 

The result of coeff = 10:

```
---- init ----
Weights: [0.19759554312433789, -0.40558792389681031, 0.1881610665854207, -0.010018568541621366, 0.62292577671254978, 0.28335137468326904, 0.37955410891913788, 0.38543953119400493]
total:168095; conc:128317; disc:39778
Kendall's coefficient: 0.527
Round 0
Gradient: [0.31934648024931223, 0.25117702575172801, -0.2051529981404536, 0.0, -0.72953469227726775, 0.010887957298406229, -0.3109159721276441, -0.40476168058077922]
New objective 44741.771
New weights: [0.16566089509940665, -0.43070562647198313, 0.20867636639946607, -0.010018568541621366, 0.6958792459402765, 0.28226257895342843, 0.41064570613190227, 0.42591569925208284]
total:168095; conc:128513; disc:39582
Kendall's coefficient: 0.529
Round 1
Gradient: [0.32786561730662439, 0.27923299762151338, 0.00028272993968685937, 0.0, -0.78137045580449072, 0.016730657457823241, -0.27355924148108107, -0.35899669551186431]
New objective 43896.313
New weights: [0.13287433336874421, -0.45862892623413448, 0.20864809340549739, -0.010018568541621366, 0.7740162915207256, 0.28058951320764614, 0.43800163028001038, 0.46181536880326929]
total:168095; conc:129023; disc:39072
Kendall's coefficient: 0.535
Round 2
Gradient: [0.34231998079275483, 0.3065472172521877, 0.037514617213062408, 0.0, -0.8098315929184362, 0.021969647406932274, -0.20756315259844837, -0.29672571716610963]
New objective 43149.924
New weights: [0.098642335289468724, -0.48928364795935325, 0.20489663168419114, -0.010018568541621366, 0.85499945081256923, 0.27839254846695288, 0.45875794553985522, 0.49148794051988026]
total:168095; conc:129395; disc:38700
Kendall's coefficient: 0.540
Round 3
Gradient: [0.34991163546790249, 0.33223779764307693, 0.04606574765725286, 0.0, -0.82977731006236666, 0.026685521080088127, -0.14100034100027575, -0.23650421261023449]
New objective 42478.607
New weights: [0.063651171742678481, -0.52250742772366099, 0.20029005691846585, -0.010018568541621366, 0.93797718181880585, 0.27572399635894407, 0.4728579796398828, 0.51513836178090366]
total:168095; conc:129840; disc:38255
Kendall's coefficient: 0.545
Round 4
Gradient: [0.34735073381210957, 0.35543056961753983, 0.052135572959673061, 0.0, -0.84281178369293308, 0.030742415659794887, -0.079180869524508077, -0.18097527726953916]
New objective 41865.835
New weights: [0.028916098361467524, -0.55805048468541496, 0.19507649962249854, -0.010018568541621366, 1.0222583601880992, 0.2726497547929646, 0.48077606659233363, 0.53323588950785761]
total:168095; conc:130326; disc:37769
Kendall's coefficient: 0.551
```

The result of coeff = 100

```
---- init ----
Weights: [0.19758882382544316, -0.40564088285303884, 0.18815466810888248, -0.010018227857031704, 0.62291571910826271, 0.28334173923021871, 0.37954120206170466, 0.38542642420092715]
total:168095; conc:128318; disc:39777
Kendall's coefficient: 0.527
Round 0
Gradient: [0.37649049625769387, 0.17896898203489425, 0.6944149265873798, 0.0, -0.50713404096672277, 0.026538443960959439, 0.21256785795641972, 0.20233289569021129]
New objective 38806.778
New weights: [0.15993977419967376, -0.42353778105652828, 0.1187131754501445, -0.010018227857031704, 0.67362912320493495, 0.28068789483412276, 0.35828441626606267, 0.365193134631906]
total:168095; conc:129474; disc:38621
Kendall's coefficient: 0.540
Round 1
Gradient: [0.56236349791964746, 0.23262377793672331, 0.041221662787663364, 0.0, -0.50129428478778804, 0.027105296849741094, 0.46369402948001281, 0.40111275049469747]
New objective 37539.576
New weights: [0.10370342440770901, -0.44680015885020063, 0.11459100917137816, -0.010018227857031704, 0.72375855168371372, 0.27797736514914867, 0.31191501331806137, 0.32508185958243624]
total:168095; conc:130779; disc:37316
Kendall's coefficient: 0.556
Round 2
Gradient: [0.44427780226348418, 0.21722243825862081, 0.42442834498001553, 0.0, -0.42552454726925482, 0.025018068156005782, 0.44082400628585533, 0.446395988030312]
New objective 36160.496
New weights: [0.059275644181360589, -0.46852240267606271, 0.0721481746733766, -0.010018227857031704, 0.76631100641063921, 0.27547555833354809, 0.26783261268947584, 0.28044226077940504]
total:168095; conc:132097; disc:35998
Kendall's coefficient: 0.572
Round 3
Gradient: [0.48992864447094286, 0.2175538936796064, -0.093811979548392335, 0.0, -0.32101453252696299, 0.021574495570441547, 0.55123655889089918, 0.54448324708333828]
New objective 34574.571
New weights: [0.010282779734266299, -0.49027779204402333, 0.081529372628215829, -0.010018227857031704, 0.79841245966333552, 0.27331810877650392, 0.21270895680038593, 0.22599393607107121]
total:168095; conc:133758; disc:34337
Kendall's coefficient: 0.591
Round 4
Gradient: [0.22885539717751244, 0.18556061936261237, 0.61559979828901834, 0.0, -0.24846817162249465, 0.019985105396853324, 0.44792742802656776, 0.52101298884515501]
New objective 32413.792
New weights: [-0.012602759983484944, -0.50883385398028458, 0.019969392799313992, -0.010018227857031704, 0.82325927682558497, 0.27131959823681862, 0.16791621399772916, 0.1738926371865557]
total:168095; conc:136095; disc:32000
Kendall's coefficient: 0.619
```

Result of coeff = 1000:

```
---- init ----
Weights: [0.197735542131732, -0.4056340469740915, 0.18815665773780726, -0.010018333794110596, 0.62286667958242414, 0.28334473540844612, 0.37954521549470294, 0.38543049986681238]
total:168095; conc:128317; disc:39778
Kendall's coefficient: 0.527
Round 0
Gradient: [0.33032406365459449, 0.17566445693403923, 0.73713864373796723, 0.0, -0.47548314498863958, 0.0095760760804390697, 0.24350647119860053, 0.1765879597593045]
New objective 38683.175
New weights: [0.16470313576627255, -0.42320049266749543, 0.11444279336401054, -0.010018333794110596, 0.67041499408128813, 0.2823871278004022, 0.35519456837484287, 0.36777170389088193]
total:168095; conc:129434; disc:38661
Kendall's coefficient: 0.540
Round 1
Gradient: [0.61838417565976855, 0.20547278445906836, -0.081427382894048564, 0.0, -0.46859474908865884, 0.02118865876175435, 0.41139246819283198, 0.42364816349876511]
New objective 37487.080
New weights: [0.10286471820029569, -0.44374777111340225, 0.1225855316534154, -0.010018333794110596, 0.71727446899015401, 0.28026826192422677, 0.31405532155555965, 0.32540688754100544]
total:168095; conc:130630; disc:37465
Kendall's coefficient: 0.554
Round 2
Gradient: [0.12516573066511172, 0.13799763812070917, 0.8601876254779941, 0.0, -0.31109225905436422, 0.020604738665902643, 0.20517562968704381, 0.293372549496697]
New objective 37107.922
New weights: [0.090348145133784516, -0.45754753492547318, 0.036566769105615987, -0.010018333794110596, 0.74838369489559042, 0.27820778805763652, 0.29353775858685527, 0.29606963259133573]
total:168095; conc:130994; disc:37101
Kendall's coefficient: 0.559
Round 3
Gradient: [0.37909849879773594, 0.15837972371412523, -0.74693183951461861, 0.0, -0.18749977417798455, 0.017955746187726888, 0.38893843143665457, 0.29417909656957225]
New objective 35989.990
New weights: [0.052438295254010919, -0.47338550729688572, 0.11125995305707785, -0.010018333794110596, 0.76713367231338891, 0.27641221343886385, 0.25464391544318982, 0.2666517229343785]
total:168095; conc:132126; disc:35969
Kendall's coefficient: 0.572
Round 4
Gradient: [0.23263837145305374, 0.18583516102841591, 0.74185192472389605, 0.0, -0.27021156612604186, 0.0091233239283293032, 0.38376901619184128, 0.3749989593852513]
New objective 34375.147
New weights: [0.029174458108705545, -0.49196902339972731, 0.037074760584688241, -0.010018333794110596, 0.79415482892599309, 0.2754998810460309, 0.21626701382400568, 0.22915182699585337]
total:168095; conc:133733; disc:34362
Kendall's coefficient: 0.591
```

The observation:

   * When coeff is very small (like default 1 used previously), 
   the portion of Sigmoid near 0 is flat linear. 
   The driving force towards our prefence pair is quite small. 
   Also, one may find that the Sigmoid objective does not agrees with 
   Kendall's coefficient. 
   Kendall's coefficient is an indicator function. 
   * When coeff is too large, there will be very small numbers in calculation. 
   Since our calculation involves exponetiation and division, 
   such small number will make it numerically unstable. 
   Using the same number of iterations, the resulting Kendall's coefficient 
   is smaller. 
   * How to set a reasonable Sigmoid coefficient??

#### Test Result -- 20121129 -- larger step size

Let's see what happens for larger step size. 
a = 1e-1. 
This time, the objective oscillates..

```
In [1]: aw.train()
---- init ----
Weights: [0.19700918514548738, -0.40576292395628, 0.18818547026477961, -0.010019867906781022, 0.62291755146181971, 0.28337699713042275, 0.37960333545118041, 0.38548952103995016]
total:168095; conc:128317; disc:39778
Kendall's coefficient: 0.527
Round 0
Gradient: [0.37344821142070367, 0.17844984573893888, 0.69715478950014054, 0.0, -0.50629141387607846, 0.026378332536923357, 0.21191522589957829, 0.2018227198788696]
New objective 72835.860
New weights: [-0.17643902627521629, -0.58421276969521885, -0.50896931923536093, -0.010019867906781022, 1.1292089653378983, 0.2569986645934994, 0.16768810955160213, 0.18366680116108056]
total:168095; conc:95444; disc:72651
Kendall's coefficient: 0.136

In [2]: aw.train()
---- init ----
Weights: [-0.17643902627521629, -0.58421276969521885, -0.50896931923536093, -0.010019867906781022, 1.1292089653378983, 0.2569986645934994, 0.16768810955160213, 0.18366680116108056]
total:168095; conc:95446; disc:72649
Kendall's coefficient: 0.136
Round 0
Gradient: [-0.10322877608969827, 0.18996414519711741, -0.91265664101758925, 0.0, -0.29861772492578292, -0.0058655617750530053, -0.15092251520567529, -0.091272903329783092]
New objective 37584.121
New weights: [-0.073210250185518022, -0.77417691489233631, 0.40368732178222833, -0.010019867906781022, 1.4278266902636811, 0.26286422636855239, 0.31861062475727742, 0.27493970449086363]
total:168095; conc:130608; disc:37487
Kendall's coefficient: 0.554

In [3]: aw.train()
---- init ----
Weights: [-0.073210250185518022, -0.77417691489233631, 0.40368732178222833, -0.010019867906781022, 1.4278266902636811, 0.26286422636855239, 0.31861062475727742, 0.27493970449086363]
total:168095; conc:130615; disc:37480
Kendall's coefficient: 0.554
Round 0
Gradient: [0.12896788389868769, 0.15367962811706187, 0.69609446127585817, 0.0, -0.30355329578622203, 0.037906707121152988, 0.36964338592335627, 0.49495919349097772]
New objective 74481.602
New weights: [-0.20217813408420571, -0.92785654300939813, -0.29240713949362984, -0.010019867906781022, 1.7313799860499031, 0.2249575192473994, -0.051032761166078855, -0.22001948900011409]
total:168095; conc:93662; disc:74433
Kendall's coefficient: 0.114

In [4]: aw.train()
---- init ----
Weights: [-0.20217813408420571, -0.92785654300939813, -0.29240713949362984, -0.010019867906781022, 1.7313799860499031, 0.2249575192473994, -0.051032761166078855, -0.22001948900011409]
total:168095; conc:93660; disc:74435
Kendall's coefficient: 0.114
Round 0
Gradient: [0.021911325526150265, 0.051750398170859795, -0.56341954491286184, 0.0, -0.15815484093381876, -0.025301885420691662, -0.49690002323952442, -0.63783809411240466]
New objective 34687.302
New weights: [-0.22408945961035598, -0.97960694118025793, 0.27101240541923199, -0.010019867906781022, 1.8895348269837218, 0.25025940466809105, 0.44586726207344557, 0.41781860511229058]
total:168095; conc:133457; disc:34638
Kendall's coefficient: 0.588
```

#### Test Result -- 20121129 -- line search preliminaries

Try line search for a suitable alpha. 

Enumerating alpha from 1 to 1e-5:

```
---- init ----
Weights: [0.19735242677037174, -0.40564755187639734, 0.18817324412988931, -0.010019216930611401, 0.62292158654711305, 0.28336971282318324, 0.37957867317742727, 0.38546447634932451]
total:168095; conc:128301; disc:39794
Kendall's coefficient: 0.527
Round 0
Gradient: [0.3755815667599362, 0.17886901601627472, 0.69551976437592533, 0.0, -0.5066417996025917, 0.026515967899250259, 0.21213834311111374, 0.2020023091597298]
origin line obj: 39951.9697935
alpha: 1.0000000
line obj: 72789.5292472
alpha: 0.5000000
line obj: 45695.2904692
alpha: 0.2500000
line obj: 38553.1236712
alpha: 0.1250000
line obj: 38612.3581747
alpha: 0.0625000
line obj: 39195.5105322
alpha: 0.0312500
line obj: 39548.5353718
alpha: 0.0156250
line obj: 39740.3564080
alpha: 0.0078125
line obj: 39844.1091423
alpha: 0.0039062
line obj: 39897.6322799
alpha: 0.0019531
line obj: 39924.7132338
alpha: 0.0009766
line obj: 39938.3212732
alpha: 0.0004883
line obj: 39945.1406826
alpha: 0.0002441
line obj: 39948.5540513
alpha: 0.0001221
line obj: 39950.2616289
alpha: 0.0000610
line obj: 39951.1156382
alpha: 0.0000305
line obj: 39951.5426977
alpha: 0.0000153
line obj: 39951.7562411
New objective 39951.863
New weights: [0.19734956131042025, -0.40564891653868995, 0.1881679377352026, -0.010019216930611401, 0.62292545191728821, 0.28336951052240278, 0.3795770546903125, 0.3854629351940117]
total:168095; conc:128318; disc:39777
Kendall's coefficient: 0.527
```

Corresponding Kendall's coefficient:

```
Current alpha: 1.0000000
total:168095; conc:95496; disc:72599
Kendall 0.1362146
Current alpha: 0.5000000
total:168095; conc:122589; disc:45506
Kendall 0.4585681
Current alpha: 0.2500000
total:168095; conc:129753; disc:38342
Kendall 0.5438056
Current alpha: 0.1250000
total:168095; conc:129697; disc:38398
Kendall 0.5431393
Current alpha: 0.0625000
total:168095; conc:129061; disc:39034
Kendall 0.5355721
Current alpha: 0.0312500
total:168095; conc:128704; disc:39391
Kendall 0.5313245
Current alpha: 0.0156250
total:168095; conc:128567; disc:39528
Kendall 0.5296945
Current alpha: 0.0078125
total:168095; conc:128439; disc:39656
Kendall 0.5281716
Current alpha: 0.0039062
total:168095; conc:128377; disc:39718
Kendall 0.5274339
Current alpha: 0.0019531
total:168095; conc:128341; disc:39754
Kendall 0.5270056
Current alpha: 0.0009766
total:168095; conc:128324; disc:39771
Kendall 0.5268033
Current alpha: 0.0004883
total:168095; conc:128315; disc:39780
Kendall 0.5266962
Current alpha: 0.0002441
total:168095; conc:128318; disc:39777
Kendall 0.5267319
Current alpha: 0.0001221
total:168095; conc:128319; disc:39776
Kendall 0.5267438
Current alpha: 0.0000610
total:168095; conc:128319; disc:39776
Kendall 0.5267438
Current alpha: 0.0000305
total:168095; conc:128320; disc:39775
Kendall 0.5267557
Current alpha: 0.0000153
total:168095; conc:128320; disc:39775
Kendall 0.5267557
```

Observation:

   * Sigmoid objective minimum happens earlier than Kendall's coefficient 
   maximimum (with decreasing step size from 1 to 1e-5). 
   * Heuristic: find farthest descending step size and shy away by half? 
   * When farthest descending step size is less than 
   1 over number of samples, we may stop. 
   (obj abs value is in proportion to number of pairs; 
   so is gradient magnitude; but we already normalized it?;
   try...)

{evermd:comment:begin}
The following are false observations... 
The data is fixed as above. 
   * The objective value of Sigmoid is monotonic in this testing. 
   * The Kendall's value is not monotonic or quadratic. 
   However, it is nearly quadratic. 
   There seem to be some good points in the middle. 
   * Heuristics for upperbound: 
   if the alpha reduce Sigmoid objective by 10%, the point may be OK. 
   * Heuristics for lowerbound:
   if the alpha is less than 1 over number of samples, 
   it may generate poor result. 
   (good in Sigmoid objective but poor Kendall's correlation)
{evermd:comment:end}

#### Test Results -- 20121129 -- line search result

Using the above heuristics of line search, 
the Kendall's score increases faster. 

After 16 rounds it almost stablize. 

   * Kendall's score increase from `0.527` to `0.738`. 
   * Sigmoid obj decrease from `39931.0853697` to `24971.187`. 

```
In [16]: aw.train()
---- init ----
Weights: [-0.017157887058912642, -0.56173540874714678, 0.0087083069096290915, -0.010018632810608647, 0.88148520903254768, 0.26612641551563387, 0.023717826182296578, 0.014411146440627057]
total:168095; conc:145935; disc:22160
Kendall's coefficient: 0.736
Round 0
Gradient: [-0.61829635590131649, 0.53349000421007464, 0.22205952781635052, 0.0, -0.4023370764240084, -0.040999643210360301, 0.21527544241487911, 0.27182344982975487]
origin line obj: 24994.3785284
alpha: 1.0000000
line obj: 83804.6184326
alpha: 0.5000000
line obj: 68125.9086417
alpha: 0.2500000
line obj: 50020.6710651
alpha: 0.1250000
line obj: 34388.6512812
alpha: 0.0625000
line obj: 27018.2106409
alpha: 0.0312500
line obj: 25317.5793520
alpha: 0.0156250
line obj: 25001.7431056
alpha: 0.0078125
line obj: 24963.8388651
New objective 24971.187
New weights: [-0.014742666918673125, -0.5638193540760924, 0.0078408868790964727, -0.010018632810608647, 0.88305683823732894, 0.26628657037192432, 0.022876906485363457, 0.013349336089729578]
total:168095; conc:146053; disc:22042
Kendall's coefficient: 0.738
```

#### Test Result -- 20121129 -- SGD pre

The ordinary GD is very slow. 
One round needs about 30s to finish...

```
[INFO][20121129-212914][utils.py][report_time_wrapper][173]Function 'train' execution time: 61.80
```

The random set v.s. gradient. 

```
Full Gradient: [0.31259481411597861, -0.062198874340903022, -0.04082817294504431, 0.90637967309427747, 0.0, -0.25485929496964255, -0.10069732907033022, 0.011468147177290168]
Number of samples: 10
Partial Gradient: [-0.0015989376508351546, 0.41351547451991166, -0.056947948939920806, -0.86794813837606222, 0.0, 0.007037811492683517, -0.16989952753477019, -0.2085904496492593]
Number of samples: 20
Partial Gradient: [0.014395592236868497, 0.40321238882029853, -0.081012891449595462, -0.52408478904540767, 0.0, -0.010538734933720534, -0.41785234410321348, -0.61747302396917014]
Number of samples: 40
Partial Gradient: [0.021926583948957384, -0.15031675908782738, -0.038467215857569549, 0.69662534146066224, 0.0, -0.018979621264527499, -0.4368129766437221, -0.54680133614042159]
Number of samples: 80
Partial Gradient: [0.037648876873639874, 0.026565050040094143, -0.042383623940600898, 0.82748033860578718, 0.0, -0.040543527619967129, -0.36305298902998256, -0.42178848651137785]
Number of samples: 160
Partial Gradient: [0.08750849846012293, 0.42980184480714229, -0.095884169497061938, 0.81021648171842997, 0.0, -0.084877714236416962, -0.36644873062458128, 0.021891028731744103]
Number of samples: 320
Partial Gradient: [0.18754051465161353, -0.17239385855478212, -0.10348509624098898, 0.86330685388349238, 0.0, -0.085541485649442667, -0.38543601033882763, -0.15239015702319811]
Number of samples: 640
Partial Gradient: [0.1378830407335801, 0.26500615309003944, -0.075389081564765759, -0.93624713419969885, 0.0, -0.058316204872123842, 0.02497532547396502, 0.15650319278830971]
Number of samples: 1280
Partial Gradient: [0.28990282450967586, -0.27426250684623127, -0.088218422921465284, -0.6856385818871148, 0.0, -0.20035632009979124, -0.56496002294899272, -0.059423833857741942]
Number of samples: 2560
Partial Gradient: [0.46498270155388233, -0.5883381371060793, -0.081229043250648794, 0.32778125989595286, 0.0, -0.3480616775753923, -0.16835160569288368, 0.417278584808565]
Number of samples: 5120
Partial Gradient: [0.14644523099080672, -0.21568788719836537, -0.035322930788425057, 0.94921009458322558, 0.0, -0.11016526797351762, -0.098998154769946584, 0.088588913653139201]
Number of samples: 10240
Partial Gradient: [0.34054392945563705, -0.51509836010672838, -0.065340058095474704, 0.70669714998727606, 0.0, -0.25180789748337307, -0.21660901640098706, -0.068459063045113511]
Number of samples: 20480
Partial Gradient: [0.24503349601999197, -0.2925381330286953, -0.043129734893707486, 0.85503893364775874, 0.0, -0.19489367900225202, -0.22952858023973033, -0.17538916501571333]
Number of samples: 40960
Partial Gradient: [0.23886953667279237, -0.34597870711457668, -0.035002299567771129, 0.8747851530743963, 0.0, -0.18728046432521867, -0.10484661142419527, -0.10343630607102509]
Number of samples: 81920
Partial Gradient: [0.22346394204400852, -0.13776396508540403, -0.033671081247274241, 0.94155838292837313, 0.0, -0.18591718788046152, -0.086966571387533942, -0.035925493270996825]
Number of samples: 163840
Partial Gradient: [0.31306981802703499, -0.059915437747229398, -0.042623842942844728, 0.90759289203182847, 0.0, -0.25470009160395496, -0.087258436661346014, 0.019225198946107351]
>>> len(aw.order)
168095
```

The observation:

   * When the number reaches half of the total, 
   repeated experiments show it is close to full gradient. 
   * If one want to find reasonably close direction to gradient, 
   maybe 5% of the samples is a cutting point. 

Test of SGD:

```
$ipython -i autoweight.py
[DEBUG][20121129-220413][tencent.py][<module>][12]../snsapi/snsapi/plugin/tencent.pyc plugged!
[DEBUG][20121129-220413][sina.py][<module>][13]../snsapi/snsapi/plugin/sina.pyc plugged!
[DEBUG][20121129-220413][renren.py][<module>][17]../snsapi/snsapi/plugin/renren.pyc plugged!
[DEBUG][20121129-220413][rss.py][<module>][18]../snsapi/snsapi/plugin/rss.pyc plugged!
[DEBUG][20121129-220413][sqlite.py][<module>][18]../snsapi/snsapi/plugin_trial/sqlite.pyc plugged!
[DEBUG][20121129-220413][twitter.py][<module>][19]../snsapi/snsapi/plugin_trial/twitter.pyc plugged!
[DEBUG][20121129-220413][emails.py][<module>][34]../snsapi/snsapi/plugin_trial/emails.pyc plugged!
Load finish. Time elapsed: 0.593
[INFO][20121129-220651][utils.py][report_time_wrapper][173]Function 'sgd' execution time: 155.57

In [1]: aw.evaluate()
total:168095; conc:147070; disc:21025
Out[1]: 0.74984383830572
```

   * 10 * len(order) rounds, about 1.6 million rounds. 
   * The same amount of time can only be used to train 5 rounds of full gradient descent. 
   * The SGD trained weights are larger in magnitude..

```
$cat weights.json
{
  "topic_nonsense": -4.8443593614580225, 
  "topic_interesting": -0.10935901251138158, 
  "text_orig_len": -0.078293811712158684, 
  "contain_link": 0.04371088430921076, 
  "test": -0.010714179481840625, 
  "topic_tech": 5.1596085987427465, 
  "text_len": 0.16374785502596151, 
  "topic_news": 1.323680773249819
}

$cat weights.json.back 
{
  "topic_nonsense": -0.65756949578471435, 
  "topic_interesting": -0.01187361884409446, 
  "text_orig_len": 0.011541341040050229, 
  "contain_link": 0.010435263366801817, 
  "test": -0.010714179481840625, 
  "topic_tech": 0.98361416982880168, 
  "text_len": 0.018320958241528143, 
  "topic_news": 0.29200466227781985
}
```

#### Test Results -- 20121201 -- null tag

This commit is to fix the null tag bug. 
In my test deployment, I created a tag called "null". 
Now "null" is a preserved tag for the system. 
Users can create a tag called "null" but it's no effect in the training. 

Before fixing, the number of pairs derived is:

```
total:254291; conc:223382; disc:30909
```

After:

```
total:923371; conc:807918; disc:115453
```

#### Test Results -- 20121201 -- training and testing

Before this, I was all play on one data set. 

Do three steps of gradient descent. 
One for training Kendall's score and one line for testing Kendall's score. 

```
Training: 0.7500665829623712
Testing: 0.744033951593
Training: 0.7506658296237111
Testing: 0.743153996691
Training: 0.7545847125518396
Testing: 0.745766362807
```

Does not see very strong overfitting phenomenon. 
So I do not consider regularization for now. 

#### Test Results -- 20121201 -- add new feature

Test add "echo" feature. 

After adding echo tag to partial relation graph, more relations are derived:

```
Training samples: 807
Training order: 224602
Testing samples: 808
Testing order: 230139
```

First round of GD:

```
{'contain_link': 0.0081270005166864858,
'echo': -0.023510000798363007,
'test': -0.010714179481840625,
'text_len': -0.053384960002645095,
'text_orig_len': 0.063083392774866201,
'topic_interesting': 0.10888488215231651,
'topic_news': 0.39813412019592981,
'topic_nonsense': -2.0146057775262007,
'topic_tech': 2.5379988552605517}
```

2nd round of GD:

```
{'contain_link': 0.019822972501529292,
'echo': -0.032339012166108294,
'test': -0.010714179481840625,
'text_len': -0.058251207129864445,
'text_orig_len': 0.065154438506658696,
'topic_interesting': 0.10945369472098074,
'topic_news': 0.39897043519360736,
'topic_nonsense': -2.0150917881009582,
'topic_tech': 2.537593079116276}
```

3rd round of GD:

```
{'contain_link': 0.0110405533753417,
'echo': -0.043498638211027063,
'test': -0.010714179481840625,
'text_len': -0.064436792113386515,
'text_orig_len': 0.06617001569993046,
'topic_interesting': 0.11046275563381745,
'topic_news': 0.40006659502034314,
'topic_nonsense': -2.0159023565099941,
'topic_tech': 2.5370427739569452}
```

Start Kendall, end Kendall. 

```
0.739131568313
0.7548641597136267
```

Three rounds of GD is more than 90s now. 

Let's Try SGD.

20W rounds of SGD:

```
{'contain_link': 0.033797105592615791,
'echo': -0.28679197707948184,
'test': -0.010714179481840625,
'text_len': -0.22235930603667214,
'text_orig_len': 0.18263521701155958,
'topic_interesting': 0.98456623929760356,
'topic_news': 7.6946692334176365,
'topic_nonsense': -8.083878873451587,
'topic_tech': 5.9213244215834253}
```

#### Test Results -- 20121201 -- noise feature

Add one dimension of noise feature: random.random()

```
$python evaluation.py
[INFO][20121201-173423][score.py][load_weight][28]Loaded weights: {'topic_nonsense': -8.083878873451587, 'contain_link': 0.03379710559261579, 'echo': -0.28679197707948184, 'topic_interesting': 0.9845662392976036, 'noise': 10.0, 'topic_news': 7.6946692334176365, 'test': -0.010714179481840625, 'topic_tech': 5.921324421583425, 'text_len': -0.22235930603667214, 'text_orig_len': 0.18263521701155958}
Load 'testing_samples.pickle' finish. Time elapsed: 0.442
total:230139; conc:123958; disc:106181
0.0772446217286

$cat conf/weights.json
{
"topic_nonsense": -8.083878873451587, 
"echo": -0.28679197707948184, 
"contain_link": 0.033797105592615791, 
"topic_interesting": 0.98456623929760356, 
"topic_news": 7.6946692334176365, 
"test": -0.010714179481840625, 
"topic_tech": 5.9213244215834253, 
"text_len": -0.22235930603667214, 
"text_orig_len": 0.18263521701155958, 
"noise": 10.0
}

$ipython -i autoweight.py
[INFO][20121201-173508][score.py][load_weight][28]Loaded weights: {'topic_nonsense': -8.083878873451587, 'contain_link': 0.03379710559261579, 'echo': -0.28679197707948184, 'topic_interesting': 0.9845662392976036, 'noise': 10.0, 'topic_news': 7.6946692334176365, 'test': -0.010714179481840625, 'topic_tech': 5.921324421583425, 'text_len': -0.22235930603667214, 'text_orig_len': 0.18263521701155958}
Load finish. Time elapsed: 0.343

In [1]: aw.sgd(200000)
Round 100000
Obj: 69246.6287363
Terminate due to maximum number of rounds
[INFO][20121201-173600][utils.py][report_time_wrapper][173]Function 'sgd' execution time: 30.88
Out[1]: 
{'contain_link': 2.2044055927017983,
'echo': -1.1956661006988245,
'noise': 1.3407107730100154,
'test': -0.010714179481840625,
'text_len': 1.4942336429946812,
'text_orig_len': 4.3976766579494964,
'topic_interesting': 1.2314182268385958,
'topic_news': 8.066024007548247,
'topic_nonsense': -9.0202696149079244,
'topic_tech': 9.1430719900370239}

In [2]: aw.evaluate()
total:224602; conc:173339; disc:51263
Out[2]: 0.5435214290166606

In [3]: aw.sgd(200000)
Round 100000
Obj: 23536.0026903
Terminate due to maximum number of rounds
[INFO][20121201-173653][utils.py][report_time_wrapper][173]Function 'sgd' execution time: 33.60
Out[3]: 
{'contain_link': 0.055660525396769717,
'echo': -0.50567603479053436,
'noise': -0.01322348599003908,
'test': -0.010714179481840625,
'text_len': -0.2502747081741592,
'text_orig_len': 0.11359552082672011,
'topic_interesting': 1.380549192080825,
'topic_news': 8.9611303118169872,
'topic_nonsense': -10.231808660003605,
'topic_tech': 9.5383716431950916}

In [4]: aw.evaluate()
total:224602; conc:202817; disc:21785
Out[4]: 0.80601241306845

In [5]: save_weights(aw)

In [6]: quit()

$python evaluation.py
[INFO][20121201-173755][score.py][load_weight][28]Loaded weights: {'noise': -0.01322348599003908, 'topic_nonsense': -10.231808660003605, 'echo': -0.5056760347905344, 'topic_interesting': 1.380549192080825, 'topic_news': 8.961130311816987, 'contain_link': 0.05566052539676972, 'test': -0.010714179481840625, 'topic_tech': 9.538371643195092, 'text_len': -0.2502747081741592, 'text_orig_len': 0.11359552082672011}
Load 'testing_samples.pickle' finish. Time elapsed: 0.401
total:230139; conc:206007; disc:24132
0.790283263593
```

   * Use [0, 1] uniform distribution to generate noise. 
   * Manual configure the noise weight to be 10 (relatively large compared to others). 
   * The testing Kendall descrease from `0.8` to `0.077`. 
   (expected because the noise is dominating)
   * After 20W SGD, the weight of noise becomes `1.3407107730100154`. 
   Training Kendall becomes `0.5435214290166606`. 
   * After another 20W SGD, the weight of noise becomes `-0.01322348599003908`. 
   Training Kendall becomes `0.80601241306845`. 
   * Testing Kendall becomes `0.790283263593`. 

Conclusion: our method is robust to noise. 

#### Test Results -- add feature: clean text length

Original feature set. 

Start with empty `weights.json`. 
That is, let autoweight script to init itself. 

Train 1 million rounds of SGD. 

```
In [1]: aw.sgd(1000000)
Round 100000
Obj: 26001.7187406
Round 200000
Obj: 24031.2460625
Round 300000
Obj: 23725.1065630
Round 400000
Obj: 22442.6170323
Round 500000
Obj: 21894.6381623
Round 600000
Obj: 21310.9103596
Round 700000
Obj: 21193.6697712
Round 800000
Obj: 21015.2003613
Round 900000
Obj: 21569.7252586
Terminate due to maximum number of rounds
[INFO][20121201-180444][utils.py][report_time_wrapper][173]Function 'sgd' execution time: 165.77
Out[1]: 
{'contain_link': 0.023405986310782972,
'echo': -0.41990839756436549,
'noise': -0.060879099710085038,
'test': 0.014265233613235857,
'text_len': -0.18003681553235829,
'text_orig_len': 0.15591151871600553,
'topic_interesting': 1.2763684561402988,
'topic_news': 9.6008443258403116,
'topic_nonsense': -10.269945924515754,
'topic_tech': 6.8715082680846633}

$python evaluation.py
0.789718387583
```

Add one more feature: clean length. 
This is the length with '@xxx' and URLs removed.

```
In [1]: aw.sgd(1000000)
Round 100000
Obj: 25208.1151041
Round 200000
Obj: 23648.3998749
Round 300000
Obj: 24961.1346787
Round 400000
Obj: 22259.1246294
Round 500000
Obj: 22681.1398709
Round 600000
Obj: 21873.6184402
Round 700000
Obj: 21088.1935524
Round 800000
Obj: 21495.4149170
Round 900000
Obj: 21758.0442106
Terminate due to maximum number of rounds
[INFO][20121201-182522][utils.py][report_time_wrapper][173]Function 'sgd' execution time: 174.63
Out[1]: 
{'contain_link': 0.0780291858610761,
'echo': -0.38212804689199642,
'noise': -0.031236283331422823,
'test': 0.014265233613235857,
'text_len': -0.017531675297471759,
'text_len_clean': -0.232390172627086,
'text_orig_len': 0.15830788072705923,
'topic_interesting': 1.2042662851275558,
'topic_news': 9.4086486597431129,
'topic_nonsense': -10.208358540732377,
'topic_tech': 6.8684959265266263}

In [2]: aw.evaluate()
total:224602; conc:202806; disc:21796
Out[2]: 0.8059144620261618

In [3]: save_weights(aw)

In [4]: quit()

$python evaluation.py
[INFO][20121201-182555][score.py][load_weight][28]Loaded weights: {'text_len': -0.01753167529747176, 'noise': -0.031236283331422823, 'topic_nonsense': -10.208358540732377, 'echo': -0.3821280468919964, 'contain_link': 0.0780291858610761, 'topic_interesting': 1.2042662851275558, 'topic_news': 9.408648659743113, 'test': 0.014265233613235857, 'topic_tech': 6.868495926526626, 'text_len_clean': -0.232390172627086, 'text_orig_len': 0.15830788072705923}
Load 'testing_samples.pickle' finish. Time elapsed: 0.539
total:230139; conc:205744; disc:24395
0.787997688354
```

The clean text length is not well developed. 
Then I removed the face icons.

```
In [1]: aw.sgd(1000000)
Round 100000
Obj: 25397.0501771
Round 200000
Obj: 25218.6178529
Round 300000
Obj: 23685.1995227
Round 400000
Obj: 22387.1577528
Round 500000
Obj: 21847.2883801
Round 600000
Obj: 21854.9256909
Round 700000
Obj: 21868.2446058
Round 800000
Obj: 21767.4519476
Round 900000
Obj: 21961.8654805
Terminate due to maximum number of rounds
[INFO][20121201-185825][utils.py][report_time_wrapper][173]Function 'sgd' execution time: 175.71
Out[1]: 
{'contain_link': 0.10476140027762838,
'echo': -0.29147767277118575,
'noise': -0.01889903839656645,
'test': 0.014265233613235857,
'text_len': -0.057577492160141568,
'text_len_clean': -0.23489599461911193,
'text_orig_len': 0.14708057586460344,
'topic_interesting': 1.2751274459850155,
'topic_news': 9.6429879521773412,
'topic_nonsense': -10.221608132423988,
'topic_tech': 6.8270632401304177}

In [2]: aw.evaluate()
total:224602; conc:202511; disc:22091
Out[2]: 0.8032875931647981

$python evaluation.py
0.782444522658
```

The single feature's Kendall correlation for modified 'text_len_clean' is higher. 
However, this does not help too much in the final training result. 
(numerically speaking)

It's also troublesome to interpret... 
The longer the worse?.. It's contradictory to my intuition. 

Although adding the clean length feature does not improve final score, 
it converges to somewhere around the final point faster. 

#### Test Results -- add user feature

Extract category user frequency and the whole user frequency. 
Use same way as TF * IDF. 

At present, only last message owner is considered. 
It should be beneficial to see who are those people in the forwarding sequence
and who are the originator of the message thread. 

Also train for 100W SGD. 

```
In [1]: aw.sgd(1000000)
Round 100000
Obj: 24470.1189331
Round 200000
Obj: 22830.6563732
Round 300000
Obj: 21553.3286561
Round 400000
Obj: 21597.7579022
Round 500000
Obj: 20434.2861231
Round 600000
Obj: 20561.4460389
Round 700000
Obj: 20395.4779086
Round 800000
Obj: 20290.9376082
Round 900000
Obj: 20593.4605599
Terminate due to maximum number of rounds
[INFO][20121201-210805][utils.py][report_time_wrapper][173]Function 'sgd' execution time: 213.36
Out[1]: 
{'contain_link': 0.085096563801526054,
'echo': -0.21377214865975008,
'noise': -0.021099168368006623,
'test': 0.014265233613235857,
'text_len': -0.16535167862943242,
'text_len_clean': -0.30012415318050478,
'text_orig_len': 0.21669382836483575,
'topic_interesting': 1.2287928824723273,
'topic_news': 8.6220201965506078,
'topic_nonsense': -7.9789832438173187,
'topic_tech': 5.9976735016759939,
'user_interesting': -0.04414832592552214,
'user_news': 1.4994420173117848,
'user_nonsense': -4.4362825212633172,
'user_tech': 1.2429788059520472}

In [2]: aw.evaluate()
total:224602; conc:204262; disc:20340
Out[2]: 0.8188796181690279

$python evaluation.py
0.805178609449
```

There are about 0.02 improvement compared to that without user feature. 
This should be significant enough. 

