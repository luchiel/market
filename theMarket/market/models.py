from django.db import models
from django.db.models import Count, Sum
from hashlib import sha1
from datetime import datetime, timedelta


class User(models.Model):
    login    = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=40)
    email    = models.EmailField()
    salt     = models.CharField(max_length=10)
    is_admin = models.BooleanField(default=False)

    def __unicode__(self):
        return self.login
    def get_password_hash(self, password):
        return sha1(self.salt + password).hexdigest()
    def get_address(self):
        return Address.objects.get(user=self)
    COMMENTS_PER_DAY = 3
    def get_user_vote_count_today(self):
        return self.votes.filter(date=datetime.today()).aggregate(Count('id'))
    def can_vote_today(self):
        return self.get_user_vote_count_today()['id__count'] < User.COMMENTS_PER_DAY


class Category(models.Model):
    depth = models.IntegerField()
    path  = models.CharField(max_length=40)
    name  = models.CharField(max_length=200)

    def get_parent_category(self):
        return Category.objects.get(path=self.path.rpartition('.')[0])

    def get_category_sequence(self):
        current = self
        categories = []
        while current.path != str(current.id):
            current = current.get_parent_category()
            categories.insert(0, current)
        return categories

    def get_child_categories(self):
        return Category.objects.filter(path__startswith=self.path + '.')

    def get_direct_child_categories(self):
        return Category.objects.filter(path__startswith=self.path + '.', depth=self.depth + 1)

    def make_path_and_depth(self, parent_id):
        parent = Category.objects.get(id=parent_id)
        self.path = parent.path + '.' + str(self.id)
        self.depth = parent.depth + 1

    def get_products(self):
        return Product.objects.filter(category=self)

    def change_parent(self, new_parent_id):
        children = self.get_direct_child_categories()
        self.make_path_and_depth(new_parent_id)
        self.save()
        for c in children:
            c.change_parent(self.id)


class Product(models.Model):
    name        = models.CharField(max_length=200)
    description = models.TextField()
    image       = models.CharField(max_length=200)
    category    = models.ForeignKey(Category)
    price       = models.IntegerField()

    def get_product_marks(self):
        #return Comment.objects.filter(product=self).values('mark').annotate(mark_count=Count('id'), rating_sum=Sum('rating')).order_by('-mark')
        #return Comment.objects.raw(
        #    'SELECT id, mark, SUM(rating) + COUNT(ID) AS total from market_comment GROUP BY mark HAVING product_id = %s', [self.id]
        #)
        return Mark.objects.filter(product=self).values('mark').annotate(total=Count('id')).order_by('-total')

    def get_product_mark_by_most_users(self):
        #marks = Comment.objects.raw(
        #    'SELECT id, mark, SUM(rating) + COUNT(ID) AS total from market_comment GROUP BY mark HAVING product_id = %s ORDER BY total DESC',
        #    [self.id]
        #)
        #return marks[0].mark if len(list(marks)) else 0
        m = Mark.objects.filter(product=self).values('mark').annotate(total=Count('id')).order_by('-total')
        return 0 if not m else m[0].mark

    def get_comments(self):
        return Comment.objects.filter(product=self).order_by('path', 'date')

    def get_comment_count(self):
        return self.get_comments().count()


class Basket(models.Model):
    session_id = models.CharField(max_length=200, null=True)
    user       = models.ForeignKey(User, null=True)

    def get_basket_goods(self):
        return Purchased.objects.filter(basket=self).filter(is_sent=False)

    def get_basket_price(self):
        counter = 0
        for product in self.get_basket_goods():
            counter += product.quantity * product.product.price
        return counter


class Purchased(models.Model):
    is_sent  = models.BooleanField(default=False)
    product  = models.ForeignKey(Product)
    basket   = models.ForeignKey(Basket)
    quantity = models.IntegerField(default=1)
    date     = models.DateField(auto_now=True)
    
    def get_max(self):
        return 20
        
    def get_price(self):
        return self.product.price * self.quantity


class Address(models.Model):
    session_id = models.CharField(max_length=200, null=True, editable=False)
    user   = models.ForeignKey(User, null=True, editable=False)
    city   = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    house  = models.IntegerField()


class Comment(models.Model):
    user    = models.ForeignKey(User, null=True, editable=False)
    product = models.ForeignKey(Product, editable=False)
    comment = models.TextField()
    rating  = models.IntegerField(default=0, editable=False)
    date    = models.DateField(auto_now_add=True)
    path    = models.CharField(max_length=40, default='', editable=False)
    depth   = models.IntegerField(default=0, editable=False)

    def make_path_and_depth(self, parent_id):
        if Comment.objects.filter(id=parent_id).exists():
            p = Comment.objects.get(id=parent_id)
            self.path = '{0}.{1}'.format(p.path, p.id)
            self.depth = Comment.objects.get(id=parent_id).depth + 1

    def get_responds(self):
        return Comment.objects.filter(path=self.path + '.' + str(self.id)).order_by('date')

    def get_parent_id(self):
        return int(self.path.split('.')[-1]) if self.path else 0


class Mark(models.Model):
    MARK_CHOICES = [(i, i) for i in range(1, 11)]
    mark    = models.IntegerField(choices=MARK_CHOICES)
    product = models.ForeignKey(Product, editable=False)


class Report(models.Model):
    is_completed = models.BooleanField(default=False)


class Vote(models.Model):
    comment = models.ForeignKey(Comment, related_name='votes')
    user    = models.ForeignKey(User, related_name='votes')
    date    = models.DateField(auto_now_add=True)
