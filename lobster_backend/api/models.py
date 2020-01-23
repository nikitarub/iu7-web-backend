from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import Count
from datetime import datetime

class UserManager(UserManager):
    def get_user_profile(self, username):
        return self.all().annotate(num_followers=Count('target', distinct=True), num_following=Count('subscriber', distinct=True), num_posts=Count('post')).get(username=username)

    def filter_user_profile(self, username):
        return self.all().annotate(num_followers=Count('target'), num_following=Count('subscriber'), num_posts=Count('post')).filter(username=username)

    def get_author_login_by_id(self, id):
        return self.all().get(id=id).username
    
    def create_user(self, username, email, password):

        if not username:
            raise ValueError('User must have a username!')

        user = self.model(
            username = username,
            email = email
        )

        user.set_password(password)
        user.save(using = self._db)

        return user

class User(AbstractUser):
    objects = UserManager()

class UserRelationsManager(models.Manager):
    def is_follow(self, subscriber, target):
        target_user = User.objects.all().get(username=target)
        return self.all().filter(subscriber=subscriber, target=target_user)

class UserRelations(models.Model):
    objects = UserRelationsManager()

    subscriber = models.ForeignKey(User, on_delete = models.CASCADE, related_name='subscriber')
    target = models.ForeignKey(User, on_delete = models.CASCADE, related_name='target')

    class Meta:
        unique_together = (("subscriber", "target"))

class PostManager(models.Manager):
    def get_my_posts(self, user, start, end, current_user):
        posts = self.all().filter(author__username=user).order_by('-create_date')
        try:
            posts[end]
            is_next = True
        except:
            is_next = False

        offset_posts = posts[start:end]
        data = []

        self.create_object_post(offset_posts, data, user)
        self.is_my_post(data, current_user)
        
        return data, is_next

    def get_posts(self, user, start, end):
        targets = UserRelations.objects.filter(subscriber=user).values('target');
        posts = Post.objects.filter(author__in=targets).order_by('-create_date')
        offset_posts = posts[start:end]
        try:
            posts[end]
            is_next = True
        except:
            is_next = False

        data = []
        self.create_object_post(offset_posts, data, user)

        return data, is_next

    def create_object_post(self, post_q_s, posts, user):
        for post in post_q_s.values():
            post['photos'] = Photo.objects.get_photo_by_post(post['id'])
            post['author'] = User.objects.get_author_login_by_id(post['author_id'])
            del post['author_id']
            posts.append(post)

    def is_my_post(self, posts, username):
        for post in posts:
            post['isMyPost'] = post['author'] == username

    def is_post_like(self, user, post_id):
        isLike = PostLike.objects.filter(user=user, post__id=post_id)
        return isLike.exists()

    def all_posts(self):
        return self.all()

    def get_post_by_id(self, id):
        return self.annotate(num_likes=Count("postlike", distinct=True), num_dislike=Count("postdislike", distinct=True))

    def get_post_by_date(self):
        return self.all().annotate(num_likes=Count("postlike", distinct=True),
                                   num_dislikes=Count("postdislike", distinct=True))


class Post(models.Model):
    objects = PostManager()

    author = models.ForeignKey(User, on_delete = models.CASCADE)

    text = models.CharField(max_length=100)
    create_date = models.DateTimeField(default=datetime.now, verbose_name=u"Время создания поста")
    is_active = models.BooleanField(default=False, verbose_name=u"Флаг удаления поста")

    def __str__(self):
        return self.text
    
    class Meta:
        ordering = ['-create_date']


class PhotoManager(models.Manager):
    def all_photos(self):
        return self.all()

    def get_photo_by_post(self, post_id):
        photos = {}
        for p in self.filter(post__id=post_id).values():
            photos[p['hash']] = p['img']
            
        return photos


class Photo(models.Model):
    objects = PhotoManager()

    post = models.ForeignKey(Post, on_delete = models.CASCADE, default=None)
    img = models.ImageField("Фотография", upload_to="uploads/%Y/%m/%d", default=None)
    hash = models.CharField(max_length=40)

    def __str__(self):
        return "фото к статье" + '"' + self.post.text + '"'
