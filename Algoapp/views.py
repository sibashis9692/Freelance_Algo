# subscriptions/views.py
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import *
from datetime import datetime, timedelta
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone 
from django.utils.timezone import make_aware
from datetime import timedelta
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib import messages

def home(request):

    # Business Details
    business_data = BusinessDetails.objects.all()

    # Blogs
    blogs = Blog.objects.all()

    # Membership Plans
    plans = list(MembershipPlan.objects.filter())
    


    context = {
        "business_data" : business_data,
        "blogs" : blogs,
        "first_plan" : plans[0],
        "second_plan" : plans[1],
        "thired_plan" : plans[2],
    }


    return render(request, 'index.html', context)


def register(request):
    if request.method == 'POST':
        f_name = request.POST.get('f_name')
        l_name = request.POST.get('l_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken. Please choose a different one.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered. Please use a different email address.')
        else:
            if password == re_password:
                user = User.objects.create_user(username=username, email=email, first_name=f_name, last_name=l_name)
                user.set_password(password)

                user.save()
                
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Passwords and Conform Password do not match.')

    return render(request, 'resgistration.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the user exists in the database

        user = User.objects.filter(username=username).first()
        if(not user):
            messages.error(request, 'Username not Found. Please choose a different one.')
            return redirect('login')
        
        # Check if the password matches
        if check_password(password, user.password):
            login(request, user)  # Log in the user after registration

            return redirect('home')  # Replace 'home' with the URL where you want to redirect after successful login
        else:
            messages.error(request, 'Wrong password')
            return redirect('login')
        
    return render(request, 'loginform.html')  # Default rendering for other cases


def user_logout(request):
    logout(request)
    return redirect('membership_plans')


@login_required(login_url = '/login/')
def active_subscription(request):
    if(request.method == 'GET'):

        existing_membership = UserMembership.objects.filter(user=request.user).first()
        if existing_membership:
            if existing_membership.expiration_date:
                expiration_date_aware = make_aware(datetime.combine(existing_membership.expiration_date, datetime.min.time()))

                print(expiration_date_aware)
                print(timezone.now())
                if expiration_date_aware > timezone.now():

                    return render(request, 'active_subscription.html', {'membership': existing_membership, 'warning': "Subscription Activated"})
                else:

                    messages.error(request, 'User membership with this User is Expired. Choice membership')

                    return redirect("/")

            else:

                return render(request, 'subscribe_error.html', {'error_message': 'Expiration date is missing'})

        return render(request, 'active_subscription.html', {'warning': "You Don't Have any Subscription"})




@login_required(login_url = '/login/')
def subscribe(request):

    if request.method == 'POST':
        subscription_period = request.POST.get('subscription_type')
        plan_name = request.POST.get('plan_name')


        print(subscription_period)
        print(plan_name)

        plan = MembershipPlan.objects.filter(name = plan_name).first()

        if(plan):


            if subscription_period == 'monthly':
                expiration_date = timezone.now() + timezone.timedelta(days=30)
            elif subscription_period == 'quarterly':
                expiration_date = timezone.now() + timezone.timedelta(days=90)
            elif subscription_period == 'yearly':
                expiration_date = timezone.now() + timezone.timedelta(days=365)


            existing_membership = UserMembership.objects.filter(user=request.user).first()
            if existing_membership:
                if existing_membership.expiration_date:
                    expiration_date_aware = make_aware(datetime.combine(existing_membership.expiration_date, datetime.min.time()))

                    print(expiration_date_aware)
                    print(timezone.now())

                    if expiration_date_aware > timezone.now():
                        
                        messages.error(request, 'Alrady You have a membership plan ')

                        return redirect('/active_subscription/')
                    else:
                        
                        # tHIS IS WHEN  subscription is expired

                        existing_membership.membership_plan = plan
                        existing_membership.expiration_date = expiration_date
                        existing_membership.subscription_period = subscription_period

                        print(subscription_period)
                        
                        existing_membership.save()


                        return render(request, 'checkout_success.html')
                else:

                    # This is for when the expirations_date is not valid

                    return render(request, 'subscribe_error.html', {'error_message': 'Expiration date is missing'})
            else:
                # This is for is user member ship is does't exitst then create a new one
                data = UserMembership(user = request.user, membership_plan = plan, expiration_date = expiration_date, subscription_period = subscription_period)
                data.save()

                redirect("/active_subscription/")

    return redirect('/')




def checkout_success(request):
    return render(request, 'checkout_success.html')
  

def newsLetter(request):
    if request.method == 'POST':
        email = request.POST.get("email")

        exists_email = Newsletter_users.objects.filter(email = email).first()
        if(not exists_email):
            data = Newsletter_users(email = email)
            data.save()
            messages.error(request, 'Success Saved Your Email')
            return redirect('/')
        else:
            messages.error(request, 'Your Email is Alrady Stroed')
            return redirect('/')
        

def contactUs(request):
    if(request.method == 'GET'):
        return render(request, 'contact.html') 

    if(request.method == 'POST'):

        f_name = request.POST.get('f_name')
        l_name = request.POST.get('l_name')
        email = request.POST.get('email')
        question = request.POST.get('question')
        phone = request.POST.get('phone')
        w_phone = request.POST.get('w_phone')
        way = request.POST.get('way')

        email_exists = our_clients.objects.filter(email = email).first()
        if(email_exists):
            if(question != email_exists.question):
                data = our_clients(first_name = f_name, last_name = l_name, email = email, phone_number = phone, whatsapp_number = w_phone, question = question, way_to_contact = way)
                data.save()
        else:
            data = our_clients(first_name = f_name, last_name = l_name, email = email, phone_number = phone, whatsapp_number = w_phone, question = question, way_to_contact = way)
            data.save()

    return redirect("/")




def aboutus(request):
    return render(request, 'about.html')

def terms(request):
    return render(request, 'terms_conditions.html')

def privacy(request):
    return render(request, 'privacy.html')

def questions(request):
    return render(request, 'questions.html')




def allblogs(request):

    allblogs = Blog.objects.all()

    context = {
        "blogs" : allblogs
    }

    return render(request, 'allpost.html', context)


def singleblogs(request, id):

    exists_blog = Blog.objects.filter(id = id).first()
    
    if(exists_blog):

        context = {
            "blog" : exists_blog
        }

        return render(request, 'singlepost.html', context)
    return redirect("/allposts/")