This is a cinema backend built with Django Rest Framework using JWT authentication and PostgreSQL database.
## Prerequisites

* Install Docker

## Getting started

* Clone the repository to your machine 
* cd to the project folder and run the docker-compose command:
```
cd /project/folder/with/docker-compose.yml
docker-compose build
docker-compose up
```
Now the app is started.

Apply migration to the database:
```
docker-compose run --rm web python ./manage.py migrate
```
Create admin user to be able to login as admin make API calls with more rights than a normal user: 
```
docker-compose run --rm web python ./manage.py createsuperuser
``` 
## Running the tests
Run command:
```bash
docker-compose run --rm web python manage.py test main.tests
```
You should be able to see passing unittest results
## Play around with API
When docker-compose up, navigate to 
```
http://127.0.0.1:8000/
```
You should see available endpoints. Login using the right upper corner button.
Create normal users with POST requests at
```
http://127.0.0.1:8000/api/accounts/
```
## Implemented
* CRUD for User
* TheaterRooms are created with migration 
* CRUD for Movie
* CRUD for Screening
* unit tests

## TODO
* Ticket reservation
* Ticket purchase
