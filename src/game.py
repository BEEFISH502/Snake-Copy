import pygame
from pathlib import Path
import sys
import random

BASE_DIR = Path(__file__).resolve().parent.parent

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1280, 720))
        self.pygame = pygame.init()
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.running = False
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        self.title_font = pygame.font.Font(BASE_DIR / "assets" / "SuperpixRegular-MV6mx.otf", 100)
        self.font = pygame.font.Font(BASE_DIR / "assets" / "SuperpixRegular-MV6mx.otf", 40)
        self.game_music_tracks = [
            BASE_DIR / "assets" / "play_music_1.mp3",
            BASE_DIR / "assets" / "play_music_2.mp3",
            BASE_DIR / "assets" / "play_music_3.mp3",
            BASE_DIR / "assets" / "play_music_4.mp3",
            BASE_DIR / "assets" / "play_music_5.mp3"

        ]
        self.MUSIC_END = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.MUSIC_END)
        self.try_again_tracks = [
            BASE_DIR / "assets" / "retry_music_1.mp3",
            BASE_DIR / "assets" / "retry_music_2.mp3",

        ]


    def run(self):
        self.dt = self.clock.tick(60) / 1000
        self.screen.fill("black")


    def quit_game(self, state):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if event.type == self.MUSIC_END and state.game_playing_state:
                track = random.choice(self.game_music_tracks)
                pygame.mixer.music.load(track)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play()

    def game_init(self,state, screen):
        self.running = True
        while self.running:
            self.run()
            screen.draw_screen()
            pygame.display.flip()
            self.quit_game(state)


class GameState:
    def __init__(self):
        self.menu_state = False
        self.game_playing_state = False
        self.end_menu_state = False
        self.current_state = ""


    def menu(self):
        if self.menu_state and not self.game_playing_state and not self.end_menu_state:
            return "Menu"
        else:
            return None


    def game_playing(self):
        if self.game_playing_state and not self.menu_state and not self.end_menu_state:
            return "Game playing"
        else:
            return None

    def game_over(self):
        if self.end_menu_state and not self.game_playing_state and not self.menu_state:
            return "Game over"
        else:
            return None

    def set_state(self):
        states = [
            self.menu(),
            self.game_playing(),
            self.game_over()
        ]
        if states:
            self.current_state = None
            for state in states:
                if state:
                    self.current_state = state
        return



    def check_game_state(self):
        self.set_state()
        current_state = self.current_state
        return f'State = "{current_state}"'

    def start_game(self):
        self.menu_state = True
        self.check_game_state()
        print(self.current_state)


class Screen:
    def __init__(self, game, state, inputs, player, food):
        self.game = game
        self.state = state
        self.inputs = inputs
        self.player = player
        self.food = food
        self.blink_timer = 0
        self.show_text = True
        self.menu_music_started = False
        self.end_track_started = False

    def draw_menu(self):
        if self.state.menu_state:
            if not self.menu_music_started:
                pygame.mixer.music.load(BASE_DIR / "assets" / "menu_sound.wav")
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                self.menu_music_started = True
            self.blink_timer = self.blink_timer + self.game.dt
            if self.blink_timer >= 0.25:
                self.show_text = not self.show_text
                self.blink_timer = 0

            title_text = self.game.title_font.render("SNAKE", False, "white")
            self.game.screen.blit(title_text, (self.game.screen.get_width() / 3.3,
                                          self.game.screen.get_height() / 4))

            if self.show_text:
                menu_text = self.game.font.render("PRESS  SPACE  TO  START", False, "white")
                self.game.screen.blit(menu_text, (self.game.screen.get_width() / 6.5,
                                             self.game.screen.get_height() / 1.5))
        if self.inputs.menu_input():
            pygame.mixer.music.fadeout(1000)
            self.menu_music_started = False
            self.state.game_playing_state = True
            self.state.menu_state = False

    def draw_game(self):
        if self.state.game_playing_state:
            self.inputs.player_input(self.player, self.game.dt)
            self.player.draw_player()
            self.player.score_text()
            self.player.player_died()

            self.food.check_food_collision()
            self.food.update_food(self.game.dt)
            self.food.draw_food()

    def draw_game_over(self):
        if not self.end_track_started:
            pygame.mixer.music.fadeout(1000)
            self.end_track_started = True
            pygame.mixer.music.load(random.choice(self.game.try_again_tracks))
            pygame.mixer.music.play()
        if self.state.end_menu_state:
            self.blink_timer = self.blink_timer + self.game.dt
            if self.blink_timer >= 0.25:
                self.show_text = not self.show_text
                self.blink_timer = 0

            end_text = self.game.font.render("You died idiot", True, "white")
            try_again = self.game.font.render("Try again?", False, "white")
            y_n = self.game.font.render("Yes / No", False, "white")
            self.game.screen.blit(end_text, (self.game.screen.get_width() / 3.6, self.game.screen.get_height() / 4))
            self.game.screen.blit(try_again, (self.game.screen.get_width() / 3.0, self.game.screen.get_height() / 2.2))

            if self.show_text:
                self.game.screen.blit(y_n, (self.game.screen.get_width() / 2.75, self.game.screen.get_height() / 1.5))

            choice = self.inputs.end_menu_input()
            if choice == "yes":
                pygame.mixer.music.fadeout(1000)
                self.player.reset()
                self.state.game_playing_state = True
                self.state.end_menu_state = False

            elif choice == "no":
                pygame.quit()
                sys.exit()

    def draw_screen(self):
        if self.state.menu_state:
            self.draw_menu()
        elif self.state.game_playing_state:
            self.draw_game()
        elif self.state.end_menu_state:
            self.draw_game_over()


class Player:
    def __init__(self, game, state):
        self.game = game
        self.state = state
        self.position = pygame.Vector2(game.screen.get_width() / 2, game.screen.get_height() / 2)
        self.speed = 180
        self.score = 0
        self.health = 100

    def draw_player(self):
        pygame.draw.rect(self.game.screen, "white", (self.position.x, self.position.y, 10,10))

    def score_text(self):
        score_text = self.game.font.render(f'Score: {self.score}', False, "white")
        self.game.screen.blit(score_text, (0,0))

    def player_died(self):
        if (
                self.position.x < 10 or
                self.position.x > 1270 or
                self.position.y < 10 or
                self.position.y > 710
        ):
            self.state.game_playing_state = False
            self.health = 0
            self.state.end_menu_state = True
        else:
            self.state.end_menu_state = False

    def reset(self):
        self.position = pygame.Vector2(self.game.screen.get_width() / 2, self.game.screen.get_height() / 2)
        self.score = 0
        self.health = 100


class Inputs:
    def __init__(self):
        self.dt = 0
    @staticmethod
    def player_input(player, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            player.position.y -= player.speed * dt
        if keys[pygame.K_s]:
            player.position.y += player.speed * dt
        if keys[pygame.K_a]:
            player.position.x -= player.speed * dt
        if keys[pygame.K_d]:
            player.position.x += player.speed * dt


    @staticmethod
    def menu_input():
        play = pygame.key.get_pressed()
        return play[pygame.K_SPACE]


    @staticmethod
    def end_menu_input():
        again = pygame.key.get_pressed()
        if again[pygame.K_y]:
            return "yes"
        elif again[pygame.K_n]:
            return "no"

        return None


class Food:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.position = pygame.Vector2(random.randint(0, self.game.screen.get_width() - 10),
                                   random.randint(0, self.game.screen.get_height() - 10))
        self.exists = True
        self.direction = random.choice([
            pygame.Vector2(100, 0),
            pygame.Vector2(-100, 0),
            pygame.Vector2(0, 100),
            pygame.Vector2(0, -100)
        ])
        self.direction_timer = 0

    def draw_food(self):
        pygame.draw.rect(self.game.screen, "green", (self.position.x, self.position.y, 8,8))

    def randomize_food(self):
        self.position = pygame.Vector2(random.randint(0, self.game.screen.get_width() - 10),
                                   random.randint(0, self.game.screen.get_height() - 10))
        self.choose_food_direction()
        self.exists = True

    def check_food_collision(self):
        player_rect = pygame.Rect(self.player.position.x, self.player.position.y, 10,10)
        food_rect = pygame.Rect(self.position.x, self.position.y, 8,8)

        if player_rect.colliderect(food_rect):
            self.exists = False
            self.randomize_food()
            self.player.score += 10
            return True

        return False

    def update_food(self, dt):
        self.direction_timer += dt
        if self.direction_timer >=  random.uniform(1,3):
            self.choose_food_direction()
            self.direction_timer = 0

        self.position += self.direction * dt
        if self.position.x <= 10 or self.position.x >= 1270:
            self.direction.x *= -1
        if self.position.y <= 10 or self.position.y >= 710:
            self.direction.y *= -1

    def choose_food_direction(self):
        self.direction = random.choice([
            pygame.Vector2(100, 100),
            pygame.Vector2(-100, 100),
            pygame.Vector2(-100, -100),
            pygame.Vector2(100, -100)
        ])

    def score(self):
        if self.check_food_collision():
            self.score += 10
        return self.score

def main():
    game = Game()
    state = GameState()
    inputs = Inputs()
    player = Player(game, state)
    food = Food(game, player)
    screen = Screen(game, state, inputs, player, food)
    state.start_game()
    game.game_init(state, screen)



if __name__ == '__main__':
    main()





