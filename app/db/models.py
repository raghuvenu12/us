from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from app.db import models

# This is an abstract model. No table will be created for this model.
class User(Model):
    phone = fields.CharField(max_length=16, null=False, )
    usr_type = fields.CharField(max_length=16, null=False, default="citizen", )
    password = fields.CharField(max_length=64, null=False, )
    created_at = fields.DatetimeField(auto_now=True, )
    class Meta:
        table = "user"

class OTP(Model):
    username = fields.CharField(max_length=64, unique=True, )
    otp = fields.IntField(max_length=6, null=False, )
    num_attempts = fields.IntField(max_length=3, null=False, )
    status = fields.CharField(max_length=16, null=False, )
    valid_till = fields.DatetimeField(null=False, )
    created_at = fields.DatetimeField(auto_now=True, )
    class Meta:
        table = "otp"

class Agency(Model):
    handle = fields.CharField(max_length=64, unique=True, )
    name = fields.CharField(max_length=64, null=False, )
    logo_url = fields.CharField(max_length=256, null=False, )
    logo_thumbnail_url = fields.CharField(max_length=256, null=False, )
    address = fields.CharField(max_length=256, null=False, )
    admin = fields.ForeignKeyField('us.User', null=False, )
    created_at = fields.DatetimeField(auto_now=True, )
    def __str__(self):
        return f"{self.tag} {self.name}"
    class Meta:
        ordering = ["-created_at"]
        table = "agency"

class Citizen(Model):
    username = fields.CharField(max_length=64, unique=True, )
    user = fields.ForeignKeyField('us.User', null=False, )
    name = fields.CharField(max_length=64, null=False, )
    created_at = fields.DatetimeField(auto_now=True, )
    def __str__(self):
        return f"{self.tag} {self.name}"
    class Meta:
        ordering = ["-created_at"]
        table = "citizen"

class Post(Model):
    text = fields.CharField(max_length=256, null=False, )
    user = fields.ForeignKeyField('us.User', null=False, )
    post_type = fields.CharField(max_length=16, null=False, default="citizen", ) # individual/community
    ip_address = fields.CharField(max_length=64, null=True, )
    mentions = fields.CharField(max_length=256, null=True, )
    hashtags = fields.CharField(max_length=256, null=True, )
    shares = fields.IntField(null=False, default=0, )
    likes = fields.IntField(null=False, default=0, )
    latitude = fields.FloatField(null=False, default=0.0, )
    longitude = fields.FloatField(null=False, default=0.0, )
    address = fields.CharField(max_length=256, null=True, )
    city = fields.CharField(max_length=64, null=True, )
    state = fields.CharField(max_length=64, null=True, )
    created_at = fields.DatetimeField(auto_now=True, )

class Media(Model):
    post = fields.ForeignKeyField('us.Post', null=False, )
    media_type = fields.CharField(max_length=16, null=False, default="image", ) # image/video
    media_url = fields.CharField(max_length=256, null=False, )
    media_thumbnail_url = fields.CharField(max_length=256, null=False, )
    created_at = fields.DatetimeField(auto_now=True, )

class Comment(Model):
    post = fields.ForeignKeyField('us.Post', null=False, )
    text = fields.CharField(max_length=256, null=False, )
    user = fields.ForeignKeyField('us.User', related_name="comment", null=False, )
    ip_address = fields.CharField(max_length=64, null=True, )
    created_at = fields.DatetimeField(auto_now=True, )
