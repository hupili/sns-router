<h1> home_timeline </h1>

<hr />

%for s in sl:
<div>
<b>{{s.parsed.username}}</b> @ <i>{{snsapi_utils.utc2str(s.parsed.time)}}</i>
<p>
{{!s.parsed.text}}
</p>
</div>
%end
