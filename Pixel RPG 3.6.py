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


################# KNOWN BUGS ########################
#Turtle skill basically does nothing because enemy.speed is not connected to the enemy speed in any way ** FIX THIS RISHI **
# ADD A SPRITE FOR SHADOW SKILL
#Sniper skill goes atop the HUD bottom
#Charge and skill broke, goes diagnolly
####################################################

################# CHANGES ########################
#Added new archer skills
#added self.ang and calculated self.ang in fire skill early so that blit does not change while attack = True
#changed colour scheme for the HUD Components
#added projectiles for archer and updated the Projectile Class (if self.kind == "Arrow")
#Ln 1072 - Fixed click so that projectile isn't created with any click
####################################################
#=================================================== Classes ===================================================#

class Player(sprite.Sprite):
    def __init__(self, health, stamina, mana, inventory, currentWeapon, currentArmour, currentBoots, money, kind, damage, defense, hotbar):
        super().__init__()
        
        self.pmovex = False #Flag to move either the screen or player in the horizontal direction
        self.pmovey = False #Flag to move either the screen or player in the vertical direction
        self.moving = False #Flag if the player is moving (used to for animations and sprint)

        self.kind = kind
        if self.kind == 'Knight':
            self.animations = [[image.load('Art\Player\Knight\Player%d%d.png' %(x,y)).convert_alpha() for y in range(5)] for x in range(4)]
        if self.kind == 'Wizard':
            self.animations = [[image.load('Art\Player\Wizard\Player%d%d.png' %(x,y)).convert_alpha() for y in range(3)] for x in range(4)]
        if self.kind == 'Archer':
            self.animations = [[image.load('Art\Player\Archer\Player%d%d.png' % (x,y)).convert_alpha() for y in range(3)] for x in range(4)]

        self.movepos = 0 #Is the player facing forward, left, right or down
        self.pos = 0 #The current pic of the animation (animation depends on movepos value)
        self.image = self.animations[self.movepos][self.pos]
        
        self.x = screen.get_width()/2+self.image.get_width()/2
        self.y = 308+self.image.get_height()/2
        self.image.set_colorkey((255,255,255))
        self.rect = Rect(screen.get_width()/2/2,308,self.image.get_width(),self.image.get_height())

        if self.kind == 'Knight':
            self.sword = image.load('Art\Weapons\Sword.png').convert()
            self.sword.set_colorkey((255,255,255))
            self.swordRect = self.sword.get_rect()
            
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

        self.inventory = inventory
        self.currentWeapon = currentWeapon
        self.currentArmour = currentArmour
        self.currentBoots = currentBoots
        self.money = money

        self.projectileHit = False
        self.mapFog = transform.scale(image.load('Art\Misc\Fog.png'),(900,600)).convert()#Surface((900,600),SRCALPHA).convert()
        self.mapFog.set_colorkey((255,0,0))

        #Used with SkillUse and skillChange
        self.attack = False 
        self.spriteCount = 0
        self.hotbar = hotbar #the hotbar skills that will exist by default when the player is created
        self.currentSkill = 0 #counter for which skill is selected in the hotbar list
        self.AIignore = False   #used for the shadow skill...will not update enemy AI if True
        self.coolDown = [False,False,False] #used to count cooldown time
        self.ang = 0

        self.skillSprites = []   #2D list of sprites
        if self.kind == "Wizard": #loading images based on what character is chosen (Skill sprites)
            self.skillSprites.append(glob.glob("Art/Skills/skillFire/*.png")) #0
            self.skillSprites.append(glob.glob("Art/Skills/skillRing/*.png")) #1
            self.skillSprites.append(glob.glob("Art/Skills/skillTurtle/*.png")) #2
            self.skillSprites.append(glob.glob("Art/Skills/Totems/*.png")) #3
            self.skillSprites.append(glob.glob("Art/Skills/skillBoost/*.png")) #4
            self.skillSprites.append(glob.glob("Art/Skills/skillHeal/*.png")) #4
        elif self.kind == "Archer":
            self.skillSprites.append(glob.glob("Art/Skills/skillSniper/*.png")) #0
            self.skillSprites.append(glob.glob("Art/Skills/skillForestGump/*.png")) #1
               
        for i in range(0,len(self.skillSprites)):
            for x in range(0,len(self.skillSprites[i])):
                self.skillSprites[i][x] = image.load(self.skillSprites[i][x])
        

    def sprint(self,key): #Changes players speed depending on if the shift button is pressed and their current stamina
        if key[K_LSHIFT] == 1:
            if self.moving:
                if self.stamina>0:
                    self.stamina -= 1
                    self.vx,self.vy = 10,10
                else:
                    self.stamina = 0
                    self.vx,self.vy = 5,5
                if self.stamina<self.maxstamina:
                    self.stamina += 0.15
        else:
            self.vx,self.vy = 5,5
            if self.stamina<self.maxstamina:
                self.stamina += 0.25

    def drawSkillBar(self,surf): #Draws the skill selection bar at the bottom of the screen
        screen.blit(surf,(0,615))
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

    def changePic(self):
        if self.moving and int(self.pos) != len(self.animations[self.movepos])-1:
            self.pos += 0.4
        else:
            self.pos = 0
        self.image = self.animations[self.movepos][int(self.pos)]
        
    def leveling(self): #Increases level of player after he has gotten 100 xp and increases stats randomly
        if self.xp<90:
            self.xp += 10
        else:
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
        
        centx = self.rect[0]+self.rect[2]/2 #Center of player horizontally
        centy = self.rect[1]+self.rect[3]/2 #Center of player vertically
        
        x = mx-centx #Distance from center to mouse horizontally
        y = my-centy #Distance from center to mouse vertically
        
        h = hypot(x,y) #Actual distance from mouse to center (pythag theorem)
        ax = 40/h*x #Find the horizonatal distance for a smilar triangle with hypot 40
        ay = 40/h*y #Find the vertical distance for a smilar triangle with hypot 40
        
        angle = -atan2(ay,ax) #Angle used to rotate sword
        
        if self.kind == 'Knight':
            display = transform.rotate(self.sword,degrees(angle)) #Rotate a copy sword with the angle we calculated
            screen.blit(display,(centx-display.get_width()//2,centy-display.get_height()//2)) #Blit the image with the offset
            
            for enemy in enemies:
                if enemy.rect.collidepoint(int(centx+ax),int(centy+ay)) or enemy.rect.collidepoint(int(centx+ax*2/3),int(centy+ay*2/3)) or enemy.rect.collidepoint(int(centx+ax/3),int(centy+ay/3)):
                    enemy.hurt = True
                    #enemy.health -= 50
        elif self.kind == 'Wizard':
            self.bullets.add(Projectile(centx,centy,10*cos(-angle),10*sin(-angle),-angle,None,'Spell'))
        elif self.kind == 'Archer':
            self.bullets.add(Projectile(centx,centy,10*cos(-angle),10*sin(-angle),-angle,None,'Arrow'))
            
    def takeDamage(self,enemies): #Checks if the player is touching an enemy and lowers the players health if it is
        if self.health <= 0:
            self.health = 0
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if self.health>0:
                    self.health -= (1-player.defense-player.currentArmour.defense-player.currentBoots.defense)*enemy.damage
                    return True
        if self.projectileHit:
            self.health -= (1-player.defense-player.currentArmour.defense-player.currentBoots.defense)*randint(7,10)
            self.projectileHit = False
            return True
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
                
    def statReset(self, health, mana,stamina, damage, defense, speed):
        'Resets the stats to normal after using a stat changing skill'
        if health != None:
            player.health = health
        if mana != None:
            player.mana = mana
        if stamina != None:
            player.stamina = stamina
        if damage != None:
            player.damage = damage
        if defense != None:
            player.defense = defense
        if speed != None:
            player.speed = speed
    
    def skillUse(self, skillFlag, attack, spriteCount, enemyList):   #skillFlag is taken in as a parameter using MOUSEBUTTONDOWN and attack keeps track if a skill is being used (no animation cut off or skill change while attack == True)
        if player.kind == "Wizard":
            if self.hotbar[self.currentSkill] == "Heal":    #adds 20% of maxhealth to health
                if skillFlag and self.health < self.maxhealth and self.mana > 2:
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
                        for i in enemyList:
                            if sprite.colliderect(i.rect):
                                i.health -= self.damage #subtracts the enemy health by your damage
                        
            elif self.hotbar[self.currentSkill] == "Ring":  #Area attack - attacks all enemies in vicinity
                if skillFlag and self.mana > 10 and attack == False:
                    player.mana -= 15
                    attack = True
                if attack:
                    if spriteCount < len(self.skillSprites[1]):
                        sprite = screen.blit(self.skillSprites[1][spriteCount],(self.x - self.skillSprites[1][spriteCount].get_width()/2 , self.y - self.skillSprites[1][spriteCount].get_height()/2))
                        spriteCount += 1
                        for i in enemyList:
                            if sprite.colliderect(i.rect):
                                i.health -= self.damage
                    else:
                        spriteCount = 0
                        attack = False
                                             
            elif self.hotbar[self.currentSkill] == "Boost" : #self.attack *= 2 and self.defense /= 2
                if skillFlag and self.mana > 5:                    
                    self.mana -= 5
                    timer = Timer(10.0 , self.statReset, [None, None, None, self.damage, self.defense,None])    #takes old stats and creates a timer
                    self.damage *= 2
                    self.defense /= 2
                    timer.start()    #starts the timer and runs self.statReset once timer is finished.
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
                    self.mana -= 10
                    attack = True
                if attack:
                    if spriteCount < len(self.skillSprites[2]):
                        sprite = screen.blit(self.skillSprites[2][int(spriteCount)],(self.x - self.skillSprites[2][int(spriteCount)].get_width()/2,  self.y - self.skillSprites[2][int(spriteCount)].get_height()/2))
                        spriteCount += 0.7  #only go up by 0.5 frames every time to reduce super fast animations
                        for i in enemyList:
                            if sprite.colliderect(i.rect):
                                i.speed -= self.damage  #reduces enemy speed by self.damage
                    else: 
                        spriteCount = 0
                        attack = False
                        
            elif self.hotbar[self.currentSkill] == "Charge":
                if skillFlag and self.mana > 5:
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
                        self.ang = atan2(mx - self.x, my - self.y)
                        self.bullets.add(Projectile(self.x, self.y, 10*cos(-self.ang), 10*sin(-self.ang), self.ang, int(spriteCount), 'BigBullet'))
                        attack = False            
                else:
                    spriteCount = 0
                        
            elif self.hotbar[self.currentSkill] == "Shadow":
                print(self.AIignore,attack,spriteCount)
                if skillFlag and self.mana > 10:
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
                if skillFlag and self.mana > 30:
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
                        for i in enemyList:
                            if sprite.colliderect(i.rect):
                                i.health -= self.damage + 50
                                
            elif self.hotbar[self.currentSkill] == "Barrage":
                print(self.bullets)
                if skillFlag and self.mana >= 30:
                    self.mana -= 30
                    attack = True
                    self.ang = atan2(mx - self.x, my - self.y) + (3*pi/2)   #have to offset with weird values for some reason
                if attack:
                    self.bullets.add(Projectile(self.x, self.y, 10*cos(-self.ang), 10*sin(-self.ang), -self.ang, None, 'Arrow'))
                    spriteCount += 1
                    if spriteCount > 30:
                        spriteCount = 0
                        attack = False
                    
                
                        
            elif self.hotbar[self.currentSkill] == "ForestGump":
                print(self.damage,self.stamina)
                if skillFlag and self.mana >= 15:
                    self.mana -= 15
                    timer = Timer(10.0 , self.statReset, [None, None, self.stamina, self.damage, None, None])    #health, mana,stamina, damage, defense, speed
                    self.damage /= 2
                    self.stamina += 9999    #TESTED, it is impossible to use all that stamina 
                    timer.start()   
                    attack = True
                if attack:
                    if spriteCount < 16:
                        sprite = screen.blit(self.skillSprites[1][int(spriteCount)], (self.x - self.skillSprites[1][int(spriteCount)].get_width()/2, self.y - self.skillSprites[1][int(spriteCount)].get_height()/2))
                        spriteCount += 1
                    else:
                        spriteCount = 0
                        attack  = False

                    
                    
                    


        return attack, spriteCount  #returning so that the last known value of attack and spriteCount can be reused

    def fillMap(self,back_x,back_y,backPic):
        draw.circle(self.mapFog,(255,0,0),(int((self.x-back_x)/backPic.get_width()*900),int((self.y-back_y)/backPic.get_height()*600)),100)
        
    def update(self,flag,mx,my,key,surf,surf2,enemies,cx,cy,directions,backPic): #Draws the player and calls most of the functions before it
        if flag:
            self.attacking(mx,my,enemies)
        else:
            self.skillChange(key)
        self.changePic()
        self.sprint(key)
        self.rect[0],self.rect[1] = self.x-self.image.get_width()/2,self.y-self.image.get_height()/2
        screen.blit(self.image,self.rect)   #(screen,(255,0,0),self.rect)
        self.bullets.update(cx,cy,None,enemies,key)
        self.HUD(surf)
        self.drawSkillBar(surf2)
        self.hurt = self.takeDamage(enemies)
        self.heal()
        self.attack , self.spriteCount = self.skillUse(rclick, self.attack, self.spriteCount, enemies)
        self.fillMap(cx,cy,backPic)
        
class Enemy(sprite.Sprite):
    def __init__(self,health,kind):
        super().__init__()
        self.kind = kind
        if self.kind == 'Archer':
            self.image = image.load('Art\Enemies\Archer.png').convert()
        elif self.kind == 'Charger':
            self.image = image.load('Art\Enemies\Knight.png').convert()
        elif self.kind == 'Thief':
            self.image = image.load('Art\Enemies\Thief.png').convert()
        elif self.kind == 'Mage':
            self.image = image.load('Art\Enemies\Mage.png').convert()
        else:
            self.image = image.load('Art\Enemies\Dragon.png').convert()
        self.image.set_colorkey((255,255,255))
        self.x = randint(0,2980)
        self.y = randint(0,2380)
        self.rect = Rect(self.x,self.y,20,20)
        self.speed = randint(3,7)
        self.hurt = False
        self.health = health
        self.damage = choice([0.5,1])
        self.vx = 5
        self.vy = 5
        self.moves = [-1,1]
        self.bullets = sprite.Group()
        self.angle = None

    def statRest(health,speed,damage):   #resets stats to remove debuffs
        if health != None:
            self.health = health
        elif speed != None:
            self.speed = speed
        elif damage != None:
            self.damage = damage

    def createProjectile(self):
        centx = self.rect[0]+self.rect[2]/2 #x coord of starting pos for arrow
        centy = self.rect[1]+self.rect[3]/2 #y coord of starting pos for arrow
        dx,dy = player.rect[0]+randint(-3,3)-centx,player.rect[1]+randint(-3,3)-centy #distance (horizontally and vertically) from player to starting pos (accuracy is +- 5)
        angle = atan2(dy,dx)
        cx = randint(10,20)*cos(angle)
        cy = randint(10,20)*sin(angle)
        self.bullets.add(Projectile(centx,centy,cx,cy,angle,None,'Enemy'))
        
    def AI(self):
        dx = player.rect[0]+player.rect[2]/2 - self.rect[0]
        dy = player.rect[1]+player.rect[3]/2- self.rect[1]
        self.angle = atan2(dy,dx)
        if self.kind == 'Charger' and -10<=self.rect[0]<=1034 and -10<=self.rect[1]<=745:
            self.x += int(5*cos(self.angle))
            self.y += int(5*sin(self.angle))
        elif self.kind == 'Archer' and 30<=self.rect[0]<=900 and 30<=self.rect[1]<=750:
            if (dx**2+dy**2)**0.5<100:
                self.x -= int(3*cos(self.angle))
                self.y -= int(3*sin(self.angle))
        elif self.kind == 'Thief':
            
            if player.movepos == 0:
                if 30<=self.rect[0]<=900 and 30<=self.rect[1]<=750:
                    if self.x<900-self.x:
                        self.x += 5
                    else:
                        self.x -= 5
                    if self.y<750-self.y:
                        self.y += 5
                    else:
                        self.y -= 5
        else:
            x = choice(self.moves)
            self.vx += x
            self.moves.append(x)
            y = choice(self.moves)
            self.vy += y
            self.moves.append(y)
            
    def takeDamage(self,enemies):
        if self.hurt:
            self.health -= 50
            self.hurt = False #ADD THINGS LIKE KNOCKBACK AND THE ENEMY FLASHES RED
        if self.health <= 0:
            enemies.remove(self)
            player.leveling()
            
    def movement(self,cx,cy):
        self.rect[0] = self.x + cx +self.vx
        self.rect[1] = self.y + cy +self.vy
        
    def update(self,cx,cy,enemies,key,enemyList):   #################################################################
        self.bullets.update(cx,cy,self.bullets,enemyList,key)
        if player.AIignore == False: #affected  by shadow skill
            self.AI()
        self.movement(cx,cy)
        self.takeDamage(enemies)
        screen.blit(self.image,(self.rect[0],self.rect[1]))

class Projectile(sprite.Sprite):
    def __init__(self,x,y,vx,vy,angle,bigBulletSize,kind):
        super().__init__()
        if player.kind == "Archer":
            self.image = image.load('Art\Weapons\Arrow.png').convert()
        elif player.kind == "Wizard":
            self.image = image.load('Art\Weapons\spell.png').convert()
        self.image.set_colorkey((255,255,255))
        self.x = x #Inital pos x
        self.y = y #Inital pos y
        self.vx = vx #Horizontal velocity
        self.vy = vy #Vertical velocity
        self.angle = angle
        self.kind = kind
        self.display = transform.rotate(self.image,degrees(-self.angle))
        if self.kind == 'BigBullet':
            self.display = transform.scale(self.display,(bigBulletSize*5,bigBulletSize*5))
            self.rect = Rect(self.x,self.y,bigBulletSize*5,bigBulletSize*5)
        else:
            self.rect = Rect(self.x,self.y,self.display.get_width(),self.display.get_height())
        
    def speed(self,key):
        #IMPROVE ORGAINZATION AND EFFICANCY
        '''
Offsets the arrow depending on where the player is moving (faster if player is moving into arrow, slower if player is moving away from arrow
        '''
        if player.pmovex == False:
            if key[K_a] or key[K_LEFT]:
                self.rect[0] += player.vx
            if key[K_d] or key[K_RIGHT]:
                self.rect[0] -= player.vx
        if player.pmovey == False:
            if key[K_w] or key[K_UP]:
                self.rect[1] += player.vy
            if key[K_s] or key[K_DOWN]:
                self.rect[1] -= player.vy
        self.rect[0] += self.vx
        self.rect[1] += self.vy
        screen.blit(self.display,(self.rect[0],self.rect[1]))
        
    def update(self,cx,cy,enemyArrows,enemyList,key):
        if self.kind == 'Spell' or self.kind == 'Arrow':
            for enemy in enemyList:
                if self.rect.colliderect(enemy.rect):
                    player.bullets.remove(self)
                    enemy.health -= player.damage
            if -50<= self.x <= 1074 and -50<= self.y <= 750:
                self.speed(key)
            else:
                group.remove(self)
        elif self.kind == 'BigBullet':
            for enemy in enemyList:
                if self.rect.colliderect(enemy.rect):
                    player.bullets.remove(self)
                    enemy.health -= player.damage*self.rect[2]
            if -50<= self.x <= 1074 and -50<= self.y <= 750:
                self.speed(key)
            else:
                group.remove(self)
        else:
            if self.rect.colliderect(player.rect):
                enemyArrows.remove(self)
                player.projectileHit = True
            elif -50<= self.x <= 1074 and -50<= self.y <= 750:
                self.speed(key)
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
        infoSurface.blit(itemStatsFont.render('Damage: %s' % (item.damage),True,(255,255,255)),(5,30))
    else:
        infoSurface.blit(itemStatsFont.render('Defense: %s' % (int(item.defense*100)),True,(255,255,255)),(5,30))
        print(item.defense)
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

def drawInventorySlots(inventRects,player,mx,my,click,infoSurface):
    for y in range(3):
        for x in range(len(player.inventory[y])):
            screen.blit(player.inventory[y][x].image,(inventRects[y][x][0],inventRects[y][x][1]))
        for rect in inventRects[y]:
            if rect.collidepoint(mx,my) and inventRects[y].index(rect) < len(player.inventory[y]):
                drawInventoryStats(infoSurface,mx-200,my-100,player.inventory[y][inventRects[y].index(rect)],y) #200,100 is the dimensions of the infoSurf
                if click:
                    changeGear(player,player.inventory[y][inventRects[y].index(rect)],y)
        if equippedRect[y].collidepoint(mx,my):
            if y == 0:
                drawInventoryStats(infoSurface,mx-200,my-100,player.currentWeapon,y)
            elif y == 1:
                drawInventoryStats(infoSurface,mx-200,my-100,player.currentArmour,y)
            elif y == 2:
                drawInventoryStats(infoSurface,mx-200,my-100,player.currentBoots,y)

def draw_inventory(player,pic,inventRects,click,mx,my,infoSurface,alphaSurf):
    drawInventoryBase(alphaSurf,pic,player)
    drawInventorySlots(inventRects,player,mx,my,click,infoSurface)

def drawMap(backPic,player,pos):
    screen.fill((0,0,0))
    screen.blit(transform.scale(backPic,(900,600)),(screen.get_width()//2-450,screen.get_height()//2-270))
    screen.blit(player.mapFog,(screen.get_width()//2-450,screen.get_height()//2-270))
    x = (player.x-back_x)/backPic.get_width()*900
    y = (player.y-back_y)/backPic.get_height()*600
    screen.blit(transform.scale(player.animations[0][int(pos)],(20,30)),(int(x)+screen.get_width()//2-460,int(y)+screen.get_height()//2-285))

def drawSkillMenu(skillPic,player):
    screen.fill((0,0,0))
    screen.blit(skillPic,(60,75))

def wallCol(img,x,y,back_x,back_y):
    if 0<=x<=screen.get_width() and 0<=y<=screen.get_height():
        if img.get_at((int(-back_x+x),int(-back_y+y))) == (255,0,0):
            return True
        else:
            return False
        
def tabs(player,pic,inventRects,click,mx,my,infoSurface,alphaSurf,tabMode,backPic,skillMenu,pos):
    if tabMode == 0:
        draw_inventory(player,pic,inventRects,click,mx,my,infoSurface,alphaSurf)
    elif tabMode == 1:
        drawMap(backPic,player,pos)
    elif tabMode == 2:
        drawSkillMenu(skillMenu,player)
    draw.rect(screen,(255,255,255),(10,10,1000,60))

def knockBack(x,y,power,angle): #NOT DONE YET
    x += power*cos(radians(angle))
    y += power*sin(radians(angle))
    return x,y

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

#===========================================================================================================================================#

running =True
screen = display.set_mode((1024,700))
clock = time.Clock()
click = False

#=========== Background ============#
'''
Loads the background map and creates the x and y variables used for to offset the background for movement
'''

back = image.load('Art\Backgrounds\Background.jpg')
back_mask = image.load('Art\Backgrounds\BackgroundMASK.png')
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
textbox3 = image.load('Art\Misc\Textbox3.png').convert() #ADDED THIS
textbox3.set_colorkey((255,255,255)) #ADDED THIS
backRect = Rect(500,670,24,10)
choiceRects = []
for i in range(3):
    choiceRects.append(Rect(3+340*i,185,300,450))
#===================================#

#===================================#

#============= Music ===============#
mixer.music.load('Song.mp3')
#===================================#

#========= Object creations =========#

#===================================#
#======================================= Variables ==============================#
#========== Surfaces ==========#
infoSurface = Surface((200,100),SRCALPHA)
alphaSurf = Surface((screen.get_width(),screen.get_height()),SRCALPHA)
    
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
for i in range(100):
    enemies.append(Enemy(100,choice(['Charger','Archer','Theif','Monster','Flying','Mage'])))

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
#==================#

#==============================#

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

titlePics = [transform.scale(image.load('Art\Player\Knight\Player00.png'),(100,200)),transform.scale(image.load('Art\Player\Wizard\Player00.png'),(100,200)),transform.scale(image.load('Art\Player\Archer\Player00.png'),(100,200))]
                                                       
#======================#

mode = 0 # 0 = menu, 1 = game, 2 = inventory, 3 = pause, 4 = save, 5 = shop
titleMode = 0 #ADDED THIS
tabMode = 0

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
            if e.key == K_z:
                if mode == 1:
                    mode = 5
                    shopArmour = []
                    for armour in generateItems(player,armourFile,11):
                        if player.kind == 'Knight':
                            shopArmour.append(Armour(armour,'Good Stuffs',gauss(0.1+player.level/20,0.05),'Art\Armour\Knight\Armour%d.png' % (randint(0,5)),'Armour'))
                        if player.kind == 'Wizard':
                            shopArmour.append(Armour(armour,'Good Stuffs',gauss(0.1+player.level/20,0.05),'Art\Armour\Knight\Armour%d.png' % (randint(0,5)),'Armour'))
                        if player.kind == 'Archer':
                            shopArmour.append(Armour(armour,'Good Stuffs',gauss(0.1+player.level/20,0.05),'Art\Armour\Knight\Armour%d.png' % (randint(0,5)),'Armour'))
                    shopWeapons = []
                    for weapon in generateItems(player,weaponFile,11):
                        if player.kind == 'Knight':
                            shopWeapons.append(Weapons(weapon,'Good Stuffs',gauss(10+5*player.level,3),'Art\Weapons\Swords\Sword%d.png' % (randint(1,11)),1,'Sword'))
                        if player.kind == 'Wizard':
                            shopWeapons.append(Weapons(weapon,'Good Stuffs',gauss(10+5*player.level/20,3),'Art\Weapons\Staffs\Staff%d.png' % (randint(1,16)),1,'Staff'))
                        if player.kind == 'Archer':
                            shopWeapons.append(Weapons(weapon,'Good Stuffs',gauss(10+5*player.level/20,3),'Art\Weapons\Bows\Bow%d.png' % (randint(0,14)),1,'Bow'))
                    shopBoots = []
                    for boot in generateItems(player,bootsFile,11):
                        shopBoots.append(Boots(boot,'Good Stuffs',gauss(0.03+player.level/20,0.02),'Art\Boots\Boot%d.png' % (randint(0,2)),'Boots'))
                elif mode == 5:
                    mode = 1
            if e.key == K_q:
                if mode == 2:
                    if tabMode != 2:
                        tabMode += 1
                    else:
                        tabMode = 0
            if e.key == K_e:
                if mode == 2:
                    if tabMode != 0:
                        tabMode -= 1
                    else:
                        tabMode = 2
                
        if e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                click = True
            if e.button == 3:
                rclick = True
        elif e.type == QUIT:      
            running = False

    kb = key.get_pressed()
    mx,my = mouse.get_pos()
    mb = mouse.get_pressed()

    if mode == 0: #CHANGED THIS
        if mixer.music.get_busy() == 0:
            mixer.music.play()
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

        if titleMode == 0:
            screen.blit(textbox2,(300,175))
            screen.blit(titleMenu,(335,180))

            for rect in range(len(titleRects)):
                if titleRects[rect].collidepoint(mx,my):
                    screen.blit(fire[int(firePos)],(titleRects[rect][0]+50,titleRects[rect][1]-20))
                    screen.blit(fire[int(firePos)],(titleRects[rect][0]+265,titleRects[rect][1]-20))
                    if click:
                        if rect == 0:
                            titleMode = 1
                        elif rect == 1:
                            print('hi;')
                        elif rect == 2:
                            print('Nope')
                        elif rect == 3:
                            running = False
        elif titleMode == 1:
            for x in range(3):
                screen.blit(textbox3,(choiceRects[x][0],choiceRects[x][1]))
                screen.blit(titlePics[x],(choiceRects[x][0]+175-titlePics[x].get_width()/2,choiceRects[x][1]+170-titlePics[x].get_height()/2))
            if choiceRects[0].collidepoint(mx,my) and click:
                titleMode = 0
                mode = 1
                #knight
                #health, stamina, mana, inventory, currentWeapon, currentArmour, currentBoots, money, kind, damage, defense, hotbar
                player = Player(100,100,20,[[],[],[]],Weapons('Rusty Sword','A REALLY bad sword',5,'Art\Weapons\swords\sword1.png',1,'Sword'),Armour('Bob2','Bob2',0.01,'Art\Armour\Knight\Armour0.png','Armour'),Boots('Base','FaNcY',0.01,'Art\Boots\Boot0.png','Boots'),100000,'Knight',10,0.1,["Heal","Fire","Ring"])
                back_x,back_y = 0,0
                mixer.music.stop()
                
            elif choiceRects[1].collidepoint(mx,my) and click:
                titleMode = 0
                mode = 1
                #Wizard
                #health, stamina, mana, inventory, currentWeapon, currentArmour, currentBoots, money, kind, damage, defense, hotbar
                player = Player(50,100,20,[[],[],[]],Weapons('Old Staff','A REALLY bad staff',5,'Art\Weapons\Staffs\staff1.png',1,'Staff'),Armour('Bob2','Bob2',0.10,'Art\Armour\Knight\Armour0.png','Armour'),Boots('Base','FaNcY',0.01,'Art\Boots\Boot0.png','Boots'),100000,'Wizard',10,0.1,["Sniper","Fire","Charge"])
                back_x,back_y = 0,0
                mixer.music.stop()
                
            elif choiceRects[2].collidepoint(mx,my) and click:
                titleMode = 0
                mode = 1
                #Archer
                #health, stamina, mana, inventory, currentWeapon, currentArmour, currentBoots, money, kind, damage, defense, hotbar
                player = Player(50,100,20,[[],[],[]],Weapons('Old Bow','A REALLY bad bow',5,'Art\Weapons\Bows\Bow0.png',1,'Bow'),Armour('Bob2','Bob2',0.10,'Art\Armour\Knight\Armour0.png','Armour'),Boots('Base','FaNcY',0.01,'Art\Boots\Boot0.png','Boots'),100000,'Archer',10,0.1,["Sniper","Barrage","ForestGump"])
                back_x,back_y = 0,0
                mixer.music.stop()
                
            draw.rect(screen,(255,255,255),backRect)
            if backRect.collidepoint(mx,my) and click:
                titleMode = 0
        
    elif mode == 2:
        tabs(player,inventoryPic,inventRects,click,mx,my,infoSurface,alphaSurf,tabMode,back,skillMenu,mapPos)
        if mapPos >= len(player.animations[0])-1:
            mapPos = 0
        else:
            mapPos += 0.1
    elif mode == 3:
        mode = pausescreen(alphaSurf,screen.copy(),pausePic,savePic,saves)
            
    elif mode == 4:
        mode = savescreen(screen.copy(),savePic,saves)

    elif mode == 5:
        if player.x<screen.get_width()/3:
            player.money = drawShop(shopFont,click,mx,my,player.money,shopPic,shopBoots)
        elif player.x>2*screen.get_width()/3:
            player.money = drawShop(shopFont,click,mx,my,player.money,shopPic,shopWeapons)
        else:
            player.money = drawShop(shopFont,click,mx,my,player.money,shopPic,shopArmour)
        
    else:

#======================================================================== Map Movement =============================================================================#
        '''
        The camera is centered on the player until the player moves to the edge of the map. At this point the character moves freely. When the character returns to
        the middle (vertically and/or horizontallly) the camera keeps the player in the center
        '''
        
        directions = {'Down': [kb[K_DOWN],kb[K_s]],'Left':[kb[K_LEFT],kb[K_a]],'Right':[kb[K_RIGHT],kb[K_d]],'Up':[kb[K_UP],kb[K_w]]}

#============================== Up/Down/Left/Right ===============================#
        '''
        Moves either the map or player (player moves if pmovex/y is True). Also turns pmovex/y False if the player returned to the center (the vertical and/or horizontal
        center). Also stops the player from going past the edge of the screen.
        '''
        player.moving = False
        
        if 1 in directions['Right'] and 1 not in directions['Left']:
            player.movepos = 2
            if wallCol(back_mask,player.rect[0]+player.rect[2]+player.vx,player.rect[1]+player.rect[3],back_x,back_y) == False and wallCol(back_mask,player.rect[0]+player.rect[2]+player.vx,player.rect[1],back_x,back_y) == False:
                player.moving = True
                if player.pmovex:
                    if player.x+player.vx <= screen.get_width():
                        player.x += player.vx
                    if 495 <= player.x <= 505:
                        player.pmovex = False
                else:
                    back_x -= player.vx
                if back_x<-back.get_width()+screen.get_width():
                    player.pmovex = True
                    back_x = -back.get_width()+screen.get_width()
                
        if 1 in directions['Left'] and 1 not in directions['Right']:
            player.movepos = 1
            if wallCol(back_mask,player.rect[0]-player.vx,player.rect[1]+player.rect[3],back_x,back_y) == False and wallCol(back_mask,player.rect[0]-player.vx,player.rect[1],back_x,back_y) == False:
                player.moving = True
                if player.pmovex:
                    if player.x-player.vx>=0:
                        player.x -= player.vx
                    if 495<= player.x <= 505:
                        player.pmovex = False
                else:
                    back_x += player.vx
                if back_x>0:
                    player.pmovex = True
                    back_x = 0
                
        if 1 in directions['Up'] and 1 not in directions['Down']:
            player.movepos = 3
            if wallCol(back_mask,player.rect[0],player.rect[1]-player.vy,back_x,back_y) == False and wallCol(back_mask,player.rect[0]+player.rect[2],player.rect[1]-player.vy,back_x,back_y) == False:
                player.moving = True
                if player.pmovey:
                    if player.y-player.vy >= 0:
                        player.y -= player.vy
                    if 335<= player.y <= 345:
                        player.pmovey = False
                else:
                    back_y += player.vy
                if back_y>0:
                    player.pmovey = True
                    back_y = 0
                    
        if 1 in directions['Down'] and 1 not in directions['Up']:
            player.movepos = 0
            if wallCol(back_mask,player.rect[0],player.rect[1]+player.rect[3]+player.vy,back_x,back_y) == False and wallCol(back_mask,player.rect[0]+player.rect[2],player.rect[1]+player.rect[3]+player.vy,back_x,back_y) == False:
                player.moving = True
                if player.pmovey:
                    if player.y+player.vy <= 615-player.rect[3]/2:
                        player.y += player.vy
                    if 335 <= player.y <= 345:
                        player.pmovey = False
                else:
                    back_y -= player.vy
                if back_y<-back.get_height()+screen.get_height():
                    player.pmovey = True
                    back_y = -back.get_height()+screen.get_height()

    #===================================================================================#

        screen.blit(back,(back_x,back_y)) #Blits updated map onto screen

#====================================================================================================================================================================#

    #============= Updates ============#
        '''
        Update all sprites (their movement, stats, etc.)
        '''
        player.mana = 100
        for enemy in enemies:
            if enemy.kind == 'Archer':
                if 30<=enemy.rect[0]<=900 and 30<=enemy.rect[1]<=600 and randint(1,50) == 1:
                    enemy.createProjectile()
            enemy.update(back_x,back_y,enemies,kb,enemies)  #updates enemies
        player.update(click,mx,my,kb,hud,skillBarPic,enemies,back_x,back_y,directions,back) #Updates player
    #==================================#
    click = False
    rclick = False
    display.flip()
    clock.tick(30)
quit()
