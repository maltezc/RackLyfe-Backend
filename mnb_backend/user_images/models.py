"""Models for UserImage"""
from mnb_backend.database import db


# region userimage
class UserImage(db.Model):
    """ Connection from the user to their profile images. """

    __tablename__ = "user_images"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )
    user = db.relationship('User', back_populates="profile_image", uselist=False)

    image_url = db.Column(
        db.Text,
        nullable=False
    )

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "image_url": self.image_url,
            "user_id": self.user_id
        }

    def __repr__(self):
        return f"< UserImage #{self.id}, Image URL: {self.image_url} >"

# endregion
