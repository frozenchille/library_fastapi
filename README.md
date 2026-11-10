# 📚 Library Management System

> A fully functional REST API backend for library management with an integrated client interface. The project is fully containerized and uses a modern technology stack to ensure security, role-based access control, and fast database operations.

---

## 🛠 Technology Stack

* **Backend:** Python, FastAPI, SQLAlchemy (ORM), Pydantic
* **Database:** PostgreSQL 15, `psycopg` driver
* **Authentication:** JWT (JSON Web Tokens), OAuth2PasswordBearer, pwdlib (Argon2 password hashing)
* **Frontend:** Vanilla JavaScript, HTML5, CSS — no framework, no build step
* **DevOps & Infrastructure:** Docker, Docker Compose, Nginx

---

## ✨ Key Features

* **Authentication & Security:** Secure user registration and issuance of JWT tokens for accessing protected endpoints.
* **Role-Based Access Control (RBAC):** Separation of access rights. Regular users can view, check out, and return books. Administrators have exclusive rights to add, edit, and delete books from the database.
* **CRUD Operations:** Full lifecycle management of books and users.
* **State Control:** Logic to verify book availability (prevents checking out already issued books).
* **Multi-Container Architecture:** Three isolated services — PostgreSQL, the FastAPI backend, and an Nginx container serving the static frontend — all started together with a single command.

---

## 📂 Project Structure

```text
library_fastapi/
├── library_front/         # Client-side interface (HTML, JS, CSS, Dockerfile)
├── auth.py                # Token generation & permission dependencies
├── database.py            # PostgreSQL connection via SQLAlchemy
├── main.py                # FastAPI initialization and endpoints
├── models.py              # SQLAlchemy database models
├── schemas.py              # Pydantic validation schemas
├── docker-compose.yml     # Multi-container orchestration config
├── Dockerfile              # FastAPI image configuration
└── requirements.txt        # Python dependencies list
```

---

# 🚀 Running the Project

## Prerequisites

* Docker and Docker Desktop (Windows/Mac). No local installation of Python or PostgreSQL is required — everything runs inside containers.

## Installation and Startup

Clone the repository:

```git clone https://github.com/your-username/library_fastapi.git```

```cd library_fastapi```


Start all three services (database, backend, frontend) in one command:

```docker compose up -d --build```

Once the containers are running:

* **Frontend (web interface):** http://localhost:3000
* **Swagger UI (API docs & testing):** http://localhost:8000/docs
* **Redoc:** http://localhost:8000/redoc

The frontend talks directly to the backend at `http://localhost:8000` — no separate setup, server, or build tool is needed. It is served by its own Nginx container as soon as `docker compose up` finishes.

### Developing the frontend without Docker

If you're actively editing `library_front/` and want faster reloads than rebuilding the container each time, you can serve it directly while the backend still runs separately (via Docker or `uvicorn`):

```cd library_front```

```python -m http.server 3000```


---

# 📌 Main API Endpoints

**Users:**
* `POST /register` — Register a new user
* `POST /token` — Get a JWT token (Login)
* `GET /me` — Get the currently authenticated user (requires token)

**Books:**
* `GET /books` — Get a list of all books
* `GET /books/{id}` — Get information about a specific book
* `POST /books` — Add a new book (Administrator rights required)
* `PUT /books/{id}` — Update book data (Administrator rights required)
* `DELETE /books/{id}` — Delete a book (Administrator rights required)

**Interacting with Books (Authentication required):**
* `POST /books/{id}/checkout` — Check out a book to read
* `POST /books/{id}/return` — Return a book to the library

---

## 🔧 Assigning Administrator Rights

By default, new users are registered as regular readers. To grant administrator rights for testing the full functionality, run the following against the database **inside the running container** — no local PostgreSQL client needed:

```docker exec -it library_fastapi-db-1 psql -U myuser -d library_db -c “UPDATE users SET is_admin = true WHERE email = ‘your_email@example.com’;”```

(Replace `library_fastapi-db-1` with your actual container name if different — check it with `docker ps`.)

If you prefer a GUI, connect with pgAdmin to `localhost:5433` (the port mapped in `docker-compose.yml`) using the credentials set in the `db` service's environment variables.
