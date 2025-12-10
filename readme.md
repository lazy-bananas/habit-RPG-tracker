# 🧩 Habit RPG Tracker - Backend

### 🚀 Setup

```bash
pip install -r requirements.txt
python app.py
```

### 🗄️ Database

```
MySQL URI → mysql+pymysql://root:123456@localhost/habit_rpg
```

Make sure MySQL is running before you start the Flask server.
You can initialize tables using:

```python
from app import db, app
with app.app_context():
    db.create_all()
```

## 🌐 API Endpoints

### 🔐 AUTH

| Method | Endpoint       | Description             |
| ------ | -------------- | ----------------------- |
| POST   | `/auth/signup` | Register a new user     |
| POST   | `/auth/login`  | Log in an existing user |

### 💪 HABITS
Method|	Endpoint             |	Description
GET   |	/habits/	           |  List all habits
POST	| /habits/	           |  Create a new habit
POST	| /habits/<id>/done	   |  Mark a habit as done + XP & streak update
POST	| /habits/daily_reset  |	Reset streaks & restore health/mana daily

### 🎁 REWARDS

| Method | Endpoint       | Description                |
| ------ | -------------- | -------------------------- |
| GET    | `/rewards/`    | List all available rewards |
| POST   | `/rewards/buy` | Purchase a reward using XP |

---

## 🧱 Example Requests & Responses

### **POST /auth/signup**

**Request**

```json
{
  "username": "Sanchit",
  "email": "sanchit@example.com",
  "password": "123456"
}
```

**Response**

```json
{
  "message": "Signup successful",
  "user_id": 1
}
```

### **POST /auth/login**

**Request**

```json
{
  "email": "sanchit@example.com",
  "password": "123456"
}
```

**Response**

```json
{
  "message": "Login successful",
  "user_id": 1
}
```

### **POST /habits/**

**Request**

```json
{
  "user_id": 1,
  "name": "Read for 30 mins",
  "habit_type": "good",
  "habit_nature": "mental",
  "xp_value": 20,
  "cover_photo": "https://example.com/book.jpg"
}
```

**Response**

```json
{
  "message": "Habit created"
}
```

### **POST /habits/<habit_id>/done**

**Request**

```json
{
  "habit_id": 2
}
```

**Response**

```json
{
  "message": "Updated XP and streak",
  "new_xp": 120,
  "level": 2
}
```

### **GET /rewards/**

**Response**

```json
[
  { "id": 1, "name": "Watch a Movie", "cost": 50 },
  { "id": 2, "name": "Eat Out", "cost": 100 }
]
```

### **POST /rewards/buy**

**Request**

```json
{
  "user_id": 1,
  "reward_id": 2
}
```

**Response**

```json
{
  "message": "Reward purchased successfully",
  "remaining_xp": 80
}
```