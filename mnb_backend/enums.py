# import enum
from sqlalchemy import Enum
from enum import Enum


class UserStatusEnums(Enum):
    """ Enum for user status """

    ACTIVE = "Active"
    INACTIVE = "Inactive"
    DELETED = "Deleted"

    # Custom JSON serializer for UserStatusEnums


class PriceEnums(Enum):
    """ Enum for price """

    ONE = 100
    TWO = 200
    THREE = 300
    FOUR = 400
    FIVE = 500
    SIX = 600
    SEVEN = 700
    EIGHT = 800
    NINE = 900
    TEN = 1000


class ReservationStatusEnum(Enum):
    """ Enum for reservation status """

    PENDING = "Pending"
    ACCEPTED = "Accepted"
    IN_PROGRESS = "In Progress"
    DECLINED = "Declined"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class ListingStatusEnum(Enum):
    """ Enum for listing status """

    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"


class RentalDurationEnum(Enum):
    """ Enum for rental duration"""

    DAILY = 'Day'
    WEEKLY = 'Week'
    MONTHLY = 'Month'


class ListingConditionEnum(Enum):
    """ Enum for listing conditions """

    LIKE_NEW = "Like New"
    FAIR = "Fair"
    USED = "Used"


class StatesEnum(Enum):
    """ Enum for states """

    ALABAMA = "AL"
    KENTUCKY = "KY"
    OHIO = "OH"
    ALASKA = "AK"
    LOUISIANA = "LA"
    OKLAHOMA = "OK"
    ARIZONA = "AZ"
    MAINE = "ME"
    OREGON = "OR"
    ARKANSAS = "AR"
    MARYLAND = "MD"
    PENNSYLVANIA = "PA"
    AMERICAN_SAMOA = "AS"
    MASSACHUSETTS = "MA"
    PUERTO_RICO = "PR"
    CALIFORNIA = "CA"
    MICHIGAN = "MI"
    RHODE_ISLAND = "RI"
    COLORADO = "CO"
    MINNESOTA = "MN"
    SOUTH_CAROLINA = "SC"
    CONNECTICUT = "CT"
    MISSISSIPPI = "MS"
    SOUTH_DAKOTA = "SD"
    DELAWARE = "DE"
    MISSOURI = "MO"
    TENNESSEE = "TN"
    DISTRICT_OF_COLUMBIA = "DC"
    MONTANA = "MT"
    TEXAS = "TX"
    FLORIDA = "FL"
    NEBRASKA = "NE"
    TRUST_TERRITORIES = "TT"
    GEORGIA = "GA"
    NEVADA = "NV"
    UTAH = "UT"
    GUAM = "GU"
    NEW_HAMPSHIRE = "NH"
    VERMONT = "VT"
    HAWAII = "HI"
    NEW_JERSEY = "NJ"
    VIRGINIA = "VA"
    IDAHO = "ID"
    NEW_MEXICO = "NM"
    VIRGIN_ISLANDS = "VI"
    ILLINOIS = "IL"
    NEW_YORK = "NY"
    WASHINGTON = "WA"
    INDIANA = "IN"
    NORTH_CAROLINA = "NC"
    WEST_VIRGINIA = "WV"
    IOWA = "IA"
    NORTH_DAKOTA = "ND"
    WISCONSIN = "WI"
    KANSAS = "KS"
    NORTHERN_MARIANA_ISLANDS = "MP"
    WYOMING = "WY"


def enum_serializer(obj):
    """
    Custom JSON serializer for UserStatusEnums"""
    if isinstance(obj, Enum):
        return obj.value

    raise TypeError(f'Object of type {type(obj)} is not JSON serializable')
