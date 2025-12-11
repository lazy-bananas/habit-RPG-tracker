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
| POST   | `/auth/logout` | For user to log out     |
|POST    | `/auth/refresh/`| To get new access token|
|GET     | `/auth/me`      | To get profile         |
|GET     | `/auth/streaks/`| To get all the streaks of a user|

### 💪 HABITS
Method|	Endpoint             |	Description
GET   |	`/habits/`           |  List all habits
POST	| `/habits/`	         |  Create a new habit
POST	| `/habits/<id>/done`  |  Mark a habit as done + XP & streak update
POST	| `/habits/daily_reset`|	Reset streaks & restore health/mana daily

### 🎁 REWARDS

| Method | Endpoint       | Description                |
| ------ | -------------- | -------------------------- |
| GET    | `/rewards/`    | List all available rewards |
| POST   | `/rewards/buy` | Purchase a reward using XP |


### 🖼️ AVATAR

|Method | Endpoint         | Description   |
| GET   | `/avatar/list`   | List all available avatars |
| POST  | `/avatar/select` | Let user select an avatar  |
|POST   | `/avatar/seed`   | To add avatars in db (to be run only once) |
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
  "user_id": 1,
  "access_token": "<JWT_ACCESS_TOKEN>",
  "refresh_token": "<JWT_REFRESH_TOKEN>"
}
```

### **POST /auth/refresh**
 **Header**
 Authorization: Bearer <refresh_token>      (without quotes)

 **Response**
 ```json
 {
  "access_token": "<new_access_token>"
}
```

### **GET /auth/me**
**Headers**
Authorization: Bearer <access_token>  (without quotes)

**Response**
```json
{
  "user_id": 1,
  "username": "Sanchit",
  "email": "test@example.com",
  "xp": 120,
  "level": 2,
  "level_name": "Dormant Beginner",
  "mana": 80,
  "health": 90,
  "current_streak": 3,
  "longest_streak": 5
}
```

### **GET /auth/streaks**
**Header**
Authorization: Bearer <refresh_token>      (without quotes)

**Response**
```json
{
  "user": {
    "current_streak": 3,
    "longest_streak": 5,
    "last_completed": "2025-12-10"
  },
  "habits": [
    {
      "habit_id": 7,
      "name": "Drink Water",
      "streak": 4,
      "longest_streak": 6,
      "last_done": "2025-12-10"
    },
    {
      "habit_id": 8,
      "name": "Read 10 pages",
      "streak": 1,
      "longest_streak": 9,
      "last_done": "2025-12-09"
    }
  ]
}
```


### **POST /auth/logout**

**Endpoint** 
POST /auth/logout

**Response**
```json
{
  "message": "Logged out successfully"
}
```


### **GET /habits/**
**Header**
Authorization: Bearer <refresh_token>      (without quotes)

**Response**
```json
[
  {
    "id": 1,
    "name": "Running",
    "habit_type": "good",
    "habit_nature": "physical",
    "xp_value": 10,
    "streak": 3,
    "last_done": "2025-12-10"
  },
  ...
]
```

### **POST /habits/**

**Request**
xp_value and cover_photo are optional
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
  "habit_id": 13,
  "message": "Habit created",
  "user_id": 1
}
```

### **POST /habits/<habit_id>/done**

**Request**

```json
{
  "habit_id": 1
}
```

**Response**

```json
{
  "health": 40,
  "level": 1,
  "longest_streak": 1,
  "mana": 40,
  "message": "Habit completed",
  "rank": "Dormant Beginner",
  "streak": 1,
  "xp": 20
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

### **GET /avatar/list**

**Resonse**
```json
[
  {
    "avatar_id": 1,
    "filename": "warrior.png",
    "url": "/static/avatars/warrior.png"
  },
  {
    "avatar_id": 2,
    "filename": "mage.png",
    "url": "/static/avatars/mage.png"
  }
]
```

### **POST /avatar/select**
 **Header**
 Authorization: Bearer <refresh_token>      (without quotes)

**Request**
```json
{
  "avatar_id": 2
}
```
**Response**
```json
{
  "message": "Avatar updated successfully"
}
```


### **POST /avatar/seed**
**Response**
```json
{
  "message": "Avatar list updated",
  "inserted": ["hero.png", "mage.png", "archer.png"]
}
```
