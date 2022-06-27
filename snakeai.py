import tkinter as tk
import math
import random
import time
import brain
import copy


def getmagn(vec):
    return math.sqrt((vec[0])**2 + (vec[1])**2)

def unitvec(vec):
    magn = getmagn(vec)
    if magn == 0:
        return [0,0]
    return [vec[0]/magn,vec[1]/magn]

class window:
    def __init__(self,master):
        self.master = master

        self.brainlayout = [14,60,60,60,60,4]

        self.population = 16
        self.snakesshown = 4
        self.popscreendiv = 2
        self.noofparents = 4
        self.mutfactor = 100
        self.newsnakechance = 8 #out of 100

        self.playing = True
        self.size = 30
        self.simul = 5
        self.delta = 0.5

        self.generation = 1
        self.snakesdead = 0
        self.snakes = []
        for i in range(self.population):
            self.snakes.append({'brain':brain.Brain(self.brainlayout),
                                'mutationfactor': random.uniform(0,1),
                                'score':0,
                                'ate':0,
                                'direction':[0,-1],
                                'apple':[random.randint(0,self.size-1),random.randint(0,self.size-1)],
                                'sparts':[[int(self.size/2),int(self.size/2)],[int(self.size/2)-1,int(self.size/2)]],
                                'dead' : False,
                                'steps' : 0
                                })

        self.genindicator = tk.Label(master,text='Generation 1',font='legacy 15 bold')
        self.genindicator.grid(row=0,column=0,columnspan=2)

        self.scoretexts = []
        for i in range(self.snakesshown):
            self.scoretexts.append(tk.Label(master,text='Score: 0+0',font='legacy 15 bold'))
            self.scoretexts[i].grid(row=int(math.floor(i/self.popscreendiv)*2)+1,column=int(i%self.popscreendiv))

        self.boards = []
        for i in range(self.snakesshown):
            self.boards.append(tk.Canvas(master,width=self.size*self.simul,height=self.size*self.simul,bg='#66bb66'))
            self.boards[i].grid(row=int(math.floor(i/self.popscreendiv)*2)+2,column=int(i%self.popscreendiv))

        #master.bind("<Key>",self.keypress)
        #self.lastkey = 0
       
    #def keypress(self,event):
        #self.lastkey = event.keycode

    def replacesnake(self,no):
        orient = random.randint(0,1)
        newdir = [0, 0]
        newdir[orient] = random.randint(0,1)*2 - 1
        newpos = [random.randint(2,self.size-3),random.randint(2,self.size-3)]
        self.snakes[no] ={'brain':brain.Brain(self.brainlayout),
                          'mutationfactor': 1,
                            'score':0,
                            'ate':0,
                            'direction': newdir,
                            'apple':[random.randint(0,self.size-1),random.randint(0,self.size-1)],
                            'sparts':[newpos,[newpos[0]-newdir[0],newpos[1]-newdir[1]]],
                            'dead' : False,
                            'steps' : 0
                            }

    def restartsnake(self,snake):
        orient = random.randint(0,1)
        newdir = [0, 0]
        newdir[orient] = random.randint(0,1)*2 - 1
        newpos = [random.randint(2,self.size-3),random.randint(2,self.size-3)]
        snake['score'] = 0
        snake['ate'] = 0
        snake['direction'] = newdir
        snake['apple'] = [random.randint(0,self.size-1),random.randint(0,self.size-1)]
        snake['sparts'] = [newpos,[newpos[0]-newdir[0],newpos[1]-newdir[1]]]
        snake['dead'] = False
        snake['steps'] = 0

    def mutate(self,snake,factor):
        snake['brain'].mutate(factor)

    def crossbreed(self,networks,fitness): #[ [weights, biases] ... ]
        fitnesschoices = []
        for i in range(len(fitness)):
            for n in range(fitness[i]):
                fitnesschoices.append(i)
        noofchoices = len(fitnesschoices)-1
       
        pbasenet = networks[0][0]
        pbasebias = networks[0][1]
        noofparents = len(networks)-1
        offspringnet = []
        offspringbias = []
        for l in range(len(pbasenet)):
            layer = pbasenet[l]
            offspringnet.append([])
            offspringbias.append([])
            for n in range(len(pbasenet[l])):
                neuron = layer[n]
                offspringnet[l].append([])
                biasfrom = fitnesschoices[random.randint(0,noofchoices)]
                newbias = networks[biasfrom][1][l][n]
                offspringbias[l].append(newbias)
                for w in range(len(pbasenet[l][n])):
                    wghtfrom = fitnesschoices[random.randint(0,noofchoices)]
                    newweight = networks[wghtfrom][0][l][n][w]
                    offspringnet[l][n].append(newweight)
        return [offspringnet, offspringbias]

    def isblocked(self,snake,pos):
        for i in snake['sparts']:
            if i == pos:
                return True
        return False

    def think(self,snake,checkinp):
        s = snake
        direction = s['direction']
        head = s['sparts'][len(s['sparts'])-1]
        forwardpos = [head[0]+direction[0],head[1]+direction[1]]
        leftpos = [-direction[1]+head[0],direction[0]+head[1]]
        rightpos = [direction[1]+head[0],-direction[0]+head[1]]
       
        uwall = ((self.size-1) - head[0])
        dwall = head[0]
        lwall = ((self.size-1) - head[1])
        rwall = head[1]

        #vision - north, northeast, east, southeast, south, southwest, west, northwest
        uvision = copy.deepcopy(uwall)
        dvision = copy.deepcopy(dwall)
        lvision = copy.deepcopy(lwall)
        rvision = copy.deepcopy(rwall)
        uwall /= self.size
        dwall /= self.size
        lwall /= self.size
        rwall /= self.size
       
        for part in s['sparts']:
            vectopart = [part[0]-head[0],part[1]-head[1]]
            disttopart = getmagn(vectopart)
            directtopart = unitvec(vectopart)
            if disttopart < uvision and directtopart == [0,-1]:
                uvision = disttopart
            elif disttopart < dvision and directtopart == [0,1]:
                dvision = disttopart
            elif disttopart < lvision and directtopart == [-1,0]:
                lvision = disttopart
            elif disttopart < rvision and directtopart == [1,0]:
                rvision = disttopart
        uvision /= self.size
        dvision /= self.size
        lvision /= self.size
        rvision /= self.size

        goingu = 0
        goingd = 0
        goingl = 0
        goingr = 0
        if direction[0] > 0:
            goingr = 1
        elif direction[0] < 0: goingl = 1
        if direction[1] > 0:
            goingd = 1
        elif direction[1] < 0: goingu = 1
       
        applepos = s['apple']
        vectoapple = [ applepos[0]-head[0], applepos[1]-head[1] ]
        appleunitvec = unitvec(vectoapple)
        #crossprod = (direction[0]*vectoapple[1])-(direction[1]*vectoapple[0])
        #dotprod = direction[0]*vectoapple[0] + direction[1]*vectoapple[1]

        appleisu = 0
        appleisd = 0
        appleisl = 0
        appleisr = 0
        if vectoapple[0] > 0:
            appleisr = appleunitvec[0]
        else: appleisl = -appleunitvec[0]
        if vectoapple[1] > 0:
            appleisd = appleunitvec[1]
        else: appleisu = -appleunitvec[1]

        disttoapple = getmagn(vectoapple) / self.size

        blockingdist = 1 / self.size
        braininput = [blockingdist,
                      #uwall,dwall,lwall,rwall,
                      uvision,dvision,lvision,rvision,
                      goingu,goingd,goingl,goingr,
                      appleisu,appleisd,appleisl,appleisr,
                      disttoapple]
        #if checkinp:
            #print(braininput)
        outputs,_ = snake['brain'].think(braininput)
        #if checkinp:
            #print(outputs[len(outputs)-1])
        return outputs[len(outputs)-1]

    def run(self):
        self.gameloop()
        self.render()

    def gameloop(self):
        checkinp = True
        for s in self.snakes:
            if s['dead']:
                continue

            outputs = self.think(s,checkinp)
            checkinp = False
            if s['direction'] != [ 0, -1 ] and outputs[0] > outputs[1] and outputs[0] > outputs[2] and outputs[0] > outputs[3]:
                s['direction'] = [ 0, 1 ]
            elif s['direction'] != [ 0, 1 ] and outputs[1] > outputs[2] and outputs[1] > outputs[3]:
                s['direction'] = [ 0, -1 ]
            elif s['direction'] != [ 1, 0 ] and outputs[2] > outputs[3]:
                s['direction'] = [ -1, 0 ]
            elif s['direction'] != [ -1, 0 ]:
                s['direction'] = [ 1, 0 ]
           
            snlength = len(s['sparts'])-1
            front = s['sparts'][snlength]

            applepos = s['apple']
            head = s['sparts'][len(s['sparts'])-1]
            oldappledist = getmagn([ applepos[0]-head[0], applepos[1]-head[1] ])
           
            newpos = [front[0]+s['direction'][0],front[1]+s['direction'][1]]
            newappledist = getmagn([ applepos[0]-head[0], applepos[1]-head[1] ])
            s['sparts'].append(newpos)

            if newappledist < oldappledist:
                s['score'] += 0.1
            else:
                s['score'] -= 0.18

            while len(s['sparts'])-1>s['ate']+1:
                del s['sparts'][0]

            hasdied = False
            for i in range(len(s['sparts'])-1):
                if s['sparts'][len(s['sparts'])-1] == s['sparts'][i]:
                    hasdied = True
            if (newpos[0]<0 and s['direction']==[-1,0]) or (newpos[0]>self.size-1 and s['direction']==[1,0]):
                hasdied = True
                #s['score'] -= (1-(self.snakesdead/self.population))*6
            elif (newpos[1]<0 and s['direction']==[0,-1]) or (newpos[1]>self.size-1 and s['direction']==[0,1]):
                hasdied = True
                #s['score'] -= (1-(self.snakesdead/self.population))*6
            #elif newpos[0]-2<0 or newpos[0]+2>self.size-1 or newpos[1]-2<0 or newpos[1]+2>self.size-1:
                #s['score'] += 0.2

            if newpos == s['apple']:
                s['steps'] = 0
                s['ate'] += 1
                s['score'] = 0
                #s['score'] += 15
                s['apple'] = [random.randint(0,self.size-1),random.randint(0,self.size-1)]
            else:
                s['steps'] += 1
                if s['steps'] > 200:
                    #s['score'] -= 10
                    hasdied = True

            if hasdied:
                self.snakesdead += 1
                #s['score'] -= (1-(self.snakesdead/self.population))
                s['dead'] = True
               

        if self.snakesdead >= self.population:
            self.newgeneration()


    def newgeneration(self):
        parents = []
        for p in range(self.noofparents):
            parents.append([p,self.snakes[p]['ate'],self.snakes[p]['score']])
        for sno in range(self.noofparents,len(self.snakes)):
            cursnake = self.snakes[sno]
            for i in range(self.noofparents):
                if cursnake['ate'] > parents[i][1] or (cursnake['ate'] == parents[i][1] and cursnake['score'] > parents[i][2]):
                    for p in range(i,self.noofparents):
                        parents[p][0] = parents[p-1][0]
                        parents[p][1] = parents[p-1][1]
                        parents[p][2] = parents[p-1][2]
                    parents[i][0] = sno
                    parents[i][1] = cursnake['ate']
                    parents[i][2] = cursnake['score']
                    break
        #print(parents)
        newparents = []
        for i in range(self.noofparents):
            newparents.append(self.snakes[parents[i][0]].copy())

        parentgenes = []
        fitnessweights = []
        for i in range(self.noofparents):
            parentgenes.append(newparents[i]['brain'].getnetwork())
            fitnessweights.append(newparents[i]['ate']+1)
            self.restartsnake(self.snakes[i])
               
        for i in range(self.population):
            isnewsnake = random.randint(0,100)
            if isnewsnake > self.newsnakechance:
                self.snakes[i]['brain'].replacenetwork(self.crossbreed(parentgenes,fitnessweights))
            else:
                self.snakes[i]['brain'] = brain.Brain(self.brainlayout)
            self.mutate(self.snakes[i],self.mutfactor)
            self.restartsnake(self.snakes[i])
            #self.snakes[i]['mutationfactor'] = random.uniform(0,2)

        self.snakesdead = 0
        self.generation += 1
        self.genindicator.config(text='Generation '+str(self.generation))

    def render(self):
        for i in range(self.snakesshown):
            board = self.boards[i]
            scoretext = self.scoretexts[i]
            snake = self.snakes[i]
            board.delete("all")

            for part in snake['sparts']:
                x = part[0]*self.simul
                y = part[1]*self.simul
                try:
                    board.create_rectangle(x,y,x+self.simul,y+self.simul,fill='white',width=0,outline='')
                except: print(x,y,self.simul)
               
            applex = snake['apple'][0]*self.simul
            appley = snake['apple'][1]*self.simul
            board.create_rectangle(applex,appley,applex+self.simul,appley+self.simul,fill='red',width=0,outline='')

            #movescore = math.floor(snake['score']*(10**3))/(10**3)
            scoretext.config(text='Score: '+str(snake['ate']))#+'+'+str(movescore))
       


root = tk.Tk()
win = window(root)
root.title("snake")
while win.playing:
    win.run()
    root.update()
root.destroy()
