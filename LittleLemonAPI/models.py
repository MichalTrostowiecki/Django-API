from django.db import models


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=250)

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title