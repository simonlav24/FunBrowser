import pygame, os, sys
from vector import *

FOLDER_COLOR = (200,200,0)
FILE_COLOR = (0,200,0)
SELECTED_COLOR = (0,0,200)
LINE_COLOR = (160,160,200)
TEXT_COLOR = (220,220,220)

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
        self.dragged = False
        self.radius = 25
        self.renderSurface()
        self.child = None
        self.parent = None
    def renderSurface(self):
        self.labelSurf = font1.render(self.label, True, TEXT_COLOR)
    def insertNode(self, path):
        if self.child is None:
            self.child = FileNode(self.finalPos + Vector(0, self.radius * 4), path)
            self.child.parent = self
        else:
            self.child.insertNode(path)
    def step(self):
        mousePos = pygame.mouse.get_pos()
        self.selected = False
        if distus(mousePos, self.pos) < self.radius **2:
            self.selected = True

        direction = self.finalPos - self.pos
        self.pos += direction * 0.1

        if self.dragged:
            self.pos = vectorCopy(mousePos)
            
        if self.parent:
            self.finalPos = self.parent.pos + Vector(0, self.radius * 4)

    def draw(self):
        if self.child is not None:
            pygame.draw.line(win, LINE_COLOR, self.pos, self.child.pos, 5)
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

homeDirectory = "D:\python\Driver-learn"
dictionary = getFileDict(homeDirectory)
x = 100
for key in dictionary:
    f = FileNode(Vector(x , 100), homeDirectory + "/" + key)
    x += 100
    if dictionary[key] is not None:
        for file in dictionary[key]:
            f.insertNode(file)

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
        if event.type == pygame.MOUSEBUTTONDOWN:
            for node in FileNode._reg:
                if node.selected:
                    node.dragged = True
        if event.type == pygame.MOUSEBUTTONUP:
            for node in FileNode._reg:
                node.dragged = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        run = False

    # step:
    for icon in FileNode._reg:
        icon.step()

    # draw
    win.fill((0,0,0))
    for icon in FileNode._reg:
        icon.draw()

    pygame.display.flip()
    fpsclock.tick(60)

pygame.quit()