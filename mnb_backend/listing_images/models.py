"""Listing Images Model"""
from mnb_backend.database import db


# region listing image

class ListingImage(db.Model):
    """ One-to-many table connecting a listing to many image paths """

    __tablename__ = "listing_images"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    listing_id = db.Column(
        db.Integer,
        db.ForeignKey("listings.id", ondelete="CASCADE"),
    )
    listing = db.relationship('Listing', back_populates='images', uselist=False)

    image_url = db.Column(
        db.Text,
        nullable=False
    )

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "listing_id": self.listing_id,
            "image_url": self.image_url,
        }

    def __repr__(self):
        return f"< Listing Image #{self.id}, ImageUrl: {self.image_url} >"


# endregion