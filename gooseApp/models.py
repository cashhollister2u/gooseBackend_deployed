import os
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import datetime

# no view / serializer jsut holds info for leaderboard
class TopTenCounterSnapshot(models.Model):
    snapShot_date = models.DateTimeField(auto_now_add=True)
    counter_data = models.JSONField()
    
    def __str__ (self):
        return f"snapshot taken {self.snapShot_data}"

    
class User(AbstractUser):
    username = models.CharField(unique=True, max_length=100)
    email = models.EmailField(unique=True)
    public_key = models.TextField(null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        self.username = self.username.lower()
        super(User, self).save(*args, **kwargs)
            
    def profile(self):
        profile = Profile.objects.get(user=self)

class Messaging(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    reciever = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reciever')
    sender_message = models.CharField(max_length=1000)
    message = models.CharField(max_length=1000)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date']
        verbose_name_plural = "Message"
        
    def __str__(self):
        return f"{self.sender} - {self.reciever}"
    
    @property 
    def sender_profile(self):
        sender_profile = Profile.objects.get(user = self.sender)
        return sender_profile
    
    @property 
    def reciever_profile(self):
        reciever_profile = Profile.objects.get(user = self.reciever)
        return reciever_profile

def default_values5():
    return ['TICKER / Company Name', 'TICKER / Company Name', 'TICKER / Company Name', 'TICKER / Company Name', 'TICKER / Company Name']

def user_directory_prof_pic(instance, filename):
    return f'{instance.user.username}/profile_picture/profile{datetime.datetime.now()}.jpg'

def user_directory_background_pic(instance, filename):
    return f'{instance.user.username}/background_picture/background{datetime.datetime.now()}.jpg'
     
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(default='Name', max_length=1000)
    bio = models.CharField(default='my bio', max_length=100)
    values5 = models.JSONField(default=default_values5)
    profile_picture = models.ImageField(upload_to=user_directory_prof_pic, default=None, blank=True, null=True)
    background_image = models.ImageField(upload_to=user_directory_background_pic, default=None, blank=True, null=True)
    verified = models.BooleanField(default=False)
    following = models.ManyToManyField(User, related_name='following', symmetrical=False, blank=True, null=True)
    
    # Paths to the default images
    DEFAULT_PROFILE_PICTURE = "default/profile_pic_def/gooseCom.png"
    DEFAULT_BACKGROUND_IMAGE = "default/background_image_def/gooseDefaultBackground.png"
    

    @property
    def username(self):
        return self.user.username
    
    @property
    def public_key(self):
        return self.user.public_key
    
    @property
    def following_profile(self):
        following_profile = Profile.objects.filter(user__in = self.following.all())
        return following_profile
    
    def save(self, *args, **kwargs):
        if self.pk:  # Check if this is an existing Profile
            old_profile = Profile.objects.get(pk=self.pk)
            if old_profile.profile_picture != self.profile_picture:
                old_file_path = os.path.join(settings.MEDIA_ROOT, old_profile.profile_picture.name)
                default_profile_pic_path = os.path.join(settings.MEDIA_ROOT, self.DEFAULT_PROFILE_PICTURE)
                if os.path.isfile(old_file_path) and old_file_path != default_profile_pic_path:
                    os.remove(old_file_path)
            if old_profile.background_image != self.background_image:
                old_file_path = os.path.join(settings.MEDIA_ROOT, old_profile.background_image.name)
                default_background_image_path = os.path.join(settings.MEDIA_ROOT, self.DEFAULT_BACKGROUND_IMAGE)
                if os.path.isfile(old_file_path) and old_file_path != default_background_image_path:
                    os.remove(old_file_path)
        super().save(*args, **kwargs)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
