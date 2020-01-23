from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import login, logout, authenticate
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer, RelationSerializer, PostSerializer, PhotosSerializer
from .models import User, UserRelations, Post
import json
from django.http import JsonResponse

def test(request):
    return JsonResponse({'ok': 'ok'}, status=200)

class UserProfile(APIView):
    """
    Get information about user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        try:
            user = User.objects.get_user_profile(username)
            my_username = request.user
            is_follow = UserRelations.objects.is_follow(my_username, username)
            is_my_page = False
        except:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        if (my_username.username == username):
            is_my_page = True

        print(user.num_followers)
        data = {
            "login": user.username,
            "followers": user.num_followers,
            "following": user.num_following,
            "posts": user.num_posts,
            "isFollow": is_follow.count() != 0,
            "isMyPage": is_my_page
        } 

        return Response(data, status=status.HTTP_200_OK)


class MyProfile(APIView):
    """
    Return auth user profile
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nickname = request.user
        user = User.objects.get_user_profile(nickname)
        data = {
            "login": user.username,
            "followers": user.num_followers,
            "following": user.num_following,
            "posts": user.num_posts,
            "isFollow": False,
            "isMyPage": True
        }

        return Response(data)


class UserLogout(APIView):
    """
    Logout user
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({}, status=status.HTTP_200_OK)


class UserSignup(APIView):
    """
    Signup user
    """
    def post(self, request):
        serializers = UserSerializer(data=request.data)

        if serializers.is_valid():
            user = serializers.save()
            if user:
                login(request, user)
                return Response({}, status=status.HTTP_201_CREATED)

        return Response(serializers.errors, status=status.HTTP_403_FORBIDDEN)

class UserSignin(APIView):
    """
    Signin user
    """

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        isUser = User.objects.filter(username=username).count() > 0
        if (not isUser):
            return Response({
                "username": "User with this login doen't exists"
            }, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({}, status=status.HTTP_200_OK)
        else:
            return Response({"password": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request):
        if (request.user.is_authenticated):
            return Response({}, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

class UserRelation(APIView):
    """
    Allow follow and unfollow user
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = {
            "subscriber_id": request.user.id,
            "target_username": request.data.get("username")
        }

        serializer = RelationSerializer(data=data)
        if serializer.is_valid():
            rel = serializer.save()
            if rel:
                return Response({}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        data = {
            "subscriber_id": request.user.id,
            "target_username": request.data.get("username")
        }

        serializer = RelationSerializer(data=data)
        if serializer.is_valid():
            rel = serializer.delete(request.user.id, request.data.get("username"))
            return Response({}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Posts(APIView):
    """
    Essence for processing posts
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = {
            "text": request.data.get("text"),
            "author_id": request.user.id
        }

        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            post = serializer.save()
            if post:
                for item in request.data.items():
                    if ('text' not in item[0]):
                        photo_data = {
                            "post_id": post.id,
                            "img": item[1],
                            "hash": item[0]
                        }

                        photoSerializer = PhotosSerializer(data=photo_data)
                        if photoSerializer.is_valid():
                            img = photoSerializer.save()

                return Response({}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, page, offset, username=None):
        start = (page - 1) * offset
        end = start + offset

        if(username == None):
            posts, is_next = Post.objects.get_posts(request.user, start, end)
        else:
            posts, is_next = Post.objects.get_my_posts(username, start, end, request.user.username)

        return Response({
            "posts": posts,
            "isNext": is_next
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        Post.objects.get(author__id=request.user.id, id=request.data.get("id")).delete()
        return Response({}, status=status.HTTP_200_OK)

