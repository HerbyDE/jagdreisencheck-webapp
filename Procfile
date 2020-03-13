release: python manage.py migrate --no-input
release: python manage.py createsu
web: gunicorn jagdreisencheck.wsgi --log-file -
