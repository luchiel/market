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
    def get_address(self):
        return Address.objects.get(user=self)

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


class Basket(models.Model):
    session_id = models.CharField(max_length=200, null=True)
    user       = models.ForeignKey(User, null=True)

    def get_basket_goods(self):
        return Purchased.objects.filter(basket=self).filter(is_sent=False)

    def get_basket_price(self):
        counter = 0
        for product in self.get_basket_goods():
            counter = counter + product.quantity * product.product.price
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
    