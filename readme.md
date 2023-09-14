# RackLyfe - Backend

### How to start the program
1) Fork  or Clone the project to your machine
2) Navigate to the projects directory
3) in your terminal run `pip3 isntall -r requirements.txt`
4) Set up aws account for AWS S3
5) Set the environment variables: `cp .env.example .env`
6) open .env and modify the environment variables
Environment Variables
The environment variables can be found and modified in the .env file.

#### Secret Key
SECRET_KEY=your_secret_key_123
DATABASE_URL=postgresql:///your_app_name
aws_access_key_id=your_aws_access_key1234
aws_secret_access_key=your_aws_secret_key


7) in your terminal run `flask run -p 5001`

### How to run tests
##### through terminal
FLASK_ENV=test python3 -m unittest discover
NOTE: must sent environment variable to test for db.engine to use mnb_test database. Otherwise will use mnb database

#### through pycharm
1) set environment variable first. 
    FLASK_DEBUG=test
2) Set this my going to Run > Edit Configurations > Edit Configuration templates... 
3) a new dialog window will open. click Python Tests > pytest
4) Set the environment variable in the Environment Variables section here.
5) click apply and ok
6) environment variable should be set and you can run tests through pycharm without having to add an env variable individually to each test file



### TODOs / Aspirations
- See github project

### Deployed link
- coming soon.

### Proud Code Snippet and How You Solved It
- coming soon


### Project Modules
├── RackLyfe-Backend
│   ├── addresses
│   ├── auth
│   ├── listing_images
│   ├── listings
│   ├── messages
│   ├── reservations
│   ├── searches
│   ├── user_images
│   └──  users


<br/>


### Useful links: 
#### GeoAlchemy
- [GeoAlchemy Docs](https://geoalchemy-2.readthedocs.io/en/latest/orm_tutorial.html) 

#### PostGIS 
- [adding postGIS extension to sql](https://stackoverflow.com/questions/6850500/postgis-installation-type-geometry-does-not-exist)
- had to install PostGIS via homebrew

#### How to use Google Books api 
- [walk through](https://rachelaemmer.medium.com/how-to-use-the-google-books-api-in-your-application-17a0ed7fa857)

### Running tests 
To run the tests, use the pytest command. It will find and run all the test functions you’ve written.

`$ pytest`
```
========================= test session starts ==========================
platform linux -- Python 3.6.4, pytest-3.5.0, py-1.5.3, pluggy-0.6.0
rootdir: /home/user/Projects/flask-tutorial
collected 23 items

tests/test_auth.py ........                                      [ 34%]
tests/test_blog.py ............                                  [ 86%]
tests/test_db.py ..                                              [ 95%]
tests/test_factory.py ..                                         [100%]

====================== 24 passed in 0.64 seconds =======================
```

If any tests fail, pytest will show the error that was raised. You can run `pytest -v` to get a list of each test function rather than dots.

To measure the code coverage of your tests, use the coverage command to run pytest instead of running it directly.

Run full test suite with test db: 
`$ FLASK_DEBUG=test pytest -v --cov=mnb_backend --cov-report term-missing`

`$ coverage run -m pytest`
You can either view a simple coverage report in the terminal:

`$ coverage report`

Name                 Stmts   Miss Branch BrPart  Cover
------------------------------------------------------
flaskr/__init__.py      21      0      2      0   100%
flaskr/auth.py          54      0     22      0   100%
flaskr/blog.py          54      0     16      0   100%
flaskr/db.py            24      0      4      0   100%
------------------------------------------------------
TOTAL                  153      0     44      0   100%
An HTML report allows you to see which lines were covered in each file:

$ coverage html
This generates files in the htmlcov directory. Open htmlcov/index.html in your browser to see the report.
