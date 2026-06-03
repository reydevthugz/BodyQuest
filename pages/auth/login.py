import flet as ft

from components.auth_layout import auth_shell
from components.buttons import link_button, neon_button
from components.theme import ERROR_TEXT_COLOR, MUTED_TEXT_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, auth_text_field, feedback_text, info_panel
from config.settings import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD
from controllers.auth_controller import handle_login
from utils.navigation import go


def login_view(page: ft.Page) -> ft.View:
    email_col, email_field = auth_text_field("Email", ft.Icons.MAIL_OUTLINE, hint_text="Enter your email")
    password_col, password_field = auth_text_field("Password", ft.Icons.LOCK_OUTLINE, password=True, hint_text="Password")
    info_text = feedback_text()

    admin_note = info_panel(
        ft.Column(
            spacing=4,
            controls=[
                ft.Text("Admin access", color=PRIMARY_COLOR, size=12, weight=ft.FontWeight.W_600),
                ft.Text(f"{DEFAULT_ADMIN_EMAIL} / {DEFAULT_ADMIN_PASSWORD}", color=MUTED_TEXT_COLOR, size=12),
                ft.Text("New users can sign up to create a normal account.", color=MUTED_TEXT_COLOR, size=11),
            ],
        ),
        accent=SECONDARY_COLOR,
    )

    def submit(_: ft.ControlEvent | None = None) -> None:
        result = handle_login(page, email_field.value or "", password_field.value or "")
        if not result["success"]:
            msg = result["message"] or (result["errors"][0] if result["errors"] else "Login failed.")
            info_text.value = msg
            info_text.color = ERROR_TEXT_COLOR
            page.snack_bar = ft.SnackBar(ft.Text(msg))
            page.snack_bar.open = True
            page.update()
            return
        go(page, result["data"]["route"])

    password_field.on_submit = submit

    form = ft.Column(
        spacing=18,
        controls=[
            email_col,
            password_col,
            neon_button("Login", ft.Icons.ARROW_FORWARD_ROUNDED, submit, width=420),
            admin_note,
            info_text,
            link_button("No account yet? Sign up", lambda _: go(page, "/signup")),
            link_button("Back to Home", lambda _: go(page, "/"), muted=True),
        ],
    )
    return auth_shell(page, "Welcome to BodyQuest", "Continue your progress today.", form)
