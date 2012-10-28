<form method="POST" action="/update">
<input name="status" type="text" />
<input type="submit" />
</form>

% setdefault('submit', False)

%if submit:

<div>
Your status: {{status}}
</div>
<div>
Result:
<pre>
{{result}}
</pre>
</div>

%end
