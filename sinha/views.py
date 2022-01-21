from django.shortcuts import render ,redirect
from django.http import HttpResponse , HttpResponseRedirect
from .models import Hotels, Rooms, Reservation, Inventory
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime
import razorpay
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import TemplateView, FormView, CreateView, ListView, UpdateView, DeleteView, DetailView, View
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from hotel import settings


from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
# Create your views here.

#homepage
def homepage(request):
    all_location = Hotels.objects.values_list('location','id').distinct().order_by()
    if request.method =="POST":
        try:
            print(request.POST)
            hotel = Hotels.objects.all().get(id=int(request.POST['search_location']))
            rr = []
            print(hotel)
            #for finding the reserved rooms on this time period for excluding from the query set
            for each_reservation in Reservation.objects.all():
                if str(each_reservation.check_in) < str(request.POST['cin']) and str(each_reservation.check_out) < str(request.POST['cout']):
                    pass
                elif str(each_reservation.check_in) > str(request.POST['cin']) and str(each_reservation.check_out) > str(request.POST['cout']):
                    pass
                else:
                    rr.append(each_reservation.room.id)
                
            room = Rooms.objects.all().filter(hotel=hotel,capacity__gte = int(request.POST['capacity'])).exclude(id__in=rr)
            
            if len(room) == 0:
                messages.warning(request,"Sorry No Rooms Are Available on this time period")
           
            data = {'rooms':room,'all_location':all_location,'flag':True, 'cin':request.POST['cin'], 'cout':request.POST['cout']}
            response = render(request, 'index.html', data)
        except Exception as e:
            messages.error(request,e)
            response = render(request, 'index.html', {'all_location':all_location})

    else:
                
        data = {'all_location':all_location}
        response = render(request, 'index.html', data)
    return HttpResponse(response)

#about
def aboutpage(request):
    return HttpResponse(render(request,'about.html'))

#contact page
def contactpage(request):
    return HttpResponse(render(request,'contact.html'))

#user sign up
def user_sign_up(request):
    if request.method =="POST":
        user_name = request.POST['username']
        
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.warning(request,"Password didn't matched")
            return redirect('userloginpage')
        
        try:
            if User.objects.all().get(username=user_name):
                messages.warning(request,"Username Not Available")
                return redirect('userloginpage')
        except:
            pass
            

        new_user = User.objects.create_user(username=user_name,password=password1)
        new_user.is_superuser=False
        new_user.is_staff=False
        new_user.save()
        messages.success(request,"Registration Successfull")
        return redirect("userloginpage")
    return HttpResponse('Access Denied')
#staff sign up
def staff_sign_up(request):
    if request.method =="POST":
        user_name = request.POST['username']
        
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.success(request,"Password didn't Matched")
            return redirect('staffloginpage')
        try:
            if User.objects.all().get(username=user_name):
                messages.warning(request,"Username Already Exist")
                return redirect("staffloginpage")
        except:
            pass
        
        new_user = User.objects.create_user(username=user_name,password=password1)
        new_user.is_superuser=False
        new_user.is_staff=True
        new_user.save()
        messages.success(request," Staff Registration Successfull")
        return redirect("staffloginpage")
    else:

        return HttpResponse('Access Denied')
        
#user login and signup page
def user_log_sign_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['pswd']

        user = authenticate(username=email,password=password)
        try:
            if user.is_staff:
                
                messages.error(request,"Incorrect username or Password")
                return redirect('staffloginpage')
        except:
            pass
        
        if user is not None:
            login(request,user)
            messages.success(request,"successful logged in")
            print("Login successfull")
            return redirect('homepage')
        else:
            messages.warning(request,"Incorrect username or password")
            return redirect('userloginpage')

    response = render(request,'user/userlogsign.html')
    return HttpResponse(response)

#logout for admin and user 
def logoutuser(request):
    if request.method =='GET':
        logout(request)
        messages.success(request,"Logged out successfully")
        print("Logged out successfully")
        return redirect('homepage')
    else:
        print("logout unsuccessfull")
        return redirect('userloginpage')

#staff login and signup page
def staff_log_sign_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username,password=password)
        
        if user.is_staff:
            login(request,user)
            return redirect('staffpanel')
        
        else:
            messages.success(request,"Incorrect username or password")
            return redirect('staffloginpage')
    response = render(request,'staff/stafflogsign.html')
    return HttpResponse(response)

#staff panel page
@login_required(login_url='/staff')
def panel(request):
    
    if request.user.is_staff == False:
        return HttpResponse('Access Denied')
    
    rooms = Rooms.objects.all()
    total_rooms = len(rooms)
    available_rooms = len(Rooms.objects.all().filter(status='1'))
    unavailable_rooms = len(Rooms.objects.all().filter(status='2'))
    reserved = len(Reservation.objects.all())

    hotel = Hotels.objects.values_list('id').distinct().order_by()

    response = render(request,'staff/panel.html',{'location':hotel,'reserved':reserved,'rooms':rooms,'total_rooms':total_rooms,'available':available_rooms,'unavailable':unavailable_rooms})
    return HttpResponse(response)

#for editing room information
@login_required(login_url='/staff')
def edit_room(request):
    if request.user.is_staff == False:   
        return HttpResponse('Access Denied')

    if request.method == 'POST' and request.user.is_staff:

        old_room = Rooms.objects.all().get(id= int(request.POST['roomid']))
        hotel = Hotels.objects.all()[0]

        old_room.room_type  = request.POST['roomtype']
        old_room.capacity   =int(request.POST['capacity'])
        old_room.price      = int(request.POST['price'])
        old_room.size       = int(request.POST['size'])
        old_room.hotel      = hotel
        old_room.status     = request.POST['status']
        old_room.room_number=int(request.POST['roomnumber'])

        old_room.save()
        messages.success(request,"Room Details Updated Successfully")
        return redirect('staffpanel')

    else:
        room_id = request.GET['roomid']
        room = Rooms.objects.all().get(id=room_id)
        response = render(request,'staff/editroom.html',{'room':room})
        return HttpResponse(response)

#for adding room
@login_required(login_url='/staff')
def add_new_room(request):
    if request.user.is_staff == False:
        return HttpResponse('Access Denied')
    if request.method == "POST":
        total_rooms = len(Rooms.objects.all())

        new_room = Rooms()
        hotel = Hotels.objects.all()[0]

        new_room.roomnumber = total_rooms + 1
        new_room.room_type  = request.POST['roomtype']
        new_room.capacity   = int(request.POST['capacity'])
        new_room.size       = int(request.POST['size'])
        new_room.capacity   = int(request.POST['capacity'])
        new_room.hotel      = hotel
        new_room.status     = request.POST['status']
        new_room.price      = request.POST['price']

        new_room.save()
        messages.success(request,"New Room Added Successfully")
    
    return redirect('staffpanel')

#booking room page
@login_required(login_url='/user')
def book_room_page(request, roomid, cin, cout):
    room = Rooms.objects.all().get(id=roomid)
    return HttpResponse(render(request,'user/bookroom.html', {'room':room, "cin":cin, "cout":cout}))

#For booking the room
client = razorpay.Client(auth=("rzp_live_9jdC23irGeM39j", "SV7ldKVM0aKUAuQeGcYU8bH8"))
@login_required(login_url='/user')
def book_room(request):
    print('hello')
    
    if request.method == "POST":

        room_id = request.POST['room_id']
        total_person = int( request.POST['person'])
        
        room = Rooms.objects.all().get(id=room_id)
        #for finding the reserved rooms on this time period for excluding from the query set

        for each_reservation in Reservation.objects.all().filter(room = room):
            if str(each_reservation.check_in) < str(request.POST['check_in']) and str(each_reservation.check_out) < str(request.POST['check_out']):
                pass
            elif str(each_reservation.check_in) > str(request.POST['check_in']) and str(each_reservation.check_out) > str(request.POST['check_out']):
                pass
            else:
                messages.warning(request,"Sorry This Room is unavailable for Booking")
                return redirect("homepage")
        #getting current user    
        current_user = request.user        
        
        user_object = User.objects.all().get(username=current_user)
        room_object = Rooms.objects.all().get(id=room_id)
       
        booking_id = str(room_id) + str(datetime.datetime.now())

        #registering rooom
        reservation = Reservation()
        reservation.guest = user_object
        reservation.room = room_object
        reservation.check_in = request.POST['check_in']
        reservation.check_out = request.POST['check_out']
        reservation.total_amount = room.price
        reservation.booking_id = booking_id

        room_object.status = '2'
        
        person = total_person

        callback_url = 'http://'+ str(get_current_site(request))+"/handlerequest/"

        amount = room.price*100
        
        payment = client.order.create({'amount': amount, 'currency': 'INR', 'receipt':booking_id, 'payment_capture': '0'})
        print(payment['id'])
        reservation.razorpay_order_id = payment['id']
        reservation.save()
        # messages.success(request, f"Congratulations! Booking Successfull")
        # return HttpResponse('Done!')

        return HttpResponse(render(request, 'payment/paymentsummaryrazorpay.html', {'reservation':reservation, 'order_id': payment['id'], 'orderId':reservation.booking_id, 'final_price':amount, 'paymentId':booking_id, 'razorpay_merchant_id':settings.razorpay_id, 'callback_url':callback_url} ))
    else:
        return HttpResponse('Access Denied')

def payment(request):
    pass

def fetch_resources(uri, rel):
    path = os.path.join(uri.replace(settings.STATIC_URL, ""))
    return path

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None



from django.core.mail import EmailMultiAlternatives
@csrf_exempt
def handlerequest(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            params_dict = { 
            'razorpay_order_id': order_id, 
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
            }
            try:
                order_db = Reservation.objects.get(razorpay_order_id=order_id)
            except:
                return HttpResponse("505 Not Found")
            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature_id = signature
            order_db.save()
            result = client.utility.verify_payment_signature(params_dict)
            if result==None:
                amount = int(order_db.total_amount) * 100   #we have to pass in paisa
                try:
                    client.payment.capture(payment_id, amount)
                    order_db.payment_status = 2
                    order_db.save()

                    ## For generating Invoice PDF
                    template = get_template('payment/invoice.html')
                    data = {
                        'order_id': order_db.booking_id,
                        'transaction_id': order_db.razorpay_payment_id,
                        'user_email': 'jatin.kshatriya2821@gmail.com',
                        'date': str(order_db.date_time_of_payment),
                        'name': order_db.guest.username,
                        'order': order_db,
                        'amount': order_db.total_amount,
                    }
                    html  = template.render(data)
                    result = BytesIO()
                    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
                    pdf = result.getvalue()
                    filename = 'Invoice_' + data['order_id'] + '.pdf'

                    mail_subject = 'Recent Order Details'
                    # message = render_to_string('firstapp/payment/emailinvoice.html', {
                    #     'user': order_db.user,
                    #     'order': order_db
                    # })
                    context_dict = {
                        'user': order_db.guest.username,
                        'order': order_db
                    }
                    template = get_template('payment/emailinvoice.html')
                    message  = template.render(context_dict)
                    to_email = 'jatin.kshatriya2821@gmail.com'
                    # email = EmailMessage(
                    #     mail_subject,
                    #     message, 
                    #     settings.EMAIL_HOST_USER,
                    #     [to_email]
                    # )

                    # for including css(only inline css works) in mail and remove autoescape off
                    email = EmailMultiAlternatives(
                        mail_subject,
                        "hello",       # necessary to pass some message here
                        settings.EMAIL_HOST_USER,
                        [to_email]
                    )
                    email.attach_alternative(message, "text/html")
                    email.attach(filename, pdf, 'application/pdf')
                    email.send(fail_silently=False)

                    return render(request, 'payment/paymentsuccess.html',{'id':order_db.id})
                except:
                    order_db.payment_status = 1
                    order_db.save()
                    print('here')
                    return render(request, 'payment/paymentfailed.html')
            else:
                order_db.payment_status = 1
                order_db.save()
                return render(request, 'payment/paymentfailed.html')
        except:
            return HttpResponse("505 not found")
    else:
        return HttpResponse("Access denied!")

class GenerateInvoice(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            order_db = Order.objects.get(id = pk, user = request.user, payment_status = 1)     #you can filter using order_id as well
        except:
            return HttpResponse("505 Not Found")
            print(order_db)
        data = {
            'order_id': order_db.order_id,
            'transaction_id': order_db.razorpay_payment_id,
            'user_email': order_db.user.email,
            'date': str(order_db.datetime_of_payment),
            'name': order_db.user.name,
            'order': order_db,
            'amount': order_db.total_amount,
        }
        pdf = render_to_pdf('payment/invoice.html', data)
        #return HttpResponse(pdf, content_type='application/pdf')

        # force download
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" %(data['order_id'])
            content = "inline; filename='%s'" %(filename)
            #download = request.GET.get("download")
            #if download:
            content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

#terms page
def term(request):
    return HttpResponse(render(request,'terms.html')) 

def handler404(request):
    return render(request, '404.html', status=404)

@login_required(login_url='/staff')   
def view_room(request):
    room_id = request.GET['roomid']
    room = Rooms.objects.all().get(id=room_id)

    reservation = Reservation.objects.all().filter(room=room)
    return HttpResponse(render(request,'staff/viewroom.html',{'room':room,'reservations':reservation}))

@login_required(login_url='/user')
def user_bookings(request):
    if request.user.is_authenticated == False:
        return redirect('userloginpage')
    user = User.objects.all().get(id=request.user.id)
    print(f"request user id ={request.user.id}")
    bookings = Reservation.objects.all().filter(guest=user)
    if not bookings:
        messages.warning(request,"No Bookings Found")
    return HttpResponse(render(request,'user/mybookings.html',{'bookings':bookings}))

@login_required(login_url='/staff')
def add_new_location(request):
    if request.method == "POST" and request.user.is_staff:
        owner = request.POST['new_owner']
        location = request.POST['new_city']
        state = request.POST['new_state']
        country = request.POST['new_country']
        
        hotels = Hotels.objects.all().filter(location = location , state = state)
        if hotels:
            messages.warning(request,"Sorry City at this Location already exist")
            return redirect("staffpanel")
        else:
            new_hotel = Hotels()
            new_hotel.owner = owner
            new_hotel.location = location
            new_hotel.state = state
            new_hotel.country = country
            new_hotel.save()
            messages.success(request,"New Location Has been Added Successfully")
            return redirect("staffpanel")

    else:
        return HttpResponse("Not Allowed")
    
#for showing all bookings to staff
@login_required(login_url='/staff')
def all_bookings(request):
   
    bookings = Reservation.objects.all()
    if not bookings:
        messages.warning(request,"No Bookings Found")
    return HttpResponse(render(request,'staff/allbookings.html',{'bookings':bookings}))
 
 #for Inventory page of staf    
@login_required(login_url='/staff')
def inventory(request):
    all_items = Inventory.objects.all()
    # Inventory.objects.all().delete()
    return render(request, 'staff/inventory.html', {'items' : all_items})

#for adding an item to inventory
@login_required(login_url='/staff')
def add_new_item(request):
    if request.user.is_staff == False:
        return HttpResponse('Access Denied')
    if request.method == "POST":
        total_item = len(Inventory.objects.all())

        new_item = Inventory()
        new_item.item_id=total_item+1
        new_item.item_name           = request.POST['name']
        new_item.item_total          = int(request.POST['total'])
        new_item.item_available      = int(request.POST['available'])
        new_item.item_not_available  = int(request.POST['total']) - int(request.POST['available'])
        
        new_item.save()
        messages.success(request,"New Item Added Successfully")
    
    return redirect('inventory')

#for editing items in inventory
@login_required(login_url='/staff')
def edit_item(request, id):
    print(id)
    if request.user.is_staff == False:   
        return HttpResponse('Access Denied')

    if request.method == 'POST' and request.user.is_staff:
        old_item = Inventory.objects.all().get(id = int(id))

        if int(request.POST['total']) == 0:
            old_item.delete()
        else:
            if request.POST['name']:
                old_item.item_name = request.POST['name']
            
            if request.POST['total']:
                old_item.item_total = int(request.POST['total'])
            
            if request.POST['available']:
                old_item.item_available = int(request.POST['available'])
            
            if request.POST['total'] and request.POST['available']:
                old_item.item_not_available  = int(request.POST['total']) - int(request.POST['available'])
            
            if request.POST['total']:
                old_item.item_not_available  = int(request.POST['total']) - old_item.item_available
            
            if request.POST['available']:
                old_item.item_not_available  = old_item.item_total - int(request.POST['available'])

            old_item.save()
            messages.success(request, "Item Details Updated Successfully")
        return redirect('/staff/inventory')
    else:
        return HttpResponse("Error 404")
  


        
