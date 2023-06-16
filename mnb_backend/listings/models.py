"""Models for listings"""
from flask import jsonify

from mnb_backend.api_helpers import aws_upload_image
from mnb_backend.database import db
from mnb_backend.enums import enum_serializer, PriceEnums, RentalDurationEnum, ListingStatusEnum, RackMountTypeEnum, \
    RackActivityTypeEnum
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

    activity_type = db.Column(
        SQLAlchemyEnum(RackActivityTypeEnum, name='rack_activity_type_enum'),
        nullable=False
    )

    rack_type = db.Column(
        SQLAlchemyEnum(RackMountTypeEnum, name='rack_type_enum'),
        nullabe=False
    )

    rate_price = db.Column(
        db.Integer,
        nullable=False
    )


    # Standardize to per Day only
    # rate_schedule = db.Column(
    #     SQLAlchemyEnum(RentalDurationEnum, name='rental_duration_enum'),
    # )

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
            "activity_type": self.activity_type,
            "rack_type": self.rack_type,
            "rate_price": self.rate_price,
            "status": enum_serializer(self.status),
            "reservations": [reservation.serialize() for reservation in self.reservations]
        }

    @classmethod
    def create_listing(cls, owner, title, activity_type, rack_mount_type, rate_price, status,
                       primary_image_url=None, images=None):
        """
        Creates a listing object and adds it to the database."""

        try:
            listing = Listing(
                owner=owner,
                title=title,
                activity_typ=activity_type,
                rack_typ=rack_mount_type,
                rate_price=rate_price,
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

    # TODO: listing must have in order to be shown but

    def __repr__(self):
        return f"< Listing #{self.id}, " \
               f"Title: {self.title}, ActivityType: {self.activity_type}, RackMountType: {self.rack_mount_type} " \
               f"Price: {self.rate_price}, Schedule: {self.rate_schedule}, Status: {self.status} >"

# endregion
