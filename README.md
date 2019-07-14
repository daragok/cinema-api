This is a cinema backend built with Django Rest Framework using JWT authentication.
## Prerequisites

* Install Docker

## Getting started

* Clone the repository on your local machine 
* cd to the project folder and run the docker-compose command:
```
cd /project/folder/with/docker-compose.yml
docker-compose build
docker-compose up
docker-compose run --rm web python ./manage.py migrate
docker-compose run --rm web python ./manage.py createsuperuser
```

## Running the tests
Run command:
```bash
docker-compose run --rm web bash python manage.py test main.tests
```

## Play around with API
When docker-compose up, navigate to 
```
http://127.0.0.1:8000/
```
You should see available endpoints. Login using using the right upper corner button.
## Implemented
* CRUD for User
* TheaterRooms are created with migration 
* CRUD for Movie
* CRUD for Screening
* unit tests

## TODO
* Ticket reservation
* Ticket purchase
