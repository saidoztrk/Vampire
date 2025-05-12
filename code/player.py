from settings import *
import pygame
from os.path import join
from os import walk

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = 'right', 0
        self.image = pygame.image.load(join('images', 'player', 'down', '0.png')).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-60, -90)

        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites

        # Sağlık ve başlangıç pozisyonu
        self.max_health = 100
        self.health = self.max_health
        self.health_bar_length = 100
        self.health_bar_height = 10
        self.health_bar_offset = pygame.Vector2(0, -40)
        self.starting_position = pos  # Oyuncunun başlangıç pozisyonunu kaydetme

    def load_images(self):
        self.frames = {'left': [], 'right': [], 'up': [], 'down': []}
        for state in self.frames.keys():
            for folder_path, _, file_names in walk(join('images', 'player', state)):
                for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.frames[state].append(surf)

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self, dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top

    def animate(self, dt):
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'

        self.frame_index = self.frame_index + 5 * dt if self.direction else 0
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def draw_health_bar(self, surface):
        health_ratio = self.health / self.max_health
        bar_x = self.rect.centerx - self.health_bar_length // 2
        bar_y = self.rect.top + self.health_bar_offset.y
        bg_rect = pygame.Rect(bar_x, bar_y, self.health_bar_length, self.health_bar_height)
        fg_rect = pygame.Rect(bar_x, bar_y, self.health_bar_length * health_ratio, self.health_bar_height)
        pygame.draw.rect(surface, 'red', bg_rect)
        pygame.draw.rect(surface, 'green', fg_rect)
        pygame.draw.rect(surface, 'black', bg_rect, 2)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
            self.kill()

    def reset(self):
        """
        Oyuncunun başlangıç değerlerini sıfırla.
        """
        self.health = self.max_health
        self.rect.center = self.starting_position
        self.hitbox_rect.center = self.starting_position

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)