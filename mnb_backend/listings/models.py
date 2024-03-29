"""Models for listings"""
from sqlalchemy import Enum as SQLAlchemyEnum
from werkzeug.exceptions import abort

from mnb_backend.database import db
from mnb_backend.enums import enum_serializer, ListingStatusEnum, RackMountTypeEnum, \
    RackActivityTypeEnum
from mnb_backend.listings.helpers import get_mount_type_enum, get_activity_type_enum


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

    mount_type = db.Column(
        SQLAlchemyEnum(RackMountTypeEnum, name='rack_mount_enum'),
        nullable=False
    )

    activity_type = db.Column(
        SQLAlchemyEnum(RackActivityTypeEnum, name='rack_activity_type_enum'),
        nullable=False
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

    record_complete = db.Column(
        db.Boolean,
        default=False,
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
            "mount_type": enum_serializer(self.mount_type),
            "activity_type": enum_serializer(self.activity_type),
            "rate_price": self.rate_price,
            "status": enum_serializer(self.status),
            # "reservations": [reservation.serialize() for reservation in self.reservations]
        }

    @classmethod
    def create_listing(cls, owner, title, activity_type, mount_type, rate_price,
                       primary_image_url=None, images=None):
        """
        Creates a listing object and adds it to the database."""

        try:
            mount_type_enum = get_mount_type_enum(mount_type)

            activity_type_enum = get_activity_type_enum(activity_type)

            listing = Listing(
                owner=owner,
                title=title,
                mount_type=mount_type_enum,
                activity_type=activity_type_enum,
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
            db.session.rollback()
            abort(500, description="Failed to create listing.")

    # TODO: listing must have in order to be shown but

    def __repr__(self):
        return f"< Listing #{self.id}, " \
               f"Title: {self.title}, ActivityType: {self.activity_type}, RackMountType: {self.mount_type} " \
               f"Price: {self.rate_price}, Status: {self.status} >"

# endregion
