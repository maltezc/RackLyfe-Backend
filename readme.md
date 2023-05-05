# Pool Party BnB - Backend

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

### TODOs / Aspirations

### Deployed link

### Proud Code Snippet and How You Solved It



### Project Structure
├── ShareBnB-Backend
│   ├── api_helpers.py
│   ├── app.py
│   ├── models.py
│   ├── readme.md
│   ├── requirements.txt
│   └── seed.py

<br/>


### Useful links: 
#### GeoAlchemy
- [GeoAlchemy Docs](https://geoalchemy-2.readthedocs.io/en/latest/orm_tutorial.html) 

#### PostGIS 
- [adding postGIS extension to sql](https://stackoverflow.com/questions/6850500/postgis-installation-type-geometry-does-not-exist)
- had to install PostGIS via homebrew

#### How to use Google Books api 
- [walk through](https://rachelaemmer.medium.com/how-to-use-the-google-books-api-in-your-application-17a0ed7fa857)
