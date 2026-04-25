python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py runserver