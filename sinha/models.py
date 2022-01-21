from django.db import models
from django.contrib.auth.models import User
import datetime
# Create your models here.
class Hotels(models.Model):
    #h_id,h_name,owner ,location,rooms
    name = models.CharField(max_length=30,default="sinha")
    owner = models.CharField(max_length=20)
    location = models.CharField(max_length=50, default="chhindwara")
    state = models.CharField(max_length=50,default="madhya pradesh")
    country = models.CharField(max_length=50,default="india")
    def __str__(self):
        return self.name


class Rooms(models.Model):
    ROOM_STATUS = ( 
    ("1", "available"), 
    ("2", "not available"),    
    ) 

    ROOM_TYPE = ( 
    ("1", "premium"), 
    ("2", "deluxe"),
    ("3","basic"),    
    ) 

    #type,no_of_rooms,capacity,prices,Hotel
    room_type = models.CharField(max_length=50,choices = ROOM_TYPE)
    capacity = models.IntegerField()
    price = models.IntegerField()
    size = models.IntegerField()
    hotel = models.ForeignKey(Hotels, on_delete = models.CASCADE)
    status = models.CharField(choices =ROOM_STATUS,max_length = 15)
    roomnumber = models.IntegerField()
    def __str__(self):
        return self.hotel.name

class Reservation(models.Model):

    PAYMENT__STATUS = ( 
    ("1", "PENDING"),
    ("2", "SUCCESS"), 
    )

    check_in = models.DateField(auto_now =False)
    check_out = models.DateField()
   
    room = models.ForeignKey(Rooms, on_delete = models.CASCADE)
    guest = models.ForeignKey(User, on_delete= models.CASCADE)
   
    total_amount = models.CharField(max_length=100, null=True, blank=True, verbose_name="total amount")
    payment_status = models.CharField(max_length=10, choices=PAYMENT__STATUS,default=None, null=True, blank=False, verbose_name="payment sucess")
    date_time_of_payment = models.DateTimeField(default=datetime.datetime.now(), null=True, blank=True, verbose_name="date time of payment")
   
    razorpay_order_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="Razorpay order id")
    razorpay_payment_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="Razorpay payment id")
    razorpay_signature_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="Razorpay signature")

    booking_id = models.CharField(max_length=100,default="null")
    def __str__(self):
        return self.guest.username


class Inventory(models.Model):

    item_id=models.IntegerField()
    item_name = models.CharField(max_length=50)
    item_total = models.IntegerField()
    item_available = models.IntegerField()
    item_not_available = models.IntegerField()
    
    def __str__(self):
        return self.item_name

