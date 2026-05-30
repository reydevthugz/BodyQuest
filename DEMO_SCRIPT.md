# BodyQuest — Final Demo Script

**Project Name: BodyQuest**

A simple, natural script for student presentation (~8–12 minutes).

---

## Intro (30 seconds)

> "Good [morning/afternoon], everyone. I'm [your name], and today I'll present **BodyQuest** — a beginner fitness plan tracker built with **Python Flet** and **MySQL on Laragon**.
>
> BodyQuest helps beginners choose a fitness goal, follow a daily workout plan, unlock activities one day at a time, and earn achievements. There's also an **admin panel** to monitor real registered users and system progress.
>
> Let me show you how it works."

---

## User Demo (5–6 minutes)

### 1. Sign up

> "First, I'll register as a new user — the system does **not** create fake demo accounts. Only the admin account is pre-seeded."

- Open app → **Sign up**
- Enter full name, email, password (8+ chars, letter and number), confirm password
- Submit → success message → redirected to **Goal Setup**

### 2. Choose goal and start plan

> "The user picks one of five beginner goals. Each goal has a suggested plan length."

- Select **General Fitness** (or any goal)
- **Plan Preview** → show first week sample
- Click **Start Plan** → snackbar → **Dashboard**

### 3. Dashboard and activity

> "The dashboard shows today's activity, progress bar, and recent achievements."

- Point out **Day 1**, progress stats
- Open **Daily Activity**
- Read warmup / main / cooldown
- Click **Mark as Completed**
- Note message: next day unlocked

### 4. Timeline and history

> "The timeline shows completed, current, and locked days. History keeps all finished workouts even if the user changes plans later."

- Open **Plan Timeline** → Day 2 unlocked, later days locked
- Open **Workout History** → Day 1 listed with date
- Open **My Achievements** → e.g. "First Step Completed"

### 5. Change plan (optional but recommended)

> "If the user wants a new goal, they can change plan. The old active plan is replaced, but completed workouts stay in history."

- **Dashboard** or **Profile** → **Change Plan** → **Continue**
- Pick a new goal → preview → **Start Plan**
- Check **Workout History** — old completions still visible

### 6. User logout

> "The user logs out and the session is cleared."

- **Profile** → **Logout** → Login page

---

## Admin Demo (4–5 minutes)

### 1. Admin login

> "Now I'll log in as the system administrator. The default admin is `admin@bodyquest.com`."

- Login: `admin@bodyquest.com` / `admin123`
- Redirect to **Admin Dashboard**

### 2. Dashboard and users

> "The admin sees totals from real MySQL data — user count excludes the admin account."

- Show stat cards, goal distribution, recent activity
- Open **User Management**
- Search or filter if needed
- Click **View Details** on the user you created

### 3. Selected user drill-down

> "Admin can inspect any user's progress without logging in as them."

- **User Details** — goal, progress %, achievements count
- **View User Achievements**
- **View User Workout History**

### 4. System-wide views

> "These pages summarize the whole system."

- **All Achievements**
- **Leaderboard** — ranking by achievements and progress
- **Reports** — most selected goal, averages, plan counts

### 5. Admin logout

- **Admin Profile** → **Logout**

---

## Outro (30 seconds)

> "To summarize: BodyQuest separates **user** and **admin** experiences, stores everything in **MySQL**, uses **role-based routing** and **password hashing**, and guides beginners with **sequential unlocks** and **achievements**.
>
> For the future, we could deploy to a cloud database, add mobile support, or email reminders.
>
> Thank you. I'm happy to answer questions."

---

## Quick Reference

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@bodyquest.com` | `admin123` |
| User | *(your signup)* | *(your password)* |

**Run before demo:**

```bash
pip install -r requirements.txt
py main.py
```

See [DEMO_CHECKLIST.md](DEMO_CHECKLIST.md) for tick-box rehearsal.
