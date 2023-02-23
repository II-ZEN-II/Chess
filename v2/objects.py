import pygame
from pygame import gfxdraw
from constants import *

pygame.init()

sprite_path = 'assets/pieces/vector/'

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
    def __init__(self, width, height, square_size, turn, white_castling_rights, black_castling_rights, en_passant_target, half_moves, full_moves):
        self.width = width
        self.height = height
        self.square_size = square_size
        self.turn = turn
        self.white_castling_rights = white_castling_rights
        self.black_castling_rights = black_castling_rights
        self.en_passant_target = en_passant_target
        self.half_moves = half_moves
        self.full_moves = full_moves

        self.white_pieces = []
        self.white_king = None
        self.black_pieces = []
        self.black_king = None

        self.in_check = False

        self.board = self.create_empty_board()
        self.squares = self.create_squares()
        self.move_preview_markers = self.create_move_preview_markers()
        self.capture_preview_markers = self.create_capture_preview_markers()
        self.hover_square = EffectSquare(SCREEN_WIDTH, SCREEN_HEIGHT, self.square_size, HOVER_COLOUR)
        self.highlight_square = EffectSquare(SCREEN_WIDTH, SCREEN_HEIGHT, self.square_size, HIGHLIGHT_COLOUR)

        self.last_move_from = EffectSquare(SCREEN_WIDTH, SCREEN_HEIGHT, self.square_size, LAST_MOVE_FROM_COLOUR)
        self.last_move_to = EffectSquare(SCREEN_WIDTH, SCREEN_HEIGHT, self.square_size, LAST_MOVE_TO_COLOUR)

    def start_player_turn(self):
        self.in_check = self.is_in_check(self.turn)
        print(f'in_check: {self.in_check}')

        pieces = self.white_pieces if self.turn == WHITE else self.black_pieces
        player_moves = []
        for piece in pieces:
            if piece.is_dead == False:
                valid_moves = piece.get_valid_moves(self)
                piece.valid_moves = valid_moves
                player_moves += valid_moves

        if len(player_moves) == 0:
            print('GAMEOVER')
            if self.in_check:
                print(f'CHECKMATED')
            else:
                print('STALEMATE')

    def perform_move(self, piece_x, piece_y, target_x, target_y, is_capture, special_move):
        piece = self.get_piece(piece_x, piece_y)
        self.last_move_from.set_position(piece_x*self.square_size, piece_y*self.square_size)
        self.set_piece(piece_x, piece_y, None) #clear piece from original square

        target = self.get_piece(target_x, target_y)
        if is_capture:
            target.is_dead = True

        self.set_piece(target_x, target_y, piece) #set piece in new square
        self.last_move_to.set_position(target_x*self.square_size, target_y*self.square_size)
        piece.set_position(target_x, target_y)

        if special_move is None:
            self.en_passant_target = None
        else:
            match special_move:
                case 'en_passant':
                    print('en passant')
                    capture_x = self.en_passant_target[0]
                    capture_y = self.en_passant_target[1]-self.turn
                    capture_target = self.get_piece(capture_x, capture_y)
                    capture_target.is_dead = True
                    self.set_piece(capture_x, capture_y, None)
                    self.en_passant_target = None
                case 'double_push':
                    print('double pawn push')
                    self.en_passant_target = (target_x, target_y - self.turn)
                case 'promote':
                    print('promotion')
                    self.en_passant_target = None
                    self.white_pieces.remove(piece) if piece.colour == WHITE else self.black_pieces.remove(piece)
                    self.place_initial_piece(target_x, target_y, Queen, self.turn)

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
        self.board[y][x] = piece

    def place_initial_piece(self, x, y, piece, colour):
        try:
            new_piece = piece(x, y, colour)
            #save new_piece to correct array
            self.white_pieces.append(new_piece) if colour == WHITE else self.black_pieces.append(new_piece)

            #place new_piece on board
            self.set_piece(x, y, new_piece)

            if piece == King:
                if colour == WHITE:
                    self.white_king = new_piece
                else:
                    self.black_king = new_piece
        except IndexError:
            print(f'Error: {piece.__class__.__name__} at position {x}, {y} is outside of board and was not placed')

    def get_marker(self, x, y, is_capture):
        if is_capture:
            return self.capture_preview_markers[y][x]
        return self.move_preview_markers[y][x]

    def inside_board(self, x, y):
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def switch_turn(self):
        self.turn = BLACK if self.turn == WHITE else WHITE
        print(f'{"WHITE" if self.turn == WHITE else "BLACK"}\'s turn')

    def is_in_check(self, colour):
        king = self.white_king if colour == WHITE else self.black_king
        opponent_pieces = self.black_pieces if colour == WHITE else self.white_pieces
        for piece in opponent_pieces:
            if piece.is_dead == False and self.is_in_possible_moves((king.x, king.y), piece.get_possible_moves(self)):
                return True
        return False

    def get_directional_moves(self, directions, x, y, colour):
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
            if self.inside_board(new_x, new_y) and self.get_piece_colour(new_x, new_y) != colour:
                possible_moves.append((new_x, new_y, True))

        return possible_moves

    def get_set_moves(self, moves, x, y, colour):
        possible_moves = []

        for move in moves:
            new_x = x + move[0]
            new_y = y + move[1]

            #skip if moving outside board
            if self.inside_board(new_x, new_y) == False:
                continue

            target_colour = self.get_piece_colour(new_x, new_y)

            #skip if same colour piece
            if target_colour == colour:
                continue

            #is capture
            if target_colour != None:
                possible_moves.append((new_x, new_y, True))
            else:
                possible_moves.append((new_x, new_y, False))

        return possible_moves

    def is_in_possible_moves(self, position, possible_moves):
        for move in possible_moves:
            if position[0] == move[0] and position[1] == move[1]:
                return True
        return False

    def get_move(self, position, possible_moves):
        for move in possible_moves:
            if move[0] == position[0] and move[1] == position[1]:
                return move
        return None

    def is_valid_move(self, piece_x, piece_y, target_x, target_y, is_capture, special_move):
        valid = False

        #perform move
        piece = self.get_piece(piece_x, piece_y)
        target = self.get_piece(target_x, target_y)

        if is_capture:
            target.is_dead = True

        self.set_piece(piece_x, piece_y, None) #clear piece from original square
        self.set_piece(target_x, target_y, piece) #set piece in new square
        piece.set_position(target_x, target_y)

        if special_move == 'en_passant':
            capture_x = self.en_passant_target[0]
            capture_y = self.en_passant_target[1]-self.turn
            capture_target = self.get_piece(capture_x, capture_y)
            capture_target.is_dead = True
            self.set_piece(capture_x, capture_y, None)

        #check if in check (if no then add)
        if not self.is_in_check(self.turn):
            valid = True

        #un-perform move
        if is_capture:
            target.is_dead = False

        self.set_piece(piece_x, piece_y, piece) #set piece in original square
        self.set_piece(target_x, target_y, target) #set target in original square
        piece.set_position(piece_x, piece_y)

        if special_move == 'en_passant':
            capture_target.is_dead = False
            self.set_piece(capture_x, capture_y, capture_target)

        return valid

    def draw(self, surface):
        #draw squares
        for square in self.squares:
            square.draw(surface)

        #draw last move squares
        self.last_move_from.draw(surface)
        self.last_move_to.draw(surface)

        #draw effect squares
        self.hover_square.draw(surface)
        self.highlight_square.draw(surface)

        for piece in self.white_pieces:
            piece.draw(surface, piece.x*self.square_size, piece.y*self.square_size)
        for piece in self.black_pieces:
            piece.draw(surface, piece.x*self.square_size, piece.y*self.square_size)

        for y in range(self.height):
            for x in  range(self.width):

                #draw preview capture markers
                capture_marker = self.get_marker(x,y,True)
                if capture_marker.visible:
                    capture_marker.draw(surface)

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

    def select_square(self, position):
        self.selected_square = position
        self.selected_piece_colour = self.game.get_piece_colour(position[0], position[1])

        self.game.highlight_square.set_position(position[0]*self.game.square_size, position[1]*self.game.square_size)

        #if one of current players pieces, draw preview marker
        if self.selected_piece_colour == self.game.turn:
            self.selected_piece_moves = self.game.get_piece(position[0], position[1]).valid_moves
            for move in self.selected_piece_moves:
                self.game.get_marker(move[0], move[1], move[2]).visible = True

    def deselect_square(self):
        self.selected_square = None
        self.selected_piece_colour = None

        self.game.highlight_square.set_position(SCREEN_WIDTH, SCREEN_HEIGHT)

        for move in self.selected_piece_moves:
            self.game.get_marker(move[0], move[1], move[2]).visible = False
        self.selected_piece_moves = [] #clear

    def update(self, surface, mouse_position, is_mouse_down, is_mouse_up):
        position = self.screen_to_square(mouse_position)

        if is_mouse_down:
            if self.selected_square == None:
                self.select_square(position)
            elif position == self.selected_square:
                self.deselect_square()
            elif not self.game.is_in_possible_moves(position, self.selected_piece_moves):
                self.deselect_square()
                self.select_square(position)

            self.game.draw(surface)

        elif is_mouse_up:
            if position != self.selected_square and self.game.is_in_possible_moves(position, self.selected_piece_moves):
                self.make_move(self.game.get_move(position, self.selected_piece_moves))

            self.game.draw(surface)

        #self.game.hover_square.set_position(position[0]*self.game.square_size, position[1]*self.game.square_size)

    def make_move(self, move):
        self.game.perform_move(self.selected_square[0], self.selected_square[1], move[0], move[1], move[2], move[3] if len(move) > 3 else None)
        self.deselect_square()
        self.game.switch_turn()
        self.game.start_player_turn()

    def screen_to_square(self, mouse_position):
        return ((int(mouse_position[0]/self.game.square_size),int(mouse_position[1]/self.game.square_size)))


class Piece:
    def __init__(self, sprite, x, y, colour, value):
        self.sprite = sprite
        self.x = x
        self.y = y
        self.colour = colour
        self.value = value
        self.valid_moves = []

        self.is_dead = False

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def draw(self, surface, x, y):
        if self.is_dead == False:
            surface.blit(self.sprite, (x,y))

    def get_possible_moves(self, game):
        # to be overriden by Parent class
        return

    def get_valid_moves(self, game):
        #get all possible moves
        possible_moves = self.get_possible_moves(game)
        valid = []
        for move in possible_moves:
            if game.is_valid_move(self.x, self.y, move[0], move[1], move[2], move[3] if len(move) > 3 else None):
                valid.append(move)

        return valid

class Pawn(Piece):
    def __init__(self, x, y, colour):
        super().__init__(white_pieces['pawn'] if colour==WHITE else black_pieces['pawn'], x, y, colour, 1)

    def get_possible_moves(self, game):
        direction = self.colour
        possible_moves = []

        new_x = self.x
        new_y = self.y + direction
        #forward one
        if game.inside_board(new_x, new_y) and game.get_piece_colour(new_x, new_y) == None:
            if new_y == game.height - 1 and direction == BLACK or new_y == 0 and direction == WHITE:
                possible_moves.append((new_x, new_y, False, 'promote'))
            else:
                possible_moves.append((new_x, new_y, False))

            #forward two
            if self.y == game.height - 2 and direction == WHITE or self.y == 1 and direction == BLACK:
                new_y = self.y + direction*2

                if game.inside_board(new_x, new_y) and game.get_piece_colour(new_x, new_y) == None:
                    possible_moves.append((new_x, new_y, False, 'double_push'))

        #captures
        new_x = self.x - 1
        new_y = self.y + direction
        if game.inside_board(new_x, new_y) and game.get_piece_colour(new_x, new_y) != None and game.get_piece_colour(new_x, new_y) != self.colour:
            if new_y == game.height - 1 and direction == BLACK or new_y == 0 and direction == WHITE:
                possible_moves.append((new_x, new_y, True, 'promote'))
            else:
                possible_moves.append((new_x, new_y, True))
        elif (new_x,new_y) == game.en_passant_target:
            possible_moves.append((new_x, new_y, False, 'en_passant'))

        new_x = self.x + 1
        new_y = self.y + direction
        if game.inside_board(new_x, new_y) and game.get_piece_colour(new_x, new_y) != None and game.get_piece_colour(new_x, new_y) != self.colour:
            if new_y == game.height - 1 and direction == BLACK or new_y == 0 and direction == WHITE:
                possible_moves.append((new_x, new_y, True, 'promote'))
            else:
                possible_moves.append((new_x, new_y, True))
        elif (new_x,new_y) == game.en_passant_target:
            possible_moves.append((new_x, new_y, False, 'en_passant'))

        return possible_moves

class Knight(Piece):
    def __init__(self, x, y, colour):
        super().__init__(white_pieces['knight'] if colour==WHITE else black_pieces['knight'], x, y, colour, 3)

    def get_possible_moves(self, game):
        moves = [(2,-1),(2,1),(-1,-2),(1,-2),(-2,-1),(-2,1),(1,2),(-1,2)]
        return game.get_set_moves(moves, self.x, self.y, self.colour)

class Bishop(Piece):
    def __init__(self, x, y, colour):
        super().__init__(white_pieces['bishop'] if colour==WHITE else black_pieces['bishop'], x, y, colour, 3)

    def get_possible_moves(self, game):
        directions = [(-1,-1),(-1,1),(1,-1),(1,1)]
        return game.get_directional_moves(directions, self.x, self.y, self.colour)

class Rook(Piece):
    def __init__(self, x, y, colour):
        super().__init__(white_pieces['rook'] if colour==WHITE else black_pieces['rook'], x, y, colour, 5)

    def get_possible_moves(self, game):
        directions = [(0,-1),(-1,0),(1,0),(0,1)]
        return game.get_directional_moves(directions, self.x, self.y, self.colour)

class Queen(Piece):
    def __init__(self, x, y, colour):
        super().__init__(white_pieces['queen'] if colour==WHITE else black_pieces['queen'], x, y, colour, 9)

    def get_possible_moves(self, game):
        directions = [(-1,-1),(-1,1),(1,-1),(1,1),(0,-1),(-1,0),(1,0),(0,1)]
        return game.get_directional_moves(directions, self.x, self.y, self.colour)

class King(Piece):
    def __init__(self, x, y, colour):
        super().__init__(white_pieces['king'] if colour==WHITE else black_pieces['king'], x, y, colour, 999)
    #TODO add castling
    def get_possible_moves(self, game):
        moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]

        return game.get_set_moves(moves, self.x, self.y, self.colour)
