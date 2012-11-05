# Brainstorm on Features

## Introduction

To classify the messages into correct category
(mark, tag, channel, etc), 
we need a set of good feature first. 

This file docments the brainstorm of features. 

## Shortlist

   * Length of messages. 
   According to Twitter statistics, `length<40` 
   messages are less retweeted while `70-100` character messsages 
   are better retweeted. 
   The threshold for Chinese should be different 
   but the perceptual rule may apply. 
   Too short messages are mostly personal nagging. 
   They are meaningless in general. 
   (It may also be some classical work)
   * Face icon, like 
   `[哈哈][哈哈][哈哈][哈哈]` on Sina. 
   Extracting such feature on multiple platform 
   is not easy. 
   There are two use. 
   1) Do sentiment analysis: positive or negative emotion. 
   2) too many or pure face icons can mean noise. 
   * "Paibi" style is the usual typesetting for 
   many interesting short messages. 
   * Data presented in a message. 
   Numerical value may be marked for later use. 
   This is a good symbol in general. 
   * "Xingzuo", it's usually nonsense. 
   * Pure images? Like scenery during one's travel. 
   * Number of users being @-ed in the message posting. 
   This may be a symbol of low quality. 
   * Number of users in the forwarding sequence. 
   This may be a symbol of high quality. 
   * Deleted messages, like "抱歉，此微博已被作者删除" on Sina. 
   It's weird that Sina will return such messages. 
   It's obvious non-informative. 
   * Use profile information to analyze the content. 
   e.g. for big V's, "flight" "late" can be categorized into "daily life". 
   for ordinary people, "eating" "photograph" can be categorized into "daily life". 

