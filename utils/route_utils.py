PUBLIC_ROUTES = {"/", "/landing", "/login", "/signup", "/404"}

AUTH_ROUTES = {"/login", "/signup"}

USER_ROUTES = {
    "/user/dashboard",
    "/user/goal-setup",
    "/user/plan-preview",
    "/user/activity",
    "/user/timeline",
    "/user/achievements",
    "/user/history",
    "/user/profile",
    "/user/change-plan",
}

ADMIN_ROUTES = {
    "/admin/dashboard",
    "/admin/users",
    "/admin/users/details",
    "/admin/users/achievements",
    "/admin/users/history",
    "/admin/achievements",
    "/admin/leaderboard",
    "/admin/reports",
    "/admin/profile",
}

ALL_ROUTES = PUBLIC_ROUTES | USER_ROUTES | ADMIN_ROUTES


def normalize_route(route: str) -> str:
    if route == "":
        return "/"
    return route


def is_known_route(route: str) -> bool:
    return route in ALL_ROUTES
