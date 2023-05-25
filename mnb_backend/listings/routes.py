"""Routes for listings blueprint."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from mnb_backend.database import db
from mnb_backend.api_helpers import db_post_book, aws_upload_image, db_add_book_image
from mnb_backend.listings.models import Book

listings_routes = Blueprint('listings_routes', __name__)


@listings_routes.post("/api/books")
@jwt_required()
def create_book():
    """Add book, and return data about new book.

    Returns JSON like:
        {book: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}}
    """
    # TODO: try posting a book object to the db first. if successful, post book image to aws, if successful,
    #  switch url for book from dummy_url to aws_url. if anything fails delete the book and the book image.
    # https://www.geeksforgeeks.org/try-except-else-and-finally-in-python/

    print("I'm in api/books")
    current_user_id = get_jwt_identity()
    if current_user_id:
        try:
            images = request.files
            title = request.form.get("title")
            author = request.form.get("author")
            isbn = int(request.form.get("isbn"))
            condition = request.form.get("condition")
            rate_price = int(request.form.get("rate_price"))
            rate_schedule = request.form.get("rate_schedule")

            # post book to db
            book_posted = db_post_book(current_user_id, title, author, isbn, condition, rate_price, rate_schedule)

            images_posted = []
            # post image to aws

            for image in images:
                image_url = aws_upload_image(images[image])
                # post image to database
                image_element = db_add_book_image(current_user_id, book_posted.id, image_url)
                images_posted.append(image_element.serialize())

            # TODO: might have to set primary book image here but then its pinging the db twice for the patch request

            return jsonify(book=book_posted.serialize(), images_posted=images_posted), 201

        except Exception as error:
            print("Error", error)
            return jsonify({"error": f"Failed to add book and book image: {error}", }), 401


@listings_routes.patch('/api/books/<int:book_uid>')
@jwt_required()
def update_book(book_uid):
    """ Update book information

    Returns JSON like:
        {book: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}}

    Authorization: must be owner of book
    """

    current_user = get_jwt_identity()
    book = Book.query.get_or_404(book_uid)
    print("book owner", book.owner_username)
    if current_user == book.owner_username:
        data = request.json

        book.orig_image_url = data['orig_image_url'],
        book.small_image_url = data['small_image_url'],
        book.title = data['title'],
        book.author = data['author'],
        book.isbn = data['isbn'],
        book.genre = data['genre'],
        book.condition = data['condition'],
        book.price = data['price'],

        db.session.add(book)
        db.session.commit()

        return jsonify(book=book.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


@listings_routes.patch('/api/users/<int:user_uid>/books/<int:book_uid>/toggle_status')
@jwt_required()
def toggle_book_status(user_uid, book_uid):
    """ Toggles book availability status. """

    current_user = get_jwt_identity()

    if current_user == user_uid:
        book = Book.query.get_or_404(book_uid)

        if book.status == "Available":
            book.status = "Checked Out"
        else:
            book.status = "Available"

        db.session.add(book)
        db.session.commit()

        return jsonify(book=book.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


@listings_routes.delete('/api/books/<int:book_uid>')
@jwt_required()
def delete_book(book_uid):
    """ update book information

    Returns JSON like:
    {book: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}}

    Authorization: must be owner of book
    """

    current_user = get_jwt_identity()
    book = Book.query.get_or_404(book_uid)
    if current_user == book.owner_id:
        db.session.delete(book)
        db.session.commit()

        return jsonify("Book successfully deleted"), 200

    return jsonify({"error": "not authorized"}), 401
