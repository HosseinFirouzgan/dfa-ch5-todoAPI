# Todo API

A simple full-stack Todo application built with **Django** and **Django REST Framework**. The project exposes a RESTful API for managing todo items and includes a minimal frontend for interacting with it.

<p align="center">
  <a href="https://ch5-todoapi-frontend.onrender.com/">Live Demo</a> •
  <a href="https://github.com/HosseinFirouzgan/dfa-ch5-todoAPI">Repository</a>
</p>

---

## Features

- Create todo items
- View all todos
- Update existing todos
- Delete todos
- Mark todos as completed
- RESTful API built with Django REST Framework
- Minimal frontend connected to the API
- Deployed on Render

---

## Tech Stack

### Backend

- Python
- Django 5
- Django REST Framework

### Frontend

- HTML
- CSS
- JavaScript

### Deployment

- Render
- Gunicorn
- WhiteNoise

---

## API Endpoints

Base URL

```
/api/
```

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/todos/` | Retrieve all todos |
| POST | `/api/todos/` | Create a new todo |
| GET | `/api/todos/<id>/` | Retrieve a single todo |
| PUT | `/api/todos/<id>/` | Replace a todo |
| PATCH | `/api/todos/<id>/` | Update part of a todo |
| DELETE | `/api/todos/<id>/` | Delete a todo |

---

## Todo Model

```json
{
    "id": 1,
    "title": "Study Django",
    "body": "Finish DRF tutorial",
    "completed": false
}
```

---

## Project Structure

```
dfa-ch5-todoAPI/
│
├── todo_app/            # Django project
├── todos/               # Todo application
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── static/
├── build.sh
├── requirements.txt
└── manage.py
```

---

## Running Locally

Clone the repository

```bash
git clone https://github.com/HosseinFirouzgan/dfa-ch5-todoAPI.git
cd dfa-ch5-todoAPI
```

Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

macOS / Linux

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run migrations

```bash
python manage.py migrate
```

Start the development server

```bash
python manage.py runserver
```

Open your browser at

```
http://127.0.0.1:8000/
```

---

## Technologies Used

- Django
- Django REST Framework
- Gunicorn
- WhiteNoise
- django-cors-headers

---

## What I Learned

This project helped me gain practical experience with:

- Building REST APIs using Django REST Framework
- Creating serializers and ViewSets
- Routing APIs with DRF routers
- Implementing CRUD operations
- Connecting a frontend to a backend API
- Deploying Django applications

---

## Future Improvements

- User authentication
- JWT authentication
- User-specific todo lists
- Filtering and search
- Pagination
- Due dates
- Categories and priorities
- Automated tests
- Docker support

---

## Author

**Hossein Firouzgan**

GitHub: https://github.com/HosseinFirouzgan

LinkedIn: https://linkedin.com/in/hosseinfirouzgan
