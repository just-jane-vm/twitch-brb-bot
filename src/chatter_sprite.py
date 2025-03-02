import pygame
import random

class Chatter(pygame.sprite.Sprite):
    def __init__(self, window, name, color, sound, font, *groups):
        self.group = groups
        super().__init__(*groups)
        self.window = window
        self.sound = sound
        self.font = font
        self.image = self.font.render(name, 1, self.convert_color(color))
        w, h = pygame.display.get_surface().get_size()
        img_w, img_h = self.image.get_rect().size
        x = random.randint(0, w - img_w)
        y = random.randint(0, h - img_h)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.velocity = 2
        self.dx = 1 if random.random() > 0.5 else -1
        self.dy = 1 if random.random() > 0.5 else -1

    def change_direction(self, window):
        if self.rect.left < 0 and self.dx < 0: 
            self.dx = -self.dx
        elif self.rect.right > window.width and self.dx > 0: 
            self.dx = -self.dx
            
        if self.rect.top < 0  and self.dy > 0:  
            self.dy = -self.dy
        elif self.rect.bottom > window.height and self.dy < 0:
            self.dy = -self.dy

    def kill(self):
        self.sound.play()
        super().kill()
        
    def update(self):
        window_rec = self.window.get_rect()
        if not window_rec.contains(self.rect):
            self.change_direction(window_rec)

        self.rect.x += self.dx * self.velocity
        self.rect.y -= self.dy * self.velocity

    def convert_color(self, color: str):
        if not color:
            return (255, 255, 255)

        color = color.lstrip('#')
        if not color or len(color) != 6:
            return (255, 255, 255)

        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
