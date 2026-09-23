import pygame



DESIGN_WIDTH = 1600
DESIGN_HEIGHT = 900
FONT_CACHE = {}


CHIPS = [
    {
        "value": 1,
        "position": (DESIGN_WIDTH * 0.2, DESIGN_HEIGHT * 0.8),
        "color": "white",
        "rect": None,
        "text_color": 'black',
    },
    {
        "value": 5,
        "position": (DESIGN_WIDTH * 0.3, DESIGN_HEIGHT * 0.8),
        "color": "red",
        "rect": None,
        "text_color": 'yellow',
    },
    {
        "value": 25,
        "position": (DESIGN_WIDTH * 0.4, DESIGN_HEIGHT * 0.8),
        "color": "green",
        "rect": None,
        "text_color": 'yellow',
    },
    {
        "value": 50,
        "position": (DESIGN_WIDTH * 0.5, DESIGN_HEIGHT * 0.8),
        "color": "blue",
        "rect": None,
        "text_color": 'yellow',
    },
    {
        "value": 100,
        "position": (DESIGN_WIDTH * 0.6, DESIGN_HEIGHT * 0.8),
        "color": "black",
        "rect": None,
        "text_color": 'white',
    },
    {
        "value": 500,
        "position": (DESIGN_WIDTH * 0.7, DESIGN_HEIGHT * 0.8),
        "color": "purple",
        "rect": None,
        "text_color": 'white',
    },
    {
        "value": 1000,
        "position": (DESIGN_WIDTH * 0.8, DESIGN_HEIGHT * 0.8),
        "color": "yellow",
        "rect": None,
        "text_color": 'black',
    },
]
COMPONENT_STYLES = {
    "button_big": {
        "shape": "rectangle",
        "size": (300, 120),
        "border_width": 3,
        "border_color": (0, 0, 0),
        "border_radius": 10,
        "font_size": 32,
        "font_name": None,
        "text_color": (0, 0, 0),
    },

    "button_small": {
            "shape": "rectangle",
            "size": (200, 80),
            "border_width": 3,
            "border_color": (0, 0, 0),
            "border_radius": 10,
            "font_size": 32,
            "font_name": None,
            "text_color": (0, 0, 0),
        },

    "chip": {
        "shape": "circle",
        "radius": 40,
        "border_width": 4,
        "border_color": (255, 255, 255),
        "font_size": 24,
        "font_name": None,
        "text_color": None,
    },

    "card": {
        "shape": "rectangle",
        "size": (100, 140),
        "border_width": 2,
        "border_color": (0, 0, 0),
        "border_radius": 8,
        "font_name": "Segoe UI Symbol",
        "font_size": 28,
        "text_color": (0, 0, 0),
    },
}
def get_font(font_size, font_name=None):
    font_key = (font_name, font_size)

    if font_key not in FONT_CACHE:
        FONT_CACHE[font_key] = pygame.font.SysFont(
            font_name,
            font_size,
        )

    return FONT_CACHE[font_key]

def draw_component(
    screen,
    component_type,
    text,
    position,
    fill_color,
    text_color=None,
):
    # 检查组件类型是否存在
    if component_type not in COMPONENT_STYLES:
        raise ValueError(
            f"Unsupported component type: {component_type}"
        )

    style = COMPONENT_STYLES[component_type]
    shape = style["shape"]

    border_width = style["border_width"]
    border_color = style["border_color"]

    # 绘制矩形组件：button和card
    if shape == "rectangle":
        component_rect = pygame.Rect(
            (0, 0),
            style["size"],
        )
        component_rect.center = position

        # 填充背景
        pygame.draw.rect(
            screen,
            fill_color,
            component_rect,
            border_radius=style["border_radius"],
        )

        # 绘制边框
        if border_width > 0:
            pygame.draw.rect(
                screen,
                border_color,
                component_rect,
                width=border_width,
                border_radius=style["border_radius"],
            )

    # 绘制圆形组件：chip
    elif shape == "circle":
        radius = style["radius"]

        # 绘制圆形背景
        pygame.draw.circle(
            screen,
            fill_color,
            position,
            radius,
        )

        # 绘制圆形边框
        if border_width > 0:
            pygame.draw.circle(
                screen,
                border_color,
                position,
                radius,
                width=border_width,
            )

        # 创建圆形的外接矩形，用于文字定位和点击检测
        component_rect = pygame.Rect(
            position[0] - radius,
            position[1] - radius,
            radius * 2,
            radius * 2,
        )

    else:
        raise ValueError(
            f"Unsupported shape: {shape}"
        )

    # 绘制文字
    font = get_font(style["font_size"], style.get("font_name"))
    if text_color is None:
        final_text_color = style["text_color"]
    else:
        final_text_color = text_color
    text_surface = font.render(
        str(text),
        True,
        final_text_color,
    )

    text_rect = text_surface.get_rect(
        center=component_rect.center,
    )

    screen.blit(text_surface, text_rect)

    # 返回区域，供点击检测使用
    return component_rect

def draw_chips(screen, chips):
    rectangles = {}
    for chip in chips:
        rectangles[chip["value"]] = draw_component(
            screen,
            "chip",
            f'${chip["value"]}',
            chip["position"],
            chip["color"],
            chip["text_color"]
        )
        


    return rectangles


def draw_background(screen, text):
    screen.fill((30, 120, 30))  # 背景颜色
    font = pygame.font.SysFont(None, 72)
    title_text = font.render(text, True, (255, 255, 255))
    title_rect = title_text.get_rect(midtop=(screen.get_width() // 2, 100))
    screen.blit(title_text, title_rect)

def draw_hand(
    screen,
    deck,
    hand,
    start_position,
    hide_second=False,
    max_width=1100,
):
    start_x, y = start_position

    for index, card in enumerate(hand):
        x = start_x + index * min(120, max_width / max(1, len(hand) - 1))
        position = (x, y)

        if hide_second and index == 1:
            card_text = "?"
            fill_color = (50, 70, 130)
            text_color = (255, 255, 255)

        else:
            suit, rank = deck.get_card_identity(card)
            card_text = f"{rank}{suit}"
            fill_color = (255, 255, 255)

            if suit in ("♥", "♦"):
                text_color = (200, 0, 0)
            else:
                text_color = (0, 0, 0)

        draw_component(
            screen,
            "card",
            card_text,
            position,
            fill_color,
            text_color=text_color,
        )
    


def draw_text(screen, text, position, size=28, color=(255, 255, 255)):
    surface = get_font(size).render(str(text), True, color)
    screen.blit(surface, position)


def draw_actions(screen, actions):
    buttons = {}
    count = len(actions)
    for index, (name, label, enabled) in enumerate(actions):
        position = (screen.get_width() * (index + 0.5) / count,
                    screen.get_height() * 0.95)
        color = (80, 200, 80)
        if name in ("stand", "quit"):
            color = (200, 80, 80)
        elif name in ("save", "menu", "odds"):
            color = (200, 200, 200)
        rect = draw_component(
            screen, "button_small", label if enabled else "", position,
            color if enabled else (130, 130, 130))
        if not enabled:
            for text, offset, size in ((label, -15, 30),
                                       ("Unavailable", 15, 22)):
                surface = get_font(size).render(text, True, (0, 0, 0))
                screen.blit(surface, surface.get_rect(
                    center=(position[0], position[1] + offset)))
        if enabled:
            buttons[name] = rect
    return buttons


def draw_menu(screen, title, choices, message="", wide=False):
    draw_background(screen, title)
    buttons = {}
    for index, (key, label) in enumerate(choices):
        position = (screen.get_width() // 2, 260 + index * 90)
        if wide:
            rect = pygame.Rect(0, 0, 1040, 72)
            rect.center = position
            pygame.draw.rect(screen, (200, 200, 200), rect, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), rect, 3, border_radius=10)
            text = get_font(30).render(label, True, (0, 0, 0))
            screen.blit(text, text.get_rect(center=rect.center))
        else:
            rect = draw_component(screen, "button_small", label, position,
                                  (200, 80, 80) if key == "quit" else (200, 200, 200))
        buttons[key] = rect
    draw_text(screen, message, (80, 800), 26)
    return buttons


def draw_table(screen, state, title, actions, hand_labels, status):
    draw_background(screen, title)
    draw_text(screen, status, (40, 30), 28)
    draw_text(screen, state["message"], (40, 780), 26)
    deck = state["deck"]
    if state["stage_name"] == "bet stage":
        draw_component(screen, "button_big",
                       f'Money: ${state["current_money"]:g}',
                       (screen.get_width() * 0.5, screen.get_height() * 0.625),
                       (200, 200, 200))
    dealer = state["dealer_hand"]
    start = screen.get_width() / 2 - min(1100, max(0, len(dealer) - 1) * 120) / 2
    draw_hand(screen, deck, dealer, (start, 300),
              hide_second=not state["hole_revealed"])
    hand_count = len(state["hands"])
    for index, hand in enumerate(state["hands"]):
        column_width = screen.get_width() / hand_count
        center = column_width * (index + 0.5)
        available = column_width - 160
        span = min(available, max(0, len(hand["cards"]) - 1) * 120)
        draw_text(screen, hand_labels[index], (center - 280, 465), 30)
        draw_hand(screen, deck, hand["cards"], (center - span / 2, 590),
                  max_width=available)
    return draw_actions(screen, actions)


def draw_odds(screen, view, counts):
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 175))
    screen.blit(shade, (0, 0))
    panel = pygame.Rect(100, 150, 1400, 650)
    pygame.draw.rect(screen, (25, 65, 45), panel, border_radius=12)
    pygame.draw.rect(screen, (255, 255, 255), panel, 2, border_radius=12)
    draw_text(screen, "Show Odds - public information only", (140, 180), 40)
    labels = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10/J/Q/K")
    draw_text(screen, "Unknown pool (includes dealer hole card):", (140, 235), 28)
    draw_text(screen, "    ".join(f"{rank}: {n}" for rank, n in zip(labels, counts)),
              (140, 275), 28)
    columns = (("Action", 140), ("Win", 380), ("Push", 600),
               ("Lose", 820), ("Samples", 1050))
    for label, x in columns:
        draw_text(screen, label, (x, 330), 30)
    for index, action in enumerate(("Stand", "Hit", "Double", "Split")):
        y = 375 + index * 52
        draw_text(screen, action, (140, y), 30)
        result = view["results"].get(action)
        if result:
            for column, label in enumerate(("Win", "Push", "Lose")):
                draw_text(screen, f'{result[label]:.2%}', (380 + column * 220, y), 30)
            draw_text(screen, result["samples"], (1050, y), 30)
        else:
            label = ("Calculating..." if action in view.get("available", ())
                     else "Unavailable")
            draw_text(screen, label, (380, y), 30)
    note = view.get("error") or (
        "Complete" if view["complete"] else "Calculating in background...")
    draw_text(screen, note, (140, 595), 26)
    draw_text(screen, "Hit / Split: then hit below 17, stand on 17+. "
              "No further doubles or splits.",
              (140, 635), 26)
    draw_text(screen, "Split: mean per-hand odds (2 hands/sample). "
              "Other pending hands use the same policy.",
              (140, 670), 26)
    return draw_component(screen, "button_small", "Close", (1280, 735),
                          (200, 200, 200))
