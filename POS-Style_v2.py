# -*- coding: utf-8 -*-

# imports
import re
from Tkinter import *
from tkFileDialog import askopenfilename
import matplotlib.pyplot as PLT
import numpy as np
from pattern.de import parse
from collections import Counter


# Global Variables
pageNumbers = []  # contains the pages for all sentences
graphs = []  # graphs
sentences = []  # (starting Char, sentence)
tagged = []  # sentences with tags
tagSentences = []  # sentences containing only the tags
transitions = []  # contains tags transitions
probs = []
graphs = []


# set up Gui
top = Tk()
top.resizable(width=FALSE, height=FALSE)
top.wm_title("Concept-Based Analytics")


def choseFile():
    document = askopenfilename()
    tDocument.delete("1.0", END)
    tDocument.insert(END, str(document))
    print(("Doument " + document + " chosen!"))


def evaluate():
    global graphs, sentences, pageNumbers, probs, graphs
    # remove old evaluation
    del sentences[:]
    del graphs[:]
    del tagged[:]
    del tagSentences[:]
    del probs[:]
    # read from GUI
    fname = tDocument.get("1.0", END).rstrip('\n')
    # read text from file
    with open(fname, 'r') as f:
        text = f.read()
    f.close()
    #f = codecs.open(fname, encoding='utf-8')
    #text = f.read()
    size = len(text)
    print(("Text with " + str(size) + " characters loaded!"))
    #print(repr(text))
    text = repr(text)
    #print(text)
    text = text.replace('\\x0c', '\\n\\x3Cnewpage\\x3E\\n\\n')
    text = eval(text)
    # mark pagenumbers
    text = re.sub(r'\n([0-9]+)\n+<newpage>', r'<pagebreak>\1<pagebreak>', text)
    #print(text)
    # replace whitespaces by spaces
    text = " ".join(text.split())
    # replace abbr.
    text = text.replace('eg.', 'eg')  # TODO: Problem here!
    text = text.replace('Dr.', 'Dr')
    text = text.replace('Prof.', 'Prof')
    text = text.replace('bzw.', 'bzw')
    text = text.replace('Vgl.', 'vgl')
    text = text.replace('vgl.', 'vgl')
    text = text.replace('etc.', 'etc')
    text = text.replace('Abb.', 'Abbildung')
    text = text.replace('z. B.', 'zum Beispiel')
    text = text.replace('ca.', 'cirka')
    text = text.replace('Nr.', 'Nr')
    text = text.replace('nr.', 'nr')
    text = text.replace('Bg.', 'Bg')
    text = text.replace('al.', 'al')
    text = text.replace('europ.', 'europ')
    text = re.sub(" [a-zA-Z]\.", "", text)
    middle_abbr = re.compile('[A-Za-z0-9]\.[A-Za-z0-9]\.')  # middle abb
    a = middle_abbr.search(text)  # find the abbreviation
    b = re.compile('\.')  # period pattern
    c = b.sub('', a.group(0))  # remove periods from abbreviation
    text = middle_abbr.sub(c, text)  # substitute new abbr for old
    # extract sentences
    pat = re.compile(r'([A-Z][^\.!?]*[\.!?])', re.M)
    sentences = pat.findall(text)
    # TODO: remove all very short sentences
    sentences = [elem for elem in sentences if not(calcWords(elem) < 4)]
    # remove all setences that contain a number
    sentences = [elem for elem in sentences if not(hasNumbers(elem))]
    # remove sentences with URL
    sentences = [elem for elem in sentences if not(hasURL(elem))]
    # remove sentences with Noise
    sentences = [elem for elem in sentences if not(hasNoise(elem))]
    # add pagenumbers to sentences
    subset = text
    del pageNumbers[:]
    for sentence in sentences:
        start = subset.find(sentence)
        subset = subset[start:]
        num = re.search("<pagebreak>[0-9]+<pagebreak>", subset).group()
        num = num.replace("<pagebreak>", "")
        pageNumbers.append(num)
    # print all sentences
    for i in range(0, len(sentences)):
        print(("Sentence Nr. " + str(i) +
        ", Page Nr. " + str(pageNumbers[i]) + ": " + sentences[i] + "\n"))
    # create pos
    for sentence in sentences:
        tagged.append(parse(sentence))
    # print all tagged sentences
    for i in range(0, len(sentences)):
        print(("Tagged Sentence Nr. " + str(i) +
        ", Page Nr. " + str(pageNumbers[i]) + ": " + tagged[i] + "\n"))
    # cut words, keep tags, simplify them
    for sentence in tagged:
        fragment = sentence.split(' ')
        tags = []
        for tag in fragment:
            fragment = tag.split('/')[1]
            # simplify tags
            fragment = fragment.replace(".", ".X")
            fragment = fragment.replace(",", ",X")
            fragment = fragment.replace(":", ":X")
            fragment = fragment.replace("(", ")X")
            fragment = fragment.replace("(", ")X")
            fragment = fragment = fragment[0:2]
            tags.append(fragment)
        tagSentences.append(tags)
    # print tags only
    for i in range(0, len(sentences)):
        print(("Sentence Nr. " + str(i) +
        ", Page Nr. " + str(pageNumbers[i]) + ": " +
        str(tagSentences[i]) + "\n"))
    print("Processing done")
    # create transitions for each sentence
    for sentence in tagSentences:
        print(sentence)
        print((sentence[0]))
        # first transition
        trans = []
        trans.append("ST" + str(sentence[0]))  # mark start
        for i in range(1, len(sentence) - 1):
            trans.append(str(sentence[i]) + str(sentence[i + 1]))
        # last transition
        trans.append(str(sentence[i]) + "EN")  # mark end
        #trans = []
        #for i in range(0, len(sentence)):
            #trans.append(str(i) + sentence[i])
        transitions.append(trans)
    print(transitions)
    # Get total probabilities
    allTrans = []
    total = 0
    for trans in transitions:
        for x in trans:
            allTrans.append(x)
            total += 1
    counts = Counter(allTrans)
    print(counts)
    # get first part of transition probabilities (for cond. prob.)
    condTrans = []
    for x in allTrans:
        condTrans.append(x[0:2])
    countsCond = Counter(condTrans)
    print(countsCond)
    # Get average probability of transitions in a sentence
    for trans in transitions:
        size = len(trans)
        score = 1
        #for x in trans:
        for x in range(0, 1):  # len(trans)):
            pTrans = counts[trans[x]]  # count of transition
            pFirst = countsCond[trans[x][0:2]]  # count of first part of trans
            #print(pTrans, pFirst)
            score *= pTrans / float(pFirst)
        probs.append(score)  # / float(size))
    print(probs)


def calcWords(array):
    return len(array.split())


def hasURL(inputString):
    if re.search("http", inputString):
        return True
    if re.search("Http", inputString):
        return True
    if re.search("HTTP", inputString):
        return True
    if re.search("www", inputString):
        return True
    return False


def hasNoise(inputString):
    if re.search("-|–|&|\(|\)|\[|\]|\?|/|\"|:", inputString):
        return True
    return False


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def runningMean(x):
    n = 10  # must be a multiple of 2
    arr = np.convolve(x, np.ones((n,)) / n, mode='full')
    arr = arr[:-n / 2]
    arr = arr[n / 2:]
    return arr


def graph():
    # calculate ticks
    pageNumbersLight = []
    pageNumbersPos = []
    current = -1
    for i in range(0, len(pageNumbers)):
        if(pageNumbers[i] != current):
            current = pageNumbers[i]
            pageNumbersLight.append(current)
            pageNumbersPos.append(i)
    # Create empty figure
    fig = PLT.figure()
    # Add subplot for features
    ax1 = fig.add_subplot(111)
    ax1.plot(probs)
    #ax1.plot(probs)
    ax11 = ax1.twiny()
    new_tick_locations = pageNumbersPos
    ax11.set_xlim(ax1.get_xlim())
    ax11.set_xticks(new_tick_locations)
    ax11.set_xticklabels(pageNumbersLight)
    # Display plot
    PLT.show()


def quit():
    top.destroy()


# Gui Layout
f1 = Frame(top)
bFile = Button(f1, text='Select File', command=choseFile)
bFile.pack(side=LEFT)

lFile = Label(f1, text="File:")
lFile.pack(side=LEFT)
f1.pack(fill=X)


tDocument = Text(top, height=1, width=100)
tDocument.insert(END, "/media/christopher/DATADRIVE1/Datasets/BA2\
/Plagiarized/Chh-short.txt")
tDocument.pack()


f2 = Frame(top)

bEval = Button(f2, text='Exit', command=quit)
bEval.pack(side=RIGHT, padx=7)

bEval = Button(f2, text='Show Graph', command=graph)
bEval.pack(side=RIGHT, padx=7)

bEval = Button(f2, text='Evaluate', command=evaluate)
bEval.pack(side=RIGHT, padx=7)
f2.pack(fill=X, pady=5)

top.mainloop()