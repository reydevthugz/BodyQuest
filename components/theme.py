"""Centralized Cyan & Black design system for GymBro."""
import flet as ft

# ── Core palette ─────────────────────────────────────────────────────────────
BACKGROUND = "#02060A"
BACKGROUND_2 = "#050B12"
SURFACE = "#07111C"
CARD = "#081A24"
CARD_HOVER = "#0A2633"

PRIMARY_CYAN = "#00E5FF"
NEON_CYAN = "#00FFFF"
DEEP_CYAN = "#008FA3"
MUTED_CYAN = "#5DAEBB"
TEXT_CYAN = "#D7FBFF"
SUBTEXT_CYAN = "#86C8D4"
BORDER_CYAN = "#00E5FF"
DARK_BORDER = "#073341"
BLACK = "#000000"

CARD_RADIUS = 20
BUTTON_RADIUS = 14
PAGE_PADDING = 28

# Compatibility aliases
BACKGROUND_COLOR = BACKGROUND
SURFACE_COLOR = SURFACE
CARD_COLOR = CARD
SURFACE_SOFT = BACKGROUND_2
PRIMARY_COLOR = PRIMARY_CYAN
SECONDARY_COLOR = DEEP_CYAN
ACCENT_COLOR = NEON_CYAN
TEXT_COLOR = TEXT_CYAN
MUTED_TEXT_COLOR = MUTED_CYAN
SUBTLE_TEXT_COLOR = SUBTEXT_CYAN
ERROR_TEXT_COLOR = NEON_CYAN

BORDER_COLOR = f"{BORDER_CYAN}30"
BORDER_STRONG = f"{BORDER_CYAN}55"
BORDER_SUBTLE = f"{BORDER_CYAN}16"
LIST_ROW_BORDER = f"{BORDER_CYAN}14"

GLASS_BG = f"{PRIMARY_CYAN}14"
GLASS_GRADIENT_START = f"{PRIMARY_CYAN}12"
CARD_SHADOW = "#00000088"
GOAL_CARD_BG = f"{PRIMARY_CYAN}10"

INPUT_BG = f"{PRIMARY_CYAN}12"
INPUT_BORDER = f"{PRIMARY_CYAN}22"
INPUT_FOCUS = PRIMARY_CYAN

SURFACE_ROW = f"{PRIMARY_CYAN}0E"
SURFACE_ROW_HOVER = f"{BORDER_CYAN}14"
PROGRESS_TRACK = f"{PRIMARY_CYAN}18"
PROFILE_SURFACE = f"{PRIMARY_CYAN}0D"

BTN_SECONDARY_BG = SURFACE
BTN_SECONDARY_BG_HOVER = CARD_HOVER
BUTTON_TEXT_ON_PRIMARY = BLACK
GLOW_CYAN = f"{PRIMARY_CYAN}40"
GLOW_AQUA = f"{NEON_CYAN}30"

TIMELINE_COMPLETED_BG = f"{NEON_CYAN}18"
TIMELINE_CURRENT_BG = GLOW_CYAN
TIMELINE_LOCKED_BG = SURFACE_ROW

DANGER_BORDER = BORDER_CYAN
DANGER_TEXT = NEON_CYAN
DANGER_BG = f"{NEON_CYAN}14"

GRADIENT_COLORS = [GLOW_CYAN, GLOW_AQUA]
SIDEBAR_GRADIENT_USER = [f"{PRIMARY_CYAN}12", SURFACE]
SIDEBAR_GRADIENT_ADMIN = [f"{NEON_CYAN}12", SURFACE]
TRANSPARENT = "#00000000"

SUCCESS_COLOR = ACCENT_COLOR
STAT_COLORS = (PRIMARY_CYAN, SECONDARY_COLOR, ACCENT_COLOR, SECONDARY_COLOR, PRIMARY_CYAN, ACCENT_COLOR)


def get_page_bg() -> ft.LinearGradient:
    return ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=[BACKGROUND, BACKGROUND_2, SURFACE, BACKGROUND],
    )


page_background = get_page_bg


def ambient_orbs() -> list[ft.Control]:
    return [
        ft.Container(
            width=440,
            height=440,
            right=-150,
            top=-190,
            border_radius=999,
            bgcolor=GLOW_CYAN,
            blur=48,
        ),
        ft.Container(
            width=380,
            height=380,
            left=-130,
            bottom=-170,
            border_radius=999,
            bgcolor=GLOW_AQUA,
            blur=52,
        ),
    ]


def glass_border(side_width: int = 1, color: str = BORDER_COLOR) -> ft.Border:
    side = ft.BorderSide(side_width, color)
    return ft.Border(top=side, right=side, bottom=side, left=side)


def accent_surface(accent: str = PRIMARY_CYAN) -> tuple[str, ft.Border]:
    """Return (bgcolor, border) for mini accent panels."""
    return f"{accent}14", glass_border(1, f"{accent}44")


def feedback_text(value: str = "", *, error: bool = False) -> ft.Text:
    return ft.Text(value, color=NEON_CYAN if error else PRIMARY_CYAN, size=12)


def auth_text_field(
    label: str,
    icon: str,
    password: bool = False,
    hint_text: str = "",
) -> tuple[ft.Column, ft.TextField]:
    field = ft.TextField(
        password=password,
        can_reveal_password=password,
        bgcolor=INPUT_BG,
        border_radius=12,
        border_color=INPUT_BORDER,
        focused_border_color=INPUT_FOCUS,
        cursor_color=PRIMARY_CYAN,
        text_style=ft.TextStyle(color=TEXT_COLOR, size=14),
        prefix_icon=icon,
        hint_text=hint_text,
        hint_style=ft.TextStyle(color=SUBTLE_TEXT_COLOR),
    )
    return (
        ft.Column(
            spacing=8,
            controls=[
                ft.Text(label, color=MUTED_TEXT_COLOR, size=13, weight=ft.FontWeight.W_500),
                field,
            ],
        ),
        field,
    )


def info_panel(content: ft.Control, accent: str = PRIMARY_CYAN) -> ft.Container:
    bg, border = accent_surface(accent)
    return ft.Container(
        padding=12,
        border_radius=12,
        bgcolor=bg,
        border=border,
        content=content,
    )


def themed_text_field(**kwargs) -> ft.TextField:
    defaults = {
        "bgcolor": INPUT_BG,
        "border_color": INPUT_BORDER,
        "focused_border_color": INPUT_FOCUS,
        "cursor_color": PRIMARY_CYAN,
        "text_style": ft.TextStyle(color=TEXT_COLOR),
        "border_radius": 12,
    }
    defaults.update(kwargs)
    return ft.TextField(**defaults)


def themed_dropdown(**kwargs) -> ft.Dropdown:
    defaults = {
        "bgcolor": INPUT_BG,
        "border_color": INPUT_BORDER,
        "focused_border_color": INPUT_FOCUS,
        "color": TEXT_COLOR,
        "border_radius": 12,
    }
    defaults.update(kwargs)
    return ft.Dropdown(**defaults)


def brand_header(size: int = 28) -> ft.Row:
    return ft.Row(
        controls=[
            ft.Icon(ft.Icons.FITNESS_CENTER, color=PRIMARY_CYAN, size=size),
            ft.Text("GYMBRO", color=TEXT_COLOR, size=size, weight=ft.FontWeight.BOLD),
            ft.Icon(ft.Icons.BOLT, color=NEON_CYAN, size=max(size // 2, 16)),
        ],
    )


def glass_container_style() -> dict[str, object]:
    return {
        "bgcolor": GLASS_BG,
        "border": glass_border(1, BORDER_CYAN),
        "border_radius": CARD_RADIUS,
        "gradient": ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[GLASS_GRADIENT_START, CARD, CARD],
        ),
        "shadow": ft.BoxShadow(spread_radius=0, blur_radius=32, color=CARD_SHADOW, offset=ft.Offset(0, 14)),
    }


def card_style() -> dict[str, object]:
    return {
        "padding": 20,
        "bgcolor": CARD,
        "border_radius": CARD_RADIUS,
        "border": glass_border(1, BORDER_CYAN),
        "shadow": ft.BoxShadow(spread_radius=0, blur_radius=24, color=CARD_SHADOW, offset=ft.Offset(0, 12)),
    }


def input_style() -> dict[str, object]:
    return {
        "bgcolor": INPUT_BG,
        "border_color": INPUT_BORDER,
        "focused_border_color": INPUT_FOCUS,
        "cursor_color": PRIMARY_CYAN,
        "text_style": ft.TextStyle(color=TEXT_COLOR),
        "border_radius": 12,
    }


def primary_button_style() -> ft.ButtonStyle:
    return ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=BUTTON_RADIUS),
        bgcolor={ft.ControlState.DEFAULT: PRIMARY_CYAN, ft.ControlState.HOVERED: NEON_CYAN},
        color={ft.ControlState.DEFAULT: BUTTON_TEXT_ON_PRIMARY, ft.ControlState.HOVERED: BUTTON_TEXT_ON_PRIMARY},
        elevation=8,
        shadow_color=GLOW_CYAN,
        padding=ft.Padding(18, 14, 18, 14),
        text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600),
    )


def secondary_button_style() -> ft.ButtonStyle:
    return ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=BUTTON_RADIUS),
        side={ft.ControlState.DEFAULT: ft.BorderSide(1, BORDER_CYAN), ft.ControlState.HOVERED: ft.BorderSide(1, NEON_CYAN)},
        color={ft.ControlState.DEFAULT: TEXT_CYAN, ft.ControlState.HOVERED: NEON_CYAN},
        bgcolor={ft.ControlState.DEFAULT: BTN_SECONDARY_BG, ft.ControlState.HOVERED: BTN_SECONDARY_BG_HOVER},
        padding=ft.Padding(16, 13, 16, 13),
        text_style=ft.TextStyle(size=13, weight=ft.FontWeight.W_600),
    )


def nav_item_style(active: bool = False) -> dict[str, object]:
    return {
        "bgcolor": CARD_HOVER if active else None,
        "border": ft.Border(
            top=ft.BorderSide(0, TRANSPARENT),
            right=ft.BorderSide(0, TRANSPARENT),
            bottom=ft.BorderSide(0, TRANSPARENT),
            left=ft.BorderSide(3, PRIMARY_CYAN if active else TRANSPARENT),
        ),
    }


def role_badge_style() -> dict[str, object]:
    return {
        "bgcolor": f"{PRIMARY_CYAN}10",
        "border_radius": 8,
        "padding": ft.Padding(8, 4, 8, 4),
        "border": glass_border(1, f"{PRIMARY_CYAN}44"),
    }


def page_title_style() -> ft.TextStyle:
    return ft.TextStyle(color=TEXT_CYAN, size=30, weight=ft.FontWeight.BOLD)


def empty_state_style() -> dict[str, object]:
    return {
        "title_color": TEXT_CYAN,
        "message_color": MUTED_CYAN,
        "icon_color": PRIMARY_CYAN,
    }
