<h1> SNSRouter Config Page </h1>

<p>
<a href="/">Back to Home</a>
</p>

<h2> Channel Configs </h2>

<table border=1>

	<tr>
		<th>channel name</th>
		<th>open</th>
		<th>expire_after (s)</th>
		<th>authed?</th>
		<th>platform</th>
		<th>methods</th>
	</tr>

%for conf in info.values():
	<tr>
		<td>{{conf['channel_name']}}</td>
		<td>{{conf['open']}}</td>
		<td>{{conf['expire_after']}}</td>
		<td>{{conf['is_authed']}}</td>
		<td>{{conf['platform']}}</td>
		%if 'methods' in conf:
			<td>{{conf['methods']}}</td>
		%else:
			<td>N/A</td>
		%end
	</tr>
%end

</table>

<h2> Auth Flow Management </h2>

<p>
	Current channel waiting for second stage:
	{{ap.current_channel}}
</p>

<table border=1>

	<tr>
		<th>channel name</th>
		<th>go to auth</th>
	</tr>

%for conf in info.values():
	<tr>
		%#if not conf['is_authed']:
		%if True:
			<td>{{conf['channel_name']}}</td>
			<td> 
				<a href="/auth/first/{{conf['channel_name']}}" target="_new">
					Go Authorization -->
				</a>
			</td>
		%end
	</tr>
%end

</table>

<h2> Feature Weight </h2>

<table border=1>
	<tr>
		<th> Feature </th>
		<th> Weight </th>
	</tr>
%for (f, w) in q.score.feature_weight.iteritems():
	<tr>
		<td> {{f}} </td>
		<td> {{w}} </td>
	</tr>
%end
</table>

<h2> Tags </h2>

<table border=1>
	<tr>
		<th> id </th>
		<th> name </th>
		<th> visible </th>
		<th> parent </th>
		<th> Toggle </th>
	</tr>
%for t in q.tags_all.values():
	<tr>
		<td> {{t['id']}} </td>
		<td> {{t['name']}} </td>
		<td> {{t['visible']}} </td>
		<td> {{t['parent']}} </td>
		<td>
			<a href="/config/tag/toggle/{{t['id']}}">
				Toggle
			</a>
		</td>
	</tr>
%end
</table>

<form method="POST" action="/config/tag/add">
	Add new tag:
	<br />
	<input type="text" name="name" />
	<input type="submit" />
</form>

