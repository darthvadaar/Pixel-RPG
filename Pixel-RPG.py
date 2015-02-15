from pygame import *
init()

def gamespeed(fps):
    change= 60/fps
    player.speed=player.speed*change
background=image.load("Art\map.jpg")
def changepos(rect,key,run,speed):
    if run:
        d = speed
    else:
        d = 1
    if key[K_UP] == 1:
        rect[1] -= d
    if key[K_DOWN] == 1:
        rect[1] += d
    if key[K_LEFT] == 1:
        rect[0] -= d
    if key[K_RIGHT] == 1:
        rect[0] += d
        
class People:
    def __init__(self,health,speed,attack,defense,mana,posx,posy):
        self.run = False
        self.size = Rect(posx,posy,10,20)
        self.health = health
        self.speed = speed
        self.attack = attack
        self.defense = defense
        self.mana = mana


class Player(People):
    def __init__(self,health,speed,attack,defense,mana,stamina,money,level,kind,posx,posy,col,):#animation
        People.__init__(self,health,speed,attack,defense,mana,posx,posy)
        self.stamina = stamina
        self.money = money
        self.level = level
        self.kind = kind
        self.col = col
        #self.animation = animation   

screen = display.set_mode((1024,768)) 
running =True
mode = 0 #What menu the user is on (0 is character selection, 1 is actual game)

clock = time.Clock()

while running:
    screen.fill((0,0,0))
    mb = mouse.get_pressed()
    mx,my = mouse.get_pos()
    kb = key.get_pressed() #Finds what keys are being pressed (similar to mouse.get_pressed())
        
    for e in event.get():
        if e.type == QUIT:      
            running = False
    if mode == 0:  #Character selections
        draw.rect(screen,(0,0,255),wizard) #The wizard box
        draw.rect(screen,(255,0,0),knight) #The kinght box
        draw.rect(screen,(0,255,0),archer)
        if wizard.collidepoint(mx,my) and mb[0] == 1:
            mode = 1
            player = Player(80,3,30,10,100,60,0,1,'Wizard',512,384,(0,0,255))
        if knight.collidepoint(mx,my) and mb[0] == 1:
            mode = 1
            player = Player(120,2,20,30,20,80,0,1,'Knight',512,384,(255,0,0))
        if archer.collidepoint(mx,my) and mb[0] == 1:
            mode = 1
            player = Player(100,4,10,20,40,100,0,1,'Archer',512,384,(0,255,0))
    if mode == 1: #When the game is actually being played
        if kb[K_LSHIFT] == 1:
            player.run = True
        else:
            player.run = False
        changepos(player.size,kb,player.run,player.speed) #Change pos of player depending on keys being pressed
        screen.blit(background,(0,0))
        draw.rect(screen,player.col,player.size)
        
    fps=clock.get_fps()
    print(fps)
    #if fps<60 and fps!=0:
        #gamespeed(fps)
    clock.tick(60)
    display.flip()
quit()
