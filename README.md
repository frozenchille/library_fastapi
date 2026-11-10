Library Management System (FastAPI + PostgreSQL + Docker)

A fully functional REST API backend for library management with an integrated client interface. The project is fully containerized and uses a modern technology stack to ensure security, role-based access control, and fast database operations.

🛠 Technology Stack

Backend: Python, FastAPI, SQLAlchemy (ORM), Pydantic

Database: PostgreSQL 15, psycopg driver

Authentication: JWT (JSON Web Tokens), OAuth2PasswordBearer, Passlib (password hashing)

Frontend: Vanilla JavaScript, HTML5, CSS (Bootstrap 5)

DevOps / Infrastructure: Docker, Docker Compose

✨ Key Features

Authentication & Security: Secure user registration and issuance of JWT tokens for accessing protected endpoints.

Role-Based Access Control (RBAC): Separation of access rights. Regular users can view, check out, and return books. Administrators have exclusive rights to add, edit, and delete books from the database.

CRUD Operations: Full lifecycle management of books and users.

State Control: Logic to verify book availability (cannot check out an already checked-out book or return one that is currently in the library).

Isolated Environment: The application and database are spun up in a single Docker network with one command, requiring no local environment setup.

Client Interface: A ready-to-use single-page application (SPA) in the library_front folder for visual interaction with the API.

📂 Project Structure

library_fastapi/
├── library_front/         # Client interface (HTML, JS, CSS)
├── auth.py                # Token generation and access rights validation logic
├── database.py            # PostgreSQL connection setup via SQLAlchemy
├── main.py                # FastAPI initialization and routes (endpoints)
├── models.py              # ORM models for database tables
├── schemas.py             # Pydantic schemas for input/output data validation
├── docker-compose.yml     # Multi-container application configuration
├── Dockerfile             # Instructions for building the FastAPI image
└── requirements.txt       # List of Python dependencies


🚀 Running the Project

Prerequisites

To run the project, you must have Docker and Docker Desktop installed on your computer (for Windows/Mac). Local installation of Python or PostgreSQL is not required.

Installation and Startup

Clone the repository:

git clone https://github.com/your-username/library_fastapi.git
cd library_fastapi


Run the containers in the background:

docker compose up -d --build


After the services start successfully, the API will be available at:

Swagger UI (Documentation & Testing): http://localhost:8000/docs

Redoc: http://localhost:8000/redoc

Running the Frontend

The interface does not require a build step. Open the library_front folder in your code editor (e.g., VS Code) and run the index.html file using the Live Server extension. The interface will automatically connect to the backend running in Docker.

📌 Main API Endpoints

Users:

POST /register — Register a new user

POST /token — Get a JWT token (Login)

Books:

GET /books — Get a list of all books

GET /books/{id} — Get information about a specific book

POST /books — Add a new book (Administrator rights required)

PUT /books/{id} — Update book data (Administrator rights required)

DELETE /books/{id} — Delete a book (Administrator rights required)

Interacting with Books (Authentication required):

POST /books/{id}/checkout — Check out a book to read

POST /books/{id}/return — Return a book to the library

🔧 Assigning Administrator Rights

By default, new users are registered as regular readers. To grant administrator rights for testing the full functionality, connect to the PostgreSQL database in the container (port 5433 or 5432 depending on your settings) and execute the following SQL query:

UPDATE users SET is_admin = true WHERE email = 'your_email@example.com';
