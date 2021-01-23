import pygame, sys, random
from pygame.locals import * # import pygame modules
import data.engine as e

pygame.mixer.pre_init(44100, -16, 2,512)

clock = pygame.time.Clock()

pygame.init()

pygame.mixer.set_num_channels(64)
pygame.display.set_caption('Platformer try')

WINDOW_SIZE = (600,400)

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate the window

display = pygame.Surface((300,200)) # used as the surface for rendering, which is scaled


my_font = pygame.font.Font("data/fonts/custom_font.ttf", 25)


pygame.mixer.music.load('data/audio/music.wav')
pygame.mixer.music.play(-1)


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

game_map = load_map('map')

player_rect = pygame.Rect(100,100,30,13)

player = e.entity(100,100,5,13, 'player')

enemies = []
for i in range(5):
    enemies.append([0, e.entity(random.randint(0,600)-300, 80, 13, 13, 'enemy')])

background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]


jumper_objects = []
for i in range(5):
    jumper_objects.append(jumper_obj((random.randint(0,600)-300, 80)))


def main_menu(screen):
    while True:
        screen.fill((146,244,255))
        draw_text('Menu principal', my_font, (255, 255, 255), screen, 20, 20)

        mx, my = pygame.mouse.get_pos()
        button_1 = pygame.Rect(50, 100, 200, 50)
        button_2 = pygame.Rect(50, 200, 200, 50)
        if button_1.collidepoint((mx, my)):
            if click:
                game()
        if button_2.collidepoint((mx, my)):
            if click:
                options(screen)

        pygame.draw.rect(screen, (255, 0, 0), button_1)
        pygame.draw.rect(screen, (255, 0, 0), button_2)
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

    jump_sound = pygame.mixer.Sound('data/audio/jump.wav')
    grass_sounds = [pygame.mixer.Sound('data/audio/grass_0.wav'), pygame.mixer.Sound('data/audio/grass_1.wav')]
    grass_sounds[0].set_volume(0.2)
    grass_sounds[1].set_volume(0.2)

    moving_right = False
    moving_left = False

    lose = 0
    edges = [99999, 99999, -99999, -99999]
    void = edges[3]

    player_y_momentum = 0
    air_timer = 0
    true_scroll = [0, 0]

    particles = []


    while running:
        display.fill((146, 244, 255))

        if grass_sound_timer > 0:
            grass_sound_timer -= 1

        true_scroll[0] += (player.x - true_scroll[0] - 152) / 20
        true_scroll[1] += (player.y - true_scroll[1] - 106) / 20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))
        for background_object in background_objects:
            obj_rect = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0],
                                   background_object[1][1] - scroll[1] * background_object[0], background_object[1][2],
                                   background_object[1][3])
            if background_object[0] == 0.5:
                pygame.draw.rect(display, (9, 80, 81), obj_rect)

            else:
                pygame.draw.rect(display, (9, 91, 81), obj_rect)

        tile_rects = []
        y = 0
        for row in game_map:
            x = 0
            for tile in row:
                if tile == '1':
                    display.blit(dirt_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                if tile == '2':
                    display.blit(grass_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                if tile != '0':
                    tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                if (x * TILE_SIZE - scroll[1]) > edges[3]:
                    edges[3] = (x * TILE_SIZE - scroll[1])
                if (x * TILE_SIZE - scroll[1]) < edges[1]:
                    edges[1] = (x * TILE_SIZE - scroll[1])
                if (y * TILE_SIZE - scroll[0]) > edges[2]:
                    edges[2] = (y * TILE_SIZE - scroll[0])
                if (y * TILE_SIZE - scroll[0]) < edges[0]:
                    edges[0] = (y * TILE_SIZE - scroll[0])

                x += 1
            y += 1

        void = edges[3]
        if player.y > void:
            if lose == 0:
                lose = 160
                print("Dead")

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
            player.set_flip(False)
            player.set_action('run')
        if player_movement[0] == 0:
            player.set_action('idle')
        if player_movement[0] < 0:
            player.set_flip(True)
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

        if player_y_momentum < 0:
            particles.append([[player.x, player.y], [random.randint(0, 20) / 10 - 1, -1], random.randint(4, 6)])


        for particle in particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.1
            particle[1][1] += 0.1
            pygame.draw.circle(display, (255, 255, 255), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))
            if particle[2] <= 0:
                particles.remove(particle)

        for enemy in enemies:
            if display_r.colliderect(enemy[1].obj.rect):
                enemy[0] += 0.2
                if enemy[0] > 3:
                    enemy[0] = 3
                enemy_movement = [0, enemy[0]]
                if player.x > enemy[1].x + 5:
                    enemy_movement[0] = 1
                if player.x < enemy[1].x - 5:
                    enemy_movement[0] = -1
                collisions_types = enemy[1].move(enemy_movement, tile_rects)
                if collisions_types['bottom'] == True:
                    enemy[0] = 0
                enemy[1].display(display, scroll)
                if player.obj.rect.colliderect(enemy[1].obj.rect):
                    player_y_momentum = - 4


        if lose > 0:
            lose -= 1
            draw_text('Dead', my_font, (255,255,255), display, 0,0)
            if lose == 1:
                player.set_pos(100, 100)
            if lose == 100:
                lose = 26

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
        button_1 = pygame.Rect(50, 100, 200, 50)
        pygame.draw.rect(screen, (255, 0, 0), button_1)
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