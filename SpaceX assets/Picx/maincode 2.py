import pygame
import random
pygame.font.init()
pygame.mixer.init()

WIDTH = 900
HEIGHT = 770
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) #set the width and the height of game window called "WIN"
pygame.display.set_caption("Space X") #set the caption of the game window

#Asteriods
ASTERIOD_1 = pygame.image.load("asteroid.png")

#Powerups
POWERUP_1 = pygame.image.load("powerup_1.png")

#Enemy Ships
ENEMY_SPACE_SHIP_RED = pygame.image.load("redship_small.png")
ENEMY_SPACE_SHIP_GREEN = pygame.image.load("greenship_small.png")
ENEMY_SPACE_SHIP_BLUE = pygame.image.load("blueship_small.png")

#Player Spaceship 
SPACESHIP_MAIN = pygame.image.load("playerShip.png")

#Lasers
RED_LASER = pygame.image.load("laser_red.png")
BLUE_LASER = pygame.image.load("laser_blue.png")
GREEN_LASER = pygame.image.load("laser_green.png")
YELLOW_LASER = pygame.image.load("laser_yellow.png")

#Background
BG = pygame.transform.scale(pygame.image.load("starfield.png"), (WIDTH, HEIGHT))

#Music
BG_MUSIC = pygame.mixer.music.load("bg_music.mp3")
pygame.mixer.music.play(-1) #it allows the music to play even after its duration ends

class Score:
    def __init__(self): #score is iniattly set 0
        self.score = 0

    def increment_score(self): #Score counter, increments the score
        self.score += 10

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.powerup_img = POWERUP_1
        self.mask = pygame.mask.from_surface(self.powerup_img)
        self.speed = 3

    def draw(self, window): #blit functions place the image on the screen with its respective x and y
        window.blit(self.powerup_img, (self.x, self.y))

    def move(self): #speed of the powerup as it falls
        self.y += self.speed  
    

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window): #blit function is used to place img
        window.blit(self.img, (self.x, self.y))

    def move(self, speed): #speed of the laser
        self.y += speed

    def off_screen(self, height): #this  function is used to tally if the laser went out of the screen 
        return not(self.y < height and self.y >= 0)
    
    def collision(self, obj): # function used to indicate collision
        return collide(self, obj)
        
class GameObject:  #parent class
    COOLDOWN = 15 # Cooldown period for shooting lasers

    def __init__(self, x, y, health = 100, speed = 3):
        self.x = x
        self.y = y 
        self.health = health
        self.speed = speed
        self.laser_img = None
        self.gameobject_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window): #main draw function
        window.blit(self.gameobject_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, speed, obj): #laser function which either hit obj or go off screen
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    
    def cooldown(self): #cooldown function which indicates after how much time delay gameobject will shoot
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1   
    
    def shoot(self): #shoot function
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.gameobject_img.get_width()

    def get_height(self):
        return self.gameobject_img.get_height()
    
class SpaceShip(GameObject):#inherited from gameobject
    def __init__(self, x, y, health=100, speed=5, score = 0):
        super().__init__(x, y, health, speed)
        self.gameobject_img = SPACESHIP_MAIN
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.gameobject_img)
        self.max_health = health
        #self.score = score()

    def move_lasers(self, speed, objs, asteroids): #function is override 
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            for obj in objs:
                if laser.collision(obj):
                    objs.remove(obj)
                    if laser in self.lasers:
                        self.lasers.remove(laser)
                    #self.score.increment_score()
                       

            for asteroid in asteroids: #this inidicates if the laser is hit asteroid will be destroyed
                if laser.collision(asteroid):
                    asteroids.remove(asteroid)
                    break  

            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)

    def draw(self, window): #draw func is override
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window): #healthbar for spaceship
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.gameobject_img.get_height() + 10, self.gameobject_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.gameobject_img.get_height() + 10, self.gameobject_img.get_width() * (self.health/self.max_health), 10))

        if self.health > self.max_health:
            self.health = self.max_health

class EnemyShip(GameObject): #inherited from gameobject
    COLOR_PATTERN = {
        "red" : (ENEMY_SPACE_SHIP_RED, RED_LASER),
        "green" : (ENEMY_SPACE_SHIP_GREEN, GREEN_LASER),
        "blue" : (ENEMY_SPACE_SHIP_BLUE, BLUE_LASER)
        
        } #color tuple is made for pygame to randomly choose
    
    def __init__(self, x, y,color, health=100, speed=2):
        super().__init__(x, y, health, speed)
        self.gameobject_img, self.laser_img = self.COLOR_PATTERN[color]
        self.mask = pygame.mask.from_surface(self.gameobject_img)

    def move(self, speed): #move function
        self.y += speed

    def shoot(self): #shoot function is override
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Asteroid(GameObject): #inherited from gameobject
    def __init__(self, x, y, size, health=100, speed=1):
        super().__init__(x, y, health, speed)
        self.size = size
        self.gameobject_img = pygame.transform.scale(ASTERIOD_1, (size, size))
        self.mask = pygame.mask.from_surface(self.gameobject_img)

    def move(self, speed): #move function for asteroid
        self.y += speed

    def collision(self, obj): #collision func for asteroid
        if isinstance(obj, SpaceShip):
            obj.health -= 5
            Asteroid.remove(self)
            return True
        return False


def collide(obj1, obj2): #this function is not defined in any class it works to indicate if the asteroid or enemy ships collides by the help of overlap func
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None 

def main():

    run = True
    FPS = 60
    level = 0
    lives = 5
    score = 0
    main_font = pygame.font.SysFont("comicsans", 35) #font used 
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 6 #no.1 of enemies or asteroids in a single wave
    enemies_speed = 1.5  

    asteroids = []
    asteroid_speed = 1

    powerups = []

    laser_speed = 6

    spaceship = SpaceShip(425,700)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window(): #redraw window which uploads the image 60 times in second
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,0,0))
        level_label = main_font.render(f"Level: {level}", 1, (255,0,0))
        score_label = main_font.render(f"Score: {score}", 1, (255,0,0))

        WIN.blit(lives_label, (10,5))
        WIN.blit(score_label, (5,50))
        WIN.blit(level_label, (WIDTH - level_label.get_width() -  10,5))

        for enemyship in enemies:
            enemyship.draw(WIN)

        spaceship.draw(WIN)

        for powerup in powerups:
            powerup.draw(WIN)

        for asteroid in asteroids:
            asteroid.draw(WIN)

        if lost:
            lost_label = lost_font.render("Game Over", 1, (255,0,0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 450))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or spaceship.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 5:
                run = False
            else:
                continue


        if len(enemies) == 0: #this indicates when enemies are 0 a new level starts with the +=6 to enemies in the new level
            level += 1
            wave_length += 6
            for i in range(wave_length): #random module is used which randomise of how many obj wil spawn
                enemyship = EnemyShip(random.randrange(100, WIDTH - 100), random.randrange(-2000, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemyship)

        if len(asteroids) == 0: #this indicates when asteroids are 0 a new wave starts with the +=2 to asteroid 
            level += 0
            wave_length += 2
            for i in range(wave_length): #random module is used
                asteroid = Asteroid(random.randrange(50, WIDTH - 50), random.randrange(-1500 , -100), 50)
                asteroids.append(asteroid)

        if random.randrange(0, 360) == 1: #random module is used for powerups
            powerup = PowerUp(random.randint(100, WIDTH - 100), -50)
            powerups.append(powerup)

        for event in pygame.event.get(): # this tells if the event type is quit or if escape is pressed game is quit 
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and spaceship.x - spaceship.speed > 0:
            spaceship.x -= spaceship.speed
        if keys[pygame.K_RIGHT] and spaceship.x + spaceship.speed + spaceship.get_width() < WIDTH:
            spaceship.x += spaceship.speed
        if keys[pygame.K_UP] and spaceship.y - spaceship.speed > 0:
            spaceship.y -= spaceship.speed
        if keys[pygame.K_DOWN] and spaceship.y + spaceship.speed + spaceship.get_height() < HEIGHT:
            spaceship.y += spaceship.speed
        if keys[pygame.K_SPACE]:
            spaceship.shoot()

        for enemyship in enemies:
            enemyship.move(enemies_speed)
            enemyship.move_lasers(laser_speed, spaceship)

            if random.randrange(0, 180) == 1:
                enemyship.shoot()

            if collide(enemyship, spaceship): #if hit with spaceship it will reduce its health
                spaceship.health -= 10
                enemies.remove(enemyship)
            elif enemyship.y + enemyship.get_height() > HEIGHT: #and if enemyship travels out of the window lives -= 1
                lives -= 1
                enemies.remove(enemyship)
        
        for asteroid in asteroids:
            asteroid.move(asteroid_speed)
            asteroid.move_lasers(laser_speed, spaceship)
            if collide(asteroid, spaceship):
                spaceship.health -= 5
                asteroids.remove(asteroid)
            elif asteroid.y + asteroid.get_height() > HEIGHT:
                asteroids.remove(asteroid)

        for powerup in powerups:
            powerup.move()

            if collide(powerup, spaceship): #with every powerup += 20 health
                spaceship.health += 20  
                powerups.remove(powerup)
        
        spaceship.move_lasers(-laser_speed, enemies, asteroids)
        
def catalog():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press SPACE to Begin...", 1, (0,0,0))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 400))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                main()
    pygame.quit()           

catalog()


