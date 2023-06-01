"""Routes for user images blueprint."""
from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from collections import defaultdict

from mnb_backend.listings.models import Listing
from mnb_backend.messages.models import (db, Message)


messages_routes = Blueprint('messages_routes', __name__)


# region MESSAGES ENDPOINTS START

@messages_routes.post("/api/messages")
@jwt_required()
def create_message():
    """ Creates a message to be sent to listing owner.

    Returns JSON like:
        {message: {message_uid, reservation_uid, sender_uid, recipient_uid, text, timestamp}}
    """

    current_user_id = get_jwt_identity()

    data = request.json
    listing_id = data.get('listing_id')
    recipient_uid = data.get('recipient_uid')
    message_text = data.get('message_text')

    try:
        message = Message(
            reservation_uid=listing_id,
            sender_uid=current_user_id,
            recipient_uid=recipient_uid,
            message_text=message_text,
        )

        db.session.add(message)
        db.session.commit()

        return jsonify(message=message.serialize(f"{message.sender.firstname} {message.sender.lastname}",
                                                 f"{message.recipient.firstname} {message.recipient.lastname}")), 201
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "not authorized"}), 401


@messages_routes.get("/api/messages/all")
@jwt_required()
def show_all_messages():
    """Gets all messages, organizing them into conversations
    Returns JSON like:
        {conversations: {recipient_uid: [message, message, ...], ...}}"""

    current_user_id = get_jwt_identity()

    # Query all messages involving the current user
    messages = (Message.query
                .filter((Message.sender_uid == current_user_id) | (Message.recipient_uid == current_user_id))
                .order_by(Message.timestamp.desc()))

    # Group messages into conversations based on sender and recipient
    conversations = defaultdict(list)
    for message in messages:
        # Determine the conversation participant
        participant_id = message.recipient_uid if message.sender_uid == current_user_id else message.sender_uid
        conversations[participant_id].append(message.serialize(f"{message.sender.firstname} {message.sender.lastname}",
                                                               f"{message.recipient.firstname} {message.recipient.lastname}"))

    conversations = dict(conversations)

    return jsonify(conversations=conversations), 200


@messages_routes.get("/api/messages/listing/<int:listing_id>")
@jwt_required()
def show_conversation(listing_id):
    """Gets the conversation between the current user and the listing owner"""

    current_user_id = get_jwt_identity()
    listing = Listing.query.get_or_404(listing_id)
    listing_owner = listing.owner

    # Query messages between the current user and the listing owner
    listing_messages = Message.query.filter(Message.reservation_uid == listing_id)

    # check for message sender is listing owner or current user
    users_messages = (listing_messages
                      .filter(((Message.sender_uid == current_user_id) & (Message.recipient_uid == listing_owner.id)) |
                              ((Message.sender_uid == listing_owner.id) & (Message.recipient_uid == current_user_id)))
                      .order_by(Message.timestamp.asc())).all()

    conversation = [message.serialize(f"{message.sender.firstname} {message.sender.lastname}",
                                      f"{message.recipient.firstname} {message.recipient.lastname}") for message in
                    users_messages]

    return jsonify(conversation=conversation), 200


@messages_routes.get("/api/messages/single/<int:message_id>")
@jwt_required()
# @is_message_sender_reciever_or_admin
def show_message(message_id):
    """ Show specific message

    Returns JSON like:
        {message: {message_uid, reservation_uid, sender_uid, recipient_uid, text, timestamp}}
    """

    message = Message.query.get_or_404(message_id)
    sender_name = f"{message.sender.firstname} {message.sender.lastname}"
    recipient_name = f"{message.recipient.firstname} {message.recipient.lastname}"

    message = message.serialize(f"{sender_name}", f"{recipient_name}")
    return jsonify(message=message), 200

# endregion
