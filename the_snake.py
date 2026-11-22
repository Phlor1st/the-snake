"""Игра «Изгиб Питона» — классическая «Змейка» на pygame."""

from random import choice
import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

SCREEN_CENTER = (
    GRID_WIDTH // 2 * GRID_SIZE,
    GRID_HEIGHT // 2 * GRID_SIZE,
)

ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

TURNS = {
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
}

MIN_BITE_LENGTH = 5

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SPEED = 20

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

CAPTION = 'Змейка. Рекорд: {record}. Выход — ESC'
pygame.display.set_caption(CAPTION.format(record=1))

clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, body_color=None):
        self.position = SCREEN_CENTER
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """Отрисовывает одну ячейку поля по заданным координатам."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color or self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовывает объект на экране."""
        pass


class Apple(GameObject):
    """Яблоко, которое змейка должна съесть."""

    def __init__(self, body_color=APPLE_COLOR, occupied_positions=None):
        super().__init__(body_color)
        self.randomize_position(occupied_positions or [])

    def randomize_position(self, occupied_positions=None):
        """Ставит яблоко в случайную ячейку, не занятую змейкой."""
        free_cells = ALL_CELLS - set(occupied_positions or [])
        self.position = choice(tuple(free_cells))

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка, которой управляет игрок."""

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.reset()
        self.direction = RIGHT

    def reset(self):
        """Возвращает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Применяет направление, выбранное игроком."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Сдвигает змейку на одну ячейку в текущем направлении.
        При выходе за границу поля змейка появляется с противоположной
        стороны.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает голову змейки и затирает её след."""
        self.draw_cell(self.get_head_position())
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и закрытие окна.
    Стрелки меняют направление змейки, ESC и закрытие окна завершают игру.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            game_object.next_direction = TURNS.get(
                (event.key, game_object.direction),
                game_object.next_direction,
            )


def main():
    """Запускает игру и основной игровой цикл."""
    pygame.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)
    record = snake.length

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head = snake.get_head_position()
        if head == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
            if snake.length > record:
                record = snake.length
                pygame.display.set_caption(CAPTION.format(record=record))
        elif head in snake.positions[MIN_BITE_LENGTH - 1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
