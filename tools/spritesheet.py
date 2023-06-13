import pygame


class SpriteSheet:
    def __init__(self, file_path: str, sprite_dimension: tuple, resize_dimension: tuple = None, smooth_scale: bool = False) -> None:
        '''Holds a spritesheet and associated sprite surfaces'''
        self.file_path = file_path
        self.sprite_dimension = sprite_dimension
        self.resize_dimension = resize_dimension
        self.smooth_scale = smooth_scale

        self.sprite_sheet = pygame.image.load(file_path).convert_alpha()

    def slice_sheet(self) -> dict[pygame.Surface]:
        '''Returns a dictionary of all sprites in the sprite sheet'''
        sprites = {}

        rows = int(self.sprite_sheet.get_height()/self.sprite_dimension[1])
        columns = int(self.sprite_sheet.get_width()/self.sprite_dimension[0])

        for y in range(rows):
            for x in range(columns):
                sprites[int(y*columns+x)] = self.get_sprite(x*self.sprite_dimension[0], y*self.sprite_dimension[1])

        return sprites

    def get_sprite(self, x: int, y: int) -> pygame.Surface:
        '''Returns a pygame surface with sprite at location (x, y) drawn on it'''
        new_sprite = pygame.Surface((self.sprite_dimension[0], self.sprite_dimension[1]), pygame.SRCALPHA).convert_alpha()
        new_sprite.blit(self.sprite_sheet, (0,0), (x, y, self.sprite_dimension[0], self.sprite_dimension[1]))
        if self.resize_dimension is not None:
            if self.smooth_scale:
                new_sprite = pygame.transform.smoothscale(new_sprite, self.resize_dimension)
            else:
                new_sprite = pygame.transform.scale(new_sprite, self.resize_dimension)
        return new_sprite
