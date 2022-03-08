import pygame, os, sys, subprocess
from vector import *

FOLDER_COLOR = (200,200,0)
FILE_COLOR = (0,200,0)
SELECTED_COLOR = (0,0,200)
LINE_COLOR = (80,80,80)
TEXT_COLOR = (220,220,220)

TYPE_REGULAR = 0
TYPE_IMAGE = 1

pictureTypes = [".jpg", ".png", ".jpeg", ".gif"]

def Popen(command):
    print(command)
    subprocess.check_call(command, shell=True)
    
def openFile(path):
    os.startfile(path)

def listFilesInDir(path):
    # returns a list of files and folders in the given directory
    res = []
    for file in os.listdir(path):
        res.append(path + "/" + file)
    return res

def getFileDict(path):
    dictionary = {}
    if os.path.isfile(path):
        dictionary[path] = [path]
    else:
        for file in os.listdir(path):
            if os.path.isdir(path + "/" + file):
                dictionary[file] = listFilesInDir(path + "/" + file)
            else:
                dictionary[file] = None
    return dictionary

class Places:
    _p = None
    def __init__(self):
        Places._p = self
        self.places = []
        self.startPos = Vector(100,100)
        self.direction = Vector(1,0)
        self.distance = 100
    def getPlace(self):
        if len(self.places) == 0:
            self.places.append((vectorCopy(self.startPos), 0))
            return self.places[-1]
        lastPlace = self.places[-1][0]
        self.places.append((lastPlace + self.distance * self.direction, len(self.places)))
        return self.places[-1]

class FileNode:
    _reg = []
    def __init__(self, pos, path):
        FileNode._reg.append(self)
        self.finalPos = vectorCopy(pos)
        self.pos = Vector()
        self.vel = Vector()
        self.acc = Vector()
        self.label = os.path.basename(path)
        self.path = path
        self.selected = False
        self.dragged = None
        self.radius = 25
        self.renderSurface()
        self.child = None
        self.parent = None
        self.place = None
        self.surf = None
        self.processFile()
        
    def processFile(self):
        self.fileType = TYPE_REGULAR
        for type in pictureTypes:
            if type in self.path:
                self.fileType = TYPE_IMAGE
                break
        
        if self.fileType == TYPE_IMAGE:
            image = pygame.image.load(self.path)
            self.surf = pygame.transform.scale(image, (self.radius * 2, self.radius * 2))
                
    def renderSurface(self):
        self.labelSurf = font1.render(self.label, True, TEXT_COLOR)
    def insertNode(self, path):
        if self.child is None:
            
            self.child = FileNode(self.pos + Vector(0, self.radius * 4), path)
            self.child.parent = self
        else:
            self.child.insertNode(path)
    def step(self):
        mousePos = pygame.mouse.get_pos()
        self.selected = False
        if distus(mousePos, self.pos) < self.radius **2:
            self.selected = True

        direction = self.finalPos - self.pos
        self.pos += direction * 0.3

        if self.dragged:
            self.pos = vectorCopy(self.dragged) + tup2vec(mousePos)
            
        if self.parent:
            self.finalPos = self.parent.pos + Vector(0, self.radius * 4)

    def draw(self):
        if self.child is not None:
            pygame.draw.line(win, LINE_COLOR, self.pos, self.child.pos, 5)
        if self.fileType == TYPE_IMAGE:
            win.blit(self.surf, self.pos - tup2vec(self.surf.get_size())//2)
        elif self.fileType == TYPE_REGULAR:
            if self.selected:
                pygame.draw.circle(win, SELECTED_COLOR, self.pos, self.radius)
            else:
                pygame.draw.circle(win, FOLDER_COLOR, self.pos, self.radius)
        win.blit(self.labelSurf, self.pos - tup2vec(self.labelSurf.get_size())//2 + Vector(0, self.radius + 10))
        
pygame.init()
fpsclock = pygame.time.Clock()
font1 = pygame.font.SysFont('Calibri', 16)
winWidth = 1280
winHeight = 720
win = pygame.display.set_mode((winWidth, winHeight), pygame.RESIZABLE)

homeDirectory = "D:\python\wormsGame"
dictionary = getFileDict(homeDirectory)

Places()

x = 100
for key in dictionary:
    place = Places._p.getPlace()
    f = FileNode(place[0], homeDirectory + "/" + key)
    f.place = place
    x += 100
    if dictionary[key] is not None:
        for file in dictionary[key]:
            f.insertNode(file)

doubleClick = False
doubleClickTime = 15
doubleClickCount = 0

run = True
# main loop
while run:
    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.VIDEORESIZE:
            winWidth = event.w
            winHeight = event.h
            win = pygame.display.set_mode((winWidth, winHeight), pygame.RESIZABLE)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if doubleClickCount <= doubleClickTime:
                # double click
                for node in FileNode._reg:
                    if node.selected:
                        openFile(node.path)
            else:
                doubleClickCount = 0
                for node in FileNode._reg:
                    if node.selected:
                        node.dragged = node.pos - tup2vec(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for node in FileNode._reg:
                node.dragged = None

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        run = False

    # step:
    for icon in FileNode._reg:
        icon.step()

    doubleClickCount += 1
    
    # draw
    win.fill((0,0,0))
    for icon in FileNode._reg:
        icon.draw()

    pygame.display.flip()
    fpsclock.tick(60)

pygame.quit()