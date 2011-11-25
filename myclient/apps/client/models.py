from django.db import models 
from django.contrib.auth.models import User 
from oauth2app.models import Code, Client, TimestampGenerator, AccessRange, KeyGenerator
from oauth2app.consts import CODE_KEY_LENGTH, CODE_EXPIRATION
from oauth2app.consts import ACCESS_TOKEN_LENGTH, REFRESH_TOKEN_LENGTH

class OauthRequest(models.Model):
    """Stores authorization request so that we can look it up
    
    **Args:**
    
    * *client:* A oauth2app.models.Client object
    * *user:* A django.contrib.auth.models.User object
    
    **Kwargs:**
    
    * *key:* A string representing the authorization code. *Default 30 
      character random string*
    * *expire:* A positive integer timestamp representing the access token's 
      expiration time.
    * *redirect_uri:* A string representing the redirect_uri provided by the 
      requesting client when the code was issued. *Default None*
    * *scope:* A list of oauth2app.models.AccessRange objects. *Default None* 
    
    """
    client = models.ForeignKey(Client)
    user = models.ForeignKey(User)
    code = models.CharField(
        unique=False, 
        max_length=CODE_KEY_LENGTH, 
        default="",
        db_index=True)
    response_type = models.CharField(max_length=20)
    key = models.CharField(
        unique=True, 
        max_length=CODE_KEY_LENGTH, 
        default=KeyGenerator(CODE_KEY_LENGTH),
        db_index=True)
    issue = models.PositiveIntegerField(
        editable=False, 
        default=TimestampGenerator())
    completed = models.PositiveIntegerField(
        default=0)
    scope = models.ManyToManyField(AccessRange)
    refresh_token = models.CharField(
        unique=False, 
        blank=True, 
        null=True, 
        max_length=REFRESH_TOKEN_LENGTH,
        default="",
        db_index=True)
    token = models.CharField(
        unique=False,
        blank=True, 
        max_length=ACCESS_TOKEN_LENGTH, 
        default="",
        db_index=True)
