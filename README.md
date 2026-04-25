Livo - Setup Guide

This project is built using Django (Python web framework).

Follow the steps below to set up the project from scratch on your local machine.

------------------------------------------------------------

PREREQUISITES

Make sure you have installed:
- Python 3.10+
- pip
- Git

------------------------------------------------------------

PROJECT SETUP FROM SCRATCH

1. Create a project directory

Create a folder anywhere in your system:

Final_Project/

Then open terminal inside that folder.

------------------------------------------------------------

2. Create a virtual environment

Inside Final_Project, run:

python -m venv .venv

------------------------------------------------------------

3. Activate virtual environment

Windows (PowerShell):
.venv\Scripts\activate

Mac/Linux:
source .venv/bin/activate

------------------------------------------------------------

4. Clone the repository

Inside Final_Project folder, run:

git clone https://github.com/fataharul/livo.git

Go into the project folder:

cd livo

------------------------------------------------------------

5. Install dependencies

pip install -r requirements.txt

------------------------------------------------------------

6. Apply database migrations

python manage.py makemigrations
python manage.py migrate

------------------------------------------------------------

7. Run the development server

python manage.py runserver

Open in browser:
http://127.0.0.1:8000/

------------------------------------------------------------