"""Listing Images Model"""
from mnb_backend.database import db
# from mnb_backend import app


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

    @classmethod
    def create_listing_image(cls, listing, image_url):
        """
        Creates an image_listing in the database."""
        try:
            listing_image = ListingImage(
                listing_id=listing.id,
                image_url=image_url
            )

            db.session.add(listing_image)
            db.session.commit()

            return listing_image
        except Exception as error:
            print("Error", error)
            db.session.rollback()
            return "Failed to create listing image."

    def __repr__(self):
        return f"< Listing Image #{self.id}, ImageUrl: {self.image_url}, Listing: {self.listing}>"

# endregion
