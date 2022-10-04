from django.db import models
from django.utils import timezone
# Create your models here.

class Contact(models.Model):
	name=models.CharField(max_length=100)
	email=models.EmailField()
	mobile=models.PositiveIntegerField()
	message=models.TextField()

	def __str__(self):
		return self.name

class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.EmailField()
	mobile=models.PositiveIntegerField()
	address=models.TextField()
	password=models.CharField(max_length=100)
	profile_pic=models.ImageField(upload_to="profile_pic/")
	usertype=models.CharField(max_length=100,default="user")

	def __str__(self):
		return self.fname+" "+self.lname

class Design(models.Model):
	CHOICE=(
		('RESIDENTAL','RESIDENTAL'),
		('RETAILDESIGN','RETAILDESIGN'),
		('SPACEADAPTATION','SPACEADAPTATION'),
		)
	designer=models.ForeignKey(User,on_delete=models.CASCADE)
	design_category=models.CharField(max_length=100,choices=CHOICE)
	pic1=models.ImageField(upload_to="pic1/")
	pic2=models.ImageField(upload_to="pic2/")
	pic3=models.ImageField(upload_to="pic3/")
	pic4=models.ImageField(upload_to="pic4/")
	price_set=models.CharField(max_length=100,default="$1000 To $5000")

	def __str__(self):
		return self.designer.fname+" "+self.design_category

class Inquery(models.Model):
	sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name='sender')
	receiver=models.ForeignKey(User,on_delete=models.CASCADE)
	description=models.TextField()
	payment_status=models.BooleanField(default=False)

	def __str__(self):
		return "From "+self.sender.fname+" To "+self.receiver.fname

class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions',on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)
