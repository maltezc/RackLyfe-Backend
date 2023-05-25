"""Routes for listing images blueprint."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db

from api_helpers import upload_to_aws
from mnb_backend.listing_images.models import BookImage
from mnb_backend.listings.models import Book

listing_images_routes = Blueprint('listing_images_routes', __name__)


@listing_images_routes.post("/api/books/<int:book_uid>/images")
@jwt_required()
def add_book_image(book_uid):
    """Add book image, and return data about book image.

    Returns JSON like:
        {book_image: {id, book_owner, image_url }}
    """
    # TODO: if we get an array of files, then we could do a list comprehension where
    # we use the helper function and add that to the table for each one in the comprehension

    current_user = get_jwt_identity()
    book = Book.query.get_or_404(book_uid)
    if current_user == book.owner_username:
        file = request.files['file']
        url = upload_to_aws(file)  # TODO: refactor to account for [orig_size_img, small_size_img]

        book_image = BookImage(
            book_owner=current_user,
            image_url=url
        )

        db.session.add(book_image)
        db.session.commit()

        return jsonify(book_image=book_image.serialize()), 201

    return jsonify({"error": "not authorized"}), 401

# TODO: MAKE DELETE ROUTE FOR BOOK IMAGE
