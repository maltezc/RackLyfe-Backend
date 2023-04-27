# noinspection PyUnresolvedReferences
from app import db
from models import User, UserImage, Address, City, State, ZipCode, Book, BookImage, Reservation, Message
from geoalchemy2 import Geography, Geometry

db.drop_all()
db.create_all()

# db.Table("User").drop()

# region create dummy users----------------------------------------


# `$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q` <--- equals 'password'
user1 = User(
    email="test1@email.com",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    status="active",
    firstname="firstname1",
    lastname="lastname1",
    address_id=1,
    image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/aiony-haust-3TLl_97HNJo-unsplash.jpg",
)

address1 = Address(
    street_address="164 Glenwood",
    city_uid=1,
    zipcode_uid=1,
    point='POINT(-122.28195023589687, 38.006370860286694)'
)

city1 = City(
    id=1,
    city_name="Hercules",
    state_uid=1,
)

state1 = State(
    id=1,
    state_abbreviation="CA",
    state_name="California",
)

zipcode1 = ZipCode(
    id=1,
    code=94547
)

user2 = User(
    email="test2@email.com",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    status="active",
    firstname="firstname2",
    lastname="lastname2",
    address_id=2,
    image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/ian-dooley-d1UPkiFd04A-unsplash.jpg",

)

address2 = Address(
    address_uid=2,
    street_address="100 Finch Court",
    city_uid=1,
    zipcode_uid=1,
    point='POINT(-122.25801, 37.999126)'
)

user3 = User(
    email="test3@email.com",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    status="active",
    firstname="firstname3",
    lastname="lastname3",
    address_id=3,
    image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/michael-dam-mEZ3PoFGs_k-unsplash.jpg",
)

address3 = Address(
    address_uid=3,
    street_address="655 E Drachman St",
    city_uid=2,
    zipcode_uid=2,
    point='POINT(-110.961431, 32.239627)'

)

city2 = City(
    id=2,
    city_name="Tucson",
    state_uid=2,
)

state2 = State(
    id=2,
    state_abbreviation="AZ",
    state_name="Arizona",
)

zipcode2 = ZipCode(
    id=2,
    code=85705
)

db.session.add_all([user1, address1, city1, state1, zipcode1, user2, address2])
db.session.add_all([user3, address3, city2, state2, zipcode2])

db.session.commit()

# endregion


# region pools---------------------------------------------

book1 = Book(
    owner_uid=1,
    # book_address=1,
    orig_image_url="https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1"
                   "&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280",
    title="The Name of the Wind",
    author="Patrick Rothfuss",
    isbn="9780756405892",
    genre="",
    condition="Like New",
    price="400",
    status="Available"
)

book2 = Book(
    owner_uid=2,
    # book_address=2,
    orig_image_url="https://books.google.com/books/content?id=IwywDY4P6gsC&pg=PP1&img=1&zoom=3&hl=en&bul=1&sig"
                   "=ACfU3U1MW8ShmkaEJSng6powPa2vADQ4Kw&w=1280",
    title="Foundation",
    author="Isaac Asimov",
    isbn="9780553900347",
    genre="",
    condition="Used",
    price="300",
    status="Available"
)

book3 = Book(
    owner_uid=3,
    # book_address=3,
    orig_image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1"
                   "&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
    title="Endurance Shackleton's Incredible Voyage",
    author="Alfred Lansing",
    isbn="9780753809877",
    genre="",
    condition="Fair",
    price="200",
    status="Available"
)

book4 = Book(
    owner_uid=1,
    # book_address=1,
    orig_image_url="https://books.google.com/books/content?id=wrOQLV6xB-wC&pg=PP1&img=1&zoom=3&hl=en&bul=1&sig"
                   "=ACfU3U0pxFjDUW9HplCcIzSmlQs0B159ow&w=1280",
    title="Harry Potter and the Sorcerer's Stone",
    author="J.K. Rowling, Olly Moss ",
    isbn="9781781100486",
    genre="",
    condition="Fair",
    price="900",
    status="Checked Out"
)


# db.session.add_all([book1])
db.session.add_all([book1, book2, book3, book4])
db.session.commit()
# endregion


# region reservations
# reservation1 = Reservation(
#     reservation_uid="1",
#     book_uid="1",
#     owner_uid="1",
#     renter_uid="2",
#     reservation_date_created="Wed, 01 Feb 2023 12:01:00 GMT",
#     start_date="Fri, 03 Feb 2023 12:01:00 GMT",
#     end_date="Sun, 05 Feb 2023 12:01:00 GMT",
#     status="Scheduled",
#     rental_period_duration=10,
#     total="1000",
# )
#
# reservation2 = Reservation(
#     reservation_uid="2",
#     book_uid="2",
#     owner_uid="2",
#     renter_uid="1",
#     reservation_date_created="Wed, 01 Feb 2023 12:01:00 GMT",
#     start_date="Fri, 03 Feb 2023 12:01:00 GMT",
#     end_date="Sun, 05 Feb 2023 12:01:00 GMT",
#     status="Scheduled",
#     rental_period_duration=10,
#     total="800",
# )
#
# reservation3 = Reservation(
#
#     reservation_uid="3",
#     book_uid="3",
#     owner_uid="3",
#     renter_uid="1",
#     reservation_date_created="Wed, 01 Feb 2023 12:01:00 GMT",
#     start_date="Fri, 03 Feb 2023 12:01:00 GMT",
#     end_date="Sun, 05 Feb 2023 12:01:00 GMT",
#     status="Scheduled",
#     rental_period_duration=10,
#     total="600",
# )
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
