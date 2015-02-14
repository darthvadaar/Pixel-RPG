from pygame import *

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
    def __init__(self,health,speed,attack,defense,mana):
        self.run = False
        self.size = Rect(0,0,10,20)
        self.health = health
        self.speed = speed
        self.attack = attack
        self.defense = defense
        self.mana = mana

class Player(People):
    def __init__(self,health,speed,attack,defense,mana,stamina,money,level,kind):
        People.__init__(self,health,speed,attack,defense,mana)
        self.stamina = stamina
        self.money = money
        self.level = level
        self.kind = kind
        
size=(1024,768)
screen = display.set_mode(size)  
running =True
mode = 0
wizard = Rect(50,100,450,450)
knight = Rect(525,100,450,450)

clock = time.Clock()

while running:
    screen.fill((0,0,0))
    mb = mouse.get_pressed()
    mx,my = mouse.get_pos()
    kb = key.get_pressed()
        
    for e in event.get():
        if e.type == QUIT:      
            running = False
    if mode == 0:
        draw.rect(screen,(0,0,255),wizard)
        draw.rect(screen,(0,0,255),knight)
        if wizard.collidepoint(mx,my) and mb[0] == 1:
            mode = 1
            player = Player(90,2,20,5,150,60,0,1,'Wizard')
        if knight.collidepoint(mx,my) and mb[0] == 1:
            mode = 2
            player = Player(110,9,20,10,40,80,0,1,'Knight')
    if mode != 0:
        if kb[K_LSHIFT] == 1:
            player.run = True
        else:
            player.run = False
        changepos(player.size,kb,player.run,player.speed) #Change pos of player depending on keys being pressed
        draw.rect(screen,(255,255,255),player.size)
        
                
    clock.tick(120)
    display.flip()
quit()