import pygame
import random
import os
import sys
import math
import imageio
from PIL import Image
import numpy as np
import tempfile
import subprocess


pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
PURPLE = (128, 0, 128)

PLAYER_IMAGE = None
GAME_MUSIC = None

def load_game_music():
    global GAME_MUSIC
    try:
        pygame.mixer.music.load('Агата Кристи - Как на войне.wav')
        print("Загружена музыка: Агата Кристи - Как на войне.wav")
    except Exception as e:
        print(f"Ошибка загрузки музыки: {e}")

def play_game_music():
    try:
        pygame.mixer.music.play(-1) 
        pygame.mixer.music.set_volume(0.5) 
        print("Воспроизводится музыка")
    except Exception as e:
        print(f"Ошибка воспроизведения музыки: {e}")

def stop_game_music():
    try:
        pygame.mixer.music.stop()
    except:
        pass

def load_player_image():
    global PLAYER_IMAGE
    try:
        img = pygame.image.load('free-png.ru-264.png')
        img = pygame.transform.scale(img, (50, 60))
        PLAYER_IMAGE = img
        print(f"Загружено изображение игрока: free-png.ru-264.png")
    except Exception as e:
        print(f"Ошибка загрузки изображения игрока: {e}")

ENEMY_IMAGES = []
VIDEO_FRAMES = []
VIDEO_FPS = 30
VIDEO_SOUND = None

def load_enemy_images():
    images = []
    files = ['tun-sahur.webp', 'IMG_0691.png']
    for filename in files:
        try:
            img = pygame.image.load(filename)
            img = pygame.transform.scale(img, (50, 60))
            images.append(img)
            print(f"Загружено изображение: {filename}, размер: {img.get_size()}")
        except Exception as e:
            print(f"Ошибка загрузки {filename}: {e}")
    print(f"Всего загружено изображений: {len(images)}")
    return images

def load_video_frames():
    global VIDEO_FRAMES, VIDEO_FPS, VIDEO_SOUND
    frames = []
    try:
        reader = imageio.get_reader('0519.mov')
        VIDEO_FPS = reader.get_meta_data().get('fps', 30)
        for frame in reader:
            frame = np.array(frame)
            surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            surface = pygame.transform.scale(surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            frames.append(surface)
        reader.close()
        print(f"Загружено кадров видео: {len(frames)}, FPS: {VIDEO_FPS}")
        
        try:
            from moviepy.editor import VideoFileClip
            
            video_clip = VideoFileClip('0519.mov')
            if video_clip.audio is not None:
                audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                audio_path = audio_file.name
                audio_file.close()
                
                video_clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
                VIDEO_SOUND = pygame.mixer.Sound(audio_path)
                print(f"Звук из видео успешно загружен")
                
                video_clip.close()
                try:
                    os.unlink(audio_path)
                except:
                    pass
            else:
                print("Видео не содержит аудиодорожки")
                
        except ImportError:
            print("moviepy не установлен, пробуем альтернативный метод...")
            try:
                import imageio_ffmpeg
                audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                audio_path = audio_file.name
                audio_file.close()
                
                exe = imageio_ffmpeg.get_ffmpeg_exe()
                result = subprocess.run(
                    [exe, '-y', '-i', '0519.mov', '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', audio_path],
                    capture_output=True
                )
                
                if result.returncode == 0 and os.path.exists(audio_path):
                    VIDEO_SOUND = pygame.mixer.Sound(audio_path)
                    print(f"Звук из видео успешно загружен (через imageio_ffmpeg)")
                    
                try:
                    os.unlink(audio_path)
                except:
                    pass
                    
            except Exception as e:
                print(f"Ошибка извлечения звука: {e}")
            
    except Exception as e:
        print(f"Ошибка загрузки видео: {e}")
    return frames

def play_video_sound():
    global VIDEO_SOUND
    if VIDEO_SOUND:
        try:
            VIDEO_SOUND.play()
            print("Воспроизводится звук видео")
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 60
        self.speed = 5
        self.health = 100
        self.max_health = 100
        
    def draw(self, screen):
        if PLAYER_IMAGE:
            screen.blit(PLAYER_IMAGE, (self.x, self.y))
        else:
            pygame.draw.rect(screen, BLUE, (self.x, self.y + 20, self.width, 40))
            pygame.draw.circle(screen, (255, 200, 150), (self.x + self.width // 2, self.y + 10), 15)
            pygame.draw.circle(screen, BLACK, (self.x + self.width // 2 - 5, self.y + 8), 3)
            pygame.draw.circle(screen, BLACK, (self.x + self.width // 2 + 5, self.y + 8), 3)
            pygame.draw.rect(screen, BLUE, (self.x - 10, self.y + 25, 10, 25))
            pygame.draw.rect(screen, BLUE, (self.x + self.width, self.y + 25, 10, 25))
        
    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(0, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(SCREEN_WIDTH - self.width, self.x + self.speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y = max(0, self.y - self.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y = min(SCREEN_HEIGHT - self.height, self.y + self.speed)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class TunTunSahur:
    def __init__(self, enemy_images, image_index, spawn_side=None):
        self.width = 50
        self.height = 60
        self.speed = random.uniform(1.5, 3.5)
        self.health = 30
        self.damage = 10
        self.attack_cooldown = 0
        self.wobble = 0
        
        self.side = spawn_side if spawn_side else random.choice(['left', 'right', 'top', 'bottom'])
        
        if self.side in ['right', 'bottom']:
            self.image_index = 1 if len(enemy_images) > 1 else 0
        else: 
            self.image_index = 0
        
        self.image = enemy_images[self.image_index] if enemy_images and len(enemy_images) > self.image_index else None
        
        if self.side == 'left':
            self.x = -self.width - random.randint(0, 50)
            self.y = random.randint(0, SCREEN_HEIGHT - self.height)
        elif self.side == 'right':
            self.x = SCREEN_WIDTH + random.randint(0, 50)
            self.y = random.randint(0, SCREEN_HEIGHT - self.height)
        elif self.side == 'top':
            self.x = random.randint(0, SCREEN_WIDTH - self.width)
            self.y = -self.height - random.randint(0, 50)
        else:  
            self.x = random.randint(0, SCREEN_WIDTH - self.width)
            self.y = SCREEN_HEIGHT + random.randint(0, 50)
        
    def draw(self, screen):
        self.wobble = (self.wobble + 0.2) % (2 * math.pi)
        offset = int(math.sin(self.wobble) * 3)
        
        if self.image:
            screen.blit(self.image, (self.x, self.y + offset))
        else:
            pygame.draw.ellipse(screen, ORANGE, (self.x + 5, self.y + 15 + offset, 35, 40))
            
            pygame.draw.circle(screen, (200, 150, 100), (self.x + 22, self.y + 12 + offset), 18)
            
            pygame.draw.circle(screen, WHITE, (self.x + 15, self.y + 8 + offset), 8)
            pygame.draw.circle(screen, WHITE, (self.x + 30, self.y + 8 + offset), 8)
            pygame.draw.circle(screen, BLACK, (self.x + 16, self.y + 9 + offset), 4)
            pygame.draw.circle(screen, BLACK, (self.x + 31, self.y + 9 + offset), 4)
            
            pygame.draw.line(screen, BLACK, (self.x + 10, self.y + 2 + offset), (self.x + 20, self.y + 5 + offset), 2)
            pygame.draw.line(screen, BLACK, (self.x + 25, self.y + 5 + offset), (self.x + 35, self.y + 2 + offset), 2)
            
            pygame.draw.arc(screen, BLACK, (self.x + 12, self.y + 12 + offset, 20, 15), 3.14, 0, 2)
            
            pygame.draw.ellipse(screen, (200, 150, 100), (self.x + 2, self.y - 2 + offset, 10, 15))
            pygame.draw.ellipse(screen, (200, 150, 100), (self.x + 32, self.y - 2 + offset, 10, 15))
        
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, 50, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, 50 * (self.health / 30), 5))
        
    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = 10
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = 0
            self.vy = 0
            
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius - 2)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("тгк: @przedviralem1")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        
        global ENEMY_IMAGES
        ENEMY_IMAGES = load_enemy_images()
        
        load_player_image()
        
        load_game_music()
        
        global VIDEO_FRAMES
        VIDEO_FRAMES = load_video_frames()
        
        self.reset_game()
        
    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = []
        self.bullets = []
        self.score = 0
        self.wave = 1
        self.enemies_per_wave = 3
        self.spawn_timer = 0
        self.spawn_delay = 60
        self.game_over = False
        self.running = True
        self.showing_video = False
        self.video_frame_index = 0
        self.video_timer = 0
        self.next_image_index = 0  
        play_game_music()
        
    def spawn_enemy(self):
        if len(self.enemies) < self.enemies_per_wave:
            sides_to_spawn = []
            
            if self.wave >= 1:
                sides_to_spawn = ['left', 'right'] 
            if self.wave >= 2:
                sides_to_spawn.extend(['top', 'bottom'])  
            
            num_to_spawn = min(2, self.enemies_per_wave - len(self.enemies))
            spawn_sides = random.sample(sides_to_spawn, min(num_to_spawn, len(sides_to_spawn)))
            
            for side in spawn_sides:
                enemy = TunTunSahur(ENEMY_IMAGES, 0, spawn_side=side)
                self.enemies.append(enemy)
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1: 
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    bullet = Bullet(
                        self.player.x + self.player.width // 2,
                        self.player.y + self.player.height // 2,
                        mouse_x, mouse_y
                    )
                    self.bullets.append(bullet)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
    def update(self):
        if self.game_over:
            return
            
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_enemy()
            self.spawn_timer = 0
            
        for enemy in self.enemies[:]:
            enemy.update(self.player)
            
            if enemy.get_rect().colliderect(self.player.get_rect()):
                if enemy.attack_cooldown == 0:
                    self.player.health -= enemy.damage
                    enemy.attack_cooldown = 60
                    
            if enemy.health <= 0:
                self.enemies.remove(enemy)
                self.score += 10
                
        for bullet in self.bullets[:]:
            bullet.update()
            
            if bullet.x < 0 or bullet.x > SCREEN_WIDTH or bullet.y < 0 or bullet.y > SCREEN_HEIGHT:
                self.bullets.remove(bullet)
                continue
                
            for enemy in self.enemies[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    enemy.health -= 20
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
                    
        if len(self.enemies) == 0:
            self.wave += 1
            self.enemies_per_wave = 3 + self.wave * 2
            self.spawn_delay = max(20, 60 - self.wave * 5)
            
        if self.player.health <= 0:
            self.game_over = True
            stop_game_music()
            if VIDEO_FRAMES:
                self.showing_video = True
                self.video_frame_index = 0
                self.video_timer = 0
                play_video_sound()
            
    def draw_background(self):
        self.screen.fill((230, 230, 235))
            
    def draw_ui(self):
        title_text = self.big_font.render("ЖИВЫМ НЕ ДАМСЯ СУКИ", True, RED)
        title_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
        self.screen.blit(title_text, (title_x, 10))
        
        pygame.draw.rect(self.screen, RED, (10, 60, 200, 25))
        pygame.draw.rect(self.screen, GREEN, (10, 60, 200 * (self.player.health / self.player.max_health), 25))
        pygame.draw.rect(self.screen, WHITE, (10, 60, 200, 25), 2)
        
        health_text = self.small_font.render(f"HP: {self.player.health}/{self.player.max_health}", True, WHITE)
        self.screen.blit(health_text, (15, 63))
        
    def draw_game_over(self):
        if self.showing_video and VIDEO_FRAMES:
            if self.video_frame_index < len(VIDEO_FRAMES):
                self.screen.blit(VIDEO_FRAMES[self.video_frame_index], (0, 0))
                
                self.video_timer += 1
                if self.video_timer >= FPS / VIDEO_FPS:
                    self.video_timer = 0
                    self.video_frame_index += 1
            else:
                self.showing_video = False
        else:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(180)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
            
            victory_text = self.font.render("Тун Тун Сахур победил!", True, ORANGE)
            self.screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, 230))
            
            score_text = self.font.render(f"Финальный счёт: {self.score}", True, WHITE)
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 280))
            
            self.draw_big_sahur(SCREEN_WIDTH // 2 - 75, 300)
            
            restart_text = self.font.render("Нажмите R для рестарта", True, GREEN)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 480))
            
            exit_text = self.small_font.render("ESC - выход", True, WHITE)
            self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 520))
        
    def draw_big_sahur(self, x, y):
        if ENEMY_IMAGES:
            big_img = pygame.transform.scale(ENEMY_IMAGES[0], (150, 180))
            self.screen.blit(big_img, (x, y))
        else:
            pygame.draw.ellipse(self.screen, ORANGE, (x + 25, y + 40, 100, 120))
            
            pygame.draw.circle(self.screen, (200, 150, 100), (x + 75, y + 25), 50)
            
            pygame.draw.circle(self.screen, WHITE, (x + 55, y + 15), 18)
            pygame.draw.circle(self.screen, WHITE, (x + 95, y + 15), 18)
            pygame.draw.circle(self.screen, BLACK, (x + 58, y + 18), 8)
            pygame.draw.circle(self.screen, BLACK, (x + 98, y + 18), 8)
            
            pygame.draw.arc(self.screen, BLACK, (x + 40, y - 5, 30, 20), 0, 3.14, 3)
            pygame.draw.arc(self.screen, BLACK, (x + 80, y - 5, 30, 20), 0, 3.14, 3)
            
            pygame.draw.arc(self.screen, BLACK, (x + 45, y + 25, 60, 40), 3.14, 0, 3)
            
            pygame.draw.ellipse(self.screen, (200, 150, 100), (x + 15, y - 20, 30, 45))
            pygame.draw.ellipse(self.screen, (200, 150, 100), (x + 110, y - 20, 30, 45))
            
            pygame.draw.ellipse(self.screen, ORANGE, (x - 10, y + 30, 40, 25))
            pygame.draw.ellipse(self.screen, ORANGE, (x + 125, y + 30, 40, 25))
        
    def run(self):
        play_game_music()
        
        while self.running:
            self.handle_events()
            self.update()
            
            self.draw_background()
            
            for bullet in self.bullets:
                bullet.draw(self.screen)
                
            for enemy in self.enemies:
                enemy.draw(self.screen)
                
            self.player.draw(self.screen)
            
            self.draw_ui()
            
            if self.game_over:
                self.draw_game_over()
                
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
