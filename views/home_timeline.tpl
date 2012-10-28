home_timeline

%for s in sl:
<div>
<b>{{s.parsed.username}}</b> @ <i>{{s.parsed.time}}</i>
<p>
{{!s.parsed.text}}
</p>
</div>
%end
