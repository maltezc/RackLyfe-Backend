from mnb_backend.addresses.states import states
# noinspection PyUnresolvedReferences
from mnb_backend.database import db

from mnb_backend.enums import ListingConditionEnum, RentalDurationEnum, ListingStatusEnum, ReservationStatusEnum, \
    PriceEnums, UserStatusEnums, RackMountTypeEnum, RackActivityTypeEnum
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



# region create dummy users----------------------------------------

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
db.session.commit()
user1.profile_image = user1Image

address1 = Address(street_address="164 Glenwood")
db.session.add(address1)
address1.user = user1

location1 = Location(point='POINT(-122.28195023589687 38.006370860286694)')
db.session.add(location1)
address1.location = location1

city1 = City(
    city_name="Hercules",
)
db.session.add(city1)

address1.city = city1

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
db.session.add_all([user3, user3Image])
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


# region listings---------------------------------------------

listing1 = Listing(
    primary_image_url="https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3&hl"
                      "=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280",
    title="Large Cargo Basket",
    mount_type=RackMountTypeEnum.ROOF,
    activity_type=RackActivityTypeEnum.CARGOBASKET,
    # condition=ListingConditionEnum.FAIR,
    rate_price=2000,
    # rate_schedule=RentalDurationEnum.WEEKLY,
    status=ListingStatusEnum.AVAILABLE,
)
user1.listings.append(listing1)

listingImage1 = ListingImage(
    image_url="https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3&hl"
              "=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280",
)
listing1.images.append(listingImage1)

listing2 = Listing(
    primary_image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/d08b4b4c-a199-4537-8bd7-01dcc60c105d",
    title="Yakima Bicycle Rack",
    mount_type=RackMountTypeEnum.ROOF,
    activity_type=RackActivityTypeEnum.BICYCLE,
    rate_price=1000,
    # rate_schedule=RentalDurationEnum.WEEKLY,
    status=ListingStatusEnum.UNAVAILABLE,
)
user1.listings.append(listing2)

listingImage2 = ListingImage(
    image_url="https://books.google.com/books/content?id=wrOQLV6xB-wC&pg=PP1&img=1&zoom=3&hl=en&bul=1&sig"
              "=ACfU3U0pxFjDUW9HplCcIzSmlQs0B15≥9ow&w=1280",
)
listing2.images.append(listingImage2)

listingImage2a = ListingImage(
    image_url="https://my-neighbors-bookshelf.s3.us-west-1.amazonaws.com/d08b4b4c-a199-4537-8bd7-01dcc60c105d",
)
listing2.images.append(listingImage2a)

db.session.add_all([listing1, listingImage1, listing2, listingImage2, listingImage2a])

listing3 = Listing(
    primary_image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1"
                      "&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
    title="Snowboard rack",
    mount_type=RackMountTypeEnum.ROOF,
    activity_type=RackActivityTypeEnum.SKISSNOWBOARD,
    rate_price=1500,
    # condition=ListingConditionEnum.USED,
    # rate_schedule=RentalDurationEnum.WEEKLY,
    status=ListingStatusEnum.AVAILABLE
)
user2.listings.append(listing3)

listingImage3 = ListingImage(
    image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1"
              "&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
)
listing3.images.append(listingImage3)

db.session.add_all([listing3, listingImage3])

listing4 = Listing(
    primary_image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul"
                      "=1&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
    title="Small Cargo Basket",
    mount_type=RackMountTypeEnum.ROOF,
    activity_type=RackActivityTypeEnum.CARGOBASKET,
    rate_price=1000,
    status=ListingStatusEnum.AVAILABLE
)
listing4.owner = user3

listingImage4 = ListingImage(
    image_url="https://books.google.com/books/publisher/content?id=oDBnAgAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1"
              "&sig=ACfU3U10EpXuljnFioBTtk3Kc_duZ83How&w=1280",
)
listing4.images.append(listingImage4)

db.session.add_all([listing4, listingImage4])

# endregion


# region reservations

start_date1 = datetime(2023, 5, 20, 12, 1)
timedelta1 = timedelta(weeks=5)
total1 = listing1.rate_price * (timedelta1.days / 7)
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
reservation1.listing = listing1

start_date2 = datetime(2023, 5, 25, 12, 1)
timedelta2 = timedelta(weeks=2)
total2 = listing2.rate_price * (timedelta2.days / 7)
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
listing2.reservations.append(reservation2)


start_date3 = datetime(2023, 5, 15, 12, 1)
timedelta3 = timedelta(weeks=3)
total3 = listing3.rate_price * (timedelta3.days / 7)
reservation3 = Reservation(
    reservation_date_created=datetime.utcnow(),
    start_date=start_date3,
    duration=timedelta3,
    end_date=start_date3 + timedelta3,
    status=ReservationStatusEnum.ACCEPTED,
    total=total3,
)

reservation3.renter = user1
listing3.reservations.append(reservation3)

db.session.add_all([reservation1, reservation2, reservation3])
db.session.commit()

# endregion


# region messages

message1 = Message(
    # message_uid=1,
    reservation_uid=reservation1.id,
    sender_uid=user1.id,
    recipient_uid=user2.id,
    message_text="hello",
    # timestamp="Wed, 01 Feb 2023 12:01:00 GMT"
)
db.session.add(message1)

user1.sent_messages.append(message1)
db.session.commit()


message2 = Message(
    # message_uid=2,
    reservation_uid=reservation1.id,
    sender_uid=user2.id,
    recipient_uid=user1.id,
    message_text="hola",
    # timestamp="Thur, 02 Feb 2023 12:01:00 GMT"
)
db.session.add(message2)
user2.sent_messages.append(message2)
db.session.commit()


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
db.session.commit()

# endregion
