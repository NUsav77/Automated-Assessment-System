# Prototype of AAS

## Django terminology
The project is called AAS and the application it runs is called automated_assessment_system.


### Django Bootstrap Sequence
+ git clone repository.
+ Open using pycharm.
+ Set a .env file (e.g. copy .tpl.env to .env)
+ Run make migration to build the schema.
```
python manage.py makemigrations
```
+ Run migrate to apply it to the sqlite3 server
```
python manage.py migrate
```
+ Create user groups (Work in progress, no users are assigned)
```
python manage.py bootstrap_groups
```
+ Create a test user to log in
```
python manage.py create_test_users
```
+ Run development server and browse to http://127.0.0.1:8000/admin/ (login:super@example.com pass:pass)
```
python manage.py runserver
```

### Cypress (e2e framework) Bootstrap
+ Install nodejs
+ Install npm
+ Install cypress
+ Follow Django bootstrap
+ Run cypress

[Walk through](https://www.linkedin.com/learning/end-to-end-javascript-testing-with-cypress-io/installing-and-opening-cypress)

[Example project](https://github.com/ccnmtl/mediathread/tree/master/cypress)
#### Cypress TODO
Right now we run migrations and use a live backend instead of using django fixtures and running of a testserver.

##### Write tests
[See for example which needs fixing](./cypress/integration/Logon/login_spec.js)

###  Service mocking
[x] - Database postgres
```bash
$ docker run --rm \ # Once you control+c out the instance will remove itself.
             -it \  # iteractive shell (for tailing logs
             --name dj-db \ # Gives a unique name to the conatiner running
             -p 5432:5432 \  # from .env file (tells what port for postres to listen on 
             -e POSTGRES_PASSWORD=password \ # from .env file
             -e POSTGRES_USER=db_user \ # from .env file
             -e POSTGRES_DB=db_name \ # from .env file
             postgres # Docker image name
```

[x] - Mock outbound email service (tests password reset workflow)

```bash
docker run --rm -it --name dj-mail # name of container created.
                     -p 8025:8025  # http://127.0.0.1:8025 web ui to see mail sent
                     -p 1025:1025  # smtp://127.0.0.1:1025 .env file of where you can configure email.
                     mailhog/mailhog # Docker image name
```