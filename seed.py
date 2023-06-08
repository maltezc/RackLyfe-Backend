# noinspection PyUnresolvedReferences
from mnb_backend.database import db

from mnb_backend.enums import ListingConditionEnum, RentalDurationEnum, ListingStatusEnum, ReservationStatusEnum, \
    PriceEnums, UserStatusEnums
from datetime import datetime, timedelta

from mnb_backend.addresses.models import State, Address, Location, City, ZipCode
from mnb_backend.listing_images.models import ListingImage
from mnb_backend.listings.models import Listing
from mnb_backend.messages.models import Message
from mnb_backend.reservations.models import Reservation
from mnb_backend.user_images.models import UserImage
from mnb_backend.users.models import User

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

# `$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q` <--- equals 'password'
user1 = User(
    email="test1@email.com",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    status=UserStatusEnums.ACTIVE,
    firstname="firstname1",
    lastname="lastname1",
)

db.session.add(user1)
user1Image = UserImage(
    image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/aiony-haust-3TLl_97HNJo-unsplash.jpg"
)
db.session.add(user1Image)
# db.session.add_all([user1, user1Image])
db.session.commit()
user1.profile_image = user1Image

address1 = Address(street_address="164 Glenwood")
db.session.add(address1)
# user1.address = address1
address1.user = user1

location1 = Location(point='POINT(-122.28195023589687 38.006370860286694)')
db.session.add(location1)
address1.location = location1

city1 = City(
    city_name="Hercules",
)
db.session.add(city1)

address1.city = city1
# city1.addresses.append(address1)

city1.state = State.query.filter(State.state_abbreviation == "CA").first()

zipcode1 = ZipCode(code=94547)
db.session.add(zipcode1)
address1.zipcode = zipcode1


user2 = User(
    email="test2@email.com",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    status=UserStatusEnums.ACTIVE,
    firstname="firstname2",
    lastname="lastname2",
)
user2Image = UserImage(
    image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/ian-dooley-d1UPkiFd04A-unsplash.jpg"
)
db.session.add_all([user2, user2Image])
user2.profile_image = user2Image

address2 = Address(street_address="100 Finch Court")
db.session.add(address2)

user2.address = address2
address2.city = city1
address2.zipcode = zipcode1

location2 = Location(point='POINT(-122.25801 37.999126)')
db.session.add(location2)
address2.location = location2

user3 = User(
    email="test3@email.com",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    status=UserStatusEnums.ACTIVE,
    firstname="firstname3",
    lastname="lastname3",
)
user3Image = UserImage(
    image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/michael-dam-mEZ3PoFGs_k-unsplash.jpg"
)
db.session.add(user3, user3Image)
user3.profile_image = user3Image

address3 = Address(street_address="655 E Drachman St")
db.session.add(address3)
user3.address = address3

location3 = Location(point='POINT(-110.961431 32.239627)')
db.session.add(location3)
address3.location = location3

city2 = City(
    city_name="Tucson",
)
db.session.add(city2)
address3.city = city2

state2 = State.query.filter(State.state_abbreviation == "AZ").first()
city2.state = state2

zipcode2 = ZipCode(code=85705)
db.session.add(zipcode2)
address3.zipcode = zipcode2

user4 = User(
    email="admin1@email.com",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    status=UserStatusEnums.ACTIVE,
    firstname="admin1",
    lastname="admin_lastname4",
    is_admin=True,
)
db.session.add(user4)
db.session.commit()

# endregion


# db.session.add_all([user4])


# region books---------------------------------------------

book1 = Listing(
    primary_image_url="https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3&hl"
                      "=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280",
    title="The Name of the Wind",
    author="Patrick Rothfuss",
    isbn=9780756405892,
    genre="",
    # condition=ListingConditionEnum.FAIR,
    rate_price=PriceEnums.FOUR,
    rate_schedule=RentalDurationEnum.WEEKLY,
    status=ListingStatusEnum.AVAILABLE,
)
user1.listings.append(book1)

bookImage1 = ListingImage(
    image_url="https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3&hl"
              "=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280",
)
book1.images.append(bookImage1)

book2 = Listing(
    primary_image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/d08b4b4c-a199-4537-8bd7-01dcc60c105d",
    title="Harry Potter and the Sorcerer's Stone",
    author="J.K. Rowling, Olly Moss ",
    isbn=9781781100486,
    genre="",
    # condition=ListingConditionEnum.LIKE_NEW,
    rate_price=PriceEnums.ONE,
    rate_schedule=RentalDurationEnum.WEEKLY,
    status=ListingStatusEnum.UNAVAILABLE,
)
user1.listings.append(book2)

bookImage2 = ListingImage(
    image_url="https://books.google.com/books/content?id=wrOQLV6xB-wC&pg=PP1&img=1&zoom=3&hl=en&bul=1&sig"
              "=ACfU3U0pxFjDUW9HplCcIzSmlQs0B15≥9ow&w=1280",
)
book2.images.append(bookImage2)

bookImage2a = ListingImage(
    image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/d08b4b4c-a199-4537-8bd7-01dcc60c105d",
)
book2.images.append(bookImage2a)

db.session.add_all([book1, bookImage1, book2, bookImage2, bookImage2a])

book3 = Listing(
    primary_image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1"
                      "&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
    title="Foundation",
    author="Isaac Asimov",
    isbn=9780553900347,
    genre="",
    # condition=ListingConditionEnum.USED,
    rate_price=PriceEnums.THREE,
    rate_schedule=RentalDurationEnum.WEEKLY,
    status=ListingStatusEnum.AVAILABLE
)
# book2.owner = user2
user2.listings.append(book3)

bookImage3 = ListingImage(
    image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1"
              "&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
)
# bookImage2.book = book2
book3.images.append(bookImage3)

db.session.add_all([book3, bookImage3])

book4 = Listing(
    primary_image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul"
                      "=1&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
    title="Endurance Shackleton's Incredible Voyage",
    author="Alfred Lansing",
    isbn=9780753809877,
    genre="",
    # condition=ListingConditionEnum.FAIR,
    rate_price=PriceEnums.ONE,
    rate_schedule=RentalDurationEnum.WEEKLY,
    status=ListingStatusEnum.AVAILABLE
)
book4.owner = user3
# user3.books.append(book3)

bookImage4 = ListingImage(
    image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1"
              "&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
)
book4.images.append(bookImage4)

db.session.add_all([book4, bookImage4])

# endregion

# TODO: set this up. check for book1.reservations.book
# region reservations

start_date1 = datetime(2023, 5, 20, 12, 1)
timedelta1 = timedelta(weeks=5)
total1 = book1.rate_price.value * (timedelta1.days/7)
reservation1 = Reservation(
    # id="1",
    reservation_date_created=datetime.utcnow(),
    start_date=start_date1,
    duration=timedelta1,
    end_date=start_date1 + timedelta1,
    status=ReservationStatusEnum.ACCEPTED,
    total=total1,
)
reservation1.renter = user2
reservation1.listing = book1

start_date2 = datetime(2023, 5, 25, 12, 1)
timedelta2 = timedelta(weeks=2)
total2 = book2.rate_price.value * (timedelta2.days/7)
reservation2 = Reservation(
    # id="2",
    reservation_date_created=datetime.utcnow(),
    start_date=start_date2,
    duration=timedelta2,
    end_date=start_date2 + timedelta2,
    status=ReservationStatusEnum.ACCEPTED,
    total=total2
)
reservation2.renter = user1
# reservation2.book = book3
book2.reservations.append(reservation2)


start_date3 = datetime(2023, 5, 15, 12, 1)
timedelta3 = timedelta(weeks=3)
total3 = book3.rate_price.value * (timedelta3.days/7)
reservation3 = Reservation(
    reservation_date_created=datetime.utcnow(),
    start_date=start_date3,
    duration=timedelta3,
    end_date=start_date3 + timedelta3,
    status=ReservationStatusEnum.ACCEPTED,
    total=total3,
)
# reservation3.book = book4
reservation3.renter = user1
book3.reservations.append(reservation3)

db.session.add_all([reservation1, reservation2, reservation3])
db.session.commit()

# endregion


# region messages

message1 = Message(
    # message_uid=1,
    reservation_uid=1,
    sender_uid=1,
    recipient_uid=2,
    message_text="hello",
    # timestamp="Wed, 01 Feb 2023 12:01:00 GMT"
)
user1.sent_messages.append(message1)

message2 = Message(
    # message_uid=2,
    reservation_uid=1,
    sender_uid=2,
    recipient_uid=1,
    message_text="hola",
    # timestamp="Wed, 02 Feb 2023 12:01:00 GMT"
)
user2.sent_messages.append(message2)


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

db.session.add_all([message1, message2])
db.session.commit()

# endregion
