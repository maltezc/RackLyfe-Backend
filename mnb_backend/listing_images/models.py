"""Listing Images Model"""
from database import db


# region book image

class BookImage(db.Model):
    """ One-to-many table connecting a book to many image paths """

    __tablename__ = "book_images"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id", ondelete="CASCADE"),
    )
    book = db.relationship('Book', back_populates='images', uselist=False)

    image_url = db.Column(
        db.Text,
        nullable=False
    )

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "book_id": self.book_id,
            "image_url": self.image_url,
        }

    def __repr__(self):
        return f"< BookImage #{self.id}, ImageUrl: {self.image_url} >"


# endregion