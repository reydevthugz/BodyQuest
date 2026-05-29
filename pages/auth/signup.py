import flet as ft

from components.auth_layout import auth_shell
from components.buttons import link_button, neon_button
from components.theme import ERROR_TEXT_COLOR, auth_text_field, feedback_text
from controllers.auth_controller import handle_signup


def signup_view(page: ft.Page) -> ft.View:
    name_col, name_field = auth_text_field("Full Name", ft.Icons.PERSON_OUTLINE, hint_text="Your full name")
    email_col, email_field = auth_text_field("Email", ft.Icons.MAIL_OUTLINE, hint_text="Enter your email")
    password_col, password_field = auth_text_field("Password", ft.Icons.LOCK_OUTLINE, password=True, hint_text="Create a password")
    confirm_col, confirm_field = auth_text_field(
        "Confirm Password",
        ft.Icons.LOCK_OUTLINE,
        password=True,
        hint_text="Re-enter password",
    )
    info_text = feedback_text()

    def submit(_: ft.ControlEvent) -> None:
        result = handle_signup(
            page,
            name_field.value or "",
            email_field.value or "",
            password_field.value or "",
            confirm_field.value or "",
        )
        msg = result["message"] or (result["errors"][0] if result["errors"] else "")
        info_text.value = msg
        if not result["success"]:
            info_text.color = ERROR_TEXT_COLOR
            page.update()
            return
        page.snack_bar = ft.SnackBar(ft.Text(result["message"]))
        page.snack_bar.open = True
        page.go(result["data"]["route"])

    form = ft.Column(
        spacing=16,
        controls=[
            name_col,
            email_col,
            password_col,
            confirm_col,
            neon_button("Create Account", ft.Icons.PERSON_ADD_ALT_1, submit, width=420),
            info_text,
            link_button("Already have an account? Login", lambda _: page.go("/login")),
            link_button("Back to Home", lambda _: page.go("/"), muted=True),
        ],
    )
    return auth_shell(page, "Create Account", "Build your beginner fitness plan.", form)
