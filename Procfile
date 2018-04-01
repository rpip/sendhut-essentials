# release: python manage.py migrate --no-input
web: newrelic-admin run-program gunicorn -b "0.0.0.0:$PORT" -w 3 sendhut.wsgi
worker: python manage.py rqworker high default low
