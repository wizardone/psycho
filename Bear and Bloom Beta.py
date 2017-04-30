import os, random, math, string
from random import randint
from math import radians, sin, cos
from psychopy import core, visual, event, gui, misc, data 

def enterSubInfo(expName):
    """Brings up a GUI in which to enter all the subject info."""
    try:
        expInfo = misc.fromFile(expName+'_lastParams.pickle')
    except:
        expInfo = {'ExpTitle':expName,'Subject':'s99', 'Subject Initials':'asb','Start at trial':0,'Experimenter Initials':'KV'}
    expInfo['dateStr']= data.getDateStr() 
    dlg = gui.DlgFromDict(expInfo, title=expName+' Exp', fixed=['dateStr'])
    if dlg.OK:
        misc.toFile(expName+'_lastParams.pickle', expInfo)
    else:
        core.quit()
    return expInfo
    
def showInstructions(instructText1,instructText2,pos=[0,.3],waitKeys=True):
    """ Displays the experiment specific instructional/descriptive text. 
    The position/wrapWidth may need to be changed depending
    on the length of the text."""
    
    instructs1 = visual.TextStim(win, color='#fdfdfd',pos=pos,wrapWidth=1.2, height=.06,text= instructText1)
    instructs2 = visual.TextStim(win, color='#fdfdfd',pos=[coord*-.8 for coord in pos],wrapWidth=1.2, height=.06,text= instructText2)
    instructs1.draw()
    instructs2.draw()
    win.flip()
    
    if waitKeys:
        event.waitKeys()
    else:
        pass
    
def makeDataFile(subject,expName):
    """Make an Excel file to save data, will not overwrite existing data"""
    fileName = subject+'_'+expName 
    ext =''
    i = 1
    while os.path.exists(fileName+ext+'.xls'): #changes the extenstion on the filename so no file is ever overwritten.
        ext = '-'+str(i)
        i +=1
    dataFile = open(fileName+ext+'.xls', 'w')
    return dataFile

def writeToFile(fileHandle,trial,sync=True):
    """Writes a trial (a dictionary) to a fileHandle, in a specific order, given 
    by overall order (general variables that are always used) and experiment 
    specific variables (variables that vary based on what you're measuring)."""

    overallOrder = ['subject','subInitials','date','experimenter','totalTime','trialNum','confAnswer']
    overallOrder.extend(expVarOrder)
    
    line = ''
    
    #place var names on first line before training
    if trialNum==0:
        for item in overallOrder:
            line += item
            line += '\t'
        line += '\n'
    
    for item in overallOrder:
        line += str(trial[item])
        line += '\t'
    line += '\n' #add a newline
    print line
    fileHandle.write(line)
    if sync:
        fileHandle.flush()
        os.fsync(fileHandle)

def generateTraining():
    """Generates initial trial list for training phase, before latencies are added."""
    
    trials = []
    
    for trial in xrange(numTraining):
        trials.append({'latency':'NA','avgChoiceTime':'NA'})
        
    return trials
    
def generateExperimental(throwOut=15):
    """Generates experimental trials."""
    
    # time before the red target appears
    choiceLatencies = [3,5,10,15,20,30,60]
    askConf = [0,1]
    
    # generate experimental trials
    # reps are number of times all latency types loop (i.e.,numTrials/numLatencies)
    trials = []
    
    for rep in xrange(reps):
        for latency in choiceLatencies:
            for asked in askConf:
                trials.append({'latency':int(latency),'avgChoiceTime':'NA','askConf':asked})
            
    # randomly shuffle only experimental trials
    random.shuffle(trials)
            
    return trials
    
def addTrialVariables():
    """Adds extra trial details to each line written to the datafile."""
    trial['subject'] = expInfo['Subject']
    trial['subInitials'] = expInfo['Subject Initials']
    trial['experimenter'] = expInfo['Experimenter Initials']
    trial['date'] = expInfo['dateStr']
    trial['totalTime'] = expClock.getTime()
    trial['trialNum'] = trialNum + 1 #add 1 because index starts at 0
    trial['circlePositions'] = circlePositions
    trial['response'] = response
    trial['responseTime'] = responseTime
    trial['choiceTime'] = choiceTime
    trial['confAnswer'] = confAnswer

def readySequence():
    """Prompts subject with "Ready" screen and counts down to stimulus presentation."""
    
    ready.draw()
    trialDisplay = visual.TextStim(win,text=trialNum+1,height=.08,pos=(0,-.8),color=[1,1,1]) #displays trial num.
    trialDisplay.draw()
    win.flip()
    
    # check for 'q' press to quit experiment prematurely
    if ['q']==event.waitKeys(keyList=['space','q']):
        quit.draw()
        win.flip()
        if ['y']==event.waitKeys(keyList=['y','n']):
            dataFile.close()
            win.close()
            core.quit()
        else:
            ready.draw()
            win.flip()
            event.waitKeys(keyList=['space'])
    
    fixation.draw()
    win.flip()
    core.wait(.5)


def presentStimuli(numCircles,askConf,latency='NA',training=False):
    """Draws non-overlapping circles in window for specified time."""

    # create circle stimuli
    circles = []
    
    for circleNum in xrange(numCircles):
        circles.append(visual.Circle(win,size=70,units='pix',fillColor=[1,1,1]))
    
    # repeatedly generate a random pos for circles until they don't overlap with other circles
    for circleNum,circle in enumerate(circles):
        tryAgain = True
        while tryAgain:
            circle.pos = (random.choice([-1,1])*(150*random.random()+25),random.choice([-1,1])*(150*random.random()+25))
            tryAgain = False      
            for i in xrange(circleNum): 
                if circle.overlaps(circles[i]):
                    tryAgain = True
                    break
    
    if training==True: ##Training Trials
        response = 'NA'
        responseTime = 'NA'
                
        # draw all non-overlapping circles
        for circle in circles:
            circle.draw(win)
        win.flip()

        choiceClock.reset()

        event.waitKeys(keyList=['space'])
        choiceTime = choiceClock.getTime()
    
    else: ##Experimental Trials
        choiceTime = 'NA'
        
        # draw all non-overlapping circles for specified latency time
        for n in xrange(latency):
            for circle in circles:
                circle.draw(win)
            win.flip()
                
        # choose target circle and fill it in red
        # (always use circle 1 as target since position is random)
        circles[1].fillColor = [1,0,0]
        
        for circle in circles:
            circle.draw(win)
        win.flip()
    
        responseClock.reset()
    
        # store whether subject guessed target circle (t/f) and when
        response = event.waitKeys(keyList=['t','f','c'])
        responseTime = responseClock.getTime()
    
        # ask the confidence question if one of the designated trials
        if askConf and response!=['c']:
            confQuestionVisual.draw(win)
            win.flip()
            confAnswer = event.waitKeys(keyList=['1','2','3','4','5'])
        else: 
            confAnswer = 'NA'
    
    # store final positions of all circles
    circlePositions = [str(circle.pos) for circle in circles]
    
    # also return choiceTime (make 'NA' for real trials) and responseTime ('NA' for real trials)
    return circlePositions,response,responseTime,choiceTime,confAnswer,

## Define Experimental Variables ##
expVarOrder = ['latency','avgChoiceTime','circlePositions','response','responseTime','choiceTime']
expInfo = enterSubInfo('Circle Choice')
dataFile = makeDataFile(expInfo['Subject'],expInfo['ExpTitle'])

win = visual.Window([1920,1080],color=[-1,-1,-1],fullscr=True,monitor='testMonitor')
ready = visual.TextStim(win,text='Ready?',height=.3,color=[1,1,1])
fixation = visual.TextStim(win,text='+',height=.07,color=[1,1,1])

quit = visual.TextStim(win,text='Quit experiment now (y/n)?',height=.1,color=[1,1,1])
confQuestionText = 'On a scale from 1 to 5, how confident are you in your response (1=not at all confident, 5=extremely confident)?'
confQuestionVisual = visual.TextStim(win,color='#fdfdfd',wrapWidth=1.2, height=.06,text=confQuestionText)

mouse = event.Mouse(visible=False,win=win)

expClock = core.Clock()
responseClock = core.Clock()
choiceClock = core.Clock()

## Practice Instructions ##
text1 = 'Welcome!The aim of it is to see how people choose shapes on a screen. \
First you will see a plus sign (+) in the middle of the screen .\
Then 2 circles will show up on the screen at different locations '

text2 = 'As quickly as you can: choose one of these circles in your head and remember which one it is. \
There is no right choice- just pick any circle you want. \
(Press any key to continue with the instructions.)'

showInstructions(text1,text2)

text1 = 'After some time (sometimes very quickly) one of the circles will turn red. \
If this was the circle you chose: press T (True).\
If it was not the circle you chose: press F (False).'

text2 = 'A circle will sometimes turn red really fast, so it is important to \
choose a circle in your head as fast as you can. \
If you still could not choose a circle before one of them turned red, press C.\
(Press any key to continue with the instructions.)'

showInstructions(text1,text2)

text1 = 'You will see the word Ready? before each new trial.\
Press SPACEBAR when you are ready to answer. Take as many breaks as you need.\
You can ask me questions before you press the SPACEBAR.'

text2 = 'We will first practice this a few times. Whenever you are ready, \
press any key to continue.'

showInstructions(text1,text2)

text1 = 'On some trials, you will be asked "How confident are you that this is the circle you chose?".\
You can answer on a 1-5 scale: 1 is "not at all confident", 5 is "extremely confident".'

text2 = 'If you feel very confident on all or most trials, it is perfectly acceptable to always answer 5.\
If you are always not sure it is perfectly acceptable to always answer with 1 or 2.\
There are no correct answers. We simply want your honest judgments. (Press any key to continue.)'

showInstructions(text1,text2)

## Practice Trials ##
reps = 1 #go through each kind of experimental trial once for practice
practiceTrials = generateExperimental()

for trialNum,trial in enumerate(practiceTrials):
    readySequence()
    presentStimuli(2,trial['askConf'],trial['latency'])
    
## Final Instructions ##
text = 'Now the real experiment will start.\
Remember that you can take as many breaks as you want\
Please ask your questions now or when the "Ready?" screen appears \
press any key to continue.'

instruct = visual.TextStim(win,color='#fdfdfd',pos=[0,0],wrapWidth=1.2,height=.06,text=text)
instruct.draw()
win.flip()
event.waitKeys()
    
## Experimental Trials ##
reps = 14 #number of experimental trials is reps*number of latencies
experimentalTrials = generateExperimental()

for trialNum,trial in enumerate(experimentalTrials):
    readySequence()
    circlePositions,response,responseTime,choiceTime,confAnswer = presentStimuli(2,trial['askConf'],trial['latency'])
    addTrialVariables()
    writeToFile(dataFile,trial)

