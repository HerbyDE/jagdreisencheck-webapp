release: python manage.py migrate --no-input
release: python manage.py createsu
release: python manage.py cms fix-tree
web: gunicorn jagdreisencheck.wsgi --log-file -
