from gooseApp.models import User, Profile, Messaging
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import PermissionDenied


class followingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['id','username', 'public_key', 'full_name', 'profile_picture', 'verified']
    
    

class UserSerializer(serializers.ModelSerializer):
    profile = followingSerializer()

    class Meta:
        model = User
        fields = ('id', 'profile', 'public_key')
    
    def get_profile(self, obj):
        profile = Profile.objects.get(user=obj)
        return ProfileSerializer(profile).data
    
class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    public_key = serializers.SerializerMethodField()
    following = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Profile
        fields = ['username', 'public_key', 'following', 'full_name', 'bio', 'profile_picture', 'background_image', 'values5', 'verified']
    def get_username(self, obj):
        return obj.user.username
    def get_public_key(self,obj):
        return obj.user.public_key

class SearchForUserPage(serializers.ModelSerializer):
    profile = ProfileSerializer()
    
    class Meta:
        model = User
        fields = ['profile', 'public_key', 'id']
        
class MessagingSerializer(serializers.ModelSerializer):
    reciever_profile = followingSerializer(read_only=True)
    sender_profile = followingSerializer(read_only=True)
    
    class Meta:
        model = Messaging
        fields = ['id', 'user','sender','sender_profile', 'reciever','reciever_profile', 'sender_message', 'message', 'is_read', 'date']

    
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        #check if user is approved by admin
        if not user.profile.verified:
            raise PermissionDenied("User is not verified.")  # You can customize the message
        token = super().get_token(user)
        
        token['full_name'] = user.profile.full_name
        token['username'] = user.username
        token['bio'] = user.profile.bio
        token['profile_picture'] = str(user.profile.profile_picture)
        token['background_image'] = str(user.profile.background_image)
        token['values5'] = user.profile.values5
        token['verified'] = user.profile.verified
        token['public_key'] = user.public_key
        following_users = user.profile.following.all()
        token['following'] = [
                                {
                                'id': f.id,
                                'public_key': f.profile.public_key, 
                                'profile': {
                                   'username': f.profile.username,
                                   'full_name': f.profile.full_name,
                                   'profile_picture': str(f.profile.profile_picture),
                                   'verified': f.profile.verified
                                   },
                                } for f in following_users
                              ]
        
        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    public_key = serializers.CharField(write_only=True, required=False)  

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'public_key')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        if attrs['username'].lower() == 'default':
            raise serializers.ValidationError(
                {"username": "A user with this username cannot be created."})

        return attrs

    def create(self, validated_data):
        public_key = validated_data.pop('public_key', None)
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            public_key=public_key
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
