<h1> home_timeline </h1>

<p>
Unseen Messages: {{meta['unseen_count']}}
</p>

<p>
<a href="/">Back to Home</a>
</p>

<hr />

%for s in sl:
<div>
	%if s.platform == "SinaWeiboStatus":
	<img src="http://weibo.com/favicon.ico" />
	%elif s.platform == "RenrenStatus":
	<img src="http://xnimg.cn/favicon.ico" />
	%elif s.platform == "RenrenShare":
	<img src="http://xnimg.cn/favicon.ico" />
	%elif s.platform == "TencentWeiboStatus":
	<img src="http://t.qq.com/favicon.ico" />
	%elif s.platform == "SQLite":
	<img src="http://www.sqlite.org/favicon.ico" />
	%elif s.platform == "Twitter":
	<img src="https://twitter.com/favicon.ico" />
	%elif s.platform == "RSS":
	<img src="http://www.girlmeetsdress.com/images/Favicon_RSS.jpg" />
	%elif s.platform == "RSS2RW":
	<img src="http://www.girlmeetsdress.com/images/Favicon_RSS.jpg" />
	%end

	<b>{{s.parsed.username}}</b> @ <i>{{snsapi_utils.utc2str(s.parsed.time)}}</i>
	<p>
	{{s.parsed.text}}
	<br />
	<a target="_new" href="/flag/seen/{{!s.msg_id}}">[Mark as Seen]</a>
	<br />
	%for (k,v) in tags.items():
		<a target="_new" href="/tag/{{k}}/{{!s.msg_id}}">{ {{v}} }</a>
	%end
	<br />
	<form target="_new" method="POST" action="/forward/{{!s.msg_id}}">
	<input name="comment" type="text" />
	<input type="submit" />
	</form>
	</p>

</div>
%end
