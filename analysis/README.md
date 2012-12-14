# SNSRouter Data Analysis

This directory contains scripts to do offline analysis. 
It was initiated in the prototyping time. 
The contents are poorly structured. 
The corresponding logic in this dir will be moved out 
so that it integrates with the frontend better. 

## Usage

After preparing all the resources, run:

```
./run-all.sh
```

You are highly recommended to look into the script first
and get some impression of what is being done there. 
Depending on the data amount, it may taks several seconds to several minutes. 

When my `srfe.db` is about 200M, it takes several minutes to complete. 

After this, some preparation work is done. 
You can use the `exp.py` script to play around. 

```
python -i exp.py
```

Messages are abstracted as Python objects. 
You can start by exploring the following components
(defaultly loaded when you invoke `exp.py`):

   * `message['message_list']`: 
   List of `snsapi.snstype.Message` object. 
   All messages from `srfe.db` will be put in. 
   * `message['seen_list']`:
   List of `snsapi.snstype.Message` object. 
   Only messages with "seen" flag will be put in.
   * `message['dict_msg']`:
   Dict of `snsapi.snstype.Message` object. 
   Key is the `msg_id` in SRFE's SQLite database. 
   * `message['tag_list']`:
   List of `(msg_id, tag_id)` pairs dumped from 
   SRFE's SQLite database. 
   * `message['dict_msg2tag']`: 
   Key is `msg_id` and value is a dict of tags. 
   If message m and tag t appears in `tag_list`, 
   one can asserts that `message['dict_msg2tag'][m][t] == 1`. 
   * `message['dict_tag2msg']`: 
   Reverse for the above. 

## Resources to prepare

### SRFE DB file

Link a `srfe.db` file to the current folder. 
It is an SRFE DB file. 
You can do any preprocessing (e.g. only keep entries within a certain time span). 
All the mining modules are based on this `srfe.db` file. 

### Wordseg dict

   * Sogodict, from 
   [http://www.sogou.com/labs/dl/w.html](http://www.sogou.com/labs/dl/w.html) . 
   download to `kdb/SogouW.tar.gz`
   * Install `pymmseg_cpp` package and copy the contained 
   `words.dic` to `kdb/words.dic`. 
   Depending on your installation path, the location will be different. 
   e.g. `~/.local/lib/python2.7/site-packages/pymmseg_cpp-1.0.0-py2.7-linux-x86_64.egg/mmseg/data/words.dic`
   is a sample path for `--user` installation. 
   You can also find the dict in `mmseg/data/words.dic` of its source package. 

After prepare the resources, run the following command:

```
./prepare_sogo.sh
./merge.sh
```

`wordseg.py` is my interface to word segmentation module. 
You can check out this file, configure to other dictionary or 
substitute the invokation of pymmseg to more advanced modules. 
