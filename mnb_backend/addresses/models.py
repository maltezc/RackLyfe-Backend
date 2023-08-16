"""Model for Address"""
from mnb_backend.addresses.address_helpers import fuzz_coordinates
from mnb_backend.database import db
from geoalchemy2 import Geometry


from sqlalchemy.sql import select
from sqlalchemy import func


# region Address
class Address(db.Model):
    """ Address in the system. """

    __tablename__ = 'addresses'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )
    user = db.relationship('User', back_populates="address", uselist=False)

    street_address = db.Column(
        db.Text,
        nullable=False
    )

    apt_number = db.Column(
        db.Integer
    )

    city_uid = db.Column(
        db.Integer,
        db.ForeignKey('cities.id')
    )
    city = db.relationship('City', back_populates="addresses", uselist=False)

    zipcode_uid = db.Column(
        db.Integer,
        db.ForeignKey('zip_codes.id')
    )
    zipcode = db.relationship('ZipCode', back_populates="addresses", uselist=False)

    location = db.relationship('Location', back_populates="address", uselist=False, cascade='delete')

    def __repr__(self):
        return f"< Address #{self.id}, Street Address: {self.street_address}, Apt Number: {self.apt_number}, " \
               f"City: {self.city}, Zipcode: {self.zipcode}, Location: {self.location} >"

    def serialize(self):
        """ returns self """

        print("location: ", self.location.serialize())

        return {
            "address_uid": self.id,
            "user_id": self.user_id,
            "street_address": self.street_address,
            "apt_number": self.apt_number,
            "city": self.city.serialize(),
            "zipcode": self.zipcode.serialize(),
            "location": self.location.serialize()
        }


# endregion


# region Location



class Location(db.Model):
    """ User's geocoded Location point. """

    __tablename__ = 'locations'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    address_id = db.Column(
        db.Integer,
        db.ForeignKey('addresses.id')
    )
    address = db.relationship("Address", back_populates="location", uselist=False)

    point = db.Column(
        Geometry(geometry_type='POINT', srid=4326),
        # nullable=False
    )

    def __repr__(self):
        return f"< Location #{self.id} >"

    def serialize(self):
        """ returns self """

        # query = text(f"SELECT ST_X(point) as x, ST_Y(point) as y FROM {self.__tablename__} WHERE id = :id")
        # result = db.session.execute(query, {"id": self.id}).fetchone()
        # x, y = result.x, result.y if result else None, None

        stmt = select(func.ST_X(self.point).label("x"), func.ST_Y(self.point).label("y"))
        stmt = stmt.select_from(self.__table__).where(self.__table__.c.id == self.id)
        result = db.session.execute(stmt).fetchone()

        x = result.x if result else None
        y = result.y if result else None

        fuzzed_lon, fuzzed_lat = fuzz_coordinates(y, x)

        return {
            "id": self.id,
            "fuzzed_point_x": fuzzed_lon,
            "fuzzed_point_y": fuzzed_lat,
            "point_x": x,
            "point_y": y,
            # "point_x": self.point.x,
            # "point_y": self.point.y,

            # "point": self.point,
        }


# endregion


# region Cities
class City(db.Model):
    """ Model for City """

    __tablename__ = 'cities'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    addresses = db.relationship("Address", back_populates="city", uselist=True)

    city_name = db.Column(
        db.Text,
        nullable=False
    )

    state = db.relationship('State', back_populates="cities", uselist=False)

    def __repr__(self):
        return f"< City # {self.id}, City Name: {self.city_name} >"

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "city_name": self.city_name,
            # "state": self.state_uid,
            "state": self.state.state_abbreviation
        }


# endregion

# region States
# NOTE: @LUCAS - keeping states to be able to do searches by relationships.
class State(db.Model):
    """ A State for the address """

    __tablename__ = 'states'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    state_abbreviation = db.Column(
        db.String(2),
        db.CheckConstraint(
            "state_abbreviation in ('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', "
            "'IL', 'IN','IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', "
            "'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', "
            "'WA', 'WV', 'WI', 'WY')"),
        unique=True
    )

    state_name = db.Column(
        db.String(15),
        unique=True
    )

    city_uid = db.Column(
        db.Integer,
        db.ForeignKey('cities.id')
    )
    cities = db.relationship('City', back_populates='state', uselist=True)

    def __repr__(self):
        return f"< State # {self.id}, State Abbreviation: {self.state_abbreviation}, State name: {self.state_name}>"

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "state_abbreviation": self.state_abbreviation,
            "state_name": self.state_name
        }


# endregion

# region Zipcodes

class ZipCode(db.Model):
    """ A zipcode for every city """
    __tablename__ = 'zip_codes'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    code = db.Column(
        db.String(5),
        unique=True
    )

    addresses = db.relationship('Address', back_populates='zipcode', uselist=True)

    def __repr__(self):
        return f"< Zipcode # {self.id}, Code {self.code} >"

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "code": self.code
        }

# endregion
