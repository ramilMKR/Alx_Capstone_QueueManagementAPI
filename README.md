# Queue Management REST API

A Django REST API for managing service queues where users can join, leave and track their position in real time.  
Administrators can manage queues and serve the next user in line.

This project demonstrates backend API development using Django, Django REST Framework, JWT authentication and real-time features.


## Features

- User registration and authentication (JWT)
- Create and manage service queues
- Join and leave queues
- View current queue position
- Admin can serve the next person in queue
- Prevent duplicate queue entries
- Queue position validation
- RESTful API structure
- Optional real-time updates with WebSockets


## Tech Stack

Backend Framework:

- Python
- Django
- Django REST Framework

Authentication:

- Simple JWT

Database:

- SQLite (development)
- PostgreSQL (production ready)

Optional Extensions:

- Django Channels (WebSockets)
- Redis
- Celery (background tasks)

Development Tools:

- Insomnia / Postman (API testing)
- Visual Studio Code


## Project Structure

```queue_api/
```│
```├── accounts/
```│ ├── models.py
```│ ├── serializers.py
```│ ├── views.py
```│ └── urls.py
```│
```├── queues/
```│ ├── models.py
```│ ├── serializers.py
```│ ├── views.py
```│ ├── routing.py
```│ ├── consumers.py
```│ └── tasks.py
```│
```├── queue_api/
```│ ├── settings.py
```│ ├── urls.py
│ └── asgi.py
│
├── manage.py
├── db.sqlite3
└── README.md


## Installation

### 1. Clone the repository

git clone <https://github.com/yourusername/queue-management-api.git>
cd queue-management-api

### 2. Create virtual environment and activate it

Create it:
python -m venv venv

Activate it:
Windows
venv\Scripts\activate

Mac/Linux
source venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Run migrations

python manage.py makemigrations
python manage.py migrate

### 5. Create admin user

python manage.py createsuperuser

### 6. Start the server

python manage.py runserver

API will run at:

<http://127.0.0.1:8000>


## API Endpoints

1. Register a user

POST /api/register/

2. Login and receive JWT token

POST /api/login/

3. Get all queues

GET /api/queues/

4. Create queue (Admin only)

POST /api/queues/create/

5. Join queue

POST /api/queues/{queue_id}/join/

6. Leave queue

POST /api/queues/{queue_id}/leave/

7. Check your position

GET /api/my-position/

8. Serve next user in queue (Admin)

POST /api/queues/{queue_id}/next/


## Testing the API

The API can be tested using:

- Insomnia
- Postman

## Author

Michael