# EpicEvents

EpicEvents is a Django application which delivers a set of secure API endpoints using the Django REST framework & ORM (with a PostgreSQL database) to support CRUD (create, read, update, and delete) operations on the various CRM objects(clients, contracts, events) for the event management and consulting firm.

## Setup

### 1. Set Up PostgreSQL

Download and install postgreSQL from https://www.postgresql.org/download/ by following required steps. Then create database named "epicDB" in posgresql. Change values of username and password for database in settings.py file.

### 2. Clone the Repository

First, clone this repository to your local machine. Then open command prompt from inside the cloned repository.

### 3. Create Virtual Environment

To create virtual environment, install virtualenv package of python and activate it by following command on terminal:

```python
pip install virtualenv
python -m venv <<name_of_env>>
Windows: <<name_of_env>>\Scripts\activate.bat
Powershell: <<name_of_env>>\Scripts\activate
Unix/MacOS: source <<name_of_env>>/bin/acivate
```

### 4. Requirements

To install required python packages, copy requirements.txt file and then run following command on terminal:

```python
pip install requirements.txt
```

### 5. Start Server

On the terminal navigate inside the folder epicevents and enter following command to start the server:

```python
python manage.py runserver
```

### 6. Test all endpoints in Postman

Once server is running, you can test all API endpoints in Postman app.
