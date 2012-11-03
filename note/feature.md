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

