"""test setup helpers"""
from mnb_backend.addresses.models import Address, Location, City, State, ZipCode
from mnb_backend.database import db
from mnb_backend.listings.models import Listing
from mnb_backend.users.models import User
from mnb_backend.user_images.models import UserImage
from mnb_backend.listing_images.models import ListingImage
from mnb_backend.reservations.models import Reservation
from mnb_backend.messages.models import Message


def delete_all_tables(self):
    """
    Deletes all tables in testing database for resetting between tests."""

    # This order is important
    Message.query.delete()
    Reservation.query.delete()
    ListingImage.query.delete()
    Listing.query.delete()
    Location.query.delete()
    Address.query.delete()  # This should come before ZipCode
    ZipCode.query.delete()
    State.query.delete()
    City.query.delete()
    UserImage.query.delete()
    User.query.delete()

    db.session.commit()  # Commit after deletion
