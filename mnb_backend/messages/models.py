"""Models for Messages"""
from datetime import datetime

from mnb_backend.database import db


# region Messages

class Message(db.Model):
    """Messages between users in the system"""

    __tablename__ = "messages"

    message_uid = db.Column(
        db.Integer,
        primary_key=True
    )

    reservation_uid = db.Column(
        db.Integer,
        nullable=False,
    )

    sender_uid = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    sender = db.relationship('User', back_populates='sent_messages', foreign_keys=[sender_uid], uselist=False)

    recipient_uid = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    recipient = db.relationship('User', back_populates='received_messages', foreign_keys=[recipient_uid], uselist=False)

    message_text = db.Column(
        db.Text,
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    # todo: add repr

    def __repr__(self):
        return f"< Message #{self.message_uid}, " \
               f"Reservation: {self.reservation_uid}, " \
               f"Sender_Id: {self.sender_uid}, " \
               f"Recipient_id: {self.recipient_uid}, " \
               f"Message: {self.message_text}, " \
               f"Timestamp: {self.timestamp} >"

    def serialize(self, sender_name, recipient_name):
        """ returns self """
        return {

            "message_uid": self.message_uid,
            "reservation_uid": self.reservation_uid,
            "sender_uid": self.sender_uid,
            "sender_name": sender_name,
            "recipient_uid": self.recipient_uid,
            "recipient_name": recipient_name,
            "message_text": self.message_text,
            "timestamp": self.timestamp,
        }

# endregion