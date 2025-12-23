import pygame
import sys
import os
import math

pygame.init()

# --- 기본 설정 ---
SCALE = 2
GRID_SIZE = 32 * SCALE
GRID_WIDTH = 10
GRID_HEIGHT = 10

GRID_PIXEL_WIDTH = GRID_WIDTH * GRID_SIZE
GRID_PIXEL_HEIGHT = GRID_HEIGHT * GRID_SIZE

INFO_PANEL_WIDTH = 200

SCREEN_WIDTH = (GRID_PIXEL_WIDTH + INFO_PANEL_WIDTH)
SCREEN_HEIGHT = GRID_PIXEL_HEIGHT

BG_COLOR = (20, 20, 20)
GRID_LINE_COLOR = (80, 80, 80)
TILE_COLOR = (60, 60, 60)
P1_COLOR = (200, 80, 80)
P2_COLOR = (80, 120, 220)
PANEL_BG_COLOR = (25, 25, 40)
TEXT_COLOR = (230, 230, 230)

EFFECT_DUR = 30

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE,pygame.SRCALPHA)
pygame.display.set_caption("Grid Arena")

clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 16)
cool_font = pygame.font.SysFont("consolas", 14, bold=True)
title_font = pygame.font.SysFont("consolas", 48)

BASE_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(BASE_DIR, "src")

p1=None
p2=None
turn=None
objects = []
effects = []
structures = []

def loadImg(dir,scale=1,flip=False):
    return pygame.transform.flip(pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR,dir)),(32*scale,32*scale)),True,False) if flip else pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR,dir)),(32*scale,32*scale))

SKILLS = {"sword":{
        "passive": loadImg("icons/sword/passive.png",SCALE//2),
        "move": loadImg("icons/sword/move.png",SCALE//2),
        "1": loadImg("icons/sword/skill1.png",SCALE//2),
        "2": loadImg("icons/sword/skill2.png",SCALE//2),
        "3": loadImg("icons/sword/skill3.png",SCALE//2)},
    "engineer":{
        "passive": loadImg("icons/engineer/passive.png",SCALE//2),
        "move": loadImg("icons/engineer/move.png",SCALE//2),
        "1": loadImg("icons/engineer/skill1.png",SCALE//2),
        "2": loadImg("icons/engineer/skill2.png",SCALE//2),
        "3": loadImg("icons/engineer/skill3.png",SCALE//2)},
    "teleporter":{
        "passive": loadImg("icons/teleporter/passive.png",SCALE//2),
        "move": loadImg("icons/teleporter/move.png",SCALE//2),
        "1": loadImg("icons/teleporter/skill1.png",SCALE//2),
        "2": loadImg("icons/teleporter/skill2.png",SCALE//2),
        "3": loadImg("icons/teleporter/skill3.png",SCALE//2)},}

CHARS = {"sword":[loadImg("chars/sword.png",SCALE),loadImg("chars/sword2.png",SCALE)],
         "engineer":[loadImg("chars/engineer.png",SCALE),loadImg("chars/engineer2.png",SCALE)],
         "teleporter":[loadImg("chars/teleporter.png",SCALE),loadImg("chars/teleporter2.png",SCALE)]}

ADJ= [(0,1),(0,-1),(1,0),(-1,0)]
DIAG = [(1,1),(1,-1),(-1,1),(-1,-1)]
NEAR = ADJ + DIAG
SELF = [(0,0)]
ALL = []
for i in range(-9,10):
    for j in range(-9,10):
        ALL.append((i,j))

def AREA(t,n=1):
    area=[]
    if t=="adj":
        for i in range(n):
            area+=list(map(lambda x:(x[0]*(i+1),x[1]*(i+1)),ADJ))
    elif t=="diag":
        for i in range(n):
            area+=list(map(lambda x:(x[0]*(i+1),x[1]*(i+1)),DIAG))
    elif t=="near":
        for i in range(n):
            area+=list(map(lambda x:(x[0]*(i+1),x[1]*(i+1)),NEAR))
    return area


FACE = {"0/-1":0,"-1/-1":1,"-1/0":2,"-1/1":3,"0/1":4,"1/1":5,"1/0":6,"1/-1":7,"0/0":-1}
XY = {0: "0/-1",1: "-1/-1",2: "-1/0",3: "-1/1",4: "0/1",5: "1/1",6: "1/0",7: "1/-1",-1:"0/0"}


EFFECTS = {"sword_adj": {"body":loadImg("effects/sword_adj.png",SCALE),
                         "left": loadImg("effects/sword_adj_left.png",SCALE),
                         "right": loadImg("effects/sword_adj_left.png",SCALE,True)},
           "sword_diag": {"body":loadImg("effects/sword_diag.png",SCALE),
                          "left": loadImg("effects/sword_diag_left.png",SCALE),
                          "right": loadImg("effects/sword_diag_left.png",SCALE,True)},
            "sword_strike":loadImg("effects/sword_strike.png",SCALE),
            "energy_ball":loadImg("effects/energy_ball.png",SCALE),
            "slash":loadImg("effects/slash.png",SCALE)}

STRUCTURES = {"turret":loadImg("structures/turret.png",SCALE)}

STATS = {"stun":loadImg("stat/stun.png",SCALE),
         "block":loadImg("stat/block.png",SCALE),
         "void":loadImg("stat/void.png",SCALE)}

D = {"sword":{"maxhp":100,"cool":[2,2,4,7],"passive":"Bloodthirst","skill":["Walk/Dash","Swing","Aura Blade","Sword Strike"],"move":4,"tiles":{"move":AREA("adj",2),"s1":NEAR,"s2":NEAR,"s3":ADJ}},
     "engineer":{"maxhp":100,"cool":[2,1,4,7],"passive":"Repair","skill":["Walk","Energy Ball","Turret","Overheat"],"move":3,"tiles":{"move":ADJ,"s1":NEAR,"s2":NEAR,"s3":SELF}},
     "teleporter":{"maxhp":50,"cool":[2,2,10,7],"passive":"Void","skill":["Blink","Slash","Shadow","Gate to Void"],"move":1,"tiles":{"move":AREA("diag",9),"s1":AREA("near",3),"s2":SELF,"s3":ALL}},
     "sword":{"maxhp":100,"cool":[2,2,4,7],"passive":"Bloodthirst","skill":["Walk","Swing","Aura Blade","Sword Strike"],"move":4,"tiles":{"move":AREA("adj",2),"s1":NEAR,"s2":NEAR,"s3":ADJ}},
     "sword":{"maxhp":100,"cool":[2,2,4,7],"passive":"Bloodthirst","skill":["Walk","Swing","Aura Blade","Sword Strike"],"move":4,"tiles":{"move":AREA("adj",2),"s1":NEAR,"s2":NEAR,"s3":ADJ}},}

class player:
    def __init__(self,xy,c,p):
        self.pos = [xy]
        self.c = c
        self.maxhp = D[c]["maxhp"]
        self.hp = self.maxhp
        self.maxcool = D[c]["cool"]
        self.cool = [0,0,0,self.maxcool[3]]
        self.passive = D[c]['passive']
        self.skill = D[c]['skill']
        self.face = 0
        self.img = CHARS[c][0]
        self.tiles = D[c]['tiles']
        self.mode = ''
        self.rect = [xy[0],xy[1],GRID_SIZE,GRID_SIZE]
        self.maxmove=D[c]['move']
        self.p = p
        self.stat = {"charge":0,"stun":0,"block":0,"void":0}
        self.setting()

    def setting(self):
        pass

    def addStat(self,stat,n):
        self.stat[stat] += n

    def coolStep(self):
        for i in range(len(self.cool)):
            if self.cool[i] > 0:
                self.cool[i]-=1

    def update(self):
        self.coolStep()
        for k in self.stat.keys():
            if self.stat[k] > 0:
                self.stat[k]-=1
                if self.stat[k] == 0:
                    self.checkStat(k)

    def checkStat(self,key):
        if key=="charge":
            pass


    def changeMode(self,mode):
        if self.mode != mode:
            self.mode = mode
        else:
            self.mode = ''

    def draw(self,surface):
        img,rot_rect = rotCenter(self.img, scaleXY(self.pos[0],32), self.face*45)
        surface.blit(img, rot_rect)

        for s in self.stat.keys():
            if self.stat[s] > 0:
                surface.blit(STATS[s],scaleXY(self.pos[0]))

        if self.mode!="":
            for tile in self.tiles[self.mode]:
                xy=scaleXY([self.pos[0][0]+tile[0],self.pos[0][1]+tile[1]])
                pygame.draw.rect(surface,(20,200,20),(xy[0],xy[1],GRID_SIZE,GRID_SIZE),width=1)

    def hurt(self,damage):
        if self.stat["block"] > 0:
            self.stat["block"]-=1
        else:
            self.hp -= damage

    def move(self,mx,my):
        for tile in self.tiles["move"]:
            x,y=tile[0]+self.pos[0][0], tile[1]+self.pos[0][1]
            if (x,y)==(mx,my) and (x,y)!=getOpponent(self.p).pos[0]:
                for s in structures:
                    if (x,y)==s.pos:
                        return
                self.face = xy2face(tile)

                self.cool[0]-=1
                if self.cool[0]<=-self.maxmove or self.stat["void"] > 0:
                    self.cool[0]=self.maxcool[0]
                self.pos[0]=(x,y)

                self.mode=''
                return True

    def skill1(self,mx,my):
        for tile in self.tiles["s1"]:
            x,y=tile[0]+self.pos[0][0], tile[1]+self.pos[0][1]
            if (x,y) == (mx,my):
                if tile!=(0,0):
                    self.face = xy2face(tile)
                self.cool[1]=self.maxcool[1]
                self.skillAction1(x,y)
                self.mode=''
                return True

    def skill2(self,mx,my):
        for tile in self.tiles["s2"]:
            x,y=tile[0]+self.pos[0][0], tile[1]+self.pos[0][1]
            if (x,y) == (mx,my):
                if tile!=(0,0):
                    self.face = xy2face(tile)
                self.cool[2]=self.maxcool[2]
                self.skillAction2(x,y)
                self.mode=''
                return True

    def skill3(self,mx,my):
        for tile in self.tiles["s3"]:
            x,y=tile[0]+self.pos[0][0], tile[1]+self.pos[0][1]
            if (x,y) == (mx,my):
                if tile!=(0,0):
                    self.face = xy2face(tile)
                self.cool[3]=self.maxcool[3]
                self.skillAction3(x,y)
                self.mode=''
                return True

    def skillAction1(self,x,y):
        pass

    def skillAction2(self,x,y):
        pass
    def skillAction3(self,x,y):
        pass

class projectile:
    def __init__(self,x,y,face,life=None,owner=None,wait=False):
        self.pos=(x,y)
        self.face=face
        self.life = life
        self.owner = owner
        self.wait = wait
        self.setting()

    def setting(self):
        self.damage = 10
        self.speed = 1
        self.hitbox=[self.pos]
        self.img = EFFECTS["img"]

    def update(self):
        if self.life:
            self.life-=1
            if self.life<=0:
                return

        if self.wait:
            self.wait=False
        else:
            for i in range(self.speed):
                if self.checkHit():
                    break

                self.pos = getPos(self.pos,self.face)
                for i in range(len(self.hitbox)):
                    self.hitbox[i]=getPos(self.hitbox[i],self.face)

        if self.life is None or self.life > 0 or self.wait:
            self.checkHit()

    def hit(self,p):
        getSelf(p).hurt(self.damage)

    def checkHit(self):
        ishit = False
        if self.owner:
            if getOpponent(self.owner).pos[0] in self.hitbox:
                self.hit(3-self.owner)
                self.life=0
                ishit=True
        else:
            if getSelf(1).pos[0] in self.hitbox:
                self.hit(1)
                self.life=0
                ishit=True
            if getSelf(2).pos[0] in self.hitbox:
                self.hit(2)
                self.life=0
                ishit=True

        for i in range(len(structures)-1,-1,-1):
            if structures[i].pos in self.hitbox:
                structures[i].hit(self.damage)
                self.life=0
                ishit=True
        return ishit


    def draw(self,surface):
        body,body_rect = rotCenter(self.img, scaleXY(self.pos,32), self.face*45)
        surface.blit(body, body_rect)

class effect:
    def __init__(self,x,y,face,life,owner):
        self.pos=(x,y)
        self.face=face
        self.life = life
        self.owner = owner
        self.setting()

    def setting(self):
        self.hitbox=[self.pos]
        self.img = EFFECTS["img"]
        self.damage = 10

    def update(self):
        self.life-=1

    def draw(self,surface):
        body,body_rect = rotCenter(self.img, scaleXY(self.pos,32), self.face*45)
        surface.blit(body, body_rect)

    def checkHit(self):
        if getOpponent(self.owner).pos[0] in self.hitbox:
            getOpponent(self.owner).hurt(self.damage)

        for i in range(len(structures)-1,-1,-1):
            if structures[i].pos in self.hitbox:
                structures[i].hit(self.damage)

class structure:
    def __init__(self,x,y,face,health,owner=None):
        self.pos=(x,y)
        self.face=face
        self.health = health
        self.owner=owner
        self.setting()

    def setting(self):
        self.img = STRUCTURES["img"]

    def update(self):
        self.health-=1

    def draw(self,surface):
        # body,body_rect = rotCenter(self.img, scaleXY(self.pos,32), self.face*45)
        # surface.blit(body, body_rect)
        surface.blit(self.img,scaleXY(self.pos,GRID_SIZE))

        health_text = font.render(str(self.health), True, (255, 255, 255))
        xy = scaleXY(self.pos)
        ix = xy[0] + GRID_SIZE//2 - health_text.get_width()//2
        iy = xy[1] + GRID_SIZE//2 - health_text.get_height()//2
        surface.blit(health_text, (ix,iy))

    def hit(self,damage):
        self.health = min(self.health - damage,20)


class pSword(player):
    def move(self,mx,my):
        for tile in self.tiles["move"]:
            x,y=tile[0]+self.pos[0][0], tile[1]+self.pos[0][1]
            if (x,y)==(mx,my) and (x,y)!=getOpponent(self.p).pos[0]:
                for s in structures:
                    if (x,y)==s.pos:
                        return
                self.face = xy2face(tile)

                if distance((x,y),self.pos[0])==2:
                    self.cool[0]=3
                else:
                    self.cool[0]-=1
                    if self.cool[0] <= -self.maxmove or self.stat["void"] > 0:
                        self.cool[0]=self.maxcool[0]

                self.pos[0]=(x,y)

                self.mode=''
                return True

    def skillAction1(self,x,y):
        effects.append(sword_e(x,y,self.face,EFFECT_DUR,self.p))
        effects[-1].checkHit()

    def skillAction2(self,x,y):
        objects.append(sword_p(x,y,self.face,owner = self.p,wait=True))

    def skillAction3(self,x,y):
        effects.append(strike(x,y,self.face,100,self.p))
        effects[-1].checkHit()

class pEngineer(player):
    def setting(self):
        self.turret_health = 20
        self.overheat = 0

    def skillAction1(self,x,y):
        objects.append(energy_ball(x,y,self.face,owner = self.p,wait = True))
        if self.overheat > 0:
            self.overheat-=1
            if self.overheat <= 0:
                self.img = CHARS["engineer"][0]
            for i in range(len(structures)):
                if structures[i].owner == self.p:
                    for xy in NEAR:
                        objects.append(energy_ball(structures[i].pos[0]+xy[0],structures[i].pos[1]+xy[1],xy2face(xy),owner=self.p,wait=True))
        else:
            for s in structures:
                if s.owner == self.p:
                    xy=getPos(s.pos,self.face)
                    objects.append(energy_ball(xy[0],xy[1],self.face,owner = self.p,wait = True))

    def skillAction2(self,x,y):
        turrets = []
        for i in range(len(structures)):
            if structures[i].owner == self.p:
                turrets.append(i)
        if len(turrets) >= 2:
            del structures[turrets[0]]
        structures.append(turret(x,y,self.face,self.turret_health,self.p))

    def skillAction3(self,x,y):
        self.overheat = 2
        self.img = CHARS["engineer"][1]

class pTeleporter(player):
    def skill1(self,mx,my):
        for tile in self.tiles["s1"]:
            x,y=tile[0]+self.pos[0][0], tile[1]+self.pos[0][1]
            if (x,y) == (mx,my) and (x,y) != getOpponent(self.p).pos[0]:
                for s in structures:
                    if (x,y)==s.pos:
                        return
                if tile!=(0,0):
                    self.face = xy2face(tile)
                self.cool[1]=self.maxcool[1]
                self.skillAction1(x,y)
                self.mode=''
                return True

    def skill3(self,mx,my):
        for tile in self.tiles["s3"]:
            x,y=tile[0]+self.pos[0][0], tile[1]+self.pos[0][1]
            if (x,y)==(mx,my) and (x,y) != getOpponent(self.p).pos[0]:
                for s in structures:
                    if (x,y)==s.pos:
                        return
                self.cool[3]=self.maxcool[3]
                self.skillAction3(x,y)
                self.mode=''
                self.img=CHARS["teleporter"][1]
                return True

    def skillAction1(self,x,y):
        self.pos[0]=(x,y)
        xy=getPos(self.pos[0],self.face)
        if self.stat["void"] ==0:
            effects.append(slash(xy[0],xy[1],self.face,EFFECT_DUR,self.p))
            effects[-1].checkHit()
        else:
            effects.append(void_slash(self.pos[0][0],self.pos[0][1],self.face,EFFECT_DUR,self.p))
            effects[-1].checkHit()


    def skillAction2(self,x,y):
        self.addStat("block",2)

    def skillAction3(self,x,y):
        self.pos[0] = (x,y)
        getOpponent(self.p).addStat("void",2)
        self.addStat("void",3)
            
    def update(self):
        self.coolStep()
        for k in self.stat.keys():
            if self.stat[k] > 0:
                self.stat[k]-=1
                if self.stat[k] == 0:
                    self.checkStat(k)

        if self.stat["void"] > 0:
            self.img=CHARS["teleporter"][1]
        else:
            self.img=CHARS["teleporter"][0]

    def hurt(self,damage):
        if self.stat["block"] > 0:
            self.stat["block"]-=1
        elif self.stat["void"] > 0:
            self.hp -= damage//2
        else:
            self.hp -= damage

class sword_p(projectile):
    def setting(self):
        self.damage = 10
        self.speed = 2
        center = backtrack(self.pos,self.face)
        self.hitbox=[self.pos,getPos(center,addFace(self.face,1)),getPos(center,addFace(self.face,-1))]
        self.img = EFFECTS["sword_adj"] if self.face % 2 == 0 else EFFECTS["sword_diag"]

    def draw(self,surface):
        body,body_rect = rotCenter(self.img["body"], scaleXY(self.pos,32), self.face*45 if self.face % 2 == 0 else addFace(self.face,-1)*45)
        surface.blit(body, body_rect)

        pos = [self.hitbox[1],self.hitbox[2]]

        left,left_rect = rotCenter(self.img["left"], scaleXY(pos[0],32), self.face*45 if self.face % 2 == 0 else addFace(self.face,-1)*45)
        right,right_rect = rotCenter(self.img["right"], scaleXY(pos[1],32), self.face*45 if self.face % 2 == 0 else addFace(self.face,1)*45)
        surface.blit(left, left_rect)
        surface.blit(right, right_rect)

    def hit(self,p):
        getSelf(p).hurt(self.damage)
        getSelf(self.owner).coolStep()

class sword_e(effect):
    def setting(self):
        self.damage = 10
        center = backtrack(self.pos,self.face)
        self.hitbox=[self.pos,getPos(center,addFace(self.face,1)),getPos(center,addFace(self.face,-1))]
        self.img = EFFECTS["sword_adj"] if self.face % 2 == 0 else EFFECTS["sword_diag"]

    def draw(self,surface):
        body,body_rect = rotCenter(self.img["body"], scaleXY(self.pos,32), self.face*45 if self.face % 2 == 0 else addFace(self.face,-1)*45)
        surface.blit(body, body_rect)

        pos = (self.hitbox[1],self.hitbox[2])

        left,left_rect = rotCenter(self.img["left"], scaleXY(pos[0],32), self.face*45 if self.face % 2 == 0 else addFace(self.face,-1)*45)
        right,right_rect = rotCenter(self.img["right"], scaleXY(pos[1],32), self.face*45 if self.face % 2 == 0 else addFace(self.face,1)*45)
        surface.blit(left, left_rect)
        surface.blit(right, right_rect)

    def checkHit(self):
        if getOpponent(self.owner).pos[0] in self.hitbox:
            getOpponent(self.owner).hurt(self.damage)
            getSelf(self.owner).coolStep()

        for i in range(len(structures)-1,-1,-1):
            if structures[i].pos in self.hitbox:
                structures[i].hit(self.damage)
                getSelf(self.owner).coolStep()

class strike(effect):
    def setting(self):
        self.damage = 15
        self.hitbox=[self.pos]
        center = backtrack(self.pos,self.face)
        row = [getPos(center,addFace(self.face,-1)),self.pos,getPos(center,addFace(self.face,1))]
        self.hitbox_stun = row[:]
        while 0<= self.hitbox[-1][0] <= 9 and 0<= self.hitbox[-1][1] <= 9:
            self.hitbox.append(getPos(self.hitbox[-1],self.face))
            row = list(map(lambda x:getPos(x,self.face),row))
            self.hitbox_stun += row
        self.img = EFFECTS["sword_strike"]

    def draw(self,surface):
        for x,y in self.hitbox:
            img,img_rect = rotCenter(self.img, scaleXY((x,y),32), self.face*45)
            surface.blit(img, img_rect)

    def checkHit(self):
        if getOpponent(self.owner).pos[0] in self.hitbox:
            getOpponent(self.owner).hurt(self.damage)
            xy = getPos(getSelf(self.owner).pos[0],self.face)
            objects.append(sword_p(xy[0],xy[1],self.face,owner = self.owner,wait=True))
            getSelf(self.owner).coolStep()
        if getOpponent(self.owner).pos[0] in self.hitbox_stun:
            getOpponent(self.owner).addStat("stun",2)

        for i in range(len(structures)-1,-1,-1):
            if structures[i].pos in self.hitbox:
                structures[i].hit(self.damage)
                getSelf(self.owner).coolStep()

class slash(effect):
    def setting(self):
        self.damage = 10
        self.hitbox=[self.pos]
        self.img = EFFECTS["slash"]

class void_slash(effect):
    def setting(self):
        self.damage = 10
        self.hitbox=[getPos(self.pos,addFace(self.face,1)),getPos(self.pos,self.face),getPos(self.pos,addFace(self.face,-1))]
        self.img = EFFECTS["slash"]

    def draw(self,surface):
        body,body_rect = rotCenter(self.img, scaleXY(getPos(self.pos,self.face),32), self.face*45)
        surface.blit(body, body_rect)
        body,body_rect = rotCenter(self.img, scaleXY(getPos(self.pos,addFace(self.face,1)),32), self.face*45)
        surface.blit(body, body_rect)
        body,body_rect = rotCenter(self.img, scaleXY(getPos(self.pos,addFace(self.face,-1)),32), self.face*45)
        surface.blit(body, body_rect)

    def checkHit(self):
        if getOpponent(self.owner).pos[0] in self.hitbox:
            getOpponent(self.owner).hurt(self.damage+5)
            getOpponent(self.owner).addStat("void",2)
            getSelf(self.owner).addStat("void",1)
            getSelf(self.owner).cool[1] = max(getSelf(self.owner).cool[1]-1,0)
            getSelf(self.owner).hurt(-5)

        for i in range(len(structures)-1,-1,-1):
            if structures[i].pos in self.hitbox:
                structures[i].hit(self.damage+5)
                getSelf(self.owner).addStat("void",1)
                getSelf(self.owner).cool[1] = max(getSelf(self.owner).cool[1]-1,0)
                getSelf(self.owner).hurt(-5)

class energy_ball(projectile):
    def setting(self):
        self.damage = 10
        self.speed = 1
        self.hitbox=[self.pos]
        self.img = EFFECTS["energy_ball"]

    def checkHit(self):
        ishit = False
        if getOpponent(self.owner).pos[0] in self.hitbox:
            self.hit(3-self.owner)
            self.life=0
            ishit=True

        for i in range(len(structures)-1,-1,-1):
            if structures[i].pos in self.hitbox:
                if structures[i].owner == self.owner:
                    structures[i].hit(-self.damage+3)
                    getSelf(self.owner).cool[0]=0
                else:
                    structures[i].hit(self.damage)
                self.life=0
                ishit=True
        return ishit

class turret(structure):
    def setting(self):
        self.img = STRUCTURES["turret"]



def face2xy(face):
    return tuple(map(int,XY[face].split("/")))
def xy2face(xy):
    return FACE[str(0 if xy[0]==0 else 1 if xy[0]>0 else -1)+"/"+str(0 if xy[1]==0 else 1 if xy[1]>0 else -1)]
def addFace(face,x):
    return face+x-8 if face+x>7 else face+x+8 if face+x < 0 else face+x
def scaleXY(xy,scale=GRID_SIZE):
    return (xy[0]*scale,xy[1]*scale)
def getSelf(p):
    return p1 if p==1 else p2
def getOpponent(p):
    return p1 if p==2 else p2
def rotCenter(img,xy, R):
    rect = img.get_rect(center=(xy[0]+32, xy[1]+32))
    rot_img = pygame.transform.rotate(img, R)
    rot_rect = rot_img.get_rect(center=rect.center)
    rot_rect[0] += xy[0]
    rot_rect[1] += xy[1]
    return rot_img,rot_rect
def backtrack(xy,face):
    rxy = face2xy(addFace(face,4))
    center = (xy[0]+rxy[0],xy[1]+rxy[1])
    return center
def getPos(xy,face):
    return (xy[0]+face2xy(face)[0],xy[1]+face2xy(face)[1])
def distance(s,e):
    return abs(e[0]-s[0])+abs(e[1]-s[1])


def draw_skill_icon(surface, icon, x, y, name="", cd=None,active=False):
    # 아이콘
    surface.blit(icon, (x, y))

    if cd and cd>0:
        s = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(s, (0,0,0,128),(x,y,32,32))
        surface.blit(s, (0, 0))
    elif active:
        s = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(s, (200,0,0,128),(x,y,32,32))
        surface.blit(s, (0, 0))

    # 아이콘 오른쪽에 스킬 이름 표시
    if name:
        text = font.render(name, True, (230, 230, 230))
        surface.blit(text, (x + icon.get_width() + 8, y + (icon.get_height() - text.get_height()) // 2))

    # 액티브 스킬 쿨타임 숫자
    if cd is not None and cd != 0:
        cd_text = cool_font.render(str(cd), True, (255, 255, 255))
        tw, th = cd_text.get_size()
        ix = x + icon.get_width() - tw - 2
        iy = y + icon.get_height() - th - 1
        pygame.draw.rect(surface, (0, 0, 0, 180), (ix - 1, iy - 1, tw + 2, th + 2))
        surface.blit(cd_text, (ix, iy))

def draw_grid(surface):
    # 타일 채우기
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(
                x * GRID_SIZE,
                y * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE
            )
            pygame.draw.rect(surface, TILE_COLOR, rect)

    # 그리드 라인
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(
            surface,
            GRID_LINE_COLOR,
            (x * GRID_SIZE, 0),
            (x * GRID_SIZE, GRID_PIXEL_HEIGHT)
        )

    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(
            surface,
            GRID_LINE_COLOR,
            (0, y * GRID_SIZE),
            (GRID_PIXEL_WIDTH, y * GRID_SIZE)
        )

def draw_objects(surface,p1,p2):
    p1.draw(surface)
    p2.draw(surface)
    for e in effects:
        e.draw(surface)
    for o in objects:
        o.draw(surface)
    for s in structures:
        s.draw(surface)

def draw_text(surface, text, x, y, font, color=TEXT_COLOR):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))
    return img.get_rect(topleft=(x, y))

def draw_info_panel(surface, font, p1, p2,p):
    panel_rect = pygame.Rect(
        GRID_PIXEL_WIDTH, 0,
        INFO_PANEL_WIDTH, SCREEN_HEIGHT
    )
    pygame.draw.rect(surface, PANEL_BG_COLOR, panel_rect)

    padding = 8
    x = GRID_PIXEL_WIDTH + padding

    # --- P1 정보 (위) ---
    y = padding
    draw_text(surface, "[P1]", x, y, font)
    y += 24
    draw_text(surface, f"HP: {p1.hp}/{p1.maxhp}", x, y, font)

    y = 70

    draw_skill_icon(surface, SKILLS[p1.c]["passive"], x, y, p1.passive)
    y += 42

    draw_skill_icon(surface, SKILLS[p1.c]["move"], x, y, p1.skill[0]+" (Q)", p1.cool[0], p1.mode=="move")
    y += 42

    draw_skill_icon(surface, SKILLS[p1.c]["1"], x, y, p1.skill[1]+" (W)", p1.cool[1],p1.mode=="s1")
    y += 42

    draw_skill_icon(surface, SKILLS[p1.c]["2"], x, y, p1.skill[2]+" (E)", p1.cool[2],p1.mode=="s2")
    y += 42

    draw_skill_icon(surface, SKILLS[p1.c]["3"], x, y, p1.skill[3]+" (R)", p1.cool[3],p1.mode=="s3")

    # 구분선
    pygame.draw.line(
        surface,
        (80, 80, 120),
        (GRID_PIXEL_WIDTH + 4, SCREEN_HEIGHT // 2),
        (SCREEN_WIDTH - 4, SCREEN_HEIGHT // 2),
        2
    )

    # --- P2 정보 (아래) ---
    y = SCREEN_HEIGHT // 2 + padding
    draw_text(surface, "[P2]", x, y, font)
    y += 24
    draw_text(surface, f"HP: {p2.hp}/{p2.maxhp}", x, y, font)

    y = SCREEN_HEIGHT // 2 + padding + 60

    draw_skill_icon(surface, SKILLS[p2.c]["passive"], x, y, p2.passive)
    y += 42

    draw_skill_icon(surface, SKILLS[p2.c]["move"], x, y, p2.skill[0]+" (U)", p2.cool[0], p2.mode=="move")
    y += 42

    draw_skill_icon(surface, SKILLS[p2.c]["1"], x, y, p2.skill[1]+" (I)", p2.cool[1], p2.mode=="s1")
    y += 42

    draw_skill_icon(surface, SKILLS[p2.c]["2"], x, y, p2.skill[2]+" (O)", p2.cool[2], p2.mode=="s2")
    y += 42

    draw_skill_icon(surface, SKILLS[p2.c]["3"], x, y, p2.skill[3]+" (P)", p2.cool[3], p2.mode=="s3")

    pygame.draw.rect(surface,(20,200,20),(GRID_PIXEL_WIDTH+padding,6,36,20) if p==1 else ((GRID_PIXEL_WIDTH+padding,SCREEN_HEIGHT//2+6,36,20)),width=1)

def changeTurn(p,step=True):
    turn = 3-p
    if step:
        for i in range(len(objects)-1,-1,-1):
            objects[i].update()
            if objects[i].life==0:
                del objects[i]
        for i in range(len(structures)-1,-1,-1):
            structures[i].update()
            if structures[i].health<=0:
                del structures[i]
        getSelf(turn).update()
    return turn

def setChar(xy,char,p):
    if char=="sword":
        return pSword(xy,"sword",p)
    elif char=="engineer":
        return pEngineer(xy,"engineer",p)
    elif char=="teleporter":
        return pTeleporter(xy,"teleporter",p)

def charSelect():
    global running
    pygame.display.set_caption("Character Select")

    characters = list(D.keys())
    font40 = pygame.font.SysFont("consolas", 40)
    font32 = pygame.font.SysFont("consolas", 32)
    font28 = pygame.font.SysFont("consolas", 28)
    title_font = pygame.font.SysFont("consolas", 60)

    # 이미지 로드
    images = {}
    for name in characters:
        try:
            img = loadImg(f"chars/{name}.png",5)
        except:
            img = pygame.Surface((160, 160))
            img.fill((120, 120, 120))
        images[name] = img

    # 카드 사이즈 및 배치
    card_w, card_h = 160, 200      # 이름 공간 때문에 높이 증가
    gap = 50
    start_y = 180

    # 전체 가로 길이 계산
    total_width = len(characters) * (card_w + gap)

    # 카드 rects: (name, base_rect_x, y)
    cards = []
    x = 100
    for name in characters:
        cards.append((name, x, start_y))
        x += card_w + gap

    # 스크롤 변수
    scroll_x = 0
    SCROLL_SPEED = 40

    selected1 = None
    selected2 = None
    showing = None  # 설명 띄우는 대상

    # 설명 카드 영역
    info_rect = pygame.Rect(150, 460, 500, 240)

    while running:
        screen.fill((30, 30, 30))

        # 제목
        title = title_font.render("Select Characters", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))

        # --- 이미지 카드 렌더링 (좌우 스크롤 적용) ---
        for name, base_x, y in cards:
            rect = pygame.Rect(base_x + scroll_x, y, card_w, card_h)

            # 카드 영역이 화면 바깥이면 스킵해서 성능 최적화
            if rect.right < -50 or rect.left > SCREEN_WIDTH + 50:
                continue

            # 카드 배경
            pygame.draw.rect(screen, (60, 60, 60), rect, border_radius=8)
            pygame.draw.rect(screen, (150, 150, 150), rect, 2, border_radius=8)

            # 이미지
            screen.blit(images[name], (rect.x, rect.y))

            # 이름
            txt = font32.render(name.capitalize(), True, (255,255,255))
            screen.blit(txt, (rect.x + card_w//2 - txt.get_width()//2, rect.y + 165))

            # 선택 표시
            if selected1 == name:
                mark = font32.render("P1", True, (255,100,100))
                screen.blit(mark, (rect.x, rect.y - 30))
            if selected2 == name:
                mark = font32.render("P2", True, (100,200,255))
                screen.blit(mark, (rect.x + 60, rect.y - 30))

        # --- 설명 카드 렌더링 ---
        if showing is not None:
            pygame.draw.rect(screen, (40, 40, 40), info_rect, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), info_rect, 3, border_radius=10)

            x = info_rect.x + 20
            y = info_rect.y + 20

            screen.blit(font40.render(showing.capitalize(), True, (255,255,255)), (x, y))
            y += 50

            passive = D[showing].get("passive", "")
            screen.blit(font28.render(f"Passive: {passive}", True, (230,230,230)), (x, y)); y += 32

            skills = D[showing]["skill"]
            screen.blit(font28.render(f"S1: {skills[1]}", True, (230,230,230)), (x, y)); y += 28
            screen.blit(font28.render(f"S2: {skills[2]}", True, (230,230,230)), (x, y)); y += 28
            screen.blit(font28.render(f"S3: {skills[3]}", True, (230,230,230)), (x, y)); y += 28

        pygame.display.flip()

        # --- 이벤트 처리 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None, None

            # 마우스 휠 좌우 스크롤
            if event.type == pygame.MOUSEWHEEL:
                # wheel up → 오른쪽 이동
                if event.y > 0:
                    scroll_x += SCROLL_SPEED
                else:
                    scroll_x -= SCROLL_SPEED

            # 키보드로 스크롤
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    scroll_x += SCROLL_SPEED
                elif event.key == pygame.K_RIGHT:
                    scroll_x -= SCROLL_SPEED

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                mx, my = event.pos

                for name, base_x, y in cards:
                    rect = pygame.Rect(base_x + scroll_x, y, card_w, card_h)

                    if rect.collidepoint(mx, my):

                        if showing != name:
                            showing = name
                            break

                        if showing == name:
                            if selected1 is None:
                                selected1 = name
                                showing = None
                                break
                            elif selected2 is None:
                                selected2 = name
                                showing = None
                                p1 = setChar((1,1), selected1, 1)
                                p2 = setChar((8,8), selected2, 2)
                                return p1, p2


    return None, None




running = True
def main():
    global p1,p2,turn,objects,effects,running,structures

    p1,p2 = charSelect()

    pygame.display.set_caption("Grid Arena")

    objects = []
    effects = []
    structures = []

    turn = 1

    while running:
        turn_player = getSelf(turn)

        for i in range(len(effects)-1,-1,-1):
            effects[i].update()
            if effects[i].life is not None and effects[i].life<=0:
                del effects[i]

        screen.fill(BG_COLOR)

        draw_grid(screen)
        draw_objects(screen,p1,p2)
        draw_info_panel(screen, font, p1, p2,turn_player.p)

        pygame.display.flip()

        if p1.hp <= 0:
            text = title_font.render("Player 2 Wins!", True, (50, 50, 255))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, rect)
            pygame.display.flip()
            break
        if p2.hp <= 0:
            text = title_font.render("Player 1 Wins!", True, (255, 50, 50))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, rect)
            pygame.display.flip()
            break

        if turn_player.stat["stun"] > 0:
            turn = changeTurn(turn,False)
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_q or event.key == pygame.K_u) and turn_player.cool[0] <= 0:
                    turn_player.changeMode("move")
                elif (event.key == pygame.K_w or event.key == pygame.K_i) and turn_player.cool[1] <= 0:
                    turn_player.changeMode("s1")
                elif (event.key == pygame.K_e or event.key == pygame.K_o) and turn_player.cool[2] <= 0:
                    turn_player.changeMode("s2")
                elif (event.key == pygame.K_r or event.key == pygame.K_p) and turn_player.cool[3] <= 0:
                    turn_player.changeMode("s3")
                elif event.key==pygame.K_SPACE:
                    turn_player.cool[0] = max(0,turn_player.cool[0])
                    turn_player.changeMode("")
                    turn = changeTurn(turn)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = event.pos

                if 0 <= mx <= GRID_SIZE * GRID_WIDTH and 0 <= my <= GRID_SIZE * GRID_HEIGHT:
                    tx = math.ceil(mx//GRID_SIZE)
                    ty = math.ceil(my//GRID_SIZE)
                    if turn_player.mode == "":
                        continue
                    elif turn_player.mode == "move":
                        if not turn_player.move(tx,ty):
                            continue
                    elif turn_player.mode == "s1":
                        if not turn_player.skill1(tx,ty):
                            continue
                    elif turn_player.mode == "s2":
                        if not turn_player.skill2(tx,ty):
                            continue
                    elif turn_player.mode == "s3":
                        if not turn_player.skill3(tx,ty):
                            continue
                    turn = changeTurn(turn)


    wait=False
    if running: wait = True
    while wait:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                wait = False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                main()
                wait=False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
