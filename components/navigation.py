import flet as ft

# User sidebar — main navigation only (goal setup / plan preview / change plan via flow, not nav)
USER_NAV_ITEMS = [
    ("dashboard", "Dashboard", ft.Icons.DASHBOARD_ROUNDED),
    ("timeline", "Plan Timeline", ft.Icons.CALENDAR_MONTH),
    ("activity", "Today's Activity", ft.Icons.DIRECTIONS_RUN),
    ("achievements", "My Achievements", ft.Icons.MILITARY_TECH),
    ("history", "Workout History", ft.Icons.HISTORY),
    ("profile", "Profile", ft.Icons.PERSON),
]

# Admin sidebar — management navigation only (user drill-down via User Management)
ADMIN_NAV_ITEMS = [
    ("dashboard", "Admin Dashboard", ft.Icons.DASHBOARD_ROUNDED),
    ("users", "User Management", ft.Icons.GROUPS_2_ROUNDED),
    ("achievements", "All Achievements", ft.Icons.EMOJI_EVENTS),
    ("leaderboard", "Leaderboard", ft.Icons.LEADERBOARD),
    ("reports", "Reports", ft.Icons.SUMMARIZE),
    ("profile", "Admin Profile", ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED),
]
