\# Async Student Management API



A RESTful API built with \*\*FastAPI, SQLAlchemy, PostgreSQL, and Pydantic\*\* for managing student records asynchronously.



\## Features



\* ✅ Create students

\* ✅ Get all students

\* ✅ Get student by ID

\* ✅ Update students

\* ✅ Delete students

\* ✅ Asynchronous database operations

\* ✅ PostgreSQL database integration

\* ✅ Request validation with Pydantic

\* ✅ Repository-Service architecture

\* ✅ Interactive Swagger API documentation



\## Technologies



\* Python

\* FastAPI

\* SQLAlchemy (Async)

\* PostgreSQL

\* asyncpg

\* Pydantic

\* Uvicorn

\* python-dotenv



\## Project Structure



```text

async-student-api/

│

├── repositories/

│   ├── \_\_init\_\_.py

│   └── student\_repository.py

│

├── services/

│   ├── \_\_init\_\_.py

│   └── student\_service.py

│

├── .gitignore

├── config.py

├── database.py

├── main.py

├── models.py

├── schemas.py

├── test\_db.py

├── requirements.txt

└── README.md

```



\## Architecture



```text

Client

&#x20;  ↓

FastAPI API Routes

&#x20;  ↓

Service Layer

&#x20;  ↓

Repository Layer

&#x20;  ↓

SQLAlchemy Async ORM

&#x20;  ↓

PostgreSQL

```



\## Installation



Clone the repository:



```bash

git clone https://github.com/Mahima2005-shetty/async-student-api.git

cd async-student-api

```



Create a virtual environment:



```powershell

python -m venv venv

```



Activate it:



```powershell

venv\\Scripts\\activate

```



Install dependencies:



```powershell

pip install -r requirements.txt

```



\## Environment Configuration



Create a `.env` file:



```env

DATABASE\_URL=your\_database\_url

SECRET\_KEY=your\_secret\_key

ALGORITHM=HS256

ACCESS\_TOKEN\_EXPIRE\_MINUTES=15

REFRESH\_TOKEN\_EXPIRE\_DAYS=7

```



\*\*Do not upload `.env` to GitHub.\*\*



\## Run the API



```powershell

uvicorn main:app --reload

```



API:



```text

http://127.0.0.1:8000

```



\## Swagger Documentation



Open:



```text

http://127.0.0.1:8000/docs

```



Swagger UI can be used to test all CRUD operations.



\## API Endpoints



| Method | Endpoint                 | Description       |

| ------ | ------------------------ | ----------------- |

| GET    | `/`                      | API status        |

| POST   | `/students`              | Create student    |

| GET    | `/students`              | Get all students  |

| GET    | `/students/{student\_id}` | Get student by ID |

| PUT    | `/students/{student\_id}` | Update student    |

| DELETE | `/students/{student\_id}` | Delete student    |



\## CRUD Testing



The API was successfully tested using Swagger UI.



\### POST



```json

{

&#x20; "name": "Test Student",

&#x20; "email": "test@gmail.com",

&#x20; "age": 21

}

```



Response:



```json

{

&#x20; "id": 2,

&#x20; "name": "Test Student",

&#x20; "email": "test@gmail.com",

&#x20; "age": 21

}

```



\### GET



Student records were successfully retrieved using:



```text

GET /students

GET /students/{student\_id}

```



\### PUT



Student information was successfully updated using:



```text

PUT /students/{student\_id}

```



\### DELETE



Student records were successfully deleted using:



```text

DELETE /students/{student\_id}

```



The DELETE operation returned:



```text

204 No Content

```



\## Learning Outcomes



\* FastAPI REST API development

\* Asynchronous Python

\* SQLAlchemy Async ORM

\* PostgreSQL integration

\* Pydantic validation

\* Repository-Service architecture

\* CRUD implementation

\* Swagger API testing

\* Git and GitHub



\## Author



\*\*Mahima M\*\*



GitHub: https://github.com/Mahima2005-shetty



\## Project Status



\*\*Completed — Async Student Management CRUD API successfully implemented and tested.\*\*



