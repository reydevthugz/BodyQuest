# GymBro — Project Structure

## Folder Tree

```
GYMBRO/
├── main.py                      # Entry: DB health, migrations, admin seed, launch Flet
├── app.py                       # Flet page setup, route change handler
├── router.py                    # Route guard + view resolver
├── requirements.txt             # flet, mysql-connector-python
├── README.md                    # Main project readme
├── SYSTEM_OVERVIEW.md           # System description for defense
├── DEFENSE_GUIDE.md             # Q&A for instructors
├── INSTALLATION_GUIDE.md          # Setup and troubleshooting
├── DEMO_SCRIPT.md               # Presentation script
├── DEMO_CHECKLIST.md            # Rehearsal checklist
├── FINAL_CHECKLIST.md           # Pre-submission checklist
├── PROJECT_STRUCTURE.md         # This file
│
├── config/
│   └── settings.py              # DB credentials, app name, admin defaults
│
├── database/
│   ├── connection.py            # MySQL connect, health check
│   ├── migrations.py            # CREATE TABLE / safe ALTER
│   ├── seeders.py               # Default admin only (no demo users)
│   └── db.py                    # Compatibility shim
│
├── models/
│   ├── user_model.py
│   ├── goal_model.py            # Goal types, durations, descriptions
│   ├── workout_model.py         # Day templates per goal
│   ├── progress_model.py
│   └── achievement_model.py
│
├── repositories/                # SQL only (parameterized)
│   ├── user_repository.py
│   ├── goal_repository.py
│   ├── workout_repository.py
│   ├── progress_repository.py
│   ├── achievement_repository.py
│   └── admin_repository.py
│
├── requests/                    # Input validation only
│   ├── auth_request.py
│   ├── goal_request.py
│   ├── progress_request.py
│   └── admin_request.py
│
├── controllers/                 # Page actions → services
│   ├── auth_controller.py
│   ├── goal_controller.py
│   ├── progress_controller.py
│   ├── achievement_controller.py
│   ├── admin_controller.py
│   └── user_controller.py
│
├── services/                    # Business logic
│   ├── auth_service.py
│   ├── session_service.py
│   ├── plan_service.py
│   ├── progress_service.py
│   ├── achievement_service.py
│   └── admin_service.py
│
├── components/                  # Reusable Flet UI
│   ├── theme.py
│   ├── cards.py
│   ├── buttons.py
│   ├── navigation.py
│   ├── user_layout.py
│   ├── admin_layout.py
│   ├── dialogs.py
│   ├── empty_states.py
│   └── ui.py                    # Re-exports
│
├── pages/
│   ├── auth/
│   │   ├── login.py
│   │   ├── signup.py
│   │   └── not_found.py
│   ├── user/
│   │   ├── dashboard.py
│   │   ├── goal_setup.py
│   │   ├── plan_preview.py
│   │   ├── activity.py
│   │   ├── timeline.py
│   │   ├── achievements.py
│   │   ├── history.py
│   │   ├── profile.py
│   │   ├── common.py
│   │   └── __init__.py          # user_view() dispatcher
│   ├── admin/
│   │   ├── dashboard.py
│   │   ├── users.py
│   │   ├── user_details.py
│   │   ├── user_achievements.py
│   │   ├── user_history.py
│   │   ├── all_achievements.py
│   │   ├── leaderboard.py
│   │   ├── reports.py
│   │   ├── profile.py
│   │   ├── _helpers.py
│   │   └── __init__.py          # admin_view() dispatcher
│   ├── auth_pages.py            # Shim imports
│   ├── user_pages.py
│   └── admin_pages.py
│
├── utils/
│   ├── route_utils.py
│   ├── response.py
│   ├── messages.py
│   ├── security.py
│   ├── validators.py
│   ├── auth_guard.py
│   ├── date_utils.py
│   └── format_utils.py
│
└── scripts/                     # Development validation (optional)
    ├── validate_phase6.py
    ├── validate_phase8.py
    ├── validate_phase8_qa.py
    ├── validate_phase9.py
    └── validate_phase10.py
```

## Purpose of Each Folder

| Folder | Purpose |
|--------|---------|
| `config/` | Constants and environment-style settings |
| `database/` | Connection, schema migrations, admin seeding |
| `models/` | Domain constants and workout templates |
| `repositories/` | All MySQL queries |
| `requests/` | Validate forms and inputs |
| `controllers/` | Bridge UI events to services; return routes/messages |
| `services/` | Rules: plans, unlocks, achievements, admin stats |
| `components/` | Shared visual building blocks |
| `pages/` | Full screens (Flet views) per route |
| `utils/` | Cross-cutting helpers |
| `scripts/` | Automated QA (not required to run the app) |

## Important Root Files

| File | Role |
|------|------|
| `main.py` | Startup sequence + `ft.run(app_main)` |
| `app.py` | Registers `on_route_change`, clears views each navigation |
| `router.py` | `route_guard()` + `resolve_view()` |

## Layer Dependency Direction

**Allowed (top → bottom only):**

```
pages → controllers → requests
                   → services → repositories → database
pages → components
pages → utils (messages, dates)
controllers → utils (response, auth_guard)
services → models
repositories → database.connection
```

**Not allowed:**

- Repositories importing pages or Flet
- Services building Flet controls
- Pages executing SQL
- Requests querying the database

## MVC + Request + Service + Repository

| Layer | Analogy | GymBro example |
|-------|---------|----------------|
| **Page (View)** | Screen | `pages/user/activity.py` |
| **Controller** | Event handler | `handle_complete_activity()` |
| **Request** | Form validator | `validate_signup()` |
| **Service** | Business rules | `complete_current_day()` |
| **Repository** | Data access | `WorkoutRepository.mark_day_completed()` |
| **Database** | Infrastructure | `get_connection()`, migrations |

This structure keeps the project **defense-ready**: each question maps to a clear layer.
