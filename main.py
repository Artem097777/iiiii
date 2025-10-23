import pygame

# Инициализация Pygame
pygame.init()

# Создание окна
screen = pygame.display.set_mode((480, 800))
pygame.display.set_caption('Pygame на Android')

# Основной игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Очистка экрана
    screen.fill((255, 255, 255))
    
    # Обновление экрана
    pygame.display.flip()

pygame.quit()
