# SNSRouter Data Analysis

## Usage

link a `srfe.db` file to the current folder. 

## Resources to prepare

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
