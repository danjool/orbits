import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (30, 30)

import pygame,math,random,time

"""CONSTS"""
WIDTH = 600; HEIGHT = 600
WORLDWIDTH, WORLDHEIGHT = 3600,3600
minimapfactor = 6

white = [255,255,255]
black = [0,0,0]
red = [255,0,0]
yellow = [200,200,0]
orange = [240,50,50]
blue = [0,0,200]
starcount = 200
planetcount = 5
G = .0012

"""VARIABLES"""
mouse = [0,0]
volume = .5
t = 0
gametime = 0
ticks = 0
screenpos = [WORLDWIDTH/2 - WIDTH/2,WORLDHEIGHT/2 - HEIGHT/2]
thrust = .4
stats = False
throttleup = 0
helptheta = 0
helpradius = 50
zoom = 1.0
goalzoom = 1.0
tickspeed = 1.0
drawpath = False
drawterrain = False
drawangle = 0


"""CLASSES"""
#########Star#########
class star():
    pos = [0,0]
    color = white
    size = 1

    def __init__(self,initpos,initcolor,initsize):
        self.pos = initpos
        self.color = initcolor
        self.size = initsize

    def draw(self,screen):
        pygame.draw.circle(screen, 
                           [50,50,50], 
                           [int(int((self.pos[0]-playership.pos[0]))%WORLDWIDTH/(6-self.size)),
                            int(int((self.pos[1]-playership.pos[1]))%WORLDHEIGHT/(6-self.size))], 
                            int(self.size*(2+2*math.sin(gametime*self.color[1]/10000)))
                           ,0)
        pygame.draw.circle(screen, 
                           self.color, 
                           [int(int((self.pos[0]-playership.pos[0]))%WORLDWIDTH/(6-self.size)),
                            int(int((self.pos[1]-playership.pos[1]))%WORLDHEIGHT/(6-self.size))], 
                            int(self.size),0)

#########Planet#######
class Planet():
    pos = [0,0]
    color = white
    size = 1
    radius = 0
    offset = 0

    def __init__(self,initpos,initcolor,initsize):
        self.pos = initpos
        self.color = initcolor
        self.size = initsize
        self.dsq = 0.0
        self.terrain = []*360
        for a in range(360):
            r = (random.random()/100+1)*self.size
            self.terrain.append(r)

    def draw(self,screen):
        pygame.draw.circle(screen, [40,40,40], [int(zoom*(self.pos[0]-playership.pos[0])+WIDTH/2),int(zoom*(self.pos[1]-playership.pos[1])+HEIGHT/2)], int(zoom*self.size*1.4),0)
        self.dsq = (self.pos[0]-playership.pos[0])**2+(self.pos[1]-playership.pos[1])**2
        if self.dsq < 4*(self.size)**2:
            terrainlist=[]
            for a in range(360):
                x =self.pos[0]+self.terrain[a]*math.cos(a*math.pi/180)
                y =self.pos[1]+self.terrain[a]*math.sin(a*math.pi/180)
                terrainlist.append( [int(zoom*(x-playership.pos[0])+WIDTH/2),int(zoom*(y-playership.pos[1])+HEIGHT/2)])
            pygame.draw.polygon(screen,self.color,terrainlist,0)
        else:
            pygame.draw.circle(screen, self.color, [int(zoom*(self.pos[0]-playership.pos[0])+WIDTH/2),int(zoom*(self.pos[1]-playership.pos[1])+HEIGHT/2)], int(zoom*self.size),0)

    def update(self):
        VOID
        # for moving planets around
        #self.pos[0] = WORLDWIDTH/2 +self.radius*math.cos(self.offset)
        #self.pos[1] = WORLDHEIGHT/2 +self.radius*math.sin(self.offset)

#########Ship#########
class Ship():
    pos = [50,50]
    shipangle = 0
    color = red
    width = 0
    height = 0
    corners = [[0,0],[0,0],[0,0]]
    corners10 = [[0,0],[0,0],[0,0]]
    corners100 = [[0,0],[0,0],[0,0]]
    firing = False
    braking = False
    acc = 0
    vel = [0,0]
    rotatingcw = False
    rotatingccw = False
    shipomega = 2
    mass = 1
    xaccel = 0
    yaccel = 0
    closestplanet = 0
    altitude = 100000
    path = []


    def __init__(self, color, width, height):
        self.pos = [WIDTH/2,HEIGHT/2]
        self.shipangle = 0
        self.color = color
        self.width = width
        self.height = height
        self.path.append(self.pos)
        self.velangle=0; self.velmag = 0; self.posangle = 0; self.zenith = 0
        self.M = 0; self.C = 0; self.perigee = 0; self.apogee = 0; self.e = 0; self.anomaly = 0
        self.semimajor = 0; self.perangle = 0

    def draw(self,screen):
        #pygame.draw.lines(screen,self.color,True,self.corners,int(3*zoom))
        if zoom < 4: pygame.draw.aalines(screen,self.color,True,self.corners,True)
        if zoom < 16:pygame.draw.aalines(screen,self.color,True,self.corners10,True)
        pygame.draw.aalines(screen,self.color,True,self.corners100,True)

        if self.firing and zoom < 16:
            pygame.draw.lines(screen,orange,True,self.thrustcorners,2)
        if drawpath:
            count = 0
            for p in self.path:
                count +=1
                pygame.draw.rect(screen,(255,255,count%256),((int(WIDTH/2+zoom*(p[0]-self.pos[0])),int(HEIGHT/2+zoom*(p[1]-self.pos[1]))),(1,1)),1)

        global stats
        if stats:
            pygame.draw.line(screen,orange,(WIDTH/2,HEIGHT/2),(WIDTH/2 +10*self.velmag*math.cos(self.velangle),HEIGHT/2 +10*self.velmag*math.sin(self.velangle)),1)
            pygame.draw.line(screen,orange,(WIDTH/2,HEIGHT/2),(WIDTH/2+math.sqrt(self.altitude)*math.cos(self.posangle),HEIGHT/2+math.sqrt(self.altitude)*math.sin(self.posangle)),1)
            pygame.draw.arc(screen,blue,((WIDTH/2-50,HEIGHT/2-50),(100,100)),2*math.pi-self.posangle,2*math.pi-self.posangle+self.zenith,1)
            #anomaly
            #pygame.draw.line(screen,yellow,(WIDTH/2,HEIGHT/2),(WIDTH/2+20*math.cos(self.anomaly),HEIGHT/2+20*math.sin(self.anomaly)),1)
            pygame.draw.circle(screen,(40,40,40),(int(WIDTH/2+zoom*(-self.pos[0]+planetList[self.closestplanet].pos[0])),int(HEIGHT/2+zoom*(-self.pos[1]+planetList[self.closestplanet].pos[1]))),int(self.apogee*zoom),1)
            pygame.draw.circle(screen,(40,40,40),(int(WIDTH/2+zoom*(-self.pos[0]+planetList[self.closestplanet].pos[0])),int(HEIGHT/2+zoom*(-self.pos[1]+planetList[self.closestplanet].pos[1]))),int(self.perigee*zoom),1)


    def upd(self,screen):
        hw = self.width/2*zoom       #half width
        ht = self.height*zoom        #height (full)
        th = self.shipangle     #ship angle theta

        self.shipangle = math.atan2(mouse[1]-HEIGHT/2,mouse[0]-WIDTH/2)
        self.acc = math.sqrt((mouse[1]-HEIGHT/2)**2+(mouse[0]-WIDTH/2)**2)/500

        self.corners     = [[WIDTH/2-hw*math.sin(th),HEIGHT/2+hw*math.cos(th)],[WIDTH/2+hw*math.sin(th),HEIGHT/2-hw*math.cos(th)],[WIDTH/2+ht*math.cos(th),HEIGHT/2+ht*math.sin(th)]]
        self.corners10  = [[WIDTH/2-hw*math.sin(th)/10,HEIGHT/2+hw*math.cos(th)/10],[WIDTH/2+hw*math.sin(th)/10,HEIGHT/2-hw*math.cos(th)/10],[WIDTH/2+ht*math.cos(th)/10,HEIGHT/2+ht*math.sin(th)/10]]
        self.corners100 = [[WIDTH/2-hw*math.sin(th)/100,HEIGHT/2+hw*math.cos(th)/100],[WIDTH/2+hw*math.sin(th)/100,HEIGHT/2-hw*math.cos(th)/100],[WIDTH/2+ht*math.cos(th)/100,HEIGHT/2+ht*math.sin(th)/100]]
        hw = 5*zoom
        self.thrustcorners = [[WIDTH/2-hw*math.sin(th),HEIGHT/2+hw*math.cos(th)],[WIDTH/2+hw*math.sin(th),HEIGHT/2-hw*math.cos(th)],[WIDTH/2-50*zoom*self.acc*math.cos(th),HEIGHT/2+50*zoom*self.acc*math.sin(-th)]]

        for a in range(planetcount):
            dsq = (planetList[a].pos[0]-self.pos[0])**2 +(planetList[a].pos[1]-self.pos[1])**2
            #figure out which is the closest planet and figure out the distance (altitude) from that
            if a == self.closestplanet: self.altitude = dsq
            else:
                if dsq < self.altitude:
                    print(str(dsq) + " of planet "+ str(a)+ " is smaller than altitude " + str(self.altitude) +" from planet " + str(self.closestplanet) )
                    self.closestplanet = a
                    self.altitude = dsq
            ad = math.atan2(planetList[a].pos[1]-self.pos[1],planetList[a].pos[0]-self.pos[0]) #angle to planet

            if a == self.closestplanet:
                self.M = (4/3)*math.pi*planetList[a].size**3
                self.xaccel += G*(self.M)*math.cos(ad)/dsq
                self.yaccel += G*(self.M)*math.sin(ad)/dsq
                self.posangle = (ad+math.pi)%(2*math.pi)

                if dsq < (planetList[a].size*1.4)**2:  #atmosphere slowdown
                    self.vel[0] = (1-.1*tickspeed)*self.vel[0]
                    self.vel[1] = (1-.1*tickspeed)*self.vel[1]
                    global goalzoom, tickspeed, drawpath
                    goalzoom = 1
                    tickspeed = .1
                    drawpath = False
                else:
                    goalzoom = 1
                    tickspeed = 1
            if dsq < (planetList[a].size)**2:  #planet surface "slowdown"
                self.vel[0] = -.5*self.vel[0]*0
                self.vel[1] = -.5*self.vel[1]*0
                self.pos[0] = planetList[a].pos[0]-1.0*planetList[a].size*math.cos(ad)
                self.pos[1] = planetList[a].pos[1]-1.0*planetList[a].size*math.sin(ad)
                global drawangle
                drawangle = ad

        if self.firing:
            self.vel[0] += self.acc*math.cos(th)*tickspeed
            self.vel[1] += self.acc*math.sin(th)*tickspeed

        self.vel[0] += self.xaccel*tickspeed
        self.vel[1] += self.yaccel*tickspeed
        self.pos[0] += self.vel[0]*tickspeed
        self.pos[1] += self.vel[1]*tickspeed
        self.velangle = math.atan2(self.vel[1],self.vel[0])%(2*math.pi)
        self.velmag = math.sqrt(self.vel[1]**2 + self.vel[0]**2)

        self.xaccel = 0
        self.yaccel = 0


        if self.braking:
            self.vel[0] = .9*self.vel[0]
            self.vel[1] = .9*self.vel[1]
        #start rotating the ship if q or e are pressed
        if self.rotatingcw: self.shipomega = .05
        if self.rotatingccw: self.shipomega = -.05
        #otherwise slow down the rotation
        if self.rotatingccw == False and self.rotatingccw == False: self.shipomega = .9*self.shipomega
        #actually rotate the ship by an increment of it's rot vel
        self.shipangle += self.shipomega

        #borders of world as physical boundaries
        if self.pos[0] < 0: self.pos[0] = 2
        if self.pos[0] > WORLDWIDTH: self.pos[0] = WORLDWIDTH-2
        if self.pos[1] < 0: self.pos[1] = +2
        if self.pos[1] > WORLDHEIGHT: self.pos[1] = WORLDHEIGHT-2

        #path crap
        self.path = []
        self.path.append([self.pos[0],self.pos[1]])

        vx = self.vel[0];vy = self.vel[1];xp=self.pos[0];yp=self.pos[1]
        for ft in range(1000):
            dsq = (planetList[self.closestplanet].pos[0]-self.path[ft][0])**2 +(planetList[self.closestplanet].pos[1]-self.path[ft][1])**2
            ad = math.atan2(planetList[self.closestplanet].pos[1]-self.path[ft][1],planetList[self.closestplanet].pos[0]-self.path[ft][0])
            xa = G*(self.M)*math.cos(ad)/dsq
            ya = G*(self.M)*math.sin(ad)/dsq
            vx += xa*tickspeed
            vy += ya*tickspeed
            xp = vx*tickspeed
            yp = vy*tickspeed
            self.path.append([self.path[ft][0]+xp,self.path[ft][1]+yp])

        #what if the mag of the vel affected the zoom?
        #I don't like it

        #  FIGURE OUT ORBITAL MECHANICS!!!!
        #figure out the zenith angle
        self.zenith = (self.posangle - self.velangle)%(2*math.pi)
        alt = math.sqrt(self.altitude)
        C = 2*G*self.M/(alt*(self.velmag**2))
        self.C = C
        ## (Rp/r1)1,2 = ( -C +- SQRT[ C^2 - 4 * (1 - C) * - sin^2 (zenith)] ) / (2*(1-C))
        ## C = 2 * G*M / (r1 * v1^2)

        det = (C**2 + 4*(1-C)*(math.sin(self.zenith)**2))

        Rp1 = alt*(float(-C+math.sqrt(det)) /(2*(1-C)))
        Rp2 = alt*(float(-C-math.sqrt(det)) /(2*(1-C)))
    
        self.perigee = max(1,min(Rp1,Rp2))
        self.apogee = max(1,max(Rp1,Rp2))


        ## e = sqrt[(alt * velmag^2 / GM - 1)^2 * sin(zen)^2 + cos(zen)^2]
        self.e = math.sqrt((float(alt * self.velmag**2) / (G * self.M) - 1)**2 * math.sin(self.zenith)**2 + math.cos(self.zenith)**2)

        ##r1 v1 sin (z1) = r2 v2 sin(z2)
        derp = float(alt*self.velmag**2) / (G*self.M)
        ## tan (v) = (derp * sin(zen)cos(zen)) / (sin^2(zen)-1)
        self.anomaly = math.atan2(derp*math.sin(self.zenith)*math.cos(self.zenith),math.sin(self.zenith)**2-1)
        #semi major axis
        self.semimajor = float(1)/(float(2)/alt - float(self.velmag**2) / (G*(self.M)))
        #angle of periapsis


#########Planet#######
"""INITS"""
pygame.init()
screen = pygame.display.set_mode([WIDTH,HEIGHT])
pygame.display.set_caption("Playground")
pygame.font.init()
font = pygame.font.SysFont('arial', 16)
done = False
clock = pygame.time.Clock()
pygame.mouse.set_visible(0)
cursor = pygame.image.load("cursor.png").convert()
cursor.set_colorkey(white)
###Make a list of stars
starList = []
for a in range(starcount):
    starList.append(star([random.randint(1,WORLDWIDTH),random.randint(1,WORLDHEIGHT)],[random.randint(200,255),random.randint(200,255),random.randint(200,255)],random.randint(1,3)))
###Make a list of planets

planetList = []
for a in range(planetcount):
    offset = 6.28*a/planetcount
    planetList.append(Planet([WORLDHEIGHT/2 +random.randint(WORLDWIDTH/4,WORLDHEIGHT/3)*math.cos(offset),WORLDHEIGHT/2 +random.randint(WORLDWIDTH/4,WORLDHEIGHT/3)*math.sin(offset)],[random.randint(1,255),random.randint(1,255),random.randint(1,255)],random.randint(20,70)))

###Make a ship###
playership = Ship(red,10,20)

music = pygame.mixer.Sound("ObservingTheStar.ogg")
music.set_volume(volume)
music.play()

while done != True:
    clock.tick(100)
    ticks+=1
    gametime += tickspeed
    #interpolate the transition from what the zoom actually is to what it needs to be
    if zoom != goalzoom: zoom += float(goalzoom - zoom)/250
    """KEYBOARD EVENTS"""
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        if event.type == pygame.MOUSEMOTION:
            mouse = event.pos

        if event.type == pygame.KEYDOWN:
            whatkeypressedlast = event.key
            if event.key == 61:
                if volume < .9: volume += .05
                music.set_volume(volume)
            if event.key == 45:
                if volume > .09: volume -= .05
                music.set_volume(volume)
            #for now let t and g control the rate "gametime" passes
            if event.key == pygame.K_t:
                tickspeed = tickspeed*2
            if event.key == pygame.K_g:
                tickspeed = tickspeed/2
            #for now let y and h control the goal zoom
            if event.key == pygame.K_y:
                goalzoom = goalzoom*2
            if event.key == pygame.K_h:
                goalzoom = goalzoom/2

            if event.key == pygame.K_f:
                if drawpath:
                    drawpath = False
                else:
                    drawpath = True
                    print(playership.path)
            if event.key == pygame.K_z:
                if stats:
                    stats = False
                else:
                    stats = True

            if event.key == pygame.K_q:
                throttleup = -.01
            if event.key == pygame.K_e:
                throttleup = +.01

            if event.key == pygame.K_w:
                playership.acc = thrust
                playership.firing = True
            if event.key == pygame.K_LSHIFT:
                playership.braking = True
            if event.key == pygame.K_d:
                playership.rotatingcw = True
            if event.key == pygame.K_a:
                playership.rotatingccw = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_q:
                throttleup = 0
            if event.key == pygame.K_e:
                throttleup = 0

            if event.key == pygame.K_w:
                playership.acc = 0
                playership.firing = False
            if event.key == pygame.K_LSHIFT:
                playership.braking = False
            if event.key == pygame.K_d:
                playership.rotatingcw = False
            if event.key == pygame.K_a:
                playership.rotatingccw = False
    """UPDATES"""
    t = time.time()
    playership.upd(screen)
    thrust += throttleup
    """for a in range(planetcount):
        planetList[a].update()"""

    """RENDER"""
    screen.fill(black)
    for a in range(starcount):
        starList[a].draw(screen)
    for a in range(planetcount):
        planetList[a].draw(screen)

    screen.blit(cursor, [mouse[0]-5,mouse[1]-5])
    #all_sprites_list.draw(screen)
    playership.draw(screen)

    #draw lines around the world
    pygame.draw.lines(screen,white,True,[[WIDTH/2-playership.pos[0],HEIGHT/2-playership.pos[1]],[WIDTH/2-playership.pos[0],WORLDHEIGHT+HEIGHT/2-playership.pos[1]],[WORLDWIDTH+WIDTH/2-playership.pos[0],WORLDHEIGHT+HEIGHT/2-playership.pos[1]],[WORLDWIDTH+WIDTH/2-playership.pos[0],HEIGHT/2-playership.pos[1]]],5)

    #minimap
    pygame.draw.lines(screen,white,True,[[0,HEIGHT],[WIDTH/minimapfactor,HEIGHT],[WIDTH/minimapfactor,WIDTH-HEIGHT/minimapfactor],[0,WIDTH-HEIGHT/minimapfactor]],1)
    for a in range(planetcount):
        pygame.draw.circle(screen, planetList[a].color, [0+int((WIDTH/2+planetList[a].pos[0])/minimapfactor**2),int(HEIGHT-100+(HEIGHT/2+planetList[a].pos[1])/minimapfactor**2)], int(planetList[a].size/(3*minimapfactor)),0)
        if a == playership.closestplanet:
            pygame.draw.circle(screen, white, [0+int((WIDTH/2+planetList[a].pos[0])/minimapfactor**2),int(HEIGHT-100+(HEIGHT/2+planetList[a].pos[1])/minimapfactor**2)], int(planetList[a].size/(3*minimapfactor)),0)

    pygame.draw.rect(screen,playership.color,[(playership.pos[0]+WIDTH/2)/minimapfactor**2,HEIGHT-100+(playership.pos[1]+HEIGHT/2)/minimapfactor**2,3,3],1)
    #thrust bar
    pygame.draw.lines(screen,orange,True,[[WIDTH/minimapfactor+2,HEIGHT],[WIDTH/minimapfactor+2,HEIGHT-100*thrust]],4)

    if stats:
        screen.blit(font.render("Ship Pos: "+str(int(playership.pos[0]))+", "+str(int(playership.pos[1])),True,white),[WIDTH-200,16])
        screen.blit(font.render("Ship Vel: "+str(int(100*playership.vel[0])/100)+", "+str(int(playership.vel[1])),True,white),[WIDTH-200,32])
        screen.blit(font.render("Ship Acc: "+str(int(1000*playership.xaccel))+", "+str(int(1000*playership.yaccel)),True,white),[WIDTH-200,48])
        screen.blit(font.render("t: "+str(int(t)),True,white),[WIDTH-200,64])
        screen.blit(font.render("thrust: "+str(thrust),True,white),[WIDTH-200,80])
        screen.blit(font.render("closest: "+str(playership.closestplanet),True,white),[WIDTH-200,96])
        screen.blit(font.render("tickspeed: "+str(tickspeed),True,white),[WIDTH-200,112])
        screen.blit(font.render("zoom: "+str(zoom)+", goalzoom: "+str(goalzoom),True,white),[WIDTH-200,128])
        screen.blit(font.render("velangle: "+str(int(180*playership.velangle/math.pi))+", posangle: "+str(int(180*playership.posangle/math.pi)),True,white),[WIDTH-200,144])
        screen.blit(font.render("zenith angle: "+str(int(180*playership.zenith/math.pi)),True,white),[WIDTH-200,160])
        screen.blit(font.render("perigee: "+str(int(playership.perigee))+", apogee: "+str(int(playership.apogee)),True,white),[WIDTH-200,176])
        screen.blit(font.render("altitude: "+str(int(math.sqrt(playership.altitude))),True,white),(WIDTH-200,192))
        screen.blit(font.render("e: "+str(round(playership.e,2))+", anomaly: "+str(round(180*playership.anomaly/math.pi,2)),True,white),(WIDTH-200,208))
        screen.blit(font.render("semimajor axis: "+str(int(playership.semimajor)),True,white),[WIDTH-200,224])
        screen.blit(font.render("drawangle: "+str(round(drawangle,2)),True,white),[WIDTH-200,240])


        for a in range(planetcount):
            screen.blit(font.render("offset,x,y: "+str(planetList[a].offset)+", "+str(planetList[a].pos[0])+", "+str(planetList[a].pos[1]),True,white),[WIDTH-500,80+16+16*a])
    #helpradius += .3
    #helptheta +=.01
    screen.blit(font.render("A left",True,white),[400-playership.pos[0],400-playership.pos[1]])
    screen.blit(font.render("W thrust",True,white),[400-playership.pos[0],420-playership.pos[1]])
    screen.blit(font.render("D right",True,white),[400-playership.pos[0],440-playership.pos[1]])
    screen.blit(font.render("music: Observing The Star by yd",True,white),[400-playership.pos[0],460-playership.pos[1]])
    pygame.display.flip()

pygame.quit()
