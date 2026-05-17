import pygame
from pathlib import Path
import random
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        self.pygame = pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((1280, 720))
        self.font = pygame.font.Font(BASE_DIR / "assets" / "SuperpixRegular-MV6mx.otf", 40)
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.player = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.food = pygame.Vector2(random.randint(0, self.screen.get_width() - 10),
                                   random.randint(0, self.screen.get_height() - 10))
        self.food_exists = True
        self.food_direction = random.choice([
            pygame.Vector2(100,0),
            pygame.Vector2(-100,0),
            pygame.Vector2(0,100),
            pygame.Vector2(0,-100)
        ])
        self.food_direction_timer = 0
        self.health = 100
        self.game_over = False
        self.menu = True
        self.title_font = pygame.font.Font(BASE_DIR / "assets" / "SuperpixRegular-MV6mx.otf", 100)
        self.game_playing = False
        self.menu_text = pygame.font.Font(BASE_DIR / "assets" / "SuperpixRegular-MV6mx.otf", 40)
        self.blink_timer = 0
        self.show_text = True
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
        self.end_track_started = False
        self.player_score = 110
        self.player_speed = 180
        self.food_speed = 1
        self.level_2 = False

    def score(self):
        if self.check_food_collision():
            self.player_score += 10
        return self.player_score

    def score_text(self, player_score):
        score_text = self.font.render(f'Score: {player_score}', False, "white")
        self.screen.blit(score_text, (0,0))

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.y -= self.player_speed * self.dt
        if keys[pygame.K_s]:
            self.player.y += self.player_speed * self.dt
        if keys[pygame.K_a]:
            self.player.x -= self.player_speed * self.dt
        if keys[pygame.K_d]:
            self.player.x += self.player_speed * self.dt

    def update(self, dt):
        if (
                self.player.x < 10 or
                self.player.x > 1270 or
                self.player.y < 10 or
                self.player.y > 710
        ):
            self.game_playing = False
            self.health = 0
            self.game_over = True
        else:
            self.game_over = False

    def choose_food_direction(self):
        self.food_direction = random.choice([
            pygame.Vector2(100, 100),
            pygame.Vector2(-100, 100),
            pygame.Vector2(-100, -100),
            pygame.Vector2(100, -100)
        ])


    def update_food(self):
        self.food_direction_timer += self.dt
        if self.food_direction_timer >=  random.uniform(1,3):
            self.choose_food_direction()
            self.food_direction_timer = 0

        self.food += self.food_direction * self.dt
        if self.food.x <= 10 or self.food.x >= 1270:
            self.food_direction.x *= -1
        if self.food.y <= 10 or self.food.y >= 710:
            self.food_direction.y *= -1


    def game_over_screen(self):
        self.blink_timer = self.blink_timer + self.dt
        if self.blink_timer >= 0.25:
            self.show_text = not self.show_text
            self.blink_timer = 0

        if not self.end_track_started:
            end_track = random.choice(self.try_again_tracks)
            pygame.mixer.music.load(end_track)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            self.end_track_started = True

        end_text = self.font.render("You died idiot", True, "white")
        try_again = self.font.render("Try again?", False, "white")
        y_n = self.font.render("Yes / No", False, "white")
        self.screen.blit(end_text, (self.screen.get_width() / 3.6, self.screen.get_height() / 4))
        self.screen.blit(try_again, (self.screen.get_width() / 3.0, self.screen.get_height() / 2.2))

        if self.show_text:
            self.screen.blit(y_n, (self.screen.get_width() / 2.75, self.screen.get_height() / 1.5))



    def draw_food(self):
        pygame.draw.rect(self.screen, "green", (self.food.x, self.food.y, 8,8))

    def randomize_food(self):
        self.food = pygame.Vector2(random.randint(0, self.screen.get_width() - 10),
                                   random.randint(0, self.screen.get_height() - 10))
        self.choose_food_direction()
        self.food_exists = True

    def check_food_collision(self):
        player_rect = pygame.Rect(self.player.x, self.player.y, 10,10)
        food_rect = pygame.Rect(self.food.x, self.food.y, 8,8)

        if player_rect.colliderect(food_rect):
            self.food_exists = False
            self.randomize_food()
            return True

        return False

    def draw_player(self):
        pygame.draw.rect(self.screen, "white", (self.player[0], self.player[1], 10,10))

    def check_level_state(self):
        if self.player_score >= 120 and not self.level_2:
            self.level_2 = True
            self.player_speed = self.player_speed * 2
            self.food_speed = self.food_speed * 1.5


    def game_loop(self):
        self.running = True
        if self.menu:
            pygame.mixer.music.load(BASE_DIR / "assets" / "menu_sound.wav")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == self.MUSIC_END and self.game_playing:
                    track = random.choice(self.game_music_tracks)
                    pygame.mixer.music.load(track)
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play()


            self.dt = self.clock.tick(60) / 1000
            self.screen.fill("black")

            if self.menu == True and self.game_playing == False and self.game_over == False:
                self.blink_timer = self.blink_timer + self.dt
                if self.blink_timer >= 0.25:
                    self.show_text = not self.show_text
                    self.blink_timer = 0


                title_text = self.title_font.render("SNAKE", False, "white")
                self.screen.blit(title_text, (self.screen.get_width() / 3.3,
                                              self.screen.get_height() / 4))

                if self.show_text:
                    menu_text = self.menu_text.render("PRESS  SPACE  TO  START", False, "white")
                    self.screen.blit(menu_text, (self.screen.get_width() / 6.5,
                                                 self.screen.get_height() / 1.5))

                play = pygame.key.get_pressed()

                if play[pygame.K_SPACE] and self.menu == True:
                    self.menu = False
                    self.game_playing = True
                    self.end_track_started = False
                    pygame.mixer.music.fadeout(1000)

            elif self.game_playing:
                self.menu = False
                self.show_text = False
                self.input()
                self.score()
                self.score_text(self.player_score)
                self.update(self.dt)
                self.draw_player()
                self.draw_food()
                self.check_food_collision()
                self.update_food()
                self.draw_food()
                self.check_level_state()


            elif self.game_over:
                self.game_over_screen()

                retry = pygame.key.get_pressed()

                if retry[pygame.K_y]:
                    self.player = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
                    self.player_score = 0
                    self.health = 100
                    self.game_over = False
                    self.game_playing = True
                    self.menu = False
                    self.game_over = False
                    self.end_track_started = False
                    pygame.mixer.music.fadeout(1000)

                elif retry[pygame.K_n]:
                    pygame.quit()
                    sys.exit()



            pygame.display.flip()

        return


def create_game():
    game = Game()
    return game

def main():
    game = create_game()
    game.game_loop()


if __name__ == '__main__':
    main()








