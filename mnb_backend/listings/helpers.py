from flask import jsonify

from mnb_backend.database import db
from mnb_backend.enums import PriceEnums
from mnb_backend.listings.models import Listing


def db_post_listing(user_id, title, author, isbn, condition, rate_price, rate_schedule, primary_image_url):
    """ Posts listing to aws while in try block and returns serialized if successful, returns an error if not.
    """

    price_enums_dict = {
        100: PriceEnums.ONE,
        200: PriceEnums.TWO,
        300: PriceEnums.THREE,
        400: PriceEnums.FOUR,
        500: PriceEnums.FIVE,
        600: PriceEnums.SIX,
        700: PriceEnums.SEVEN,
        800: PriceEnums.EIGHT,
        900: PriceEnums.NINE,
        1000: PriceEnums.TEN,
    }

    price = price_enums_dict[rate_price]

    # need to somehow take a  for a price
    try:
        listing = Listing.create_listing(
            owner_id=user_id,
            title=title,
            author=author,
            isbn=isbn,
            # condition=condition,
            rate_price=price,
            rate_schedule=rate_schedule,
            primary_image_url=primary_image_url

        )

        db.session.add(listing)
        db.session.commit()

        return listing
    except Exception as error:
        print("Error, Failed in aws_post_listing: ", error)
        return jsonify({"error": "Failed to add listing"}), 401
