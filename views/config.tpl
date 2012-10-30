<h1> SNSRouter Config Page

<h2> Channel Configs

<table border=1>

	<tr>
		<th>channel name</th>
		<th>open</th>
		<th>authed?</th>
		<th>platform</th>
		<th>methods</th>
	</tr>

%for ch in sp.values():
	%conf = ch.jsonconf
	<tr>
		<td>{{conf['channel_name']}}</td>
		<td>{{conf['open']}}</td>
		<td>N/A</td>
		<td>{{conf['platform']}}</td>
		%if 'methods' in conf:
			<td>{{conf['methods']}}</td>
		%else:
			<td>N/A</td>
		%end
	</tr>
%end

</table>
