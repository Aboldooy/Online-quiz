# Django starter

Starter project with a custom user model, role-based access (`user` and `admin`), registration, login/logout, and a Bootstrap base template.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Create the database: `python manage.py migrate`
4. Start the server: `python manage.py runserver`

Open `http://127.0.0.1:8000/`.

## Roles

- `user` is assigned to newly registered accounts.
- `admin` can be assigned in Django Admin. Create an administrator with `python manage.py createsuperuser` and open `/admin/`.

