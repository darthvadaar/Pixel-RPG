from pygame import *
from math import *
from random import *
from pickle import *
from threading import Timer
from os import listdir
from os.path import isfile, join
import glob
from threading import Timer
init()


################# TO DO ########################
#Basic AI
#Boss Integration
#Fix enemy movement 
#Create enemy to 
####################################################

################# CHANGES ########################
#Desert: 1673, 2681
#Forest: 213, 1341
#Ice: 1913, 2609
#ADD MENU Q-E Top
####################################################
#=================================================== Classes ===================================================#

class Player(sprite.Sprite):
    def __init__(self, health, stamina, mana, inventory, currentWeapon, currentArmour, currentBoots, money, kind, damage, defense, hotbar):
        super().__init__()
        
        self.pmovex = False #Flag to move either the screen or player in the horizontal direction
        self.pmovey = False #Flag to move either the screen or player in the vertical direction
        self.moving = False #Flag if the player is moving (used to for animations and sprint)

        self.kind = kind
        
        self.skillSprites = []   #2D list of the skill sprite
        self.levelingup=False
        self.levelspritenum=0
        self.levelupanimation=[image.load(x)for x in glob.glob("Art/levelup/*.png")]
        #"Block","Rambo","Bomb","Magnet","Siphon","Freeze","Helper"
        if self.kind == 'Knight':
            self.animations = [[image.load('Art\Player\Knight\Player%d%d.png' %(x,y)).convert_alpha() for y in range(5)] for x in range(4)]
            self.skillicons=glob.glob("Art\Skillicons\Knight\*.png")
            self.skillSprites.append(glob.glob("Art/Skills/skillBomb/*.png")) #0
            self.skillSprites.append(glob.glob("Art/Skills/skillMagnet/*.png"))#1
            self.skillSprites.append(glob.glob("Art/Skills/skillHelper/*.png"))#2
            self.skillSprites.append(glob.glob("Art/Skills/skillSiphon/*.png"))#3
            self.skillSprites.append(glob.glob("Art/Skills/skillFreeze/*.png"))#4
            self.skillSprites.append(glob.glob("Art/Skills/skillRambo/*.png"))#5
            self.skillSprites.append(glob.glob("Art/Skills/skillBlock/*.png"))#6
            
            self.sound={"Hit":mixer.Sound("Art/Sound/Wizard/Hit.wav"),"Map":mixer.Sound("Art/Sound/Wizard/Map.wav"),"Block":mixer.Sound("Art/Sound/Knight/Block.wav")
                        #,"Rambo":mixer.Sound("Art/Sound/Knight/Rambo.wav")
                        ,"Bomb":mixer.Sound("Art/Sound/Knight/Bomb.wav"),"Magnet":mixer.Sound("Art/Sound/Knight/Magnet.wav")
                        #,"Siphon":mixer.Sound("Art/Sound/Knight/Siphon.wav")
                        ,"Freeze":mixer.Sound("Art/Sound/Knight/Freeze.wav"),"Helper":mixer.Sound("Art/Sound/Knight/Helper.wav")}
        elif self.kind == 'Wizard':
            self.animations = [[image.load('Art\Player\Wizard\Player%d%d.png' %(x,y)).convert_alpha() for y in range(3)] for x in range(4)]
            self.animations.append([image.load("Art\Player\Wizard\Playerghost.png")])
            self.skillicons=glob.glob("Art\Skillicons\Wizard\*.png")
            self.skillSprites.append(glob.glob("Art/Skills/skillFire/*.png")) #0
            self.skillSprites.append(glob.glob("Art/Skills/skillRing/*.png")) #1
            self.skillSprites.append(glob.glob("Art/Skills/skillTurtle/*.png")) #2
            self.skillSprites.append(glob.glob("Art/Skills/Totems/*.png")) #3
            self.skillSprites.append(glob.glob("Art/Skills/skillBoost/*.png")) #4
            self.skillSprites.append(glob.glob("Art/Skills/skillHeal/*.png")) #5
            self.sound={"Attack":mixer.Sound("Art/Sound/Wizard/Attack.wav"),"Heal":mixer.Sound("Art/Sound/Wizard/Heal.wav"),"Fire":mixer.Sound("Art/Sound/Wizard/Fire.wav")
                               ,"Ring":mixer.Sound("Art/Sound/Wizard/Ring.wav"),"Boost":mixer.Sound("Art/Sound/Wizard/Boost.wav"),
                          "Charge":mixer.Sound("Art/Sound/Wizard/Charge.wav"),"Turtle":mixer.Sound("Art/Sound/Wizard/Turtle.wav"),"Shadow":mixer.Sound("Art/Sound/Wizard/Shadow.wav")
                        ,"Hit":mixer.Sound("Art/Sound/Wizard/Hit.wav"),"Map":mixer.Sound("Art/Sound/Wizard/Map.wav")}#dictionary full of sound effects
        elif self.kind == 'Archer':
            self.animations = [[image.load('Art\Player\Archer\Player%d%d.png' % (x,y)).convert_alpha() for y in range(3)] for x in range(4)]
            self.skillicons = glob.glob("Art\Skillicons\Archer\*.png")
            self.skillSprites.append(glob.glob("Art/Skills/skillSniper/*.png")) #0
            self.skillSprites.append(glob.glob("Art/Skills/skillForestGump/*.png")) #1
            self.skillSprites.append(glob.glob("Art/Skills/skillFear/*.png")) #2
            self.sound={"Attack":mixer.Sound("Art/Sound/Archer/Attack.wav"),"Hit":mixer.Sound("Art/Sound/Wizard/Hit.wav"),"Map":mixer.Sound("Art/Sound/Wizard/Map.wav")
                        ,"Sniper":mixer.Sound("Art/Sound/Archer/Snipershot.wav"),"Rapidfire":mixer.Sound("Art/Sound/Archer/Rapidfire.wav"),
                        "ForestGump":mixer.Sound("Art/Sound/Archer/Boost.wav"),"Fear":mixer.Sound("Art/Sound/Archer/Fear.wav")}

        for i in range(0,len(self.skillSprites)):   #Turn all the globbed images into surfaces
            for x in range(0,len(self.skillSprites[i])):
                self.skillSprites[i][x] = image.load(self.skillSprites[i][x])
        for i in range(0,len(self.skillicons)):
            self.skillicons[i] = image.load(self.skillicons[i])

        self.movepos = 0 #Is the player facing forward, left, right or down
        self.pos = 0 #The current pic of the animation (animation depends on movepos value)
        self.image = self.animations[self.movepos][self.pos]
        
        self.x = 500#screen.get_width()/2+self.image.get_width()/2
        self.y = 340#308+self.image.get_height()/2
        self.image.set_colorkey((255,255,255))
        self.rect = Rect(screen.get_width()/2/2,308,self.image.get_width(),self.image.get_height())

        if self.kind == 'Knight':
            self.sword = image.load('Art\Weapons\Sword.png').convert()
            self.sword.set_colorkey((255,255,255))
            self.swordRect = self.sword.get_rect()
            
        elif self.kind == 'Wizard' or self.kind == "Archer":
            self.bullets = sprite.Group()
        
        self.level = 1
        self.xp = 0
        self.vx = 5
        self.vy = 5
        
        self.maxhealth = health
        self.health = health
        self.healthRegen = 0.01
        self.hurt = False
        
        self.maxstamina = stamina
        self.stamina = stamina
        self.staminaRegen = 0.005
        
        self.maxmana = mana
        self.mana = mana
        self.manaRegen = 0.005

        self.damage = damage
        self.defense = defense
        self.speeds = [(0,5),(-5,0),(5,0),(0,-5)]
        self.confused = False

        self.inventory = inventory
        self.currentWeapon = currentWeapon
        self.currentArmour = currentArmour
        self.currentBoots = currentBoots
        self.money = money

        self.projectileHit = False
        self.mapFog = mapList[mapNum][2]
        self.mapFog.set_colorkey((255,0,0))

        #Used with SkillUse and skillChange
        self.attack = False 
        self.spriteCount = 0
        self.hotbar = hotbar #the hotbar skills that will exist by default when the player is created
        self.currentSkill = 0 #counter for which skill is selected in the hotbar list
        self.AIignore = False   #used for the shadow skill...will not update enemy AI if True
        self.coolDown = [False,False,False] #used to count cooldown time
        self.siphoning = False #checks if the siphoning skill is True or False

        self.speech = 0

    def sprint(self,key): #Changes players speed depending on if the shift button is pressed and their current stamina
        if key[K_LSHIFT] == 1 and self.moving and self.stamina>0:
            self.stamina -= 1
            self.vx *= 2
            self.vy *= 2
        elif self.stamina<self.maxstamina:
            self.stamina += 0.25
            
    def findMoveType(self,back,back_x,back_y):
            if 495 <= self.x+self.vx <= 505:
                self.pmovex = False
            
            if back_x < -back.get_width()+screen.get_width() or back_x > 0:
                if back_x > 0:
                    back_x = 0
                else:
                    back_x = -back.get_width()+screen.get_width()
                self.pmovex = True

            if 330 <= self.y+self.vy <= 345:
                self.pmovey = False
                
            if back_y < -back.get_height()+screen.get_height() or back_y > 0:
                if back_y > 0:
                    back_y = 0
                else:
                    back_y = -back.get_height()+screen.get_height()
                self.pmovey = True
            
            return back_x,back_y
        
    def movement(self,directions,back,back_mask,back_x,back_y,key):
        self.vx,self.vy = 0,0
        self.moving = False
        for direction in range(len(directions)):
            if 1 in directions[direction]:
                self.movepos = direction
                if True not in wallCol(back_mask,self.collidePoints[direction],back_x,back_y):
                    self.moving = True
                    self.vx += self.speeds[direction][0]
                    self.vy += self.speeds[direction][1]
                    
        self.sprint(key)
        if self.vx != 0 and self.vy != 0:
            self.vx = self.vx*cos(radians(45))
            self.vy = self.vy*sin(radians(45))
        elif self.vx == 0 and self.vy == 0:
            self.moving = False

        if self.pmovex:
            self.x += self.vx
        else:
            back_x -= self.vx
            
        if self.pmovey:
            self.y += self.vy
        else:
            back_y -= self.vy
        return self.findMoveType(back,back_x,back_y)

    def drawSkillBar(self,surf): #Draws the skill selection bar at the bottom of the screen
        screen.blit(surf,(0,615))
        screen.blit(player.skillicons[0],(22, 620))#bliting the 3 skills selected
        screen.blit(player.skillicons[1],(110, 620))
        screen.blit(player.skillicons[2],(200, 620))
        if self.currentSkill == 0:    #highlights selected skill
            draw.rect(screen,(0,0,0),(22, 620, 72, 72),5)
        elif self.currentSkill == 1:
            draw.rect(screen,(0,0,0),(110, 620, 72, 72),5)
        elif self.currentSkill == 2:
            draw.rect(screen,(0,0,0),(200, 620, 72, 72),5)

    def HUD(self,surf): #Draw the HUD for the player
        surf.fill((0,0,0))
        draw.rect(surf,(255,0,0),(10,10,int(self.health*2),20))
        draw.rect(surf,(0,255,0),(10,40,int(self.stamina)*2,20))
        draw.rect(surf,(0,0,255),(10,70,int(self.mana*2),20))
        draw.rect(surf,(255,255,0),(10,130,self.xp*2,5))
        screen.blit(surf,(10,10))

    def npcInteract(self,currentQuest):#IAN

        if currentQuest[0].collidepoint(-back_x+530,-back_y+345): #
            screen.blit(questSpeech[self.speech],(800,20))
            screen.blit(image.load("Art/Quests/questTip.png"),(800,500))

            if kb[K_p]:
                currentQuest.pop(0)
                currentQuest.append(quests[self.speech])
                self.speech+=1

        if armorShop.collidepoint(-back_x+530,-back_y+345):#IA
            screen.blit(image.load("Art/Quests/armorShopText.png"),(800,20))
            screen.blit(image.load("Art/Quests/questTip.png"),(800,500))

        if bootShop.collidepoint(-back_x+530,-back_y+345):
            screen.blit(image.load("Art/Quests/bootShopText.png"),(800,20))
            screen.blit(image.load("Art/Quests/questTip.png"),(800,500))

        if weaponShop.collidepoint(-back_x+530,-back_y+345):
            screen.blit(image.load("Art/Quests/weaponShopText.png"),(800,20))
            screen.blit(image.load("Art/Quests/questTip.png"),(800,500))

        if doorKeeper.collidepoint(-back_x+530,-back_y+345):
            screen.blit(image.load("Art/Quests/doorKeeper.png"),(800,20))

        if Rect(-back_x+530,-back_y+345,50,50).collidelist(helpMeRects)!= -1:
            screen.blit(helpSay,(800,20))
            
    def changePic(self):
        if self.moving and int(self.pos) != len(self.animations[self.movepos])-1:
            self.pos += 0.4
        else:
            self.pos = 0
        if self.hotbar[self.currentSkill] == "Shadow" and self.attack:#drawing the ghost sprite
            self.image = self.animations[4][0]
        else:
            self.image = self.animations[self.movepos][int(self.pos)]
        
    def leveling(self): #Increases level of player after he has gotten 100 xp and increases stats randomly
        if self.xp<90:
            self.xp += 10
        else:
            self.levelingup=True
            self.levelspritenum=0
            self.xp = 10
            self.level += 1
            if self.maxhealth<=90:
                self.maxhealth += randint(3,6)
                self.health = self.maxhealth
            if self.maxstamina<= 90:
                self.maxstamina += randint(3,6)
                self.stamina = self.maxstamina
            if self.maxmana<= 90:
                self.maxmana += randint(3,6)
                self.mana = self.maxmana

    def attacking(self,mx,my,enemies): #Draws a sword and when the sword hits an enemy decrease its health
        '''
        Please correct and make it more efficent/organized
        Draws a sword to be lined with the mouse. There are two points (the tip of sword and middle of sword) that are used to damage enemies
        If an enemy collides with either point it takes damage.
        '''   
        x = mx-self.x #Distance from center to mouse horizontally
        y = my-self.y #Distance from center to mouse vertically
        
        h = hypot(x,y) #Actual distance from mouse to center (pythag theorem)
        ax = 40/h*x #Find the horizonatal distance for a smilar triangle with hypot 40
        ay = 40/h*y #Find the vertical distance for a smilar triangle with hypot 40
        
        angle = atan2(ay,ax) #Angle used to rotate sword
        
        if self.kind == 'Knight':
            display = transform.rotate(self.sword,degrees(-angle)) #Rotate a copy sword with the angle we calculated
            screen.blit(display,(self.x-display.get_width()//2,self.y-display.get_height()//2)) #Blit the image with the offset
            if mode == 1:
                for enemy in enemies:
                    if enemy.rect.collidepoint(int(self.x+ax),int(self.y+ay)) or enemy.rect.collidepoint(int(self.x+ax*2/3),int(self.y+ay*2/3)) or enemy.rect.collidepoint(int(self.x+ax/3),int(self.y+ay/3)):
                        enemy.hurt = True
            elif mode == 6:
                if boss.rect.collidepoint(int(self.x+ax),int(self.y+ay)) or boss.rect.collidepoint(int(self.x+ax*2/3),int(self.y+ay*2/3)) or boss.rect.collidepoint(int(self.x+ax/3),int(self.y+ay/3)):
                    boss.hurt = True
        elif self.kind == 'Wizard':
            self.bullets.add(Projectile(self.x,self.y,10*cos(angle),10*sin(angle),angle,None,'Spell'))
            if mixer.get_busy()==0:
                self.sound["Attack"].play()
        elif self.kind == "Archer":
            self.bullets.add(Projectile(self.x,self.y,10*cos(angle),10*sin(angle),angle,None,'Arrow'))
            if mixer.get_busy()==0:
                self.sound["Attack"].play()
    def takeDamage(self,enemies): #Checks if the player is touching an enemy and lowers the players health if it is
        if self.health <= 0:
            self.health = 0
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if self.health > 0 and self.siphoning == False:
                    hiteffect=randint(0,50)
                    if hiteffect==0:
                        player.sound["Hit"].play()
                    self.health -= (1-player.defense-player.currentArmour.defense-player.currentBoots.defense)*enemy.damage
                    return True
                elif self.health < self.maxhealth and self.siphoning:
                    self.health += (1-player.defense-player.currentArmour.defense-player.currentBoots.defense)*enemy.damage
                    return True
        if self.projectileHit and self.siphoning == False:
            self.health -= 1
            self.projectileHit = False
            return True
        elif self.health < self.maxhealth and self.siphoning:
            self.health += (1-player.defense-player.currentArmour.defense-player.currentBoots.defense)*randint(7,10)
            self.projectileHit = False
            return True
        self.projectileHit = False
        return False
                    
    def heal(self):
        if self.hurt == False and self.health<self.maxhealth:
            self.health += self.healthRegen

    def skillChange(self,key): #changes which skill is currently selected
       if self.attack != True:  #can only change skills while attack is False
            if key[K_1] == 1:
                self.currentSkill = 0
            elif key[K_2] == 1:
                self.currentSkill = 1
            elif key[K_3] == 1:
                self.currentSkill = 2
                
    def statReset(self, health, mana, stamina, damage, defense, speed, confused, siphoning):
        'Resets the stats to normal after using a stat changing skill'
        if health != None:
            self.health = health
        if mana != None:
            self.mana = mana
        if stamina != None:
            self.stamina = stamina
        if damage != None:
            self.damage = damage
        if defense != None:
            self.defense = defense
        if speed != None:
            self.speeds = speed
        if confused != None:
            self.confused = confused
        if siphoning != None:
            self.siphoning = siphoning
    
    def skillUse(self, skillFlag, attack, spriteCount, enemyList):   #skillFlag is taken in as a parameter using MOUSEBUTTONDOWN and attack keeps track if a skill is being used (no animation cut off or skill change while attack == True)
        if player.kind == "Wizard":
            if self.hotbar[self.currentSkill] == "Heal":    #adds 20% of maxhealth to health
                if skillFlag and self.health < self.maxhealth and self.mana > 2:
                    self.sound["Heal"].play()
                    self.health += self.maxhealth * 0.20
                    self.mana -= 5
                    attack = True
                if attack:
                    if spriteCount < 9:
                        sprite = screen.blit(self.skillSprites[5][int(spriteCount)], (self.x - self.skillSprites[5][int(spriteCount)].get_width()/2 ,self.y - self.skillSprites[5][int(spriteCount)].get_height()/2))
                        spriteCount +=0.5
                    else:
                        spriteCount = 0
                        attack = False                    
            if self.health > self.maxhealth:    #prevents overhealing
                self.health = self.maxhealth
                
            elif self.hotbar[self.currentSkill] == "Fire":  #breathe fire and kill enemies
                if skillFlag and self.mana > 5 and attack == False:
                    self.sound["Fire"].play()
                    player.mana -= 5
                    attack = True
                    self.ang = degrees(atan2(mx - self.x, my - self.y )) + 180   #doesn't follow mouse if 180 is not added
                if attack:
                    if spriteCount == len(self.skillSprites[0]):
                        spriteCount = 0
                        attack = False
                    else:
                        fire_img = transform.rotate(self.skillSprites[0][int(spriteCount)], self.ang)
                        fire_img_rectNew = fire_img.get_rect()
                        posx,posy = player.rect.center
                        posx += 50 * cos(radians(self.ang + 90))     #calculates where sprite should blit to be in between the clicked location and the character
                        posy -= 50 * sin(radians(self.ang + 90))    #the first number changes how far in front of the character the sprite will blit
                        fire_img_rectNew.center = (posx,posy)
                        sprite = screen.blit(fire_img,fire_img_rectNew)
                        spriteCount += 0.5
                        if mode == 1:
                            for i in enemyList:
                                if sprite.colliderect(i.rect):
                                    i.health -= self.damage + 10 #subtracts the enemy health by your damage
                        elif mode == 6:
                            if sprite.colliderect(boss.rect):
                                boss.health -= self.damage + 10 #subtracts the enemy health by your damage

            elif self.hotbar[self.currentSkill] == "Ring":  
                if skillFlag and self.mana > 10 and attack == False:
                    self.sound["Ring"].play()
                    player.mana -= 15
                    attack = True
                if attack:
                    if spriteCount < len(self.skillSprites[1]):
                        sprite = screen.blit(self.skillSprites[1][spriteCount],(self.x - self.skillSprites[1][spriteCount].get_width()/2 , self.y - self.skillSprites[1][spriteCount].get_height()/2))
                        spriteCount += 1
                        if mode == 1:
                            for i in enemyList:
                                if sprite.colliderect(i.rect):
                                    i.health -= self.damage + 10
                        elif mode == 6:
                            if sprite.colliderect(boss.rect):
                                boss.health -= self.damage + 10
                    else:
                        spriteCount = 0
                        attack = False
                                             
            elif self.hotbar[self.currentSkill] == "Boost" :
                if skillFlag and self.mana > 5 and attack == False:
                    self.sound["Boost"].play() 
                    self.mana -= 5
                    timerBoost = Timer(10.0 , self.statReset, [None, None, None, self.damage, self.defense,None, None, None])    #takes old stats and creates a timer
                    self.damage *= 2
                    self.defense /= 2
                    timerBoost.start()    #starts the timer and runs self.statReset once timer is finished.
                    attack = True
                if attack:
                    if spriteCount < 16:
                        sprite = screen.blit(self.skillSprites[4][int(spriteCount)], (self.x - self.skillSprites[4][int(spriteCount)].get_width()/2, self.y - self.skillSprites[4][int(spriteCount)].get_height()/2))
                        spriteCount += 1
                    else:
                        spriteCount = 0
                        attack  = False
                                                                             
            elif self.hotbar[self.currentSkill] == "Turtle":
                if skillFlag and self.mana > 10 and attack == False:
                    self.sound["Turtle"].play()
                    self.mana -= 10
                    attack = True
                if attack:
                    if spriteCount < len(self.skillSprites[2]):
                        sprite = screen.blit(self.skillSprites[2][int(spriteCount)],(self.x - self.skillSprites[2][int(spriteCount)].get_width()/2,  self.y - self.skillSprites[2][int(spriteCount)].get_height()/2))
                        spriteCount += 0.7  #only go up by 0.7 frames every time to reduce super fast animations
                        if mode == 1:
                            for i in enemyList:
                                if sprite.colliderect(i.rect):
                                    i.speed *= 0.9
                        elif mode == 6:
                            if sprite.colliderect(boss.rect):
                                boss.speed *= 0.9
                    else: 
                        spriteCount = 0
                        attack = False
                        
            elif self.hotbar[self.currentSkill] == "Charge":
                if skillFlag and self.mana > 5 and attack == False:
                    self.sound["Charge"].play()
                    attack = True
                if attack:
                    self.mana -= 5
                    spriteCount += 0.5  #using spriteCount for the radius for this skill
                    draw.circle(screen, (0,0,0), (int(self.x), int(self.y)), int(spriteCount))  #Inted self.x and y b/c it doesn't take floats
                    if spriteCount > 30:
                        spriteCount = 30
                        self.health -= 0.5
                    if mb[0] == 1:
                        #add to projectile list as a bullet and shoot it!
                        self.ang = atan2(mx - self.x, my - self.y) + 3*pi/2
                        self.bullets.add(Projectile(self.x, self.y, 10*cos(-self.ang), 10*sin(-self.ang), self.ang, int(spriteCount), 'BigBullet'))
                        attack = False            
                else:
                    spriteCount = 0
                        
            elif self.hotbar[self.currentSkill] == "Shadow":
                if skillFlag and self.mana > 10 and attack == False:
                    self.sound["Shadow"].play()
                    self.mana -= 10
                    attack = True
                if attack:
                    self.AIignore = True
                    spriteCount += 1
                    if spriteCount > 100:   #using spriteCount for counting time
                        self.AIignore = False
                        spriteCount = 0
                        attack = False

        elif player.kind == "Archer":
            if self.hotbar[self.currentSkill] == "Sniper":
                if skillFlag and self.mana > 30 and attack == False:
                    self.sound["Sniper"].play()
                    self.mana -= 30
                    self.ang = degrees(atan2(mx - self.x, my - self.y)) + 180
                    attack = True
                if attack:
                    if spriteCount > 8:
                        spriteCount = 0
                        attack = False
                    else:                        
                        spriteCount += 1
                        spriteImg = transform.rotate(self.skillSprites[0][int(spriteCount)], self.ang)
                        spriteImgNew = spriteImg.get_rect()
                        playerX,playerY = player.rect.center
                        playerX += 250 * cos(radians(self.ang + 90))     #calculates where sprite should blit to be in between the clicked location and the character
                        playerY -= 250 * sin(radians(self.ang + 90))     #the first number changes how far in front of the character the sprite will blit
                        spriteImgNew.center = (playerX,playerY)
                        sprite = screen.blit(spriteImg, spriteImgNew)
                        if mode == 1:
                            for i in enemyList:
                                if sprite.colliderect(i.rect):
                                    i.health -= self.damage + 15
                        elif mode == 6:
                            if sprite.colliderect(boss.rect):
                                    boss.health -= self.damage + 15
            elif self.hotbar[self.currentSkill] == "Barrage":
                if skillFlag and self.mana >= 10 and attack == False:
                    self.sound["Rapidfire"].play()
                    self.mana -= 10
                    attack = True
                    self.ang = atan2(mx - self.x, my - self.y) + (3*pi/2)   #have to offset with weird values for some reason
                if attack:
                    self.bullets.add(Projectile(self.x, self.y, 10*cos(-self.ang), 10*sin(-self.ang), -self.ang, None, 'Arrow'))
                    spriteCount += 1
                    if spriteCount > 25:
                        spriteCount = 0
                        attack = False

            elif self.hotbar[self.currentSkill] == "RadiusBarrage":
                if skillFlag and self.mana >= 10 and attack == False:
                    self.sound["Rapidfire"].play()
                    self.mana -= 10
                    attack = True
                    self.ang = 0
                if attack:
                    self.ang += 6
                    self.bullets.add(Projectile(self.x, self.y, 10*cos(-self.ang), 10*sin(-self.ang), -self.ang, None, 'Arrow'))
                    if self.ang > 360 :
                        self.ang = 0
                        attack = False

            elif self.hotbar[self.currentSkill] == "PoisonArrow":
                if skillFlag and self.mana >= 5 and attack == False:
                    self.sound["Attack"].play()
                    self.mana -= 5
                    self.ang = atan2(mx - self.x, my - self.y) + (3*pi/2)   #have to offset with weird values for some reason
                    self.bullets.add(Projectile(self.x, self.y, 10*cos(-self.ang), 10*sin(-self.ang), -self.ang, None, 'PoisonArrow'))

            elif self.hotbar[self.currentSkill] == "FollowMe":
                if skillFlag and self.mana >= 15 and attack == False:
                    self.sound["Rapidfire"].play()
                    self.mana -= 15
                    self.ang = atan2(mx - self.x, my - self.y) + (3*pi/2)   #have to offset with weird values for some reason
                    attack = True
                if attack:
                    self.bullets.add(Projectile(self.x, self.y, 10*cos(-self.ang), 10*sin(-self.ang), -self.ang, None, 'HomingArrow'))
                    spriteCount += 1
                    if spriteCount > 20:
                        spriteCount = 0
                        attack = False

            elif self.hotbar[self.currentSkill] == "Fear":
                 if skillFlag and self.mana > 10 and attack == False:
                    self.sound["Fear"].play()
                    self.mana -= 10
                    attack = True
                 if attack:
                    if spriteCount < len(self.skillSprites[2]):
                        sprite = screen.blit(self.skillSprites[2][int(spriteCount)],(self.x - self.skillSprites[2][int(spriteCount)].get_width()/2,  self.y - self.skillSprites[2][int(spriteCount)].get_height()/2))
                        spriteCount += 0.7
                        for i in enemyList:
                            if sprite.colliderect(i.rect):
                                if i.speed > 0:
                                    i.speed *= -1  #makes enemies run away in fear
                    else: 
                        spriteCount = 0
                        attack = False
                                             
            elif self.hotbar[self.currentSkill] == "ForestGump":
                if skillFlag and self.mana >= 15 and attack == False:
                    self.sound["ForestGump"].play()
                    self.mana -= 15
                    timerForestGump = Timer(10.0 , self.statReset, [None, None, self.stamina, self.damage, None, None,  None, None])
                    self.damage /= 2
                    self.stamina += 9999    #Tested, it is impossible to use all that stamina 
                    timerForestGump.start()   
                    attack = True
                if attack:
                    if spriteCount < 16:
                        sprite = screen.blit(self.skillSprites[1][int(spriteCount)], (self.x - self.skillSprites[1][int(spriteCount)].get_width()/2, self.y - self.skillSprites[1][int(spriteCount)].get_height()/2))
                        spriteCount += 1
                    else:
                        spriteCount = 0
                        attack  = False

        elif self.kind == "Knight":
            if self.hotbar[self.currentSkill] == "Block":
                if skillFlag and self.mana >= 5:
                    self.sound["Block"].play()
                    self.mana -= 5
                    timerBlock = Timer(5.0, self.statReset, [None, None, None, None, self.defense, None, None, None])
                    self.speed = 0  #player will not move once merged with rishis code
                    timerBlock.start()
                    self.defense = 9999
                    attack = True
                if attack:
                    if spriteCount < len(self.skillSprites[6]):
                        sprite = screen.blit(self.skillSprites[6][spriteCount],(self.x - self.skillSprites[6][spriteCount].get_width()/2 , self.y + self.rect.h- self.skillSprites[6][spriteCount].get_height()/2-20))
                        spriteCount += 1
                    else:
                        spriteCount = 0
                        attack = False
            elif self.hotbar[self.currentSkill] == "Rambo":
                if skillFlag and self.mana >= 10:
                    self.mana -= 10
                    timerRambo = Timer(3.0, self.statReset, [None, None, None, self.damage, self.defense, None, None, None]) #health, mana, stamina, damage, defense, speed, confused
                    self.defense = 999999
                    self.damage /= 10
                    timerRambo.start()
                    attack = True
                if attack:
                    if spriteCount < len(self.skillSprites[5]):
                        sprite = screen.blit(self.skillSprites[5][spriteCount],(self.x - self.skillSprites[5][spriteCount].get_width()/2 , self.y - self.skillSprites[5][spriteCount].get_height()/2))
                        spriteCount += 1
                    else:
                        spriteCount = 0
                        attack = False
            elif self.hotbar[self.currentSkill] == "Bomb":
                if skillFlag and self.mana >= 15:
                    self.sound["Bomb"].play()
                    self.mana -= 15
                    attack = True
                if attack:
                    if spriteCount < len(self.skillSprites[0]):
                        sprite = screen.blit(self.skillSprites[0][spriteCount],(self.x - self.skillSprites[0][spriteCount].get_width()/2 , self.y - self.skillSprites[0][spriteCount].get_height()/2))
                        spriteCount += 1
                        if mode == 1:
                            for i in enemyList:
                                if sprite.colliderect(i.rect):
                                    i.health -= self.damage + 10
                        elif mode == 6:
                            if sprite.colliderect(boss.rect):
                                    boss.health -= self.damage + 10
                    else:
                        spriteCount = 0
                        attack = False
            elif self.hotbar[self.currentSkill] == "Freeze":
                if skillFlag and self.mana >= 10:
                    self.sound["Freeze"].play()
                    self.mana -= 10
                    attack=True
                    timerFreeze = Timer(10.0, self.statReset, [None, None, None, self.damage, None, self.speeds, None, None]) #health, mana, stamina, damage, defense, speed, confused
                    self.speeds = [(0,1),(-1,0),(1,0),(0,-1)]
                    self.damage *= 2
                    timerFreeze.start()
                if attack:
                    if spriteCount < len(self.skillSprites[4]):
                        sprite = screen.blit(self.skillSprites[4][spriteCount],(self.x - self.skillSprites[4][spriteCount].get_width()/2 , self.y - self.skillSprites[4][spriteCount].get_height()/2))
                        spriteCount += 1
                    else:
                        spriteCount = 0
                        attack = False

            elif self.hotbar[self.currentSkill] == "Siphon":
                if skillFlag and self.mana >= 10:
                    self.mana -= 10
                    attack==True
                    timerSiphon = Timer(10.0, self.statReset, [None, None, None, None, None, None, None, False]) #health, mana, stamina, damage, defense, speed, confused
                    self.siphoning = True
                    timerSiphon.start()
                if attack:
                    if spriteCount < len(self.skillSprites[3]):
                        sprite = screen.blit(self.skillSprites[3][spriteCount],(self.x - self.skillSprites[3][spriteCount].get_width()/2 , self.y - self.skillSprites[3][spriteCount].get_height()/2))
                        spriteCount += 1
                    else:
                        spriteCount = 0
                        attack = False

            elif self.hotbar[self.currentSkill] == "Magnet":
                if skillFlag and self.mana >= 10:
                    self.sound["Magnet"].play()
                    self.mana -= 10
                    attack = True 
                if attack:
                    if spriteCount < len(self.skillSprites[1]):
                        sprite = screen.blit(self.skillSprites[1][spriteCount],(self.x - self.skillSprites[1][spriteCount].get_width()/2 , self.y + self.rect.h- self.skillSprites[1][spriteCount].get_height()/2-20))
                        spriteCount += 1
                    else:
                        spriteCount = 0
                        attack = False
                    dist = hypot(mx - self.x, my - self.y)
                    for i in enemies:
                        if hypot(self.x - i.x, self.y - i.y ) < 1000:
                            i.x += int(10*cos(i.angle))
                            i.y += int(10*sin(i.angle))

            elif self.hotbar[self.currentSkill] == "Helper":
                if skillFlag and self.mana > 10:
                    self.sound["Helper"].play()
                    self.mana -= 10
                    attack = True
                    
                if attack:
                    if spriteCount < len(self.skillSprites[2]):
                        sprite = screen.blit(self.skillSprites[2][spriteCount],(self.x - self.skillSprites[2][spriteCount].get_width()/2 , self.y + self.rect.h- self.skillSprites[2][spriteCount].get_height()/2-20))
                        spriteCount += 1
                    else:
                        spriteCount = 0
                        attack = False
                    lst = [self.health, self.mana, self.stamina]
                    if min(lst) == lst[0]:
                        self.health += 2
                    elif min(lst) == lst[1]:
                        self.mana += 2
                    elif min(lst) == lst[2]:
                        self.stamina += 2
                    if spriteCount >= 10:
                        spriteCount = 0
                        attack = False
                
        
                    
        return attack, spriteCount  #returning so that the last known value of attack and spriteCount can be reused

    def fillMap(self,back_x,back_y,backPic):
        draw.circle(self.mapFog,(255,0,0),(int((self.x-back_x)/backPic.get_width()*900),int((self.y-back_y)/backPic.get_height()*600)),100)
        
    def update(self,flag,mx,my,key,surf,surf2,enemies,cx,cy,directions,backPic,back_mask): #Draws the player and calls most of the functions before it
        self.attack , self.spriteCount = self.skillUse(rclick, self.attack, self.spriteCount, enemies)
        self.fillMap(cx,cy,backPic)
        self.mapFog = mapList[mapNum][2]
        self.mapFog.set_colorkey((255,0,0))
        if self.levelingup and self.levelspritenum<=28:
            screen.blit(self.levelupanimation[int(self.levelspritenum)],(self.x-self.levelupanimation[int(self.levelspritenum)].get_width()/2,self.y-self.levelupanimation[int(self.levelspritenum)].get_height()/2))
            self.levelspritenum+=0.5
        else:
            self.levelingup=False
        if flag:
            self.attacking(mx,my,enemies)
        else:
            self.skillChange(key)
        self.changePic()
        self.rect[0],self.rect[1] = self.x-self.image.get_width()/2,self.y-self.image.get_height()/2
        screen.blit(self.image,self.rect)   #(screen,(255,0,0),self.rect)
        if self.kind == 'Wizard' or self.kind == 'Archer':
            self.bullets.update(cx,cy,None,enemies,key)
        self.HUD(surf)
        self.drawSkillBar(surf2)
        self.hurt = self.takeDamage(enemies)
        self.heal()
        self.fillMap(cx,cy,backPic)
        if mode == 1:
            self.npcInteract(currentQuest)#IAN
        if self.confused:
            self.collidePoints = [
            [(self.rect[0]+self.rect[2]/3,self.rect[1]+3/4*self.rect[3]),(self.rect[0]+2/3*self.rect[2],self.rect[1]+3/4*self.rect[3]),(self.rect[0]+self.rect[2]/2,self.rect[1]+3/4*self.rect[3])],#Down
            [(self.rect[0]+self.rect[2],self.rect[1]+7/8*self.rect[3])], #Right
            [(self.rect[0],self.rect[1]+7/8*self.rect[3])], #Left
            [(self.rect[0]+self.rect[2]/3,self.rect[1]+self.rect[3]),(self.rect[0]+2/3*self.rect[2],self.rect[1]+self.rect[3]),(self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3])]
            ] #Holds the points to check for wall collisions
        else:
            self.collidePoints = [
            [(self.rect[0]+self.rect[2]/3,self.rect[1]+self.rect[3]),(self.rect[0]+2/3*self.rect[2],self.rect[1]+self.rect[3]),(self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3])], #Down
            [(self.rect[0],self.rect[1]+7/8*self.rect[3])], #Left
            [(self.rect[0]+self.rect[2],self.rect[1]+7/8*self.rect[3])], #Right
            [(self.rect[0]+self.rect[2]/3,self.rect[1]+3/4*self.rect[3]),(self.rect[0]+2/3*self.rect[2],self.rect[1]+3/4*self.rect[3]),(self.rect[0]+self.rect[2]/2,self.rect[1]+3/4*self.rect[3])]
            ] #Holds the points to check for wall collisions
        back_x,back_y = self.movement(directions,backPic,back_mask,cx,cy,key)
        return back_x,back_y
        
class Enemy(sprite.Sprite):
    def __init__(self,health,kind,x,y):
        #super().__init__()
        self.kind = kind
        self.spritenum=0
        self.direction="up"
        self.images=[]
        if self.kind == 'Archer':
            self.loadenemyimages()
            self.image = self.images[0][0]
        elif self.kind == 'Charger':
            self.loadenemyimages()
            self.image = self.images[0][0]
        elif self.kind == 'Thief':
            self.loadenemyimages()
            self.image = self.images[0][0]
        elif self.kind == 'Mage':
            self.loadenemyimages()
            self.image = self.images[0][0]
        else:
            self.loadenemyimages()
            if self.images != []:
                self.image = self.images[0][0]
            else:
                self.image = Surface((50,50))
        self.draw = True
        self.image.set_colorkey((255,255,255))
        if x == None:
            self.x = randint(0,back.get_width())
        else:
            self.x = x
        if y == None:
            self.y = randint(0,back.get_height())
        else:
            self.y = y
        self.x = randint(0,2980)
        self.y = randint(0,2380)
        self.rect = Rect(self.image.get_rect())
        self.speed = randint(3,7)
        self.hurt = False
        self.health = health
        self.damage = choice([0.5,1])
        self.vx = 5
        self.vy = 5
        self.moves = [-1,1]
        self.bullets = sprite.Group()
        self.angle = None
        self.poisoned = []
    def loadenemyimages(self):
        self.images.append(glob.glob("Art\\Enemies\\"+self.kind+"\\up\\*.png"))
        self.images.append(glob.glob("Art\\Enemies\\"+self.kind+"\\down\\*.png"))
        self.images.append(glob.glob("Art\\Enemies\\"+self.kind+"\\right\\*.png"))
        self.images.append(glob.glob("Art\\Enemies\\"+self.kind+"\\left\\*.png"))
        for i in range (len(self.images)):
                for x in range (len(self.images[i])):
                    self.images[i][x]=image.load(self.images[i][x])
    def statRest(health,speed,damage):   #resets stats to remove debuffs
        if health != None:
            self.health = health
        elif speed != None:
            self.speed = speed
        elif damage != None:
            self.damage = damage

    def createProjectile(self, kind):
        centx = self.rect[0]+self.rect[2]/2 #x coord of starting pos for arrow
        centy = self.rect[1]+self.rect[3]/2 #y coord of starting pos for arrow
        dx,dy = player.rect[0]+randint(-3,3)-centx,player.rect[1]+randint(-3,3)-centy #distance (horizontally and vertically) from player to starting pos (accuracy is +- 5)
        angle = atan2(dy,dx)
        cx = randint(10,20)*cos(angle)
        cy = randint(10,20)*sin(angle)
        self.bullets.add(Projectile(centx,centy,cx,cy,angle,None,kind))

    def grouping(self,enemies):
        for enemy in enemies:
            if enemy != self and hypot(self.x-enemy.x,self.y-enemy.y)<50:
                dx = self.x-enemy.x
                dy = self.y-enemy.y
                dist = max(1,hypot(dx,dy))
                d2 = dist**2
                self.vx += 10*dx/d2
                self.vy += 10*dy/d2
        
    def AI(self,back_x,back_y,back_mask):
        self.vx,self.vy = 0,0
        dx = player.rect[0]+player.rect[2]/2 - self.rect[0]
        dy = player.rect[1]+player.rect[3]/2- self.rect[1]
        self.angle = atan2(dy,dx)
        dist = hypot(dx,dy)
        
        if -3*3.14/4<=self.angle <-3.14/4:
            self.direction="up"
        if 3*3.14/4<=self.angle or self.angle<-3*3.14/4:
            self.direction="left"
        if 3.14/4<=self.angle<3*3.14/4:
            self.direction="down"
        elif -3.14/4<=self.angle<3.14/4:
            self.direction="right"
            
        if self.kind == 'Monster' and -10<=self.rect[0]<=1034 and -10<=self.rect[1]<=745:
            if dist>50:
                self.vx += int(self.speed*cos(self.angle))
                self.vy += int(self.speed*sin(self.angle))
            else:
                self.vx -= int(self.speed*cos(self.angle))
                self.vy -= int(self.speed*sin(self.angle))
        elif self.kind == 'Archer' and 30<=self.rect[0]<=900:
            if dist<100:
                self.vx -= int(self.speed*cos(self.angle))
                self.vy -= int(self.speed*sin(self.angle))
        elif self.kind == 'Dragon':
            if dist>50:
                self.vx += int(self.speed*cos(self.angle))
                self.vy += int(self.speed*sin(self.angle))
            else:
                self.vx -= int(self.speed*cos(self.angle))
                self.vy -= int(self.speed*sin(self.angle))
        elif self.kind == 'Mage':
            if dist<100:
                if randint(1,50) == 1:
                    self.x = randint(-100,100)+player.x
                    self.y = randint(-100,100)+player.y
            else:
                self.vx += int(self.speed*cos(self.angle))
                self.vy += int(self.speed*sin(self.angle))
        elif self.kind == 'Ghost': 
            if dist<100:
                self.draw = True
                self.vx += int(self.speed*cos(self.angle))
                self.vy += int(self.speed*sin(self.angle))
            else:
                if randint(1,2) == 1:
                    self.draw == True
                else:
                    self.draw = False
        elif self.kind == 'Theif':
            if dist<100:
                if randint(1,100) == 1 and len(enemies)<150:
                    enemies.append(Enemy(100,choice(['Charger','Archer','Theif','Monster','Dragon','Mage']),self.x+choice([-20,20]),self.y+choice([-20,20])))
            else:
                self.vx -= int(self.speed*cos(self.angle))
                self.vy -= int(self.speed*sin(self.angle))
        elif self.kind == 'Healer':
            for enemy in enemies:
                if enemy != self and dist<100:
                    if enemy.health < 100:
                        enemy.health += 1
        else:
            if -10<=self.rect[0]<=1034 and -10<=self.rect[1]<=745:
                if dist<50:
                    self.vx += int(self.speed*cos(self.angle))
                    self.vy += int(self.speed*sin(self.angle))
                else:
                    self.vx -= int(self.speed*cos(self.angle))
                    self.vy -= int(self.speed*sin(self.angle))

                print(self.vx,self.vy)

    def attacking(self):
        if 30<=enemy.rect[0]<=900 and 30<=enemy.rect[1]<=600:
            if self.kind == 'Archer' and randint(1,50) == 1:
                enemy.createProjectile('Enemy') #CHANGE ENEMY TO ENEMY ARCHER
            elif self.kind == 'Mage' and randint(1,50) == 1:
                enemy.createProjectile('HomingEnemy')
        
    def takeDamage(self,enemies):
        if self.hurt:
            self.health -= 50
            self.hurt = False #ADD THINGS LIKE KNOCKBACK AND THE ENEMY FLASHES RED
        if self.health <= 0:
            enemies.remove(self)
            player.leveling()
            
    def movement(self,cx,cy):
        if self.kind == 'Flying':
            self.x += self.vx
            self.y += self.vy
        elif wallCol(back_mask,[(self.x+self.vx+back_x,self.y+self.vy+back_y)],back_x,back_y) == [False]:
            self.x += self.vx
            self.y += self.vy
        
    def update(self,cx,cy,enemies,key,enemyList,back_mask):
        self.spritenum += 0.2
        if self.spritenum >= 3:
            self.spritenum = 0
        for i in self.poisoned:
            i.health -= 1
        self.rect[0],self.rect[1] = self.x+cx,self.y+cy#-self.rect[2]/2+back_x,self.y-self.rect[3]/2+back_y
        self.bullets.update(cx,cy,self.bullets,enemyList,key)
        if player.AIignore == False: #affected  by shadow skill
            self.AI(cx,cy,back_mask)
        self.movement(cx,cy)
        self.attacking()
        self.takeDamage(enemies)
        #screen.blit(self.image,(self.rect[0],self.rect[1]))
        if self.draw == True:
            if self.images != []:
                if self.direction=="up":
                    screen.blit(self.images[0][int(self.spritenum)],self.rect)
                if self.direction=="down":
                    screen.blit(self.images[1][int(self.spritenum)],self.rect)
                if self.direction=="right":
                    screen.blit(self.images[2][int(self.spritenum)],self.rect)
                if self.direction=="left":
                    screen.blit(self.images[3][int(self.spritenum)],self.rect)
            else:
                screen.blit(self.image,(self.rect[0],self.rect[1]))

class Boss(sprite.Sprite):
    def __init__(self,health,x,y,kind):
        super().__init__()
        self.health = health
        self.kind = kind
        self.direction="up"
        self.spritenum=0
        self.images=[]
        self.loadbossimages()
        self.x,self.y = x,y
        self.rect = Rect(x,y,50,50)
        self.hurt = False
        self.trapList = [] #Contains rects of all traps
        self.suckCoord = None #The x,y coord for the pos the player is pushed towards
        self.sucking = False #Used to stop enemy if he is sucking player in
        self.healRect = None #A rect for the spot where the enemy heals at
        self.healing = False #Used to stop the enemy from moving when he is healing
        self.bullets = sprite.Group() #Hold enemys projectiles
        self.angle = None #Angle towards destination
    def loadbossimages(self):
        self.images.append(glob.glob("Art\\Enemies\\"+self.kind+"\\up\\*.png"))
        self.images.append(glob.glob("Art\\Enemies\\"+self.kind+"\\down\\*.png"))
        self.images.append(glob.glob("Art\\Enemies\\"+self.kind+"\\right\\*.png"))
        self.images.append(glob.glob("Art\\Enemies\\"+self.kind+"\\left\\*.png"))
        for i in range (len(self.images)):
                for x in range (len(self.images[i])):
                    self.images[i][x]=image.load(self.images[i][x])
    def createHealTotem(self): #Creates a totem for the enemy to heal in a random corner of the map
        self.healRect = Rect(choice([200,724]),choice([200,400]),50,50)
        self.healing = True
    def heal(self): #Checks if the enemy is near the totem and heals him if he is
        draw.rect(screen,(255,255,0),self.healRect)
        if self.healRect.collidepoint(self.x,self.y):
            self.health += 0.1
    def confusion(self):#,player): #Causes the player controls to be reversed
        timerConfusion = Timer(5, player.statReset, [None, None, None, None, None,[(0,5),(-5,0),(5,0),(0,-5)],False,False])
        for pos in range(len(player.speeds)):
            player.speeds[pos] = (player.speeds[pos][0]*-1,player.speeds[pos][1]*-1)
        timerConfusion.start()
        player.confusion = True #Used to stop the player from geting confused while confused (which makes controls normal - opposite of opposite is normal)
    def reset(self,trapList,suck): #Empties trapList or stops sucking once done with it
        if trapList:
            self.trapList = []
        if suck:
            self.sucking = False
            self.suckCoord = None
    def traps(self,width,height,amount): #Randomly generates traps
        timerTrap = Timer(5,self.reset,[True,False])
        for i in range(amount):
            x = randint(0,screen.get_width()-width)
            y = randint(0,screen.get_height()-height)
            if player.rect.colliderect(Rect(x,y,width,height)) == False: #Stops a trap from being created on player
                self.trapList.append(Rect(x,y,width,height))
        timerTrap.start()
    def suck(self,x,y): #Gets or randomly sets an x,y pos to draw player to
        suckTimer = Timer(5,self.reset,[False,True])
        suckTimer.start()
        self.sucking = True
        if x == None:
            suckx = randint(100,screen.get_width()-100)
        else:
            suckx = x
        if y == None:
            y = randint(100,screen.get_width()-100)
        else:
            sucky = y #Its a sucky variable name
        self.suckCoord = (suckx,sucky)

    def takeDamage(self):
        if self.hurt:
            self.health -= 10
            self.hurt = False
        
    def drawTraps(self):#,player): #Draws traps and checks for collision with player
        for trap in trapList:
            draw.rect(screen,(255,255,255),trap)
            if player.rect.colliderect(trap):
                player.health -= 20
    def createArrow(self): 
        self.bullets.add(Projectile(self.x,self.y,4,4,self.angle,None,'HomingEnemy'))
    def movement(self): #moves boss either to player or healing totem
        if self.healing:
            dx = self.healRect[0]+self.healRect[2]/2-self.x
            dy = self.healRect[1]+self.healRect[3]/2-self.y
            self.angle = atan2(dy,dx)
            self.x += 5*cos(self.angle)
            self.y += 5*sin(self.angle)
        else:
            dx = player.x-self.x
            dy = player.y-self.y
            dist = hypot(dx,dy)
            self.angle = atan2(dy,dx)
            if dist>150:
                self.x += 5*cos(self.angle)
                self.y += 5*sin(self.angle)
            elif dist<100:
                self.x -= 3*cos(self.angle)
                self.y -= 3*sin(self.angle)
        self.rect[0],self.rect[1] = self.x,self.y
        if -3*3.14/4<=self.angle <-3.14/4:
            self.direction="up"
        if 3*3.14/4<=self.angle or self.angle<-3*3.14/4:
            self.direction="left"
        if 3.14/4<=self.angle<3*3.14/4:
            self.direction="down"
        elif -3.14/4<=self.angle<3.14/4:
            self.direction="right"
    def attack(self):
        if randint(1,100) == 1 and len(self.trapList) == 0:
            self.traps(50,50,10)
        if randint(1,100) == 1 and player.confused == False:
            self.confusion()
        if randint(1,100) == 1:
           choice([self.createArrow(),self.suck(self.x,self.y)])
    def update(self,cx,cy,enemyList,key):
        if self.images != []:
            if self.spritenum >= len(self.images[0]):
                self.spritenum = 0
            if self.direction=="up":
                screen.blit(self.images[0][int(self.spritenum)],self.rect)
            if self.direction=="down":
                screen.blit(self.images[1][int(self.spritenum)],self.rect)
            if self.direction=="right":
                screen.blit(self.images[2][int(self.spritenum)],self.rect)
            if self.direction=="left":
                screen.blit(self.images[3][int(self.spritenum)],self.rect)
            self.spritenum+=1
        self.attack()
        self.takeDamage()
        if self.health<20 and self.healing == False:
           self.createHealTotem()
        if self.healing:
            self.heal()
        if self.health>50:
            self.healing = False
            self.healRect = None
        if self.sucking: #Moves player to spot
            draw.circle(screen,(0,0,255),(int(self.suckCoord[0]),int(self.suckCoord[1])),5)
            player.x += 2*cos(atan2(self.suckCoord[1]-player.y,self.suckCoord[0]-player.x))
            player.y += 2*sin(atan2(self.suckCoord[1]-player.y,self.suckCoord[0]-player.x))
        else:
            self.movement()
        
        self.bullets.update(cx,cy,self.bullets,enemyList,key) #Updates boss` projectiles

class Projectile(sprite.Sprite):
    def __init__(self,x,y,vx,vy,angle,bigBulletSize,kind):
        super().__init__()
        self.image = image.load('Art\Weapons\Arrow.png').convert()
        self.image.set_colorkey((255,255,255))
        self.x = x #Inital pos x
        self.y = y #Inital pos y
        self.vx = vx #Horizontal velocity
        self.vy = vy #Vertical velocity
        self.angle = angle
        self.kind = kind
        self.display = transform.rotate(self.image,degrees(-self.angle))
        if self.kind == "PoisonArrow":
            self.image = image.load('Art\Weapons\poisonArrow.png').convert()
        else:
            if player.kind == "Archer":
                self.image = image.load('Art\Weapons\Arrow.png').convert()
            elif player.kind == "Wizard" or player.kind == "Knight":
                self.image = image.load('Art\Weapons\spell.png').convert()  
        self.image.set_colorkey((255,255,255))
        self.display = transform.rotate(self.image,degrees(-self.angle))
        if self.kind == 'BigBullet':
            self.display = transform.scale(self.display,(bigBulletSize*5,bigBulletSize*5))
            self.rect = Rect(self.x,self.y,bigBulletSize*5,bigBulletSize*5)
        else:
            self.rect = Rect(self.x,self.y,self.display.get_width(),self.display.get_height())
    def speed(self,key):
        #IMPROVE ORGAINZATION AND EFFICIENCY
        '''
Offsets the arrow depending on where the player is moving (faster if player is moving into arrow, slower if player is moving away from arrow
        '''
        if player.pmovex == False:
            if key[K_a] or key[K_LEFT]:
                self.x -= player.vx
            if key[K_d] or key[K_RIGHT]:
                self.x -= player.vx
        if player.pmovey == False:
            if key[K_w] or key[K_UP]:
                self.y -= player.vy
            if key[K_s] or key[K_DOWN]:
                self.y -= player.vy
        if self.kind == 'HomingEnemy':
            dx = player.x-self.x
            dy = player.y-self.y
            self.angle = atan2(dy,dx)
            self.vx,self.vy = 4*cos(self.angle),4*sin(self.angle)
            self.display = transform.rotate(self.image,degrees(-self.angle))
        self.x +=  self.vx
        self.y +=  self.vy
        self.rect[0],self.rect[1] = self.x,self.y
        screen.blit(self.display,(self.rect[0],self.rect[1]))
        if self.kind == 'HomingArrow':
            dx = mx-self.x
            dy = my-self.y
            self.angle = atan2(dy,dx)
            self.vx,self.vy = 5*cos(self.angle),5*sin(self.angle)
            self.display = transform.rotate(self.image,degrees(-self.angle))
        self.x +=  self.vx
        self.y +=  self.vy
        self.rect[0],self.rect[1] = self.x,self.y
        screen.blit(self.display,(self.rect[0],self.rect[1]))
        
    def update(self,cx,cy,enemyArrows,enemyList,key):
        #and wallCol(back_mask,[(self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3]/2)],back_x,back_y) == [False]
        if self.kind == 'Spell' or self.kind == 'Arrow':    #Basic attacks
            if mode == 1:
                for enemy in enemyList:
                    if self.rect.colliderect(enemy.rect):
                        player.bullets.remove(self)
                        enemy.health -= player.damage
                if -50<= self.x <= 1074 and -50<= self.y <= 750 and wallCol(back_mask,[(self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3]/2)],back_x,back_y) == [False]:
                    self.speed(key)
                else:
                    player.bullets.remove(self)
            elif mode == 6:
                if self.rect.colliderect(boss.rect):
                    player.bullets.remove(self)
                    boss.health -= player.damage
                if -50<= self.x <= 1074 and -50<= self.y <= 750 and wallCol(back_mask,[(self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3]/2)],back_x,back_y) == [False]:
                    self.speed(key)
                else:
                    player.bullets.remove(self)
#Skills and more complex projectiles
        elif self.kind == 'PoisonArrow':
            if mode == 1:
                for enemy in enemyList:
                    if self.rect.colliderect(enemy.rect):
                        player.bullets.remove(self)
                        enemy.poisoned.append(enemy)
                if -50<= self.x <= 1074 and -50<= self.y <= 750 and wallCol(back_mask,[(self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3]/2)],back_x,back_y) == [False]:
                    self.speed(key)
                else:
                    player.bullets.remove(self)
        elif self.kind == 'BigBullet':
            if mode == 1:
                for enemy in enemyList:
                    if self.rect.colliderect(enemy.rect):
                        player.bullets.remove(self)
                        enemy.health -= player.damage*self.rect[2]
                if -50<= self.x <= 1074 and -50<= self.y <= 750 and wallCol(back_mask,[(self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3]/2)],back_x,back_y) == [False]:
                    self.speed(key)
                else:
                    player.bullets.remove(self)
            elif mode == 6:
                if self.rect.colliderect(boss.rect):
                    player.bullets.remove(self)
                    boss.health -= player.damage*self.rect[2]
                if -50<= self.x <= 1074 and -50<= self.y <= 750 and wallCol(back_mask,[(self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3]/2)],back_x,back_y) == [False]:
                    self.speed(key)
                else:
                    player.bullets.remove(self)
        elif self.kind == 'HomingArrow':
            for enemy in enemyList:
                if self.rect.colliderect(enemy.rect):
                    player.bullets.remove(self)
                    enemy.health -= player.damage*self.rect[2]
            if -50<= self.x <= 1074 and -50<= self.y <= 750 and wallCol(back_mask,[(self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3]/2)],back_x,back_y) == [False]:
                self.speed(key)
            else:
                player.bullets.remove(self)
        else:
            if self.rect.colliderect(player.rect):
                enemyArrows.remove(self)
            elif -50<= self.x <= 1074 and -50<= self.y <= 750 and wallCol(back_mask,[(self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3]/2)],back_x,back_y) == [False]:
                self.speed(key)
                player.projectileHit = True
            else:
                enemyArrows.remove(self)
                
class Weapons(sprite.Sprite):
    def __init__(self,name,description,damage,pic,speed,kind):
        self.name = name
        self.image = image.load(pic)
        self.kind = kind
        
        self.description = description
        self.damage = damage
        self.price = int(gauss(self.damage,3))
        self.damage = damage
        self.speed = speed

class Armour(sprite.Sprite):
    def __init__(self,name,description,defense,pic,kind):
        self.name = name
        self.image = image.load(pic)
        self.description = description
        self.defense = defense
        self.price = int(gauss(self.defense*100,3))
        self.pic = pic
        self.kind = kind

class Boots(sprite.Sprite):
    def __init__(self,name,description,defense,pic,kind):
        self.name = name
        self.image = image.load(pic)
        self.description = description
        self.defense = defense
        self.price = int(gauss(self.defense*100,3))
        self.pic = pic
        self.kind = kind
        
#=================================================== Classes ===================================================#

#================================================== Functions ==================================================#
def newEnemies(mode):
    enemies = []
    if mode != 0:
        for i in range(50):
            enemy = Enemy(100,choice(['Theif','Charger','Archer','Monster','Dragon','Mage',]),None, None)#Snake,Scorpie
            '''if wallCol(back_mask,[(enemy.x,enemy.y)],back_x,back_y) == [False]:'''
            enemies.append(enemy)
    return enemies

def changeMap(mapList,mapNum,back_mask,back_x,back_y,back,player):
    global enemies
    if back_mask.get_at((int(-back_x+player.x),int(-back_y+player.y+20))) == (255,255,0):
        enemies = newEnemies(mode)
        if mapNum == 0:
            mapList[mapNum][2] = player.mapFog
            if int(-back_x+player.x)<back.get_width()/4: #mapNum,back_x,back_y,player.x,player.y
                player.mapFog = mapList[1][2]
                return 1,-2100,-1000,900,400,1 #Left (ICE)
            elif int(-back_x+player.x)>3*back.get_width()/4:
                player.mapFog = mapList[3][2]
                return 3,0,-461,112,400,1 #Right (DESERT)
            elif int(-back_y+player.y)>back.get_height()/4:
                player.mapFog = mapList[2][2]
                return 2,-1000,0,500,400,1 #Bottom (FOREST)
            elif int(-back_y+player.y)<back.get_height()/4 :
                return 0,0,0,200,200,6 #Top
        elif mapNum == 1:#left map
            mapList[mapNum][2] = player.mapFog
            player.mapFog = mapList[0][2]
            return 0,0,-1233+400,100,400,1
        elif mapNum == 2: #bottom map
            mapList[mapNum][2] = player.mapFog
            player.mapFog = mapList[0][2]
            return 0,-1561+500,-3081+400,500,400,1
        elif mapNum == 3: #right
            mapList[mapNum][2] = player.mapFog
            player.mapFog = mapList[0][2]
            return 0,-3057+900,-1205+400,900,400,1
    elif back_mask.get_at((int(-back_x+player.x),int(-back_y+player.y+20))) == (0,255,0):
        return mapNum,0,0,player.x,player.y,6
    else:
        return mapNum,back_x,back_y,player.x,player.y,1
    
def drawShopBack(money,pic):
    shopRects = []
    screen.fill((255,255,255))
    screen.blit(pic,(348,0))
    draw.rect(screen,(255,0,0),(0,600,1024,168))
    draw.rect(screen,(0,0,0),(0,600,1024,168),5)
    draw.rect(screen,(37,37,37),(0,0,400,600))
    draw.rect(screen,(0,0,0),(0,0,400,600),5)
    screen.blit(shopFont.render('$'+str(money),True,(0,0,0)),(960,40))

def drawShopItems(shopItems,mx,my,pic):
    x,y = 400,130
    shopRects = []
    tot = 0
    for item in shopItems:
        x += 100
        if x>800:
            y += 90
            x = 500
        tot += 1
        screen.blit(item.image,(x,y)) #Blits the images for users to see
        screen.blit(shopFont.render(item.name,True,(255,255,255)),(10,10+30*tot))
        screen.blit(shopFont.render("$"+str(item.price),True,(255,255,255)),(320,10+30*tot))
        shopRects.append(Rect(10,10+30*tot,390,30)) #Creates a rect for the user to click if they want to purchase the item (this is not a rect fot the image above)
        if shopRects[shopItems.index(item)].collidepoint(mx,my):
            draw.rect(screen,(0,0,0),shopRects[shopItems.index(item)])
            screen.blit(shopFont.render(item.name,True,(255,255,255)),(10,10+30*tot))
            screen.blit(shopFont.render("$"+str(item.price),True,(255,255,255)),(320,10+30*tot))
            screen.blit(shopFont.render("Information: "+item.description,True,(0,0,0)),(10,650))
            if item.kind in ['Sword','Bow','Staff']:
                screen.blit(shopFont.render("Damage: "+str(int(item.damage)),True,(0,0,0)),(800,650))
            else:
                screen.blit(shopFont.render("Defense: "+str(int(item.defense*100)),True,(0,0,0)),(800,650))
            screen.set_clip(Rect(x,y-10,80,80)) #Check this
            screen.blit(pic,(348,0))
            screen.blit(transform.scale(item.image,(80,80)),(x,y-10))
            screen.set_clip(None)
    return shopRects

def purchase(shopRects,mbFlag,money,shopItems):
    for item in shopRects:
        if mbFlag and item.collidepoint(mx,my):
            if shopItems[shopRects.index(item)].kind in ['Sword','Staff','Bow']:
                pos = 0
            elif shopItems[shopRects.index(item)].kind == 'Armour':
                pos = 1
            else:
                pos = 2
            if len(player.inventory[pos])<len(inventRects[pos]) and shopItems[shopRects.index(item)].price <= money:
                money -= shopItems[shopRects.index(item)].price
                draw.rect(screen,(0,255,0),item)
                player.inventory[pos].append(shopItems[shopRects.index(item)])
                choice(npcsound["Bought"]).play()
                del shopItems[shopRects.index(item)]
            else:
                draw.rect(screen,(255,0,0),item)
                display.flip()
                time.delay(50)
    return money

def drawShop(shopFont,mbFlag,mx,my,money,pic,shopItems):
    drawShopBack(money,pic)
    shopRects = drawShopItems(shopItems,mx,my,pic)
    return purchase(shopRects,mbFlag,money,shopItems)


def savescreen(surf,savePic,saves):
    saveRects = [Rect(78,68,840,180),Rect(78,287,840,180),Rect(78,501,840,180),Rect(464,683,91,35)]
    for player in saves: #The number of saves
        x,y = saveRects[saves.index(player)].topleft
        savePic.blit(itemStatsFont.render("Health:  " + str(player.maxhealth),True,(255,255,255)),(x+240,y+25))
        savePic.blit(itemStatsFont.render("Mana:  " + str(player.maxmana),True,(255,255,255)),(x+240,y+65))
        savePic.blit(itemStatsFont.render("Attack:  " + str(player.attack),True,(255,255,255)),(x+240,y+105))
        savePic.blit(itemStatsFont.render("Experience: " + str(player.xp),True,(255,255,255)),(x+240,y+145))
        savePic.blit(itemStatsFont.render("Stamina:  " + str(player.maxstamina),True,(255,255,255)),(x+440,y+25))
        savePic.blit(itemStatsFont.render("Defence:  " + str((player.defense+player.currentArmour.defense+player.currentBoots.defense)*100),True,(255,255,255)),(x+440,y+65))
        savePic.blit(itemStatsFont.render("Money:  " + str(player.money),True,(255,255,255)),(x+440,y+105))
        savePic.blit(player.animation[0][1],(x+55,y+41))

        if saveRects[saves.index(player)].collidepoint(mx,my):
            if click == True:
                 dump(player,open("saves\save%d.p" % (saves.index(player)),"wb"))
                 return 0
            
    alphasurf=Surface((1024,768),SRCALPHA).convert()
    alphasurf.fill((0,0,0,200))
    screen.blit(surf,(0,0))
    screen.blit(alphasurf,(0,0))
    screen.blit(savePic,(0,0))

    if saveRects[3].collidepoint(mx,my):#quit
        if click == True:
            return 3
    return 4

def pausescreen(alphaSurf,surf,pausePic,savePic,saves):
    options = [Rect(410,185,200,60),Rect(410,265,200,60),Rect(410,345,200,60),Rect(410,425,200,60)] 
    screen.blit(surf,(0,0))
    alphaSurf.fill((0,0,0,200))
    if options[0].collidepoint(mx,my):#resume
        draw.rect(alphaSurf,(50,50,50,200),options[0])
        if click == True:
            return 1
    if options[1].collidepoint(mx,my):#save
        draw.rect(alphaSurf,(50,50,50,200),options[1])
        if click == True:
            return 4
    if options[2].collidepoint(mx,my):#cheats
        draw.rect(alphaSurf,(50,50,50,200),options[2])
        if click == True:
            return 1 #CHANGE THIS LATER TO ACUTALLY DO SOMETHING
    if options[3].collidepoint(mx,my):#quit
        draw.rect(alphaSurf,(50,50,50,200),options[3])
        if click == True:
            return 0
    screen.blit(alphaSurf,(0,0))
    screen.blit(pausePic,(0,0))
    return 3

def drawInventoryBase(alphaSurf,pic,player):
    alphaSurf.fill((0,0,0,200))
    screen.blit(alphaSurf,(0,0))
    screen.blit(pic,(60,75))
    screen.blit(transform.scale(player.animations[0][0],(player.rect[2]+100,player.rect[3]+100)),(210-(player.rect[2]+100)//2,245-(player.rect[3]+100)//2)) #Instead take center x,y of where you want to blit and subtract half of images width and height
    screen.blit(player.currentWeapon.image,(366.5-player.currentWeapon.image.get_width()/2,165.5-player.currentWeapon.image.get_height()/2))
    screen.blit(player.currentArmour.image,(366.5-player.currentArmour.image.get_width()/2,255.5-player.currentArmour.image.get_height()/2))
    screen.blit(player.currentBoots.image,(366.5-player.currentArmour.image.get_width()/2,340.5-player.currentBoots.image.get_height()/2))

    screen.blit(itemStatsFont.render("Health: %s" % (player.maxhealth),True,(0,0,0)),(166,503))
    screen.blit(itemStatsFont.render("Mana: %s" % (player.maxmana),True,(0,0,0)),(166,540))
    screen.blit(itemStatsFont.render("Attack: %s" % (player.damage+player.currentWeapon.damage),True,(0,0,0)),(166,576))
    screen.blit(itemStatsFont.render("Experience: %s/%d" % (player.xp,90),True,(0,0,0)),(166,616))
    screen.blit(itemStatsFont.render("Stamina: %s" % (player.maxstamina),True,(0,0,0)),(371,503))
    screen.blit(itemStatsFont.render("Defence: %s" % (int((player.defense+player.currentArmour.defense+player.currentBoots.defense)*100)),True,(0,0,0)),(371,540))
    screen.blit(itemStatsFont.render("Money: $%s" % (player.money),True,(0,0,0)),(371,576))

    if player.kind == "Wizard":
        screen.blit(inventFont.render("Staff",True,(255,255,255)),(440,128))
        screen.blit(inventFont.render("Robe",True,(255,255,255)),(440,218))
        screen.blit(inventFont.render("Shoes",True,(255,255,255)),(440,308))
    elif player.kind == 'Knight':
        screen.blit(inventFont.render("Sword",True,(255,255,255)),(440,128))
        screen.blit(inventFont.render("Armour",True,(255,255,255)),(440,218))
        screen.blit(inventFont.render("Boots",True,(255,255,255)),(440,308))
    elif player.kind == 'Archer':
        screen.blit(inventFont.render("Bow",True,(255,255,255)),(440,128))
        screen.blit(inventFont.render("Clothes",True,(255,255,255)),(440,218))
        screen.blit(inventFont.render("Arrow",True,(255,255,255)),(440,308))

def drawInventoryStats(infoSurface,x,y,item,kind):
    infoSurface.fill((0,0,0,230))
    draw.rect(infoSurface,(255,255,255,255),(0,0,infoSurface.get_width(),infoSurface.get_height()),4)
    infoSurface.blit(itemStatsFont.render(item.name,True,(255,255,255)),(5,5))
    if kind == 0:
        infoSurface.blit(itemStatsFont.render('Damage: %s' % (int(item.damage)),True,(255,255,255)),(5,30))
    else:
        infoSurface.blit(itemStatsFont.render('Defense: %s' % (int(item.defense*100)),True,(255,255,255)),(5,30))
    infoSurface.blit(itemStatsFont.render(item.description,True,(255,255,255)),(5,45))
    screen.blit(infoSurface,(x,y))

def changeGear(player,equipping,kind):
    if kind == 0: #Weapon
        x = player.currentWeapon
        player.currentWeapon = equipping
        player.inventory[kind][player.inventory[kind].index(equipping)] = x
    if kind == 1: #Armour
        x = player.currentArmour
        player.currentArmour = equipping
        player.inventory[kind][player.inventory[kind].index(equipping)] = x
    if kind == 2: #Boots
        x = player.currentBoots
        player.currentBoots = equipping
        player.inventory[kind][player.inventory[kind].index(equipping)] = x

def drawInventorySlots(inventRects,player,mx,my,click,infoSurface,rclick):
    for y in range(3):
        for x in range(len(player.inventory[y])):
            screen.blit(player.inventory[y][x].image,(inventRects[y][x][0],inventRects[y][x][1]))
        for rect in inventRects[y]:
            if rect.collidepoint(mx,my) and inventRects[y].index(rect) < len(player.inventory[y]):
                drawInventoryStats(infoSurface,mx-200,my-100,player.inventory[y][inventRects[y].index(rect)],y) #200,100 is the dimensions of the infoSurf
                if click:
                    changeGear(player,player.inventory[y][inventRects[y].index(rect)],y)
                elif rclick:
                    del player.inventory[y][inventRects[y].index(rect)]
    if equippedRect[y].collidepoint(mx,my):
            if y == 0:
                drawInventoryStats(infoSurface,mx-200,my-100,player.currentWeapon,y)
            elif y == 1:
                drawInventoryStats(infoSurface,mx-200,my-100,player.currentArmour,y)
            elif y == 2:
                drawInventoryStats(infoSurface,mx-200,my-100,player.currentBoots,y)

def draw_inventory(player,pic,inventRects,click,mx,my,infoSurface,alphaSurf,rclick):
    drawInventoryBase(alphaSurf,pic,player)
    drawInventorySlots(inventRects,player,mx,my,click,infoSurface,rclick)

def drawMap(backPic,player,pos):
    screen.fill((0,0,0))
    screen.blit(transform.scale(backPic,(900,600)),(screen.get_width()//2-450,screen.get_height()//2-270))
    screen.blit(player.mapFog,(screen.get_width()//2-450,screen.get_height()//2-270))
    x = (player.x-back_x)/backPic.get_width()*900
    y = (player.y-back_y)/backPic.get_height()*600
    screen.blit(transform.scale(player.animations[0][int(pos)],(20,30)),(int(x)+screen.get_width()//2-460,int(y)+screen.get_height()//2-285))

def drawSkillMenu(skillPic,player,click,mx,my,selectedskill,key):
    screen.fill((0,0,0))
    screen.blit(skillPic,(60,75))
    index=0
    if selectedskill!= None:
        if key[K_1] == 1 and selectedskill!=0:
            player.skillicons.insert(0,player.skillicons.pop(selectedskill))
            player.skillicons.insert(selectedskill,player.skillicons.pop(1))
            player.hotbar.insert(0,player.hotbar.pop(selectedskill))
            player.hotbar.insert(selectedskill,player.hotbar.pop(1))

            selectedskill=None
        if key[K_2] == 1 and selectedskill!=1:
            player.skillicons.insert(1,player.skillicons.pop(selectedskill))
            player.hotbar.insert(1,player.hotbar.pop(selectedskill))
            if selectedskill!=0:
                player.skillicons.insert(selectedskill,player.skillicons.pop(2))
                player.hotbar.insert(selectedskill,player.hotbar.pop(2))
            selectedskill=None
        if key[K_3] == 1 and selectedskill!=2:
            player.skillicons.insert(2,player.skillicons.pop(selectedskill))
            player.skillicons.insert(selectedskill,player.skillicons.pop(3))
            player.hotbar.insert(2,player.hotbar.pop(selectedskill))
            player.hotbar.insert(selectedskill,player.hotbar.pop(3))
            selectedskill=None
    for x in range(178,273,94):
        for y in range(215,492,86):
            if index <len (player.skillicons):
                iconrect=screen.blit(player.skillicons[index],(x,y))
                if index== selectedskill:
                    draw.rect(screen,(0,0,0),iconrect,10)
                if iconrect.collidepoint((mx,my)) and click:
                    selectedskill=index
            index+=1
    return selectedskill

###########################################################
def wallCol(img,coordList,back_x,back_y):
    checkList = []
    for coord in coordList:
        #draw.circle(screen,(0,0,0),(int(coord[0]),int(coord[1])),5)
        if 0<=coord[0]<=screen.get_width() and 0<=coord[1]<=screen.get_height():
            if img.get_at((int(-back_x+coord[0]),int(-back_y+coord[1]))) == (255,0,0):
                #draw.circle(screen,(255,0,0),(int(coord[0]),int(coord[1])),5)
                checkList.append(True)
            else:
                checkList.append(False)
    return checkList
##################################################################
        
def tabs(player,pic,inventRects,click,mx,my,infoSurface,alphaSurf,tabMode,backPic,skillMenu,pos,selectedskill,key):
    if tabMode == 0:
        draw_inventory(player,pic,inventRects,click,mx,my,infoSurface,alphaSurf,rclick)
    elif tabMode == 1:
        drawMap(backPic,player,pos)
    elif tabMode == 2:
        selectedskill = drawSkillMenu(skillMenu,player,click,mx,my,selectedskill,key)
        return selectedskill
    draw.rect(screen,(255,255,255),(10,10,1000,60))

################################ ADDED ########################################
def knockBack(x,y,power,angle): #NOT DONE YET
    x += power*cos(radians(angle))
    y += power*sin(radians(angle))
    return x,y

def confusion(player):
    timerConfusion = Timer(5, player.statReset, [None, None, None, None, None,[(0,5),(-5,0),(5,0),(0,-5)],False, None])
    for pos in range(len(player.speeds)):
        player.speeds[pos] = (player.speeds[pos][0]*-1,player.speeds[pos][1]*-1)
    timerConfusion.start()
    return True


def deleteList(lst):
    lst = []
    return lst

def traps(trapList,screen,width,height,amount):
    trapList = []
    timerTrap = Timer(5 , deleteList(trapList))
    for i in range(amount):
        x = randint(0,screen.get_width()-width)
        y = randint(0,screen.get_height()-height)
        if player.rect.colliderect(Rect(x,y,width,height)) == False:
            trapList.append(Rect(x,y,width,height))
    return trapList

def drawTraps(screen,player,trapList):
    for trap in trapList:
        draw.rect(screen,(255,255,255),trap)
        if player.rect.colliderect(trap):
            player.health -= 20

def slow(player):
    timerSlow = Timer(5 , self.statReset, [None, None, None, None, None,[self.speed],None, None])
    for val in player.speed:
        player.speed[player.speed.index(val)] = val*0.6
    timerConfusion.start()

def pull(player,x,y):
    dx,dy = x-player.x,y-player.y #################################################### FINISH
####################################################################################################################
    

def generateItems(player,fileList,times):
    items = []
    if player.kind == "Knight":
        pos = 1
    elif player.kind == 'Archer':
        pos = 2
    elif player.kind == 'Wizard':
        pos = 3
    for i in range(times):
        adjective = choice(fileList[0])
        item = choice(fileList[pos])
        person = choice(fileList[4])
        items.append('%s %s of %s' % (adjective,item,person))
    return items

##################################################### ADDED ######################################################
def drawIntroEffects(tx,ty,titleScrollx,titleScrolly,back,textbox1,name,fire,firePos):
    if tx == -back.get_width()+screen.get_width() or tx == 0:
        titleScrollx *= -1
    if ty == -back.get_height()+screen.get_height() or ty == 0:
        titleScrolly *= -1

    screen.blit(back,(tx,ty))
    screen.blit(textbox1,(300,40))
    screen.blit(name,(400,65))
    screen.blit(fire[int(firePos)],(350,50))
    screen.blit(fire[int(firePos)],(675,50))

    if firePos >= 3:
        firePos = 0
    else:
        firePos += 0.3
    tx += titleScrollx
    ty += titleScrolly
    return firePos,tx,ty,titleScrollx,titleScrolly

def selectMenu(fire,firePos,titleMenu,titleRects,click,mx,my):
    screen.blit(textbox2,(300,175))
    screen.blit(titleMenu,(335,180))
    for rect in range(len(titleRects)):
        if titleRects[rect].collidepoint(mx,my):
            screen.blit(fire[int(firePos)],(titleRects[rect][0]+50,titleRects[rect][1]-20))
            screen.blit(fire[int(firePos)],(titleRects[rect][0]+265,titleRects[rect][1]-20))
            if click:
                if rect == 0:
                    return 1
                elif rect == 1:
                    return 1
                elif rect == 2:
                    return 1
                elif rect == 3:
                    return 2
    return 0
                    
def characterSelection(click,choiceRects,backRect):
    mode = 0
    titleMode = 1
    player = None
    choices = [
        [Weapons('Rusty Sword','A REALLY bad sword',5,'Art\Weapons\swords\sword1.png',1,'Sword'),'Knight',["Block","Rambo","Bomb","Magnet","Siphon","Freeze","Helper"]],
        [Weapons('Old Staff','A REALLY bad staff',5,'Art\Weapons\Staffs\staff1.png',1,'Staff'),'Wizard',["Heal","Fire","Ring","Boost","Charge","Turtle","Shadow"]],
        [Weapons('Old Bow','A REALLY bad bow',5,'Art\Weapons\Bows\Bow0.png',1,'Bow'),'Archer',["Sniper", "Barrage", "PoisonArrow", "FollowMe","Fear","RadiusBarrage","ForestGump"]]
        ]
    for x in range(3):
        screen.blit(textbox3,(choiceRects[x][0],choiceRects[x][1]))
        screen.blit(titlePics[x],(choiceRects[x][0]+175-titlePics[x].get_width()/2,choiceRects[x][1]+170-titlePics[x].get_height()/2))
        if choiceRects[x].collidepoint(mx,my) and click:
            player = Player(100,100,100,[[],[],[]],choices[x][0],Armour('Bob2','Bob2',0.01,'Art\Armour\Knight\Armour0.png','Armour'),Boots('Base','FaNcY',0.01,'Art\Boots\Boot0.png','Boots'),100000,choices[x][1],10,0.1,choices[x][2])
            mixer.music.load("Song2.wav")
            mixer.music.play()
            mode = 1
            titleMode = 0
            circleout(screen.copy(),0)
    draw.rect(screen,(255,255,255),backRect)
    if backRect.collidepoint(mx,my) and click:
        mode = 0
        titleMode = 0
    return mode,titleMode,player

def drawIntroScreen(tx,ty,titleScrollx,titleScrolly,back,back_x,back_y,textbox1,name,fire,firePos,titleMenu,titleRects,titleMode,click,choiceRects,backRect,mx,my,running):
    player = None
    if mixer.music.get_busy() == 0:
        mixer.music.play()
    firePos,tx,ty,titleScrollx,titleScrolly = drawIntroEffects(tx,ty,titleScrollx,titleScrolly,back,textbox1,name,fire,firePos)
    if titleMode == 0:
        titleMode = selectMenu(fire,firePos,titleMenu,titleRects,click,mx,my)
        mode = 0
    elif titleMode == 1:
        mode, titleMode, player = characterSelection(click,choiceRects,backRect)
    elif titleMode == 2:
        mode = 0
        running = False
    return mode,0,0,firePos,running,titleMode,player,tx,ty,titleScrollx,titleScrolly, 0

fadein=True
#============ Animations======#
def drawcircle(w,h,s):
    circlesurf=Surface((w,h),SRCALPHA)
    draw.ellipse(circlesurf,(0,0,0),(0,0,w,h))
    draw.ellipse(circlesurf,(255,255,255,0),(s,s,w-s*2,h-s*2))
    screen.blit(circlesurf,((screen.get_width()-w)//2,(screen.get_height()-h)//2))
    return
def drawemptycircle(w,h):
    circlesurf=Surface((screen.get_width(),screen.get_height()),SRCALPHA)
    circlesurf.fill((0,0,0))
    draw.ellipse(circlesurf,(255,255,255,0),(((screen.get_width()-w)//2),((screen.get_height()-h)//2),w,h))
    screen.blit(circlesurf,(0,0))
    return
def circleout (pic,tim):
    if pic!= None:
        screen.blit(pic,(0,0))
    radius=int((screen.get_width()**2+screen.get_height()**2)**0.5)
    wh=radius
    for i in range(radius//2):
        if wh<=5:
            draw.ellipse(screen,(0,0,0),(0,0,5,5))
            break
        else:
            drawcircle(wh,wh,5)
        wh-=5
        time.delay(tim)
        display.flip()
    return
def circlein (pic,tim):
    radius=int((screen.get_width()**2+screen.get_height()**2)**0.5)
    wh=1
    for i in range(radius//5):
        screen.blit(pic,(0,0))
        drawemptycircle(wh,wh)
        wh+=5
        time.delay(tim)
        display.flip()
    return




#===========================================================================================================================================#
boss1 = True
boss2 = True
boss3 = True
mapNum = 0
running =True
screen = display.set_mode((1024,700))
clock = time.Clock()
click = False
#===========SOUNDS=============#
npcsound={"Hello":[mixer.Sound(x)for x in glob.glob("Art/Sound/npc/hello/*.wav")],"Bye":[mixer.Sound(x)for x in glob.glob("Art/Sound/npc/bye/*.wav")],"Bought":[mixer.Sound(x)for x in glob.glob("Art/Sound/npc/bought/*.wav")]}
#=========== Background ============#
'''
Loads the background map and creates the x and y variables used for to offset the background for movement
'''
mapList = [ #[Map, map_mask, fog]
    [image.load('Art/Backgrounds/Background.jpg'),image.load('Art/Backgrounds/BackgroundMASK.png'),transform.scale(image.load('Art\Misc\Fog.png'),(900,600)).convert()],
    [image.load('Art/Backgrounds/map2.png'),image.load('Art/Backgrounds/map2mask.png'),transform.scale(image.load('Art\Misc\Fog.png'),(900,600)).convert()],
    [image.load('Art/Backgrounds/map3.png'),image.load('Art/Backgrounds/map3mask.png'),transform.scale(image.load('Art\Misc\Fog.png'),(900,600)).convert()],
    [image.load('Art/Backgrounds/map4.png'),image.load('Art/Backgrounds/map4mask.png'),transform.scale(image.load('Art\Misc\Fog.png'),(900,600)).convert()]
    ]
back = mapList[mapNum][0]#IAN
back_mask = mapList[mapNum][1]
back_x = 0
back_y = 0
#===================================#

#=============== HUD ===============#
'''
Creates a surface (thats translucent) to show health, stamina, mana, money and level
'''
hud = Surface((250,150))
hud.fill((0,0,0))
hud.set_alpha(200)
#===================================#

#============ Animations ===========#

fire = []
for i in range(4):
    firePic = image.load('Art/Misc/Fire/fire%d.png' % (i)).convert()
    firePic.set_colorkey((255,255,255))
    fire.append(firePic)
firePos = 0
mapPos = 0

#===================================#

#============== Title ==============#
name = image.load('Art\Misc\Title.png').convert()
name.set_colorkey((255,255,255))
tx,ty = 0,0
titleScrollx,titleScrolly = 1,1 #Used for the title screen scrolling feature
textbox1 = image.load('Art\\Misc\\textbox.gif').convert()
textbox2 = image.load('Art\Misc\Textbox2.png').convert()
textbox2.set_colorkey((255,255,255))
textbox3 = image.load('Art\Misc\Textbox3.png').convert() 
textbox3.set_colorkey((255,255,255)) 
backRect = Rect(500,670,24,10)
choiceRects = []
for i in range(3):
    choiceRects.append(Rect(3+340*i,185,300,450))

#============= Music ===============#
mixer.music.load('Song.mp3')
#===================================#
#======================================= Variables ==============================#
#========== Surfaces ==========#
infoSurface = Surface((200,100),SRCALPHA)
alphaSurf = Surface((screen.get_width(),screen.get_height()),SRCALPHA)
trapList = []
#============ Lists ===========#
weaponFile = []
for line in open('Weapons.txt').read().strip().split('\n'):
    weaponFile.append(line.split())
armourFile = []
for line in open('Armor.txt').read().strip().split('\n'):
    armourFile.append(line.split())
bootsFile = []
for line in open('Boots.txt').read().strip().split('\n'):
    bootsFile.append(line.split())

shopWeapons = []
shopArmour = []
shopBoots = []
        
saves = []
#for i in range(len(listdir("saves"))):
    #saves.append(load(open("saves\save"+str(i)+".p","rb")))

enemies = []
#for i in range(100):
#    enemies.append(Enemy(100,choice(['Theif','Charger','Archer','Monster','Dragon','Mage']),None, None))#Snake,Scorpien


quests = [Rect(1675,1660,70,70),Rect(1200,1300,50,50),Rect(1300,1300,50,50),Rect(1400,1300,50,50)]#IAN
currentQuest = [Rect(1675,1660,70,70)]#IAN    enemies.append(Enemy(100,choice(['Ghost','Charger','Archer','Monster','Dragon','Mage']),None, None))#Snake,Scorpien

bootShop=Rect(1960,2400,50,50)
armorShop=Rect(1120,2220,50,50)
weaponShop=Rect(1150,870,50,50)
doorKeeper=Rect(680,1200,50,50)
wellMan=Rect(1748,570,50,50)
helpMeRects=[Rect(1040,505,50,50),Rect(1740,570,50,50),Rect(1740,1160,50,50),Rect(2160,1970,50,50),Rect(2255,1790,50,50)]

inventRects = [[],[],[]]
for i in range(2):
    for x in range(3):
        for y in range(2):
            inventRects[i].append(Rect(678+93*x,135+86*y+172*i,80,80))
for x in range(5):
    for y in range(2):
        inventRects[2].append(Rect(514+87*x,485+85*y,80,80))

equippedRect = []
for y in range(3):
    equippedRect.append(Rect(330,130+85*y,80,80))

titleRects = []
for i in range(4):
    titleRects.append(Rect(348,260+60*i,350,50))
#=== Animations ===#

#======== Fonts ========#
shopFont = font.SysFont('Times New Roman',25)
saveFont1 = font.SysFont('Tw Cen MT Condensed Extra Bold',21)
saveFont2 = font.SysFont('Tw Cen MT Condensed Extra Bold',90)
inventFont = font.SysFont('Tw Cen MT Condensed Extra Bold',90)
moneyFont = font.SysFont('Times New Roman',30)
statsFont = font.SysFont('Times New Roman',20)
itemStatsFont = font.SysFont('Times New Roman',15)

#======= Images =======#
npcPics = [image.load("Art\\NPCs\\shop.png")]
pausePic=image.load("Art\\Menus\\pausescreen.png") #Words for the pause screen (Resume,Exit,etc.)
savePic = image.load("Art\\Menus\\Saves.png")
skillBarPic = image.load("Art\\Menus\\hud_bottom.jpg")
inventoryPic = image.load("Art\\Menus\\inventory.png")
shopPic = image.load("Art\\Menus\\shelfs.jpg")
titleMenu = image.load('Art\\Misc\\Start_Title.png')
skillMenu = image.load('Art\\Menus\\skills.png')

#======= Speech =======#IAN

quest1= image.load("Art//Quests//quest1.png")
quest2= image.load("Art//Quests//quest2.png")
quest3= image.load("Art//Quests//quest3.png")
questSpeech=[image.load("Art//Quests//quest1Speech.png"),image.load("Art//Quests//quest2Speech.png"),image.load("Art//Quests//quest3Speech.png"),image.load("Art//Quests//quest2Speech.png")#IAN
             ,image.load("Art//Quests//quest2Speech.png")]
helpSay=choice([image.load("Art/Quests/helpMe1.png"),image.load("Art/Quests/helpMe2.png")
                ,image.load("Art/Quests/helpMe3.png"),image.load("Art/Quests/helpMe4.png")])
titlePics = [transform.scale(image.load('Art\Player\Knight\Player00.png'),(150,200)),transform.scale(image.load('Art\Player\Wizard\Player00.png'),(150,200)),transform.scale(image.load('Art\Player\Archer\Player00.png'),(150,200))]
                                                       
#======================#
bossmaps=[image.load('Art/Backgrounds/boss/map.png'),image.load('Art/Backgrounds/boss/icemap.png'),
          image.load('Art/Backgrounds/boss/forestmap.png'),image.load('Art/Backgrounds/boss/desertmap.png')]
bossmasks=[image.load('Art/Backgrounds/boss/mapmask.png'),image.load('Art/Backgrounds/boss/icemapmask.png'),image.load('Art/Backgrounds/boss/forestmapmask.png'),image.load('Art/Backgrounds/boss/desertmapmask.png')]
bosses = [Boss(1,100,100,'Eiznekcam'),Boss(5000,100,100,'Skeletonmage'),Boss(5000,100,100,'Greentroll'),Boss(5000,100,100,'Hairymonster')]
mode = 0 # 0 = menu, 1 = game, 2 = inventory, 3 = pause, 4 = save, 5 = shop
enemies = newEnemies(mode)
titleMode = 0 #ADDED THIS
tabMode = 0
selectedskill = None
while running:    
    for e in event.get():
        if e.type == KEYDOWN:
            if e.key == K_m:
                if mode == 1:
                    mode = 2
                elif mode == 2:
                    mode = 1
            if e.key == K_ESCAPE:
                if mode == 1:
                    mode = 3
                elif mode == 3:
                    mode = 1
            if e.key == K_b:
                if mapNum<3:
                    mapNum += 1
                else:
                    mapNum = 0
            if e.key == K_p:
                if mode == 1:
                    if armorShop.collidepoint(-back_x+530,-back_y+345):
                        mode = 5
                        choice(npcsound["Hello"]).play()
                        shopArmour = []
                        for armour in generateItems(player,armourFile,11):
                            if player.kind == 'Knight':
                                shopArmour.append(Armour(armour,'Good Stuffs',gauss(0.1+player.level/20,0.05),'Art/Armour/Knight/Armour%d.png' % (randint(0,5)),'Armour'))
                            if player.kind == 'Wizard':
                                shopArmour.append(Armour(armour,'Good Stuffs',gauss(0.1+player.level/20,0.05),'Art/Armour/Knight/Armour%d.png' % (randint(0,5)),'Armour'))
                            if player.kind == 'Archer':
                                shopArmour.append(Armour(armour,'Good Stuffs',gauss(0.1+player.level/20,0.05),'Art/Armour/Knight/Armour%d.png' % (randint(0,5)),'Armour'))

                    elif weaponShop.collidepoint(-back_x+530,-back_y+345):
                        mode = 5
                        choice(npcsound["Hello"]).play()
                        shopWeapons = []
                        for weapon in generateItems(player,weaponFile,11):
                            if player.kind == 'Knight':
                                shopWeapons.append(Weapons(weapon,'Good Stuffs',gauss(10+5*player.level,3),'Art/Weapons/Swords/Sword%d.png' % (randint(1,11)),1,'Sword'))
                            if player.kind == 'Wizard':
                                shopWeapons.append(Weapons(weapon,'Good Stuffs',gauss(10+5*player.level/20,3),'Art/Weapons/Staffs/Staff%d.png' % (randint(1,16)),1,'Staff'))
                            if player.kind == 'Archer':
                                shopWeapons.append(Weapons(weapon,'Good Stuffs',gauss(10+5*player.level/20,3),'Art/Weapons/Bows/Bow%d.png' % (randint(0,14)),1,'Bow'))
                    elif bootShop.collidepoint(-back_x+530,-back_y+345):
                        mode = 5
                        choice(npcsound["Hello"]).play()
                        shopBoots = []
                        for boot in generateItems(player,bootsFile,11):
                            shopBoots.append(Boots(boot,'Good Stuffs',gauss(0.03+player.level/20,0.02),'Art/Boots/Boot%d.png' % (randint(0,2)),'Boots'))
                elif mode == 5:
                    choice(npcsound["Bye"]).play()  
                    mode = 1
            if e.key == K_q:
                if mode == 2:
                    player.sound["Map"].play()
                    if tabMode != 2:
                        tabMode += 1
                    else:
                        tabMode = 0
            if e.key == K_e:
                if mode == 2:
                    player.sound["Map"].play()
                    if tabMode != 0:
                        tabMode -= 1
                    else:
                        tabMode = 2

                
        if e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                click = True
            if e.button == 3:
                pass
                #trapList = traps(trapList,screen,50,50,50)
            if e.button == 3:
                rclick = True
        elif e.type == QUIT:
            running = False

    kb = key.get_pressed()
    mx,my = mouse.get_pos()
    mb = mouse.get_pressed()

    if mode == 0: 
        mode,back_x,back_y,firePos,running,titleMode,player,tx,ty,titleScrollx,titleScrolly, mapNum = drawIntroScreen(tx,ty,titleScrollx,titleScrolly,back,back_x,back_y,textbox1,name,fire,firePos,titleMenu,titleRects,titleMode,click,choiceRects,backRect,mx,my,running)
        if fadein==True:
            circlein(screen.copy(),0)
            fadein=False
    elif mode == 2:
        selectedskill = tabs(player,inventoryPic,inventRects,click,mx,my,infoSurface,alphaSurf,tabMode,back,skillMenu,mapPos,selectedskill,kb)
        if mapPos >= len(player.animations[0])-1:
            mapPos = 0
        else:
            mapPos += 0.1
    elif mode == 3:
        mode = pausescreen(alphaSurf,screen.copy(),pausePic,savePic,saves)
            
    elif mode == 4:
        mode = savescreen(screen.copy(),savePic,saves)

    elif mode == 5:
        if weaponShop.collidepoint(-back_x+530,-back_y+345):
           player.money = drawShop(shopFont,click,mx,my,player.money,shopPic,shopWeapons)
        elif bootShop.collidepoint(-back_x+530,-back_y+345):
           player.money = drawShop(shopFont,click,mx,my,player.money,shopPic,shopBoots)
        elif armorShop.collidepoint(-back_x+530,-back_y+345):
            player.money = drawShop(shopFont,click,mx,my,player.money,shopPic,shopArmour)
    elif mode==6:
        boss = bosses[mapNum]
        back = bossmaps[mapNum]
        back_mask = bossmasks[mapNum]
        screen.blit(back,(back_x,back_y))
        directions = [[kb[K_DOWN],kb[K_s]],[kb[K_LEFT],kb[K_a]],[kb[K_RIGHT],kb[K_d]],[kb[K_UP],kb[K_w]]]
        boss.update(back_x,back_y,enemies,kb)
        for trap in boss.trapList:
            draw.rect(screen,(0,0,0),trap)
            if player.rect.colliderect(trap):
                player.health -= 10
        back_x,back_y = player.update(click,mx,my,kb,hud,skillBarPic,enemies,back_x,back_y,directions,back,back_mask)
        if boss.health<= 0:
            mode = 1
            mapNum = 0
            player.x,player.y = 300,300
    else:

#======================================================================== Map Movement =============================================================================#
        '''
        The camera is centered on the player until the player moves to the edge of the map. At this point the character moves freely. When the character returns to
        the middle (vertically and/or horizontallly) the camera keeps the player in the center
        '''
        
        directions = [[kb[K_DOWN],kb[K_s]],[kb[K_LEFT],kb[K_a]],[kb[K_RIGHT],kb[K_d]],[kb[K_UP],kb[K_w]]]

#============================== Up/Down/Left/Right ===============================#
        '''
        Moves either the map or player (player moves if pmovex/y is True). Also turns pmovex/y False if the player returned to the center (the vertical and/or horizontal
        center). Also stops the player from going past the edge of the screen.
        '''
    #===================================================================================#

        screen.blit(back,(back_x,back_y)) #Blits updated map onto screen

#====================================================================================================================================================================#

    #============= Updates ============#
        '''
        Update all sprites (their movement, stats, etc.)
        '''
        if boss1 and boss2 and boss3:
            mapList[0][0] = image.load('Art//Backgrounds//BackgroundOpen.jpg')
            mapList[0][1] = image.load('Art//Backgrounds//backgroundOpenMASK.png')
            boss1,boss2,boss3 = False,False,False
        for enemy in enemies:
            enemy.update(back_x,back_y,enemies,kb,enemies,back_mask)  #updates enemies
        back_x,back_y = player.update(click,mx,my,kb,hud,skillBarPic,enemies,back_x,back_y,directions,back,back_mask) #Updates player
        back = mapList[mapNum][0]
        back_mask = mapList[mapNum][1]
        mapNum,back_x,back_y,player.x,player.y,mode = changeMap(mapList,mapNum,back_mask,back_x,back_y,back,player)
        if player.health < 1:
            quit()
        player.health = 100
    #==================================#
    click = False
    rclick = False
    display.flip()
    clock.tick(30)
quit()
