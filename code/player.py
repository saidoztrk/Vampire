from settings import *
import pygame
from os.path import join
from os import walk

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)

        # Animasyon verileri
        self.frames = self.load_images()
        self.state = 'right'
        self.frame_index = 0
        self.image = self.frames[self.state][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-60, -90)

        # Hareket ve çarpışma
        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites

        # Sağlık
        self.max_health = 100
        self.health = self.max_health
        self.health_bar_length = 100
        self.health_bar_height = 10
        self.health_bar_offset = pygame.Vector2(0, -40)

    def load_images(self):
        frames = {'left': [], 'right': [], 'up': [], 'down': []}
        for state in frames.keys():
            for folder_path, _, file_names in walk(join('images', 'player', state)):
                for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    frames[state].append(surf)
        return frames

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()

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
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    elif self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                elif direction == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                    elif self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom

    def animate(self, dt):
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        elif self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'

        if self.direction.length_squared() > 0:
            self.frame_index += 5 * dt
            self.frame_index %= len(self.frames[self.state])
        else:
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]

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
        if self.health <= 0:
            self.health = 0
            self.kill()

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
