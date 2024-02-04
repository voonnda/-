import pygame
from pygame.sprite import Sprite, Group
import random
from pygame import font

#Шрифти
font.init()
font1 = font.Font(None, 80)
win = font1.render("ТИ ПЕРЕМІГ", True, (255, 255, 255))
lose = font1.render("ТИ ПРОГРАВ", True, (180, 0, 0))
font2 = font.Font(None, 36)
#Змінні
score = 0
lost = 0
max_lost = 10
lives = 3

# Клас предок
class GameSprite(Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(player_image), (65, 65))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# Клас гравця
class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__(player_image, player_x, player_y, player_speed)
        self.bullets = Group()
        self.alive = True
        self.score = 0
        self.lives = 3

    def update(self):
        if not self.alive:
            return
#рух гравця
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -5
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > win_width:
            self.rect.right = win_width

        # Взаємодія з ворогами
        self.collide_with_enemy(enemies)

    def collide_with_enemy(self, enemies_group):
        if not self.alive:
            return

        collisions = pygame.sprite.spritecollide(self, enemies_group, True)
        for enemy in collisions:
            self.lives -= 1
            if self.lives <= 0:
                self.alive = False
            else:
                self.rect.x = random.randrange(win_width - self.rect.width)
                self.rect.y = win_height - 80
#Постріл
    def shoot(self):
        bullet1 = Bullet(self.rect.centerx - 45, self.rect.top)
        bullet2 = Bullet(self.rect.centerx - 9, self.rect.top)
        self.bullets.add(bullet1, bullet2)
        all_sprites.add(bullet1, bullet2)

class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__(player_image, player_x, player_y, player_speed)
        self.speed_y = random.randrange(1, 5)
        self.shoot_delay = random.randint(50, 200)
        self.shoot_timer = 0

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > win_height:
            self.rect.x = random.randrange(win_width - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 5)

        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay:
            self.shoot()
            self.shoot_timer = 0

    def shoot(self):
        enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(enemy_bullet)
        enemy_bullets.add(enemy_bullet)
#Клас кулі ворога
class EnemyBullet(GameSprite):
    def __init__(self, x, y):
        super().__init__('ENEMY_BULLET.png', x, y, 5)
        self.speed_y = 5

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.colliderect(player.rect):
            player.lives -= 1
            self.kill()
            global max_lost
            max_lost = max_lost +1

# Клас кулі
class Bullet(GameSprite):
    def __init__(self, x, y):
        super().__init__('PULA.png', x, y, 10)
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

    def collide_with_enemy(self, enemies_group):
        collisions = pygame.sprite.spritecollide(self, enemies_group, True)
        for enemy in collisions:
            self.kill()
            global score
            score = score + 1

# Створення вікна
win_width = 700
win_height = 500
window = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Шутер")
background = pygame.transform.scale(pygame.image.load("kosmos.jpg"), (win_width, win_height))

# музика
# mixer.init()
# mixer.music.load('space.ogg')
# mixer.music.play()

# Додаємо гравця
player = Player('PLAYER.png', 5, win_height - 80, 4)

game = True
clock = pygame.time.Clock()
FPS = 60
# Створення групи
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

enemy_spawn_threshold_1 = 50
enemy_spawn_threshold_2 = 100
is_difficulty_1_spawned = False
is_difficulty_2_spawned = False

finish = False
game = True

# Основний цикл
while game:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            game = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                player.shoot()

    if not finish:
        window.blit(background, (0, 0))

    text_lives = font2.render("Життя: " + str(player.lives), 1, (255, 255, 255))
    window.blit(text_lives, (10, 80))

    text = font2.render("Рахунок " + str(score), 1, (255, 255, 255))
    window.blit(text, (10, 20))

    text_lose = font2.render("Пропущено " + str(lost), 1, (255, 255, 255))
    window.blit(text_lose, (10, 50))

    if lost >= max_lost:
        finish = True
        window.blit(lose, (200, 200))
        pygame.display.update()
        pygame.time.delay(10000)
        game = False

    player.update()
    player.reset()

    # Ворог
    if len(enemies) < 5:
        enemy = Enemy('VRAG.png', random.randrange(win_width - 64), -64, 1)
        enemies.add(enemy)
        all_sprites.add(enemy)

    for enemy_bullet in enemy_bullets:
        enemy_bullet.update()
        if pygame.sprite.spritecollide(player, enemy_bullets, True):
            player.lives -= 1

    # Куля
    for bullet in player.bullets:
        bullet.update()
        if bullet.collide_with_enemy(enemies):
            score += 1

    player.bullets.draw(window)
    all_sprites.update()
    all_sprites.draw(window)
    all_sprites.add(enemy_bullets)
    enemy_bullets.add(enemy_bullets)

    if not player.alive:
        game_over_text = font1.render("Гра завершена!", True, (255, 0, 0))
        window.blit(game_over_text, (
        win_width // 2 - game_over_text.get_width() // 2, win_height // 2 - game_over_text.get_height() // 2))
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
