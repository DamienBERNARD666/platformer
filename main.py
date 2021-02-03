import pygame, sys, random
from pygame.locals import * # import pygame modules
import data.engine as e

pygame.mixer.pre_init(44100, -16, 2,512)

clock = pygame.time.Clock()

pygame.init()

icon = pygame.image.load('data/images/entities/player/run/run_1.png')
pygame.display.set_icon(icon)

pygame.mixer.set_num_channels(64)
pygame.display.set_caption('Wolfy\'s dream')

WINDOW_SIZE = (600,400)

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate the window

display = pygame.Surface((300,200)) # used as the surface for rendering, which is scaled


my_font = pygame.font.Font("data/fonts/custom_font.ttf", 25)

sound1 = pygame.mixer.Sound('data/audio/music.mp3')
sound1.set_volume(0.1)
sound1.play()

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, 1, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


def load_map(path):
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map


def gen_clouds(edges):
    clouds_list = ['cloud_O', 'cloud_1', 'cloud_2']
    x = edges[0]
    y = edges[1]
    x -= 160
    y -= 460
    size_x = edges[2] - edges[0]
    size_y = edges[3] - edges[1]
    size_x += 640
    size_y +=  840
    area = size_x * size_y
    clouds = []
    for depth in range(3):
        depth = 4 - depth
        for i in range(int(area/(1024*90))):
            clouds.append([random.choice(clouds_list), random.randint(x,x+size_x)/depth, random.randint(y,y+size_y)/depth, depth])
    return clouds


jumper_img = pygame.image.load('data/images/jumper.png').convert()
jumper_img.set_colorkey((255, 255, 255))


class jumper_obj():
    def __init__(self, loc):
        self.loc = loc

    def render(self, surf, scroll):
        surf.blit(jumper_img, (self.loc[0] - scroll[0], self.loc[1] - scroll[1]))

    def get_rect(self):
        return pygame.Rect(self.loc[0], self.loc[1], 8, 9)

    def collision_test(self, rect):
        jumper_rect = self.get_rect()
        return jumper_rect.colliderect(rect)


e.load_animations('data/images/entities/')

player_rect = pygame.Rect(100,100,30,13)

player = e.entity(100,100,32,32, 'player')

enemies = []

background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]


jumper_objects = []


def main_menu(screen):
    click = False
    e.set_global_colorkey((255,0,255))
    while True:
        bg = pygame.image.load('data/images/parallax-mountain-bg.png')
        screen.blit(bg, (0,0))
        draw_text('Menu principal    -    Wolfy\'s Dream', my_font, (255, 255, 255), screen, 20, 15)

        mx, my = pygame.mouse.get_pos()
        button_play = pygame.image.load('data/images/button-1.png')
        button_options = pygame.image.load('data/images/button-2.png')
        button_1 = pygame.Rect(50, 100, 200, 50)
        button_2 = pygame.Rect(50, 200, 200, 50)
        screen.blit(button_play, (50, 100))
        screen.blit(button_options, (50, 200))

        if button_1.collidepoint((mx, my)):
            if click:
                game()
        if button_2.collidepoint((mx, my)):
            if click:
                options(screen)

        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        pygame.display.update()
        clock.tick(60)


def game():
    running = True
    grass_sound_timer = 0
    grass_image = pygame.image.load('data/images/grass.png')

    TILE_SIZE = grass_image.get_width()
    dirt_image = pygame.image.load('data/images/dirt.png')
    fox_image = pygame.image.load('data/images/fox.png')
    cloud_1_image = pygame.image.load('data/images/cloud_1.png')
    cloud_2_image = pygame.image.load('data/images/cloud_2.png')
    cloud_3_image = pygame.image.load('data/images/cloud_3.png')
    cloud_dictonnary = {'cloud_O': cloud_1_image, 'cloud_1': cloud_2_image, 'cloud_2': cloud_3_image}

    jump_sound = pygame.mixer.Sound('data/audio/jump.wav')
    hit_sound = pygame.mixer.Sound('data/audio/hit.wav')
    victory_sound = pygame.mixer.Sound('data/audio/victory.wav')
    grass_sounds = [pygame.mixer.Sound('data/audio/grass_0.wav'), pygame.mixer.Sound('data/audio/grass_1.wav')]
    grass_sounds[0].set_volume(0.2)
    grass_sounds[1].set_volume(0.2)


    moving_right = False
    moving_left = False

    lose = 0
    win = 0
    edges = [-480, -208, 408, 208]
    clouds = gen_clouds(edges)

    player_y_momentum = 0
    air_timer = 0
    true_scroll = [0, 0]

    particles = []

    current_level = 1
    health = 200

    def level_bluider(level):
        if level == 2:
            enemies.append([0, e.entity(200, 80, 32, 32, 'enemy')])
            jumper_objects.append(jumper_obj((300, 80)))
        if level == 3:
            jumper_objects.append(jumper_obj((520, 200)))


    while running:
        print(player.obj.x)
        print(player.obj.y)

        display.fill((171, 106, 140))

        if grass_sound_timer > 0:
            grass_sound_timer -= 1

        true_scroll[0] += (player.x - true_scroll[0] - 152) / 20
        true_scroll[1] += (player.y - true_scroll[1] - 106) / 20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        for cloud in clouds:
            display.blit(cloud_dictonnary[cloud[0]], (cloud[1] - scroll[0] / cloud[3], cloud[2] - scroll[1] / cloud[3]))

        tile_rects = []
        y = 0
        game_map = load_map('level_' + str(current_level))
        for row in game_map:
            x = 0

            for tile in row:
                if tile == '1':
                    display.blit(dirt_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                if tile == '2':
                    display.blit(grass_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                if tile == '3':
                    if win == 0:
                        display.blit(fox_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                if tile != '0':
                    if tile == '3':
                        itemR = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        if player.obj.rect.colliderect(itemR):
                            win = 1
                    else:
                     tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                x += 1
            y += 1
        edges[0] = - (x * TILE_SIZE)
        edges[2] = (x * TILE_SIZE)
        edges[1] = - (y * TILE_SIZE)
        edges[3] = (y * TILE_SIZE)
        void = edges[3]
        if player.y > void:
            draw_text('Oups...you fall', my_font, (255, 255, 255), display, 60, 80)
            if lose == 0:
                lose = 100


        player_movement = [0, 0]
        if moving_right:
            player_movement[0] += 2
        if moving_left:
            player_movement[0] -= 2
        player_movement[1] += player_y_momentum
        player_y_momentum += 0.2
        if player_y_momentum > 3:
            player_y_momentum = 3

        if player_movement[0] > 0:
            player.set_flip(True)
            player.set_action('run')
        if player_movement[0] == 0:
            player.set_flip(True)
            player.set_action('idle')
        if player_movement[0] < 0:
            player.set_flip(False)
            player.set_action('run')

        collisions_types = player.move(player_movement, tile_rects)

        if collisions_types['bottom']:
            player_y_momentum = 0
            air_timer = 0
            if player_movement[0] != 0:
                if grass_sound_timer == 0:
                    grass_sound_timer = 30
                    random.choice(grass_sounds).play()
        elif collisions_types['top']:
            player_y_momentum = 0
            air_timer = 0
        else:
            air_timer += 1

        player.change_frame(1)
        player.display(display, scroll)

        for jumper in jumper_objects:
            jumper.render(display, scroll)
            if jumper.collision_test(player.obj.rect):
                player_y_momentum = -8

        display_r = pygame.Rect(scroll[0], scroll[1], 300, 200)


        for particle in particles:
           try:
               particle[0][0] += particle[1][0]
               particle[0][1] += particle[1][1]
               particle[2] -= 0.1
               particle[1][1] += 0.1
               pygame.draw.circle(display, (255, 255, 255), [int(particle[0][0]), int(particle[0][1])],
                                  int(particle[2]))
               if particle[2] <= 0:
                   particles.remove(particle)
           except KeyError:
                particles.remove(particle)


        for enemy in enemies:
            if display_r.colliderect(enemy[1].obj.rect):
                enemy[0] += 0.2
                if enemy[0] > 3:
                    enemy[0] = 3
                enemy_movement = [0, enemy[0]]

                if enemy_movement[0] == 0:
                    enemy[1].set_flip(False)
                    enemy[1].set_action('idle')

                if player_movement[0] != 0:
                    if player.x > enemy[1].x + 5:
                        enemy[1].set_flip(True)
                        enemy_movement[0] = 1
                    if player.x < enemy[1].x - 5:
                        enemy[1].set_flip(False)
                        enemy_movement[0] = -1

                collisions_types = enemy[1].move(enemy_movement, tile_rects)
                if collisions_types['bottom'] == True:
                    enemy[0] = 0
                enemy[1].change_frame(1)
                enemy[1].display(display, scroll)

                if player.obj.rect.colliderect(enemy[1].obj.rect):
                    health -= 2
                    if health < 100:
                        hit_sound.play()
                        lose = 200
                        enemies.remove(enemy)


        # win condition
        if win == 1:
            victory_sound.play()
            win = 0
            enemies.clear()
            jumper_objects.clear()
            current_level += 1
            if current_level != 3:
                 player.set_pos(100, 100)
            else:
                player.set_pos(2, 160)
            clouds = gen_clouds(edges)
            level_bluider(current_level)

        if health < 100:
            draw_text('You\'ve failed', my_font, (255, 255, 255), display, 60, 80)

        #death condition
        if lose > 0:
            lose -= 1
            if lose == 1:
                enemies.clear()
                if current_level != 3:
                    player.set_pos(100, 100)
                else:
                    player.set_pos(2, 160)
                level_bluider(current_level)
                if health < 100:
                    health = 200
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_k:
                    pygame.mixer.music.fadeout(1000)
                if event.key == K_RIGHT:
                    moving_right = True
                if event.key == K_LEFT:
                    moving_left = True
                if event.key == K_UP:
                    if air_timer < 6:
                        jump_sound.play()
                        player_y_momentum = -5

            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    moving_right = False
                if event.key == K_LEFT:
                    moving_left = False

        surf = pygame.transform.scale(display, WINDOW_SIZE)
        screen.blit(surf, (0, 0))
        pygame.display.update()
        clock.tick(60)

def options(screen):
    monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
    fullscreen = False
    running = True
    while running:
        screen.fill((146, 244, 255))
        draw_text('Options', my_font, (255, 255, 255), screen, 20, 20)

        mx, my = pygame.mouse.get_pos()
        button_options = pygame.image.load('data/images/button-3.png')
        button_1 = pygame.Rect(50, 100, 200, 50)
        screen.blit(button_options, (50,100))
        if button_1.collidepoint((mx, my)):
            if click:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((screen.get_width(), screen.get_height()), pygame.RESIZABLE)
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        pygame.display.update()
        clock.tick(60)


main_menu(screen)