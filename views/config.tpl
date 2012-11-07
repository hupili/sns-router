<h1> SNSRouter Config Page </h1>

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

<p>
<a href="/">Back to Home</a>
</p>
