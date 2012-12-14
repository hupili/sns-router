<p>
<a href="/">Back to Home</a>
</p>

<h1> Operations </h1>

<p>
Most of the following operations are executed periodically in a backend thread.
Users usually do not have to execute them manually. 
They are here to react to special demand, 
e.g. after changing the configs, reload them and trigger weight adapation. 
</p>

<h2> Reload Config </h2>


<h2> Weight Training </h2>

<ul>
	<li>
	<a href="/operation/weight/prepare_training_data" target="result">
		Prepare Training Data
	</a>
	Dump data from SQLite to pickle, preprocessing, sample training data, etc. 
	This process may take several seconds to minutes depending on how large is your DB. 
	<b>Please wait until result is returned to the frame below. </b>
	</li>

	<li>
	<a href="/operation/weight/train/10000" target="result">
		Train 10000 Steps
	</a>
	Use SGD to train 1W steps. 
	If weights are not satisfying, one can trigger another more 1W rounds. 
	Depending on your sample size, this may take a few seconds to a dozon seconds. 
	<b>Please wait until result is returned to the frame below. </b>
	Number of steps is parameterized in the URL. 
	One can examine it for more inof. 
	</li>

	<li>
	<a href="/operation/weight/reweight_all/86400" target="result">
		Reweight Latest 1 Day 
	</a>
	When weights are changed, new incoming messages will be scored using new weights. 
	However, score of old messages is stored in DB. 
	This operation refreshes score of old messages up to a certain age (1 day by default). 
	<b>Please wait until result is returned to the frame below. </b>
	Age is parameterized in the URL. 
	It should be the same as the age used in "ranked_hometimeline". 
	</li>
</ul>

<h2> Result </h2>

<iframe name="result">
Init
</iframe>
