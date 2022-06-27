import math,random
import json

def sigmoid(x):
    try:
        return 1/(1+math.exp(-x))
    except:
        return 0

def sigmoid_der(x):
    return x*(1-x)


class Brain:
    def __init__(self,layers): #layers = [2,2,1]
        self.rate = 1
        self.network = [] #network[layer][neuron][weight]
        self.bias = [] #bias[layer][neuron]
        #declare neurons n stuff
        for i in range(len(layers)-1):
            self.network.append([])
            self.bias.append([])
            for n in range(layers[i+1]):
                self.network[i].append([])
                self.bias[i].append(0)
                for w in range(layers[i]):
                    self.network[i][n].append(random.random())

    def think(self,inputs):
        outputs = []
        outputs.append(inputs)
        for l in range(len(self.network)):
            outputs.append([])
            layer = self.network[l]
            for n in range(len(layer)):
                neuron = layer[n]
                curoutput = 0
                for w in range(len(neuron)):
                    curoutput += outputs[l][w]*neuron[w]
                outputs[l+1].append(sigmoid(curoutput+self.bias[l][n]))
        return outputs, outputs[len(outputs)-1][0]

    def train(self,inputs,expected):
        outputs, _ = self.think(inputs)
        delta = [[]]
        finalouts = outputs[len(outputs)-1]
        for i in range(len(finalouts)):
            outerror = 2*(expected[i] - finalouts[i])
            outdelta = outerror * sigmoid_der(finalouts[i])
            delta[0].append(outdelta)
        #get all deltas
        for l in reversed(range(len(self.network)-1)):
            layer = self.network[l]
            errors = []
            for n in range(len(layer)):
                curerror = 0
                for out in range(len(self.network[l+1])):
                    curerror += self.network[l+1][out][n] * delta[len(self.network)-2][out]
                errors.append(curerror)
            delta.append([])
            for n in range(len(layer)):
                delta[len(self.network)-1-l].append(errors[n] * sigmoid_der(outputs[l+1][n]))
        delta.reverse()
        #update weights
        for l in range(len(self.network)):
            for n in range(len(self.network[l])):
                for w in range(len(self.network[l][n])):
                    self.network[l][n][w] += delta[l][n] * outputs[l][w] * self.rate
                self.bias[l][n] -= delta[l][n] / 10000

    def mutate(self,factor):
        for l in range(len(self.network)):
            layer = self.network[l]
            for n in range(len(layer)):
                self.bias[l][n] += random.uniform(-1,1)*(factor/10)
                neuron = layer[n]
                for w in range(len(neuron)):
                    neuron[w] += random.uniform(-1,1)*factor

    def getnetwork(self):
        return self.network, self.bias

    def replacenetwork(self,newnets):
        self.network = newnets[0]
        self.bias = newnets[1]

    def save(self,filename):
        newfile = open(str(filename)+'.txt','w')
        sasvedata = []
        savedata.append(self.network)
        savedata.append(self.bias)
        json.dump(savedata, newfile)

    def load(self,filename):
        newfile = open(str(filename)+'.txt','r')
        loaddata = json.load(newfile)
        self.network = loaddata[0]
        self.bias = loaddata[1]
