import os
from dotenv import load_dotenv
import boto3
from werkzeug.utils import secure_filename
import uuid
from PIL import Image
import io
from pathlib import Path
import traceback


load_dotenv()

aws_access_key_id = os.environ['aws_access_key_id']
aws_secret_access_key = os.environ['aws_secret_access_key']

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key)
BUCKET_NAME_LARGE_IMAGES = 'sharebnb-gmm'
BUCKET_NAME_SMALL_IMAGES = 'sharebnb-gmm-small-images'


bucket_base_url_large_images = "https://sharebnb-gmm.s3.us-west-1.amazonaws.com/"
bucket_base_url_small_images = "https://sharebnb-gmm-small-images.s3.us-west-1.amazonaws.com/"


def upload_to_aws(file):
    """ Uploads a file to the aws """

    filename = f"{uuid.uuid4()}"
    try:
        s3.put_object(
            Body=file,
            Bucket=BUCKET_NAME_LARGE_IMAGES,
            Key=filename
        )
    except Exception as e:
        print("failed to upload orig image: ", e)

    orig_image_url = f"{bucket_base_url_large_images}{filename}"

    small_image_file = resize_image(file)

    try:
        s3.put_object(
            Body=small_image_file,
            Bucket=BUCKET_NAME_SMALL_IMAGES,
            Key=f"{filename}-small"
        )
        small_image_url = f"{bucket_base_url_small_images}{filename}-small"
    except Exception as e:
        print("failed to upload thumbnail image: ", e)
        traceback.print_exc()

    return [orig_image_url, small_image_url]


def resize_image(file):
    """ Resizes image to height of 140 and sizes width proportionally"""

    img = Image.open(file)

    try:
        orig_height = int(img.height)
        orig_width = int(img.width)
        orig_height_to_140_ratio = orig_height / 140
        new_height = 140

        new_width = int(orig_width / orig_height_to_140_ratio)

        new_image_size = (new_width, new_height)
        resized_img = img.resize(
            new_image_size, resample=Image.Resampling.BICUBIC)
        in_mem_file = io.BytesIO()
        resized_img.save(in_mem_file, format=img.format)

        in_mem_file.seek(0)
        img.close()

        return in_mem_file
    except Exception as e:
        print("failing at resize_image with error: ", e)
        traceback.print_exc()


def make_thumbnail(file):
    """ Given an image file, create a thumbnail for it and return as an
    in-memory file """

    img = Image.open(file)
    img.thumbnail((200, 200))

    in_mem_file = io.BytesIO()
    img.save(in_mem_file, format=img.format)
    in_mem_file.seek(0)

    return in_mem_file


def aux_make_thumbnail_manual(file):
    """ Given an image file, create a thumbnail for it and open it """

    file_name = (Path(file).stem)
    img = Image.open(file)
    img.thumbnail((560, 1380), Image.Resampling.LANCZOS)
    img.save(f"{file_name}-small.jpg",'JPEG', dpi=(300,300) )
    img.show()

# TODO: write function to re-thumbnail entire AWS bucket
