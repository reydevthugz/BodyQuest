# GymBro — Demo Checklist

Use this checklist before and during your presentation.

**Related docs:** [DEMO_SCRIPT.md](DEMO_SCRIPT.md) (spoken script) · [FINAL_CHECKLIST.md](FINAL_CHECKLIST.md) (full submission) · [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

---

## Section 1: Before Demo

- [ ] Start **Laragon**
- [ ] Start **MySQL** (green in Laragon)
- [ ] Optional: open **phpMyAdmin** → confirm database **`gymbro`** exists
- [ ] Open terminal in project folder: `C:\laragon\www\GYMBRO`
- [ ] Install dependencies (if needed):
  ```bash
  pip install -r requirements.txt
  ```
- [ ] Run the app:
  ```bash
  py main.py
  ```
- [ ] Confirm console shows admin seed message (created or already exists)
- [ ] Confirm **no demo user accounts** are created automatically

**Default admin only:**

- Email: `admin@gymbro.com`
- Password: `admin123`

---

## Section 2: User Demo Flow

1. [ ] Open app → Login page shows **admin note only** (no demo user credentials)
2. [ ] Click **Sign up**
3. [ ] Register a **new real user** (your name + email)
4. [ ] See success message → redirected to **Goal Setup** (`/user/goal-setup`)
5. [ ] Select a fitness goal (e.g. General Fitness)
6. [ ] **Plan Preview** → review first week
7. [ ] Click **Start Plan** → snackbar: plan ready → **Dashboard**
8. [ ] Open **Today's Activity** → complete Day 1
9. [ ] Confirm message: next activity unlocked
10. [ ] **Plan Timeline** → Day 2 unlocked
11. [ ] **My Achievements** → at least one badge (e.g. First Step)
12. [ ] **Workout History** → completed day listed
13. [ ] **Change Plan** → confirm dialog → pick new goal → start new plan
14. [ ] **Workout History** → old completed days still visible
15. [ ] **Logout** → back to Login

---

## Section 3: Admin Demo Flow

1. [ ] Login as admin: `admin@gymbro.com` / `admin123`
2. [ ] Redirect to **Admin Dashboard** (`/admin/dashboard`)
3. [ ] If no users yet: friendly **empty states** (no crash)
4. [ ] After user demo: refresh stats on dashboard
5. [ ] **User Management** → see registered user(s)
6. [ ] **View Details** → progress, goal, achievements count
7. [ ] **User Achievements** → badges for that user
8. [ ] **User Workout History** → completed workouts
9. [ ] **All Achievements** → system-wide list
10. [ ] **Leaderboard** → ranked users (or empty state before users)
11. [ ] **Reports** → summary metrics
12. [ ] **Admin Profile** → admin info
13. [ ] **Logout** → Login page

---

## Section 4: Common Questions & Answers

### Why Python Flet?

Flet lets us build a modern desktop UI in pure Python—good fit for a fitness dashboard with fast iteration and a single language stack.

### Why MySQL / Laragon?

Laragon provides a local MySQL server similar to production setups. Data persists across sessions: users, plans, progress, and achievements.

### What is the admin role?

The admin monitors the system: registered users, active plans, achievements, and reports. Only one default admin is seeded; admins do not follow workout plans as end users.

### How does the unlock system work?

Day 1 starts unlocked. Completing the current day marks it done and unlocks the next day in sequence until the plan is finished.

### How does change plan work?

The user picks a new goal. The active plan is replaced; completed workout days remain in **Workout History** under their original plans.

### How are achievements earned?

Rules include first completed day, streaks (3/7 days), goal-type badges, and completing the full plan. Achievements are stored in MySQL when conditions are met.

### Why are there no demo user accounts?

The system uses only a default admin account. Normal users are created through the **Signup** page so the demo reflects real registration and real progress tracking.

---

## Section 5: Quick Verification

| Check | Expected |
|-------|----------|
| `py main.py` | App window opens |
| Admin seed | One admin only; no sample users |
| Signup | Creates `role = user` in MySQL |
| User routes | All `/user/*` pages load |
| Admin routes | All `/admin/*` pages load |
| 404 | Unknown route shows not-found page |
| Logout | Clears session, returns to login |

---

## Final Run Command

```bash
pip install -r requirements.txt
py scripts\validate_phase10.py
py main.py
```
