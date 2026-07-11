web: gunicorn -c gunicorn.conf.py backend.wsgi:app
worker: celery -A backend.celery_worker worker --loglevel=info
beat: celery -A backend.celery_worker beat --loglevel=info