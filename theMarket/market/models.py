from django.db import models
from hashlib import sha1

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

class Category(models.Model):
    depth  = models.IntegerField()
    parent = models.ForeignKey('self')
    path   = models.CharField(max_length=40)
    name   = models.CharField(max_length=200)

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
        #self.parent_id = parent_id
        self.parent = Category.objects.get(id=parent_id)
        #parent = Category.objects.get(id=parent_id)
        self.path = self.parent.path + '.' + str(self.id)
        self.depth = self.parent.depth + 1

    def get_products(self):
        return Product.objects.filter(category=self.id)

class Product(models.Model):
    name     = models.CharField(max_length=200)
    category = models.ForeignKey(Category)
