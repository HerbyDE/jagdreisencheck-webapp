# Readme for Jagdreisencheck's Alpha Version

## Contents

- Installation Guide
- Functional Sections
- Contributors
- Disclaimer
- Legal Notice


## Installation Guide
This web application purely relies on `Python 3` and `PostgreSQL`. 
For this section we assume that you have already configured your infrastructure (preferably Ubuntu/Rancher, NginX, Postgres, Python3).
Before starting the application run `pip3 install -r requirements.txt`
To get the application running you have to clone the repository to the server and configure the `settings.py` accordingly.

- DEBUG = False
- ALLOWED_HOSTS = ['YOUR IP ADDRESS']
- Cache Engine must be installed (Memcached)

After the initial configuration you have to create migrations and migrate your DB with the scheme.
That's it. Now you can register your Superuser and start off.

## Functional Sections
We have devided the project into the core sub-projects:

- Accounts with emailing and user-role management
- Search Engine optimized to find trips (still in Dev)
- Travel Platform handling the trips and rating 
- Analytics deriving information from user input
In addition this project will support:
- Containerization with Docker
- Continuous Integration with Travis 
- CD Pipeline as soon as there is need for it

## Contributors

- Herbert Woisetschläger (herbert.woisetschlaeger@jagdreisencheck.de, Technical Lead)

## Disclaimer
This project is in alpha state and only meant for demonstrative purposes. It shall not be distributed and 
especially the accounts application may not be shared with unauthorized individuals. 

## Legal Notice
The Jagdreisencheck Alpha version is distributed under the MIT License just as Django and Python 3. Further Details will follow. 
Distribution and unauthorized use is prohibited.

