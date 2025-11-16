import pygame
import sys
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Start Screen")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (0, 200, 0)
BUTTON_HOVER = (0, 255, 0)

font = pygame.font.SysFont(None, 48)

button_width, button_height = 300, 80
button_rect = pygame.Rect((WIDTH - button_width)//2, HEIGHT - 150, button_width, button_height)

background_image = pygame.image.load("interface_enter.png")

background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

def draw_button():
    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, button_rect)
    
    text_surface = font.render("Click to Start", True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

def start_main_game():
    running_game = True
    clock = pygame.time.Clock()

    while running_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_game = False

        """Game code"""

        pygame.display.flip()
        clock.tick(60)

def main():
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    start_main_game()
                    
        screen.blit(background_image, (0, 0))
        draw_button()

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()
