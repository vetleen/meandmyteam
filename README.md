# vetletemplate
My personal Django/bootstrap for Heroku ready-to-go out-of-the-box repo

# Get the repo up and running
- on github make a new repo with vetletemplate as template. Give it the desired name.
- mkvirtualenv desired_name (or workon existing_venv - not reccomended)
- git clone https://github.com/vetleen/newrepo.git (where newrepo is the name of the new repo you just made) or use SSH-key
- sudo apt-get install python-pip python-dev libpq-dev postgresql postgresql-contrib
- pip install psycopg2-binary
- pip install -r requirements.txt (should have python installed)
- python manage.py makemigrations (should give no changes messages)
- python manage.py migrate
- python manage.py collectstatic (so we can run tests)
- set environment variable DJANGO_SECURE_SSL_REDIRECT=False (if it's True, tests don't work). Alternatively, you can update settings.py to set SECURE_SSL_REDIRECT=False, when you are running tests.
- python manage.py test (should not fail)
- python manage.py runserver
- open http://127.0.0.1:8000/ in browser and it should work


#change the vetletemplate name
- change the name everywhere it appears
- grep -nir vetletemplate to find those places
- should be:
-> README (not stricly neccessary)
-> wsgi.py
-> urls.py
-> settings.py
-> asgi.py
-> Procfile
-> manage.py
-> bunch of stuff in __pycache__ (I deleted it, although I don't know if this is required)
- run grep again to double check
- python manage.py test (should not fail)
- python manage.py runserver
-> Error stories: I once managed to rename my URLs import, whiich I wasn't supposed to do, which caused some confusion. But bugs can be fixed.
- open http://127.0.0.1:8000/ in browser and it should work

#get onto heroku
- have heroku installed (> snap install heroku --classic)
- heroku login
- heroku create desiredappname
- update settings.pys ALLOWED_HOST-setting
- add and commit changes to git
- push to heroku (git push heroku master)
- heroku run python manage-py makemigrations (should give no changes message)
- heroku run python manage-py migrate
- heroku open
- try to sign up, log out, log in, change password and change user details.
- heroku run python manage.py createsuperuser
- try /admin/

#have fun creating your next project!
