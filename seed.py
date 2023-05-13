# noinspection PyUnresolvedReferences
from app import db
from models import User, UserImage, Address, Location, City, State, ZipCode, Book, BookImage, Reservation, Message
from geoalchemy2 import Geography, Geometry
from enums import ConditionEnum, StatesEnum

db.drop_all()
db.create_all()

# db.Table("User").drop()

# region create dummy users----------------------------------------


states = [
    {'name': 'Alabama', 'abbreviation': 'AL'},
    {'name': 'Alaska', 'abbreviation': 'AK'},
    {'name': 'Arizona', 'abbreviation': 'AZ'},
    {'name': 'Arkansas', 'abbreviation': 'AR'},
    {'name': 'California', 'abbreviation': 'CA'},
    {'name': 'Colorado', 'abbreviation': 'CO'},
    {'name': 'Connecticut', 'abbreviation': 'CT'},
    {'name': 'Delaware', 'abbreviation': 'DE'},
    {'name': 'Florida', 'abbreviation': 'FL'},
    {'name': 'Georgia', 'abbreviation': 'GA'},
    {'name': 'Hawaii', 'abbreviation': 'HI'},
    {'name': 'Idaho', 'abbreviation': 'ID'},
    {'name': 'Illinois', 'abbreviation': 'IL'},
    {'name': 'Indiana', 'abbreviation': 'IN'},
    {'name': 'Iowa', 'abbreviation': 'IA'},
    {'name': 'Kansas', 'abbreviation': 'KS'},
    {'name': 'Kentucky', 'abbreviation': 'KY'},
    {'name': 'Louisiana', 'abbreviation': 'LA'},
    {'name': 'Maine', 'abbreviation': 'ME'},
    {'name': 'Maryland', 'abbreviation': 'MD'},
    {'name': 'Massachusetts', 'abbreviation': 'MA'},
    {'name': 'Michigan', 'abbreviation': 'MI'},
    {'name': 'Minnesota', 'abbreviation': 'MN'},
    {'name': 'Mississippi', 'abbreviation': 'MS'},
    {'name': 'Missouri', 'abbreviation': 'MO'},
    {'name': 'Montana', 'abbreviation': 'MT'},
    {'name': 'Nebraska', 'abbreviation': 'NE'},
    {'name': 'Nevada', 'abbreviation': 'NV'},
    {'name': 'New Hampshire', 'abbreviation': 'NH'},
    {'name': 'New Jersey', 'abbreviation': 'NJ'},
    {'name': 'New Mexico', 'abbreviation': 'NM'},
    {'name': 'New York', 'abbreviation': 'NY'},
    {'name': 'North Carolina', 'abbreviation': 'NC'},
    {'name': 'North Dakota', 'abbreviation': 'ND'},
    {'name': 'Ohio', 'abbreviation': 'OH'},
    {'name': 'Oklahoma', 'abbreviation': 'OK'},
    {'name': 'Oregon', 'abbreviation': 'OR'},
    {'name': 'Pennsylvania', 'abbreviation': 'PA'},
    {'name': 'Rhode Island', 'abbreviation': 'RI'},
    {'name': 'South Carolina', 'abbreviation': 'SC'},
    {'name': 'South Dakota', 'abbreviation': 'SD'},
    {'name': 'Tennessee', 'abbreviation': 'TN'},
    {'name': 'Texas', 'abbreviation': 'TX'},
    {'name': 'Utah', 'abbreviation': 'UT'},
    {'name': 'Vermont', 'abbreviation': 'VT'},
    {'name': 'Virginia', 'abbreviation': 'VA'},
    {'name': 'Washington', 'abbreviation': 'WA'},
    {'name': 'West Virginia', 'abbreviation': 'WV'},
    {'name': 'Wisconsin', 'abbreviation': 'WI'},
    {'name': 'Wyoming', 'abbreviation': 'WY'}
]

# Insert all states into the database
for state_data in states:
    state = State(state_name=state_data['name'], state_abbreviation=state_data['abbreviation'])
    db.session.add(state)

db.session.commit()

# `$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q` <--- equals 'password'
user1 = User(
    email="test1@email.com",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    status="active",
    firstname="firstname1",
    lastname="lastname1",
)

user1Image = UserImage(
    image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/aiony-haust-3TLl_97HNJo-unsplash.jpg"
)
user1.profile_image = user1Image

address1 = Address(street_address="164 Glenwood")
user1.address = address1

location1 = Location(point='POINT(-122.28195023589687 38.006370860286694)')
address1.location = location1

city1 = City(
    city_name="Hercules",
)

address1.city = city1
# state1 = State(state_name="California", state_abbreviation="CA")
# city1.state = state1
# breakpoint()
city1.state = State.query.filter(State.state_abbreviation == "CA").first()

zipcode1 = ZipCode(code=94547)
address1.zipcode = zipcode1

user2 = User(
    email="test2@email.com",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    status="active",
    firstname="firstname2",
    lastname="lastname2",
)
user2Image = UserImage(
    image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/ian-dooley-d1UPkiFd04A-unsplash.jpg"
)
user2.profile_image = user2Image

address2 = Address(street_address="100 Finch Court")
user2.address = address2
address2.city = city1
address2.zipcode = zipcode1
location2 = Location(point='POINT(-122.25801 37.999126)')
address2.location = location2

user3 = User(
    email="test3@email.com",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    status="active",
    firstname="firstname3",
    lastname="lastname3",
)
user3Image = UserImage(
    image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/michael-dam-mEZ3PoFGs_k-unsplash.jpg"
)
user3.profile_image = user3Image

address3 = Address(street_address="655 E Drachman St")
user3.address = address3

location3 = Location(point='POINT(-110.961431 32.239627)')
address3.location = location3

city2 = City(
    city_name="Tucson",
)
address3.city = city2
# state2 = State(state_name="Arizona", state_abbreviation="AZ")
city2.state = State.query.filter(State.state_abbreviation == "AZ").first()
# city2.state = state2

zipcode2 = ZipCode(code=85705)
address3.zipcode = zipcode2

user4 = User(
    email="admin1@gmail.com",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    status="active",
    firstname="admin1",
    lastname="admin_lastname4",
    is_admin=True,
)

# endregion
db.session.add_all([user1, user1Image, address1, location1, city1, zipcode1])
db.session.add_all([user2, user2Image, address2, location2, address3, location3, city2, zipcode2])
db.session.add_all([user3, user3Image, user4])
db.session.commit()


# region books---------------------------------------------

book1 = Book(
    primary_image_url="https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3&hl"
                      "=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280",
    title="The Name of the Wind",
    author="Patrick Rothfuss",
    isbn=9780756405892,
    genre="",
    condition=ConditionEnum.FAIR.value,
    rate_price="400",
    rate_schedule="Weekly",
    status="Available"
)
user1.books.append(book1)

bookImage1 = BookImage(
    image_url="https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3&hl"
              "=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280",
)
book1.images.append(bookImage1)

book4 = Book(
    primary_image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/d08b4b4c-a199-4537-8bd7-01dcc60c105d",
    title="Harry Potter and the Sorcerer's Stone",
    author="J.K. Rowling, Olly Moss ",
    isbn=9781781100486,
    genre="",
    condition=ConditionEnum.LIKE_NEW.value,
    rate_price="100",
    # rate_schedule="Weekly",
    status="Checked Out"
)
user1.books.append(book4)
# book4.owner = user1


bookImage4 = BookImage(
    image_url="https://books.google.com/books/content?id=wrOQLV6xB-wC&pg=PP1&img=1&zoom=3&hl=en&bul=1&sig"
              "=ACfU3U0pxFjDUW9HplCcIzSmlQs0B15≥9ow&w=1280",
)
book4.images.append(bookImage4)

bookImage5 = BookImage(
    image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/d08b4b4c-a199-4537-8bd7-01dcc60c105d",
)
book4.images.append(bookImage5)

# book1.owner = user1
db.session.add_all([book1, bookImage1, book4, bookImage4, bookImage5])
db.session.commit()

# user1.books = [book1, book4]


# db.session.commit()

# user1.books.append(book2)
# breakpoint()
# db.session.commit()

# db.session.add_all([])
# db.session.commit()

book2 = Book(
    # owner_uid=2,
    primary_image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1"
                      "&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
    title="Foundation",
    author="Isaac Asimov",
    isbn=9780553900347,
    genre="",
    condition=ConditionEnum.USED.value,
    rate_price="300",
    rate_schedule="Weekly",
    status="Available"
)
# book2.owner = user2
user2.books.append(book2)

bookImage2 = BookImage(
    image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1"
              "&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
)
# bookImage2.book = book2
book2.images.append(bookImage2)

db.session.add_all([book2, bookImage2])
db.session.commit()

book3 = Book(
    primary_image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul"
                      "=1&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
    title="Endurance Shackleton's Incredible Voyage",
    author="Alfred Lansing",
    isbn=9780753809877,
    genre="",
    condition=ConditionEnum.FAIR.value,
    rate_price="200",
    rate_schedule="Weekly",
    status="Available"
)
# book3.owner = user3
user3.books.append(book3)

bookImage3 = BookImage(
    image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1"
              "&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
)
book3.images.append(bookImage3)

db.session.add_all([book3, bookImage3])
db.session.commit()


# endregion

# TODO: set this up. check for book1.reservations.book
# region reservations
# reservation1 = Reservation(
#     id="1",
#     # book_uid="1",
#     # owner_uid="1",
#     # renter_uid="2",
#     reservation_date_created="Wed, 01 Feb 2023 12:01:00 GMT",
#     start_date="Fri, 03 May 2023 12:01:00 GMT",
#     end_date="Sun, 05 May 2023 12:01:00 GMT",
#     status="Scheduled",
#     rental_period_duration=10,
#     total="1000",
# )
# book1.reservations.append(reservation1)
# # reservation1.book = book1
#
# reservation2 = Reservation(
#     id="2",
#     # book_uid="2",
#     # owner_uid="2",
#     # renter_uid="1",
#     reservation_date_created="Wed, 01 Feb 2023 12:01:00 GMT",
#     start_date="Fri, 03 Feb 2023 12:01:00 GMT",
#     end_date="Sun, 05 Feb 2023 12:01:00 GMT",
#     status="Scheduled",
#     rental_period_duration=10,
#     total="800",
# )
# book2.reservations.append(reservation2)
#
#
# reservation3 = Reservation(
#     id="3",
#     # book_uid="3",
#     # owner_uid="3",
#     # renter_uid="1",
#     reservation_date_created="Wed, 01 Feb 2023 12:01:00 GMT",
#     start_date="Fri, 03 May 2023 12:01:00 GMT",
#     end_date="Sun, 05 May 2023 12:01:00 GMT",
#     status="Scheduled",
#     rental_period_duration=10,
#     total="600",
# )
# book3.reservations.append(reservation3)
#
#
# db.session.add_all([reservation1, reservation2, reservation3])
# db.session.commit()

# endregion


# region messages

# message1 = Message(
#     message_uid=1,
#     reservation_uid=1,
#     sender_uid=1,
#     recipient_uid=2,
#     message_text="hello",
#     timestamp="Wed, 01 Feb 2023 12:01:00 GMT"
# )
#
# message2 = Message(
#     message_uid=2,
#     reservation_uid=1,
#     sender_uid=2,
#     recipient_uid=1,
#     message_text="hola",
#     timestamp="Wed, 02 Feb 2023 12:01:00 GMT"
# )


# message1 = Message(
#     sender_username="test1",
#     recipient_username="test2",
#     title="is your pool available?",
#     body="Hi there, i'd like to see if your pool is available for this weekend?",
#     listing=1,
#     timestamp="Wed, 01 Feb 2023 12:01:00 GMT"
# )

# message2 = Message(
#     sender_username="test2",
#     recipient_username="test1",
#     title="I love your pool!",
#     body="Hi there, my friends and I were wondeirng if your pool is free this weekend?",
#     listing=1,
#     timestamp="Thu, 02 Feb 2023 12:01:00 GMT"
# )

# message3 = Message(
#     sender_username="test1",
#     recipient_username="test2",
#     title="Great! Come through!",
#     body="yes its available! book it and you can come through!",
#     listing=1,
#     timestamp="Thu, 02 Feb 2023 12:11:00 GMT"
# )

# db.session.add_all([message1, message2])
# db.session.commit()

# endregion
