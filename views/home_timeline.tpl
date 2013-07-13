%include header

<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>

<script>
%include polish.js
</script>

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
	<div>
		channel: <pre style="display:inline;color:red">{{s.ID.channel}}</pre>
	</div>

	<a target="_blank" href="/raw/{{!s.msg_id}}">[raw]</a>

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
	%elif s.platform == "TwitterStatus":
	<img src="https://twitter.com/favicon.ico" />
	%elif s.platform == "RSS":
	<img src="http://www.girlmeetsdress.com/images/Favicon_RSS.jpg" />
	%elif s.platform == "RSS2RW":
	<img src="http://www.girlmeetsdress.com/images/Favicon_RSS.jpg" />
	%elif s.platform == "RSSSummary":
	<img src="http://www.girlmeetsdress.com/images/Favicon_RSS.jpg" />
	%elif s.platform == "Email":
	<img src="https://mail.google.com/favicon.ico" />
	%elif s.platform == "FacebookFeed":
	<img src="http://facebook.com/favicon.ico" />
	%end

	<b>{{s.parsed.username}}</b> @ <i>{{snsapi_utils.utc2str(s.parsed.time)}}</i>
	<a target="result" href="/flag/seen/{{!s.msg_id}}">[Flag as Seen]</a>
	<font color="red"> {{s.weight}} </font> 
	<a href="/why/{{!s.msg_id}}" > why? </a>
	<div class="message_body">
		{{s.parsed.text.strip()}}
	</div>
	%for a in s.parsed.attachments:
	<div>
		%if a['format'][0] == 'link':
			%if a['type'] == 'picture':
				pic:
				<br />
				<img width="400" src="{{a['data']}}" alt="" />
			%else:
				link: <a href="{{a['data']}}" target="_blank">{{a['data']}}</a>
			%end
		%end
	</div>
	%end
	<div>
		%for (k,v) in tags.items():
			<a target="result" href="/tag/{{k}}/{{!s.msg_id}}">{ {{v}} }</a>
		%end
		<br />
		<form target="result" method="POST" action="/forward/{{!s.msg_id}}">
		<input name="comment" type="text" />
		<input type="submit" value="forward"/>
		</form>
	</div>
</div>
%end

<hr />

Operation result frame: <br />

<iframe name="result">
Init
</iframe>

%include footer
