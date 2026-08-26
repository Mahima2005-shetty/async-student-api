Async Student Management API



A production-style asynchronous REST API for managing student records using FastAPI, SQLAlchemy, PostgreSQL, and Pydantic.



The project follows a clean Repository–Service architecture to separate database operations, business logic, and API routes.



🚀 Features



\* Create student records

\* Retrieve all students

\* Retrieve a student by ID

\* Update student information

\* Delete student records

\* Asynchronous database operations

\* PostgreSQL database integration

\* Pydantic request and response validation

\* Repository–Service architecture

\* Automatic API documentation with Swagger UI

\* Environment-based configuration

\* Proper HTTP status codes and error handling



🛠️ Technologies Used



| Technology    | Purpose                       |

| ------------- | ----------------------------- |

| Python        | Programming language          |

| FastAPI       | REST API framework            |

| SQLAlchemy    | Async ORM                     |

| PostgreSQL    | Relational database           |

| asyncpg       | PostgreSQL async driver       |

| Pydantic      | Data validation               |

| Uvicorn       | ASGI server                   |

| python-dotenv | Environment configuration     |

| Swagger UI    | API testing and documentation |



📁 Project Structure



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



🏗️ Architecture



The application follows a layered architecture:



```text

Client

&#x20; ↓

FastAPI Routes

&#x20; ↓

Service Layer

&#x20; ↓

Repository Layer

&#x20; ↓

SQLAlchemy Async ORM

&#x20; ↓

PostgreSQL Database

```



\### Repository Layer



Handles database operations such as:



\* Creating students

\* Fetching students

\* Updating students

\* Deleting students



Service Layer



Contains the application/business logic and communicates with the repository layer.



API Layer



FastAPI routes receive HTTP requests, validate data, call the service layer, and return responses.



⚙️ Installation



&#x20;1. Clone the repository



```bash

git clone https://github.com/Mahima2005-shetty/async-student-api.git

cd async-student-api

```



2\. Create a virtual environment



Windows:



```powershell

python -m venv venv

```



3\. Activate the virtual environment



```powershell

venv\\Scripts\\activate

```



4\. Install dependencies



```powershell

pip install -r requirements.txt

```



🗄️ Database Configuration



This project uses PostgreSQL.



Create a `.env` file in the project directory:



```env

DATABASE\_URL=your\_database\_url

SECRET\_KEY=your\_secret\_key

ALGORITHM=HS256

ACCESS\_TOKEN\_EXPIRE\_MINUTES=15

REFRESH\_TOKEN\_EXPIRE\_DAYS=7

```



> Never commit `.env` files or database passwords to GitHub.



&#x20;▶️ Run the Application



Start the FastAPI development server:



```powershell

uvicorn main:app --reload

```



The API will be available at:



```text

http://127.0.0.1:8000

```



📚 API Documentation



FastAPI automatically provides interactive Swagger documentation.



Open:



```text

http://127.0.0.1:8000/docs

```



Alternative ReDoc documentation:



```text

http://127.0.0.1:8000/redoc

```



🔗 API Endpoints



| Method | Endpoint                 | Description       |

| ------ | ------------------------ | ----------------- |

| GET    | `/`                      | Check API status  |

| POST   | `/students`              | Create a student  |

| GET    | `/students`              | Get all students  |

| GET    | `/students/{student\_id}` | Get student by ID |

| PUT    | `/students/{student\_id}` | Update a student  |

| DELETE | `/students/{student\_id}` | Delete a student  |



🧪 CRUD Testing



The following CRUD operations were tested successfully using Swagger UI:



\### Create



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



Read



Student records were successfully retrieved using:



```text

GET /students

GET /students/{student\_id}

```



Update



Student information was successfully modified using:



```text

PUT /students/{student\_id}

```



Delete



Student records were successfully deleted using:



```text

DELETE /students/{student\_id}

```



The DELETE operation returned:



```text

204 No Content

```



A subsequent GET request confirmed that the deleted student was no longer available.



🔒 Security



Sensitive configuration is stored in environment variables.



The following files are excluded from Git:



```text

.env

students.db

venv/

\_\_pycache\_\_/

```



🎯 Learning Outcomes



Through this project, the following concepts were implemented:



\* Asynchronous Python programming

\* REST API development

\* FastAPI routing and dependency injection

\* Pydantic validation

\* SQLAlchemy ORM

\* PostgreSQL database connectivity

\* Repository pattern

\* Service layer architecture

\* CRUD operations

\* API testing using Swagger UI

\* Git and GitHub version control



👩‍💻 Author



Mahima M



GitHub:

https://github.com/Mahima2005-shetty



📌 Project Status



Completed — Async CRUD REST API successfully implemented and tested.



