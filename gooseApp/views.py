from django.http import JsonResponse
from django.db.models import Q
from gooseApp.models import User, Profile, Messaging, TopTenCounterSnapshot
from gooseApp.serializer import followingSerializer, MyTokenObtainPairSerializer, RegisterSerializer, SearchForUserPage, MessagingSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
import json
     
        
class MyInbox(APIView):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        non_user_id = kwargs.get('non_user_id')
        batch_number = int(kwargs.get('batch_number'))

        batch_size = 15
        batch_index = batch_number * batch_size

        messages = Messaging.objects.filter(
            (Q(sender_id=user_id) & Q(reciever_id=non_user_id)) | 
            (Q(reciever_id=user_id) & Q(sender_id=non_user_id))
        ).order_by("-id")

        total_messages = messages.count()
        messages_subset = messages[batch_index:batch_index + batch_size]
        serializer = MessagingSerializer(messages_subset, many=True)

        return Response({
            'total_messages': total_messages,
            'messages': serializer.data
        })
    
class ConversationList(generics.ListAPIView):
    serializer_class = followingSerializer
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']

        user = User.objects.get(pk=user_id)
        user_username = user.username
        
        messages = Messaging.objects.filter(
            Q(sender_id=user_id) | Q(reciever_id=user_id)
        ).order_by("id")

    
        unique_profiles = []

        for message in messages:
            
            if message.sender_profile.username != user_username:
                if message.sender_profile not in unique_profiles:
                    unique_profiles.append(message.sender_profile)
            if message.reciever_profile.username != user_username:
                if message.reciever_profile not in unique_profiles:
                    unique_profiles.append(message.reciever_profile)

        return unique_profiles
            

class SendMessages(generics.CreateAPIView):
    serializer_class = MessagingSerializer
   
    def perform_create(self, serializer):       
        serializer.save()
        
        
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class SearchFunction(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = SearchForUserPage
    lookup_field = 'username'
    parser_classes = (MultiPartParser, FormParser,)
    
    def get_queryset(self):
        username = self.kwargs.get('username').lower()  # Get the username parameter from the URL and lowercase it
        queryset = User.objects.filter(username__iexact=username)  # Perform a case-insensitive match
        return queryset
    def get_object(self):
        
        queryset = self.filter_queryset(self.get_queryset())

        return queryset.first()
    
class LeaderboardView(generics.RetrieveAPIView):
     permission_classes = [IsAuthenticated]
     def get(self, request, *args, **kwargs):
        queryset = Profile.objects.all()
        values5_list = queryset.values_list('values5', flat=True)
        
        flat_list = []
        consol_list = []
        topTen_counter = {}
        
        for sublist in values5_list:
            flat_list.extend(sublist)
        for val in flat_list:
            if val == '' or val == 'null' or val is None:
                continue
            elif val == 'TICKER / Company Name':
                continue
            else:
                consol_list.append(val)
        for company in range(len(consol_list)):
            topTen_counter[consol_list[company]] = 1 + topTen_counter.get(consol_list[company], 0)
        
        topten_counter_exists = False
        for snapshot in TopTenCounterSnapshot.objects.all():
             if snapshot.counter_data == topTen_counter:
                topten_counter_exists = True
                break
                
        previous_snapshot = TopTenCounterSnapshot.objects.order_by('-snapShot_date').last()
        previous_state = previous_snapshot.counter_data if previous_snapshot else {}
     
        previous_list = [[k, v] for k, v in sorted(previous_state.items(), key=lambda item: item[1], reverse=True)]
        ranked_list = [[k, v] for k, v in sorted(topTen_counter.items(), key=lambda item: item[1], reverse=True)]
        
        if previous_list != ranked_list:
            for rankIndex, rankStock in enumerate(ranked_list):
                foundMatch = False
                for prevIndex, prevStock in enumerate(previous_list):
                    if rankStock[0] == prevStock[0]:
                        foundMatch = True
                        if rankIndex < prevIndex:
                            ranked_list[rankIndex].append('positive')
                        elif rankIndex > prevIndex:
                            ranked_list[rankIndex].append('negative')
                        else:
                            ranked_list[rankIndex].append('neutral')
                        break
                if not foundMatch:
                    ranked_list[rankIndex].append('positive')
        else:
            for rankIndex, rankStock in enumerate(ranked_list):
                for prevIndex, prevStock in enumerate(previous_list):
                    if rankStock[0] == prevStock[0]:
                        if rankIndex < prevIndex:
                            ranked_list[rankIndex].append('positive')
                        elif rankIndex > prevIndex:
                            ranked_list[rankIndex].append('negative')
                        else:
                            ranked_list[rankIndex].append('neutral')
                        break
                            
       
            if not topten_counter_exists:
                snapshot = TopTenCounterSnapshot(counter_data=topTen_counter)
                snapshot.save()
                
                snapshots = TopTenCounterSnapshot.objects.order_by('-snapShot_date')
                if snapshots.count() > 1:
                    snapshots.last().delete()
                    
                #if i have to clear the model 
                #TopTenCounterSnapshot.objects.all().delete()
             
        return Response({'ranked_list': ranked_list[0:25]})
    
# Get All Routes
@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/gooseApp/token/',
        '/gooseApp/register/',
        '/gooseApp/token/refresh/',
        'test/',
        'search/<str:username>/',
        'stockdict/',
        'stockdict/<int:pk>/',
        'stocklist/',
        'stocklist/<int:pk>/',
        'leaderboard/',
    ]
    return Response(routes)


class ProfileUpdate(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
   
    def get(self, request):
        # Generate a new token for the user using your custom serializer
        token_serializer = MyTokenObtainPairSerializer()
        token = token_serializer.get_token(request.user)
        return JsonResponse({'authToken': str(token)})

    def post(self, request):
        # Check if the request is for follow or unfollow
        action = request.data.get('action')  # Assuming 'action' specifies 'follow' or 'unfollow'
        target_user_id = request.data.get('target_user_id')  # Assuming 'target_user_id' specifies the user to follow/unfollow
        
        
        
        user = request.user.profile
        target_profile = User.objects.get(id=target_user_id)
        
        
        if action == 'follow':
            # Check if the user is not trying to follow themselves
            if user != target_profile:
                user.following.add(target_profile)  # Add the profile, not the user
                return JsonResponse({'followeduser': target_user_id})
            else:
                return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        elif action == 'unfollow':
            user.following.remove(target_profile)  # Remove the profile, not the user
            return Response({'detail': 'User unfollowed successfully.'}, status=status.HTTP_200_OK)
    def patch(self, request):
        #request.user means updates apply solely to the user with the authtoken
        user = request.user

        new_name = request.data.get('full_name')
        new_bio = request.data.get('bio')
        new_values5_string = request.data.get('values5')
        new_values5 = json.loads(new_values5_string) if new_values5_string else None
        new_background_image = request.data.get('background_image')
        new_profile_picture = request.data.get('profile_picture')
       
        
        # Update user data if corresponding fields are provided
        if new_name:
            user.profile.full_name = new_name
        if new_bio:
            user.profile.bio = new_bio
        if new_values5:
            if len(new_values5) > 25:
                 return JsonResponse(
                {'error': 'values5 cannot have more than 25 elements.'},
                status=400  # Bad Request
            )
            if new_values5 != user.profile.values5:
                user.profile.values5 = new_values5
           
        if new_background_image:
            user.profile.background_image = new_background_image
        if new_profile_picture:
            user.profile.profile_picture = new_profile_picture
        
            
        # Save the updated user
        user.save()

        return Response({'response': 'User data updated successfully'}, status=status.HTTP_200_OK)