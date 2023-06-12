"""Models for listings"""
from flask import jsonify

from mnb_backend.api_helpers import aws_upload_image
from mnb_backend.database import db
from mnb_backend.enums import enum_serializer, PriceEnums, RentalDurationEnum, ListingStatusEnum
from sqlalchemy import Enum as SQLAlchemyEnum

from mnb_backend.listing_images.models import ListingImage


# region Listings
class Listing(db.Model):
    """ Listing in the system """

    __tablename__ = 'listings'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )
    owner = db.relationship("User", back_populates="listings", uselist=False)

    primary_image_url = db.Column(
        db.Text,
        nullable=True
    )

    images = db.Relationship("ListingImage", back_populates="listing", uselist=True)

    title = db.Column(
        db.Text,
        nullable=False
    )

    author = db.Column(
        db.Text,
        nullable=False
    )

    isbn = db.Column(
        db.BigInteger,
        nullable=False
    )

    genre = db.Column(
        db.Text,
    )

    rate_price = db.Column(
        SQLAlchemyEnum(PriceEnums, name='rental_price_enum'),
        nullable=False  # select from $1-$10 / week
    )

    rate_schedule = db.Column(
        SQLAlchemyEnum(RentalDurationEnum, name='rental_duration_enum'),
    )

    status = db.Column(
        SQLAlchemyEnum(ListingStatusEnum, name='listing_status_enum'),
        nullable=False
    )

    reservations = db.relationship('Reservation', back_populates='listing', uselist=True)

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "owner": self.owner.serialize(),
            "primary_image_url": self.primary_image_url,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "genre": self.genre,
            # "condition": enum_serializer(self.condition),
            "rate_price": enum_serializer(self.rate_price),
            "rate_schedule": enum_serializer(self.rate_schedule),
            "status": enum_serializer(self.status),
            "reservations": [reservation.serialize() for reservation in self.reservations]
        }

    @classmethod
    def create_listing(cls, owner, title, author, isbn, genre, rate_price, rate_schedule, status,
                       primary_image_url=None, images=None):
        """
        Creates a listing object and adds it to the database."""

        price_enums_dict = {
            100: PriceEnums.ONE,
            200: PriceEnums.TWO,
            300: PriceEnums.THREE,
            400: PriceEnums.FOUR,
            500: PriceEnums.FIVE,
            600: PriceEnums.SIX,
            700: PriceEnums.SEVEN,
            800: PriceEnums.EIGHT,
            900: PriceEnums.NINE,
            1000: PriceEnums.TEN,
        }

        try:
            listing = Listing(
                owner=owner,
                title=title,
                author=author,
                isbn=isbn,
                genre=genre,
                rate_price=price_enums_dict[rate_price],
                rate_schedule=RentalDurationEnum.WEEKLY,
                status=ListingStatusEnum.AVAILABLE,
                primary_image_url=primary_image_url
            )
            db.session.add(listing)
            db.session.commit()

            owner.listings.append(listing)
            db.session.commit()

            # TODO: bring this to routes
            # if images is not None:
            #     if len(images) > 0:
            #         for i, image in enumerate(images.values()):
            #
            #             # add to aws first
            #             image_url = aws_upload_image(image)
            #
            #             if i == 0:
            #                 listing.primary_image_url += image_url
            #
            #             # post image to database
            #             ListingImage.create_listing_image(listing, image_url)

                    # image_element = db_add_listing_image(current_user_id, listing_posted.id, image_url)
                    # images_posted.append(image_element.serialize())

                    # then set db objects with urls created.

            return listing

        except Exception as error:
            print("Error", error)
            db.session.rollback()
            return jsonify(error="Failed to create listing.")

    # TODO: USE LISTING_MUST_HAVE_IMAGE IN ORDER TO CREATE LIST

    def __repr__(self):
        return f"< Listing #{self.id}, " \
               f"Title: {self.title}, Author: {self.author}, ISBN: {self.isbn}, Genre: {self.genre}, " \
               f"Price: {self.rate_price}, Schedule: {self.rate_schedule}, Status: {self.status} >"

# endregion
