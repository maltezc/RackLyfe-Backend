from flask import jsonify

from mnb_backend.database import db
from mnb_backend.enums import PriceEnums, RackMountTypeEnum, RackActivityTypeEnum
# from mnb_backend.listings.models import Listing




# # mount_type_enum = RackMountTypeEnum[mount_type.upper()]
# activity_type_enum = RackActivityTypeEnum[activity_type.upper().replace(" ", "").replace("/", "")]


def get_mount_type_enum(mount_type):
    """Gets mount type enum"""

    mount_type_enum = RackMountTypeEnum[mount_type.upper()]
    return mount_type_enum


def get_activity_type_enum(activity_type):
    """Gets activity type enum"""

    activity_type_enum = RackActivityTypeEnum[activity_type.upper().replace(" ", "").replace("/", "")]
    return activity_type_enum
