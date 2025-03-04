import pygame
import random
import os

class DVD(pygame.sprite.Sprite):
    def __init__(self, window, config, sounds, cheer, *groups):
        self.group = groups
        super().__init__(*groups)
        self.sounds = sounds
        self.window = window
        path = os.path.join(config.assets_dir, 'logo.png')
        self.sprite = pygame.image.load(path).convert_alpha()
        rect = self.sprite.get_rect().fit(pygame.Rect(0, 0, 200, 200))
        self.sprite = pygame.transform.scale(self.sprite, (rect.width, rect.height))
        self.image = self.sprite
        self.rect = self.sprite.get_rect(center=self.window.get_rect().center)
        self.cheer = cheer
        print(self.cheer is not None)


        pixel_array = pygame.PixelArray(self.image)
        self.current_color = (255, 255, 255)
        for x in range(self.rect.width):
            for y in range(self.rect.height):
                if (pixel_array[x, y] != 0):
                    pixel_array[x, y] = self.current_color
        
        self.velocity = 10
        self.dx = 1 if random.random() > 0.5 else -1
        self.dy = 1 if random.random() > 0.5 else -1
        
    def get_random_color(self):
        return (random.randint(60, 255), random.randint(60, 255), random.randint(60, 255))
        
    def change_color(self):
        color = self.get_random_color()
        pygame.PixelArray(self.image).replace(self.current_color, color)
        self.current_color = color

    def change_direction(self, window):
        corner_hit = -1
        if self.rect.left < 0 and self.dx < 0: 
            corner_hit += 1
            self.dx = -self.dx
        elif self.rect.right > window.width and self.dx > 0: 
            corner_hit += 1
            self.dx = -self.dx
            
        if self.rect.top < 0  and self.dy > 0:  
            corner_hit += 1
            self.dy = -self.dy
        elif self.rect.bottom > window.height and self.dy < 0:
            corner_hit += 1
            self.dy = -self.dy

        return corner_hit == 1

    def speed_up(self):
        self.velocity = min(20, self.velocity + 4)

    def slow_down(self):
        self.velocity = max(1, self.velocity - 4)
        
    def update(self):
        window_rec = self.window.get_rect()
        if not window_rec.contains(self.rect):
            self.change_color()
            if (self.change_direction(window_rec) and self.cheer):
                self.cheer.play()
            else:
                sound = self.sounds.pop(0)
                sound.play()
                self.sounds.append(sound)

        self.rect.x += self.dx * self.velocity
        self.rect.y -= self.dy * self.velocity
