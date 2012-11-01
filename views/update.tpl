<form method="POST" action="/update">
<textarea name="status" cols=100 rows=5>
</textarea>
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

<p>
<a href="/">Back to Home</a>
</p>
