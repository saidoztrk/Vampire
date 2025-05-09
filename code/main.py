from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from random import randint, choice
from os.path import dirname, abspath, join
import pygame
import os

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Survivor')
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 100

        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []

        # BASE PATH
        base_path = dirname(dirname(abspath(__file__)))

        # Ses dosyaları
        self.shoot_sound = pygame.mixer.Sound(join(base_path, 'audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.2)
        self.impact_sound = pygame.mixer.Sound(join(base_path, 'audio', 'impact.ogg'))
        self.music = pygame.mixer.Sound(join(base_path, 'audio', 'music.wav'))
        self.music.set_volume(0.5)

        # Game over görseli
        self.game_over_image = pygame.image.load(join(base_path, 'images', 'ig', 'gameover.png')).convert_alpha()
        self.game_over_image = pygame.transform.scale(self.game_over_image, (400, 150))

        self.load_images()
        self.setup()

    def load_images(self):
        base_path = dirname(dirname(abspath(__file__)))
        self.bullet_surf = pygame.image.load(join(base_path, 'images', 'gun', 'bullet.png')).convert_alpha()
        folders = list(os.walk(join(base_path, 'images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in os.walk(join(base_path, 'images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])): 
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def setup(self):
        base_path = dirname(dirname(abspath(__file__)))
        map = load_pygame(join(base_path, 'data', 'maps', 'world.tmx'))

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        # Spawn pozisyonlarını filtreleme (600 piksel uzaklık)
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            else:
                # Spawn pozisyonunun 600 pikselden uzak olmasını sağlamak
                if abs(obj.x - self.player.rect.centerx) >= 450 and abs(obj.y - self.player.rect.centery) >= 450:
                    self.spawn_positions.append((obj.x, obj.y))

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        sprite.destroy()
                    bullet.kill()

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.player.take_damage(20)
            if self.player.health <= 0:
                self.game_over = True

    def show_game_over_screen(self):
        image_rect = self.game_over_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.display_surface.blit(self.game_over_image, image_rect)
        pygame.display.update()
        pygame.time.wait(3000)

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event and not self.game_over:
                    Enemy(
                        choice(self.spawn_positions),
                        choice(list(self.enemy_frames.values())),
                        (self.all_sprites, self.enemy_sprites),
                        player=self.player,
                        collision_sprites=self.collision_sprites
                    )

            if not self.game_over:
                self.gun_timer()
                self.input()
                self.all_sprites.update(dt)
                self.bullet_collision()
                self.player_collision()

                self.display_surface.fill('black')
                self.all_sprites.draw(self.player.rect.center)
                self.player.draw_health_bar(self.display_surface)
                pygame.display.update()
            else:
                self.show_game_over_screen()
                self.running = False

        pygame.quit()


# PROGRAM BAŞLATMA KONTROLÜ
if __name__ == '__main__':
    game = Game()
    game.run()
