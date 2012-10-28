Configs for SNSRouter
====

Simple Guide
----

Please refer to snsapi `conf` folder for 
`channel.json` and `pocket.json`. 
Those are standard snsapi configs. 

The reason to put the configs here instead of 
the `snsapi` subfolder is because we assume 
SNSRouter is invoked from its own root folder. 
By default SNSAPI read `./conf` from the current working folder. 
(This can be changed by passing extra parameters
but we want to keep simplicity)
