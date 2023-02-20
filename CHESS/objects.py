import pygame
from pygame import gfxdraw
from constants import *

pygame.init()

font = pygame.font.Font('assets/Hack-Bold.ttf', FONT_SIZE)

sprite_path= 'assets/pieces/vector/'

white_pieces = {
    'pawn' : pygame.image.load(f'{sprite_path}wp.png'),
    'knight' : pygame.image.load(f'{sprite_path}wn.png'),
    'bishop' : pygame.image.load(f'{sprite_path}wb.png'),
    'rook' : pygame.image.load(f'{sprite_path}wr.png'),
    'queen' : pygame.image.load(f'{sprite_path}wq.png'),
    'king' : pygame.image.load(f'{sprite_path}wk.png')
}

black_pieces = {
    'pawn' : pygame.image.load(f'{sprite_path}bp.png'),
    'knight' : pygame.image.load(f'{sprite_path}bn.png'),
    'bishop' : pygame.image.load(f'{sprite_path}bb.png'),
    'rook' : pygame.image.load(f'{sprite_path}br.png'),
    'queen' : pygame.image.load(f'{sprite_path}bq.png'),
    'king' : pygame.image.load(f'{sprite_path}bk.png')
}

for key, image in white_pieces.items():
    white_pieces[key] = pygame.transform.smoothscale(image, (PIECE_SIZE,PIECE_SIZE))
for key, image in black_pieces.items():
    black_pieces[key] = pygame.transform.smoothscale(image, (PIECE_SIZE,PIECE_SIZE))


class Square:
    def __init__(self, x, y , square_size, colour):
        self.x = x
        self.y = y
        self.square_size = square_size
        self.colour = colour

        self.transparent_surface = pygame.Surface((square_size,square_size), pygame.SRCALPHA)
        self.set_surface()

    def set_surface(self):
        self.transparent_surface.fill(self.colour)

    def draw(self, surface):
        surface.blit(self.transparent_surface, (self.x, self.y))


class EffectSquare(Square):
    def __init__(self, x, y , square_size, colour):
        super().__init__(x, y, square_size, colour)

    def set_position(self, x, y):
        self.x = x
        self.y = y


class MovePreviewMarker(Square):
    def __init__(self, x, y , square_size, radius, colour):
        self.radius = radius
        self.visible = False
        super().__init__(x, y, square_size, colour)

    def set_surface(self):
        gfxdraw.aacircle(self.transparent_surface, int(self.square_size/2), int(self.square_size/2), self.radius, self.colour)
        gfxdraw.filled_circle(self.transparent_surface, int(self.square_size/2), int(self.square_size/2), self.radius, self.colour)

    def draw(self, surface):
        surface.blit(self.transparent_surface, (self.x, self.y))


class CapturePreviewMarker(Square):
    def __init__(self, x, y , square_size, radius, width, colour):
        self.radius = radius
        self.width = width
        self.visible = False
        super().__init__(x, y, square_size, colour)

    def set_surface(self):
        gfxdraw.aacircle(self.transparent_surface, int(self.square_size/2), int(self.square_size/2), self.radius, self.colour)
        gfxdraw.filled_circle(self.transparent_surface, int(self.square_size/2), int(self.square_size/2), self.radius, self.colour)
        #hollow out
        gfxdraw.aacircle(self.transparent_surface, int(self.square_size/2), int(self.square_size/2), int(self.radius-self.width/2), TRANSPARENT)
        gfxdraw.filled_circle(self.transparent_surface, int(self.square_size/2), int(self.square_size/2), int(self.radius-self.width/2), TRANSPARENT)

    def draw(self, surface):
        surface.blit(self.transparent_surface, (self.x, self.y))


class Game:
    def __init__(self, width, height, square_size, turn, white_can_castle, black_can_castle):
        self.width = width
        self.height = height
        self.square_size = square_size
        self.turn = turn

        self.white_can_castle = white_can_castle
        self.black_can_castle = black_can_castle

        self.squares = self.create_squares()
        self.board = self.create_empty_board()
        self.move_preview_markers = self.create_move_preview_markers()
        self.capture_preview_markers = self.create_capture_preview_markers()
        self.hover_square = EffectSquare(SCREEN_WIDTH, SCREEN_HEIGHT, self.square_size, HOVER_COLOUR)
        self.highlight_square = EffectSquare(SCREEN_WIDTH, SCREEN_HEIGHT, self.square_size, HIGHLIGHT_COLOUR)

    def move_piece(self, piece_x, piece_y, target_x, target_y):
        piece = self.get_piece(piece_x, piece_y)
        self.set_piece(piece_x, piece_y, None) #clear piece from original square
        self.set_piece(target_x, target_y, piece) #set piece in new square

    def create_squares(self):
        return [Square(x*self.square_size, y*self.square_size, self.square_size, WHITE_SQUARE_COLOUR if (x+y)%2 == 0 else BLACK_SQUARE_COLOUR) for x in range(self.width) for y in range(self.height)]

    def create_empty_board(self):
        return [[None for x in range(self.width)] for y in range(self.height)]

    def create_move_preview_markers(self):
        return [[MovePreviewMarker(x*self.square_size, y*self.square_size, self.square_size, MOVE_PREVIEW_MARKER_SIZE, MOVE_PREVIEW_MARKER_COLOUR) for x in range(self.width)] for y in range(self.height)]

    def create_capture_preview_markers(self):
        return [[CapturePreviewMarker(x*self.square_size, y*self.square_size, self.square_size, CAPTURE_PREVIEW_MARKER_SIZE, CAPTURE_PREVIEW_MARKER_WIDTH, CAPTURE_PREVIEW_MARKER_COLOUR) for x in range(self.width)] for y in range(self.height)]

    def get_piece(self, x, y):
        return self.board[y][x]

    def get_piece_colour(self, x, y):
        try:
            return self.get_piece(x,y).colour
        except:
            return None

    def set_piece(self, x, y, piece):
        try:
            self.board[y][x] = piece
        except IndexError:
            print(f'Error: {piece.__class__.__name__} at position {x}, {y} was outside of board and was not placed')

    def get_marker(self, x, y, is_capture):
        if is_capture:
            return self.capture_preview_markers[y][x]
        return self.move_preview_markers[y][x]

    def get_move_type(self, x, y):
        target_colour = self.get_piece_colour(x,y)
        if target_colour == self.turn or target_colour == None:
            return (x, y, False)
        else:
            return (x, y, True)

    def inside_board(self, x, y):
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def switch_turn(self):
        self.turn = BLACK if self.turn == WHITE else WHITE
        print(f'{"WHITE" if self.turn == WHITE else "BLACK"}\'s turn')
        self.flip_board()

    def flip_board(self):
        self.board.reverse()
        for row in self.board:
            row.reverse()

    def get_directional_moves(self, directions, x, y):
        possible_moves = []

        for direction in directions:
            new_x = x + direction[0]
            new_y = y + direction[1]

            # while inside board and empty
            while self.inside_board(new_x, new_y) and self.get_piece_colour(new_x, new_y) == None:
                possible_moves.append((new_x, new_y, False))
                new_x += direction[0]
                new_y += direction[1]

            # add captures
            if self.inside_board(new_x, new_y) and self.get_piece_colour(new_x, new_y) != self.turn:
                possible_moves.append((new_x, new_y, True))

        return possible_moves

    def get_set_moves(self, moves, x, y):
        possible_moves = []

        for move in moves:
            new_x = x + move[0]
            new_y = y + move[1]

            #skip if moving outside board
            if self.inside_board(new_x, new_y) == False:
                continue

            target_colour = self.get_piece_colour(new_x, new_y)

            #skip if same colour piece
            if target_colour == self.turn:
                continue

            #is capture
            if target_colour != None:
                possible_moves.append((new_x, new_y, True))
            else:
                possible_moves.append((new_x, new_y, False))

        return possible_moves

    def draw(self, surface):
        #draw squares
        for square in self.squares:
            square.draw(surface)

        #draw effect squares
        self.hover_square.draw(surface)
        self.highlight_square.draw(surface)


        for y in range(self.height):
            for x in  range(self.width):

                #draw preview capture markers
                capture_marker = self.get_marker(x,y,True)
                if capture_marker.visible:
                    capture_marker.draw(surface)

                #draw pieces
                piece = self.get_piece(x,y)
                if piece is not None:
                    piece.draw(surface, x*self.square_size, y*self.square_size)

                #draw preview move markers
                move_marker = self.get_marker(x,y,False)
                if move_marker.visible:
                    move_marker.draw(surface)


class Player:
    def __init__(self, game):
        self.game = game

        self.selected_square = None
        self.selected_piece_colour = None
        self.selected_piece_moves = []

    def select_square(self, square):
        self.selected_square = square
        self.selected_piece_colour = self.game.get_piece_colour(square[0], square[1])

        self.game.highlight_square.set_position(square[0]*self.game.square_size, square[1]*self.game.square_size)

        #if one of current players pieces, draw preview marker
        if self.selected_piece_colour == self.game.turn:
            self.selected_piece_moves = self.game.get_piece(square[0], square[1]).get_possible_moves(self.game, square[0], square[1])
            for move in self.selected_piece_moves:
                self.game.get_marker(move[0], move[1], move[2]).visible = True

    def deselect_square(self):
        self.selected_square = None
        self.selected_piece_colour = None

        self.game.highlight_square.set_position(SCREEN_WIDTH, SCREEN_HEIGHT)

        for move in self.selected_piece_moves:
            self.game.get_marker(move[0], move[1], move[2]).visible = False
        self.selected_piece_moves = [] #clear

    def update(self, mouse_position, is_mouse_down, is_mouse_up):
        position = self.screen_to_square(mouse_position)
        square = self.game.get_move_type(position[0], position[1])

        if is_mouse_down:
            if self.select_square == None:
                self.select_square(square)
            elif square == self.selected_square:
                self.deselect_square()
            elif square not in self.selected_piece_moves:
                self.deselect_square()
                self.select_square(square)

        elif is_mouse_up:
            if self.selected_square != square and self.selected_piece_colour == self.game.turn and square in self.selected_piece_moves:
                self.make_move(square)

        self.game.hover_square.set_position(position[0]*self.game.square_size, position[1]*self.game.square_size)

    def make_move(self, target):
        self.game.move_piece(self.selected_square[0], self.selected_square[1], target[0], target[1])
        self.game.switch_turn()
        self.deselect_square()

    def screen_to_square(self, mouse_position):
        return ((int(mouse_position[0]/self.game.square_size),int(mouse_position[1]/self.game.square_size)))


class Piece:
    def __init__(self, sprite, colour, value):
        self.sprite = sprite
        self.colour = colour
        self.value = value

    def draw(self, surface, x, y):
        surface.blit(self.sprite, (x,y))

    def get_possible_moves(self, game, x, y):
        return

    def is_possible_move(self, game, piece_x , piece_y, target_x, target_y):
        if (target_x, target_y) in self.get_possible_moves(game, piece_x, piece_y):
            return True
        else:
            return False

class Pawn(Piece):
    def __init__(self, colour):
        super().__init__(white_pieces['pawn'] if colour==WHITE else black_pieces['pawn'], colour, 1)

    def get_possible_moves(self, game, x, y):
        direction = -1 #relies on board being flipped
        possible_moves = []

        new_x = x
        new_y = y + direction

        #forward one
        if game.inside_board(new_x, new_y) and game.get_piece_colour(new_x, new_y) == None:
            possible_moves.append((new_x, new_y, False))
        #forward two
        if y == game.height - 2 and len(possible_moves) > 0:
            new_y = y + direction*2
            if game.inside_board(new_x, new_y) and game.get_piece_colour(new_x, new_y) == None:
                possible_moves.append((new_x, new_y, False))

        #captures
        new_x = x - 1
        new_y = y + direction
        if game.inside_board(new_x, new_y) and game.get_piece_colour(new_x, new_y) != None and game.get_piece_colour(new_x, new_y) != game.turn:
            possible_moves.append((new_x, new_y, True))

        new_x = x + 1
        new_y = y + direction
        if game.inside_board(new_x, new_y) and game.get_piece_colour(new_x, new_y) != None and game.get_piece_colour(new_x, new_y) != game.turn:
            possible_moves.append((new_x, new_y, True))

        #TODO enpassant, and promotion

        return possible_moves

class Knight(Piece):
    def __init__(self, colour):
        super().__init__(white_pieces['knight'] if colour==WHITE else black_pieces['knight'], colour, 3)

    def get_possible_moves(self, game, x, y):
        moves = [(2,-1),(2,1),(-1,-2),(1,-2),(-2,-1),(-2,1),(1,2),(-1,2)]
        return game.get_set_moves(moves, x, y)

class Bishop(Piece):
    def __init__(self, colour):
        super().__init__(white_pieces['bishop'] if colour==WHITE else black_pieces['bishop'], colour, 3)

    def get_possible_moves(self, game, x, y):
        directions = [(-1,-1),(-1,1),(1,-1),(1,1)]
        return game.get_directional_moves(directions, x, y)

class Rook(Piece):
    def __init__(self, colour):
        super().__init__(white_pieces['rook'] if colour==WHITE else black_pieces['rook'], colour, 5)

    def get_possible_moves(self, game, x, y):
        directions = [(0,-1),(-1,0),(1,0),(0,1)]
        return game.get_directional_moves(directions, x, y)

class Queen(Piece):
    def __init__(self, colour):
        super().__init__(white_pieces['queen'] if colour==WHITE else black_pieces['queen'], colour, 9)

    def get_possible_moves(self, game, x, y):
        directions = [(-1,-1),(-1,1),(1,-1),(1,1),(0,-1),(-1,0),(1,0),(0,1)]
        return game.get_directional_moves(directions, x, y)

class King(Piece):
    def __init__(self, colour):
        super().__init__(white_pieces['king'] if colour==WHITE else black_pieces['king'], colour, 999)

    def get_possible_moves(self, game, x, y):
        moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
        #TODO add castling
        return game.get_set_moves(moves, x, y)
