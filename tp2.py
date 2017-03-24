#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
import math
import operator

def read_paragraph_file(filepointer):
    paragraphs = []
    for line in filepointer.readlines():
        if line.strip()=="": continue # ignore blank paragraphs
        paragraphs.append(line.lower().strip()) # remove whitespace with strip()
    return paragraphs

def segment_into_sents(paragraph):

    cannot_precede = ["M", "Prof", "Sgt", "Lt", "Ltd", "co", "etc", "[A-Z]", "[Ii].e", "[eE].g"] # non-exhaustive list
    regex_cannot_precede = "(?:(?<!"+")(?<!".join(cannot_precede)+"))"
    
    if "\n" in paragraph: exit("Error in paragraph: paragraph contains \n.")       
    newline_separated = re.sub(regex_cannot_precede+"([\.\!\?]+([\'\’\"\)]*( |$)| [\'\’\"\) ]*))", r"\1\n", paragraph)
    sents = newline_separated.strip().split("\n")
    for s, sent in enumerate(sents):
        sents[s] = "_BEGIN_ " + sent.strip() + " _END_"
    return sents


def normalise(sent):
    sent = re.sub("\'\'", '"', sent) # two single quotes = double quotes
    sent = re.sub("[`‘’]+", r"'", sent) # normalise apostrophes/single quotes
    sent = re.sub("[≪≫“”]", '"', sent) # normalise double quotes
    sent = re.sub("([a-z]{3,})or", r"\1our", sent) # replace ..or words with ..our words (American versus British)
    sent = re.sub("([a-z]{2,})iz([eai])", r"\1is\2", sent) # replace ize with ise (..ise, ...isation, ..ising)
    return sent
    

def tokenise(sent):

    # deal with apostrophes
    sent = re.sub("([^ ])\'", r"\1 '", sent) # separate apostrophe from preceding word by a space if no space to left
    sent = re.sub(" \'", r" ' ", sent) # separate apostrophe from following word if a space if left

    # separate on punctuation by first adding a space before punctuation that should not be stuck to
    # the previous word and then splitting on whitespace everywhere
    cannot_precede = ["M", "Prof", "Sgt", "Lt", "Ltd", "co", "etc", "[A-Z]", "[Ii].e", "[eE].g"] #non-exhaustive list
                                        
    # creates a regex of the form (?:(?<!M)(?<!Prof)(?<!Sgt)...), i.e. whatever follows cannot be
    # preceded by one of these words (all punctuation that is not preceded by these words is to be
    # replaced by a space plus itself
    regex_cannot_precede = "(?:(?<!"+")(?<!".join(cannot_precede)+"))" 
    
    sent = re.sub(regex_cannot_precede+"([\.\,\;\:\)\(\"\?\!]( |$))", r" \1", sent)

    # then restick several consecutive fullstops ... or several ?? or !! by removing the space
    # inbetween them
    sent = re.sub("((^| )[\.\?\!]) ([\.\?\!]( |$))", r"\1\2", sent) 
  
    sent = sent.split() # split on whitespace
    return sent


def tok2count(sents):
    #Create a dictionnary, read the 2D table and add words
    dict = {}
    #For every sentence in all sentences
    for sent in sents:
        for word in sent:
            if not(word in dict.keys()):
                dict[word] = 1
            else:
                dict[word] += 1
    return dict
    

def tok2logprobas(dict):
    logDict = {}
    count = 0;

    for elem in dict:
        count += dict[elem]

    for elem in dict:
        logDict[elem] = math.log(dict[elem]/count)
    return logDict


def train_lm_unigram(sents):
    counts = tok2count(sents)
    prob = tok2logprobas(counts)
    #print(sorted(counts.items(),key=operator.itemgetter(1)))
    return prob


def test_lm_unigram(sent,prob):
    probSent = 0;
    tokens = tokenise(normalise(sent))
    for elem in tokens:
        if elem in prob.keys():
            probSent += prob[elem]        
    return probSent

def bigram2counts(sents):
    #Create a dictionnary, read the 2D table and add words
    list = []
    for sent in sents:
        for i in range(0,len(sent)):
            if(sent[i] != "_END_"):
                list.append(sent[i]+" "+sent[i+1])

    counts = {}
    for sent in list:
        if not sent in counts.keys():
            counts[sent] = 1
        else:
            counts[sent] += 1

    #print(sorted(counts.items(),key=operator.itemgetter(1)))
    return counts


def bigram2logprobas(counts):
    logDict = {}
    
    count = 0
    for elem in counts:
        count += counts[elem]

    for elem in counts:
        logDict[elem] = math.log(counts[elem]/count)

    #print(sorted(logDict.items(),key=operator.itemgetter(1)))
    return logDict

def train_lm_bigram(sents):
    counts = bigram2counts(sents)
    prob = bigram2logprobas(counts)
    #print(sorted(prob.items(),key=operator.itemgetter(1)))
    return prob


def test_lm_bigram(sent,prob):
    probSent = 0;
    sent = "_BEGIN_ " + sent + " _END_" 
    tokens = tokenise(normalise(sent))
    list = []
    for i in range(0,len(tokens)):
            if(tokens[i] != "_END_"):
                list.append(tokens[i]+" "+tokens[i+1])

    for elem in list:
        if elem in prob.keys():
            probSent += prob[elem]        
    return probSent

if __name__=="__main__":
    with open(sys.argv[1],"r") as file_pointer:
        paragraphs = read_paragraph_file(file_pointer)
        sents = []
        for p in paragraphs:
            sents.extend(segment_into_sents(p))
        sents[:] = [tokenise(normalise(sent)) for sent in sents]
        
        train_lm_bigram(sents)
        #prob = train_lm_unigram(sents)
        #print(test_lm_unigram("alice was beginning to get very tired",prob))
        
