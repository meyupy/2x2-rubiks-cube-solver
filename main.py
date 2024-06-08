import pygame
import random

pygame.init()

W = 1024   # screen width
BG_COLOR, BG_PANEL_COLOR = (15, 15, 15), (31, 31, 31)
BUTTON_COLOR_1, BUTTON_COLOR_2 = (95, 95, 95), (79, 79, 79)
TEXT_COLOR_1_1, TEXT_COLOR_1_2 = (95, 95, 95), (63, 63, 63)
TEXT_COLOR_2_1, TEXT_COLOR_2_2 = (0, 155, 72), (0, 91, 8)

gui_font, gui_font_large = pygame.font.Font(None, W // 32), pygame.font.Font(None, W // 16)

screen = pygame.display.set_mode((W, 3 * W // 4))
pygame.display.set_caption("2x2 Rubik's Cube Solver")
bg_panel = pygame.rect.Rect(0, 0, 3 * W // 4, 9 * W // 16)
clock = pygame.time.Clock()

NOTATIONS = ["F ", "F2", "F'", "U ", "U2", "U'", "R ", "R2", "R'"]


class Button:

    def __init__(self, surface, text, font, x, y, width, height,
                 button_color_1, button_color_2, text_color, border_radius):
        self.surface = surface
        self.button_color_1 = button_color_1
        self.button_color_2 = button_color_2
        self.color = button_color_1
        self.border_radius = border_radius
        self.body_rect = pygame.rect.Rect(x, y, width, height)
        self.text = text
        self.text_surf = font.render(text, True, text_color)
        self.text_rect = self.text_surf.get_rect(center=self.body_rect.center)
        self.press_allowed = True
        self.pressed = False

    def is_clicked(self):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if self.body_rect.collidepoint(pygame.mouse.get_pos()):
            if mouse_pressed:
                self.pressed = True
            elif self.pressed and self.press_allowed:
                self.pressed = False
                return True
        else:
            self.pressed = False
            if mouse_pressed:
                self.press_allowed = False
            else:
                self.press_allowed = True
        return False

    def draw(self):
        if self.body_rect.collidepoint(pygame.mouse.get_pos()):
            self.color = self.button_color_2
        else:
            self.color = self.button_color_1
        pygame.draw.rect(self.surface, self.color, self.body_rect, border_radius=self.border_radius)
        self.surface.blit(self.text_surf, self.text_rect)


def convert_path_into_display_text(solution_path):
    solution_text = ""
    for n in range(0, len(solution_path), 2):
        text_part = solution_path[n:n + 2]
        solution_text += text_part
        if text_part[1] == " ":
            solution_text += " "
        else:
            solution_text += "  "
    return solution_text[:-2]


def produce_random_scramble():
    random_scramble = random.choice(NOTATIONS)
    num_notations_in_scramble = random.randint(9, 10)
    while len(random_scramble) < num_notations_in_scramble * 2:
        random_notation = random.choice([the_notation for the_notation in NOTATIONS
                                         if the_notation[0] != random_scramble[-2]])
        random_scramble += random_notation
    return random_scramble


def produce_permutation_for_turner_buttons(notation, perm):
    [f1, f2, f3, f4, u1, u2, u3, u4, r1, r2, r3, r4,
     b1, b2, b3, b4, d1, d2, d3, d4, l1, l2, l3, l4] = perm
    permutation_dict = {
        "F": [f3, f1, f4, f2, u1, u2, l4, l2, u3, r2, u4, r4,
              b1, b2, b3, b4, r3, r1, d3, d4, l1, d1, l3, d2],
        "F2": [f4, f3, f2, f1, u1, u2, d2, d1, l4, r2, l2, r4,
               b1, b2, b3, b4, u4, u3, d3, d4, l1, r3, l3, r1],
        "F'": [f2, f4, f1, f3, u1, u2, r1, r3, d2, r2, d1, r4,
               b1, b2, b3, b4, l2, l4, d3, d4, l1, u4, l3, u3],
        "U": [r1, r2, f3, f4, u3, u1, u4, u2, b1, b2, r3, r4,
              l1, l2, b3, b4, d1, d2, d3, d4, f1, f2, l3, l4],
        "U2": [b1, b2, f3, f4, u4, u3, u2, u1, l1, l2, r3, r4,
               f1, f2, b3, b4, d1, d2, d3, d4, r1, r2, l3, l4],
        "U'": [l1, l2, f3, f4, u2, u4, u1, u3, f1, f2, r3, r4,
               r1, r2, b3, b4, d1, d2, d3, d4, b1, b2, l3, l4],
        "R": [f1, d2, f3, d4, u1, f2, u3, f4, r3, r1, r4, r2,
              u4, b2, u2, b4, d1, b3, d3, b1, l1, l2, l3, l4],
        "R2": [f1, b3, f3, b1, u1, d2, u3, d4, r4, r3, r2, r1,
               f4, b2, f2, b4, d1, u2, d3, u4, l1, l2, l3, l4],
        "R'": [f1, u2, f3, u4, u1, b3, u3, b1, r2, r4, r1, r3,
               d4, b2, d2, b4, d1, f2, d3, f4, l1, l2, l3, l4],
        "B": [f1, f2, f3, f4, r2, r4, u3, u4, r1, d4, r3, d3,
              b3, b1, b4, b2, d1, d2, l1, l3, u2, l2, u1, l4],
        "B2": [f1, f2, f3, f4, d4, d3, u3, u4, r1, l3, r3, l1,
               b4, b3, b2, b1, d1, d2, u2, u1, r4, l2, r2, l4],
        "B'": [f1, f2, f3, f4, l3, l1, u3, u4, r1, u1, r3, u2,
               b2, b4, b1, b3, d1, d2, r4, r2, d3, l2, d4, l4],
        "D": [f1, f2, l3, l4, u1, u2, u3, u4, r1, r2, f3, f4,
              b1, b2, r3, r4, d3, d1, d4, d2, l1, l2, b3, b4],
        "D2": [f1, f2, b3, b4, u1, u2, u3, u4, r1, r2, l3, l4,
               b1, b2, f3, f4, d4, d3, d2, d1, l1, l2, r3, r4],
        "D'": [f1, f2, r3, r4, u1, u2, u3, u4, r1, r2, b3, b4,
               b1, b2, l3, l4, d2, d4, d1, d3, l1, l2, f3, f4],
        "L": [u1, f2, u3, f4, b4, u2, b2, u4, r1, r2, r3, r4,
              b1, d3, b3, d1, f1, d2, f3, d4, l3, l1, l4, l2],
        "L2": [b4, f2, b2, f4, d1, u2, d3, u4, r1, r2, r3, r4,
               b1, f3, b3, f1, u1, d2, u3, d4, l4, l3, l2, l1],
        "L'": [d1, f2, d3, f4, f1, u2, f3, u4, r1, r2, r3, r4,
               b1, u3, b3, u1, b4, d2, b2, d4, l2, l4, l1, l3],
    }
    return permutation_dict[notation]


def produce_permutation_from_path(perm, path):
    for n in range(0, len(path), 2):
        notation = path[n:n+2]
        perm = produce_permutation(notation, perm)
    return perm


def produce_permutations_from_path(perm, path):
    perms = [perm]
    for n in range(0, len(path) - 2, 2):
        notation = path[n:n + 2]
        perm = produce_permutation(notation, perm)
        perms.append(perm)
    return perms


def produce_permutation(notation, perm):
    (f1, f2, f3, f4, u1, u2, u3, u4, r1, r2, r3, r4,
     b1, b2, b3, b4, d1, d2, d3, d4, l1, l2, l3, l4) = perm
    if notation == "F ":
        perm = f3 + f1 + f4 + f2 + u1 + u2 + l4 + l2 + u3 + r2 + u4 + r4 + \
               b1 + b2 + b3 + b4 + r3 + r1 + d3 + d4 + l1 + d1 + l3 + d2
    elif notation == "F2":
        perm = f4 + f3 + f2 + f1 + u1 + u2 + d2 + d1 + l4 + r2 + l2 + r4 + \
               b1 + b2 + b3 + b4 + u4 + u3 + d3 + d4 + l1 + r3 + l3 + r1
    elif notation == "F'":
        perm = f2 + f4 + f1 + f3 + u1 + u2 + r1 + r3 + d2 + r2 + d1 + r4 + \
               b1 + b2 + b3 + b4 + l2 + l4 + d3 + d4 + l1 + u4 + l3 + u3
    elif notation == "U ":
        perm = r1 + r2 + f3 + f4 + u3 + u1 + u4 + u2 + b1 + b2 + r3 + r4 + \
               l1 + l2 + b3 + b4 + d1 + d2 + d3 + d4 + f1 + f2 + l3 + l4
    elif notation == "U2":
        perm = b1 + b2 + f3 + f4 + u4 + u3 + u2 + u1 + l1 + l2 + r3 + r4 + \
               f1 + f2 + b3 + b4 + d1 + d2 + d3 + d4 + r1 + r2 + l3 + l4
    elif notation == "U'":
        perm = l1 + l2 + f3 + f4 + u2 + u4 + u1 + u3 + f1 + f2 + r3 + r4 + \
               r1 + r2 + b3 + b4 + d1 + d2 + d3 + d4 + b1 + b2 + l3 + l4
    elif notation == "R ":
        perm = f1 + d2 + f3 + d4 + u1 + f2 + u3 + f4 + r3 + r1 + r4 + r2 + \
               u4 + b2 + u2 + b4 + d1 + b3 + d3 + b1 + l1 + l2 + l3 + l4
    elif notation == "R2":
        perm = f1 + b3 + f3 + b1 + u1 + d2 + u3 + d4 + r4 + r3 + r2 + r1 + \
               f4 + b2 + f2 + b4 + d1 + u2 + d3 + u4 + l1 + l2 + l3 + l4
    else:  # notation == "R'":
        perm = f1 + u2 + f3 + u4 + u1 + b3 + u3 + b1 + r2 + r4 + r1 + r3 + \
               d4 + b2 + d2 + b4 + d1 + f2 + d3 + f4 + l1 + l2 + l3 + l4
    return perm


def is_cube_solved(perm):
    for s in range(0, 24, 4):
        if perm[s] * 4 != perm[s:s+4]:
            return False
    return True


def scan(paths, perms):
    new_paths = []
    new_perms = []
    for n in range(len(paths)):
        for notation in NOTATIONS:
            if paths[n][-2] != notation[0]:
                new_path = paths[n]
                new_path += notation
                new_perm = produce_permutation(notation, perms[n])
                new_paths.append(new_path)
                new_perms.append(new_perm)
                if is_cube_solved(new_perm):
                    return None, None, new_path
    return new_paths, new_perms, None


def find_solution(perm):
    if is_cube_solved(perm):
        return []
    paths = [notation for notation in NOTATIONS]
    perms = [produce_permutation(path, perm) for path in paths]
    for n in range(len(paths)):
        if is_cube_solved(perms[n]):
            return paths[n]
    print(f"\n\n1) {((pygame.time.get_ticks() - last_time) // 100) / 10}")
    for _ in range(10):
        paths, perms, solution_path = scan(paths, perms)
        if solution_path is not None:
            print(f"\nsolved in {((pygame.time.get_ticks() - last_time) // 100) / 10} seconds")
            return solution_path
        print(f"{_+2}) {((pygame.time.get_ticks() - last_time) // 100) / 10}")


CUBE_FACE_POSITIONS = [(W // 4, 7 * W // 32), (W // 4, 3 * W // 32), (3 * W // 8, 7 * W // 32),
                       (W // 2, 7 * W // 32), (W // 4, 11 * W // 32), (W // 8, 7 * W // 32)]

TURNER_BUTTON_POSITIONS = [(25 * W // 32, W // 32), (27 * W // 32, W // 32), (29 * W // 32, W // 32),
                           (25 * W // 32, 3 * W // 32), (27 * W // 32, 3 * W // 32), (29 * W // 32, 3 * W // 32),
                           (25 * W // 32, 5 * W // 32), (27 * W // 32, 5 * W // 32), (29 * W // 32, 5 * W // 32),
                           (25 * W // 32, 7 * W // 32), (27 * W // 32, 7 * W // 32), (29 * W // 32, 7 * W // 32),
                           (25 * W // 32, 9 * W // 32), (27 * W // 32, 9 * W // 32), (29 * W // 32, 9 * W // 32),
                           (25 * W // 32, 11 * W // 32), (27 * W // 32, 11 * W // 32), (29 * W // 32, 11 * W // 32)]

TURNER_BUTTON_TEXTS = ["F", "F2", "F'", "U", "U2", "U'", "R", "R2", "R'",
                       "B", "B2", "B'", "D", "D2", "D'", "L", "L2", "L'"]

color_to_rgb_dict = {
    "g": (0, 155, 72), "w": (223, 223, 223), "r": (183, 18, 52),
    "b": (0, 70, 173), "y": (255, 213, 0), "o": (255, 88, 0),
}

square_rects = []
turner_buttons = []

for x_position, y_position in CUBE_FACE_POSITIONS:
    x_position, y_position = x_position + W // 256, y_position + W // 256
    for position in [(x_position, y_position), (x_position + W // 16, y_position),
                     (x_position, y_position + W // 16), (x_position + W // 16, y_position + W // 16)]:
        new_square_rect = pygame.rect.Rect(position, (7 * W // 128, 7 * W // 128))
        square_rects.append(new_square_rect)

for i in range(18):
    x_position, y_position = TURNER_BUTTON_POSITIONS[i]
    x_position, y_position = x_position + W // 256, y_position + W // 256
    new_button = Button(screen, TURNER_BUTTON_TEXTS[i], gui_font, x_position, y_position, 7 * W // 128, 7 * W // 128,
                        BUTTON_COLOR_1, BUTTON_COLOR_2, BG_COLOR, W // 256)
    turner_buttons.append(new_button)

scramble = ""
last_scrambled_permutation = None

solution = ""
last_solution_permutations = []

last_permutation_solved = None

scramble_surf = gui_font_large.render("", True, TEXT_COLOR_1_1)
scramble_rect = scramble_surf.get_rect(center=(3 * W // 8, 79 * W // 128))
solution_surf = gui_font_large.render("", True, TEXT_COLOR_2_1)
solution_rect = solution_surf.get_rect(center=(3 * W // 8, 89 * W // 128))

button_reset = Button(screen, "Reset", gui_font, 13 * W // 16, 29 * W // 64, W // 8, W // 16,
                      BUTTON_COLOR_1, BUTTON_COLOR_2, BG_COLOR, W // 64)
button_scramble = Button(screen, "Scramble", gui_font, 13 * W // 16, 35 * W // 64, W // 8, W // 16,
                         BUTTON_COLOR_1, BUTTON_COLOR_2, BG_COLOR, W // 64)
button_solve = Button(screen, "Solve", gui_font, 13 * W // 16, 41 * W // 64, W // 8, W // 16,
                      BUTTON_COLOR_1, BUTTON_COLOR_2, BG_COLOR, W // 64)

DEFAULT_PERMUTATION = "ggggwwwwrrrrbbbbyyyyoooo"

current_permutation = DEFAULT_PERMUTATION

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    for turner_button in turner_buttons:
        if turner_button.is_clicked():
            current_permutation = "".join(produce_permutation_for_turner_buttons
                                          (turner_button.text, current_permutation))
            if current_permutation == last_scrambled_permutation:
                scramble_surf = gui_font_large.render(scramble, True, TEXT_COLOR_1_1)
            else:
                scramble_surf = gui_font_large.render(scramble, True, TEXT_COLOR_1_2)
            if current_permutation in last_solution_permutations:
                solution_surf = gui_font_large.render(solution, True, TEXT_COLOR_2_1)
            else:
                solution_surf = gui_font_large.render(solution, True, TEXT_COLOR_2_2)

    if button_reset.is_clicked():
        current_permutation = DEFAULT_PERMUTATION
        scramble = ""
        solution = ""
        last_scrambled_permutation = None
        last_solution_permutations = []
        last_permutation_solved = None
        scramble_surf = gui_font_large.render("", True, TEXT_COLOR_1_1)
        solution_surf = gui_font_large.render("", True, TEXT_COLOR_2_1)

    if button_scramble.is_clicked():
        scramble = produce_random_scramble()
        current_permutation = produce_permutation_from_path(DEFAULT_PERMUTATION, scramble)
        last_scrambled_permutation = current_permutation
        scramble = convert_path_into_display_text(scramble)
        scramble_surf = gui_font_large.render(scramble, True, TEXT_COLOR_1_1)
        scramble_rect = scramble_surf.get_rect(center=(3 * W // 8, 79 * W // 128))
        solution = ""
        last_solution_permutations = []
        solution_surf = gui_font_large.render("", True, TEXT_COLOR_2_1)

    if button_solve.is_clicked():
        if not is_cube_solved(current_permutation) and current_permutation != last_permutation_solved:
            last_time = pygame.time.get_ticks()
            solution = find_solution(current_permutation)
            last_solution_permutations = produce_permutations_from_path(current_permutation, solution)
            last_permutation_solved = current_permutation
            solution = convert_path_into_display_text(solution)
            solution_surf = gui_font_large.render(solution, True, TEXT_COLOR_2_1)
            solution_rect = solution_surf.get_rect(center=(3 * W // 8, 89 * W // 128))
            if current_permutation != last_scrambled_permutation:
                scramble = ""
                last_scrambled_permutation = None
                scramble_surf = gui_font_large.render("", True, TEXT_COLOR_1_1)
        elif is_cube_solved(current_permutation) and "" == scramble:
            solution = ""
            last_solution_permutations = []
            solution_surf = gui_font_large.render("", True, TEXT_COLOR_2_1)

    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, BG_PANEL_COLOR, bg_panel)

    for i in range(24):
        pygame.draw.rect(screen, color_to_rgb_dict[current_permutation[i]], square_rects[i], border_radius=W//256)

    for turner_button in turner_buttons:
        turner_button.draw()

    button_reset.draw()
    button_scramble.draw()
    button_solve.draw()

    screen.blit(scramble_surf, scramble_rect)
    screen.blit(solution_surf, solution_rect)

    clock.tick(30)
    pygame.display.update()
