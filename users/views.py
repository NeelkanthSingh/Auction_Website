from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.models import User
import razorpay
from .models import Pay,Profile
from django.views.decorators.csrf import csrf_exempt

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)

@login_required
def payment(request):
    return render(request, 'users/payment.html')

@login_required
def payment_index(request):
    if request.method == "POST":
        name = request.POST.get("name")
        amount = int(request.POST.get("amount"))*100
        client = razorpay.Client(auth=("rzp_test_SJHZ4NwBecih2i","4q5nyPlUeUUMIyXCmP2Swpr2"))
        payment_=client.order.create({'amount':amount, 'currency':'INR', 'payment_capture':'1'})
        pay = Pay(name = name, amount = amount//100, payment_id = payment_['id'], author = request.user)
        pay.save()
        return render(request, "users/payment_index.html", {'payment_' : payment_})
    return render(request, 'users/payment_index.html')

@login_required
@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        a = request.POST
        order_id = ""
        data = {}
        for key, val in a.items():
            if key == 'razorpay_order_id':
                data['razorpay_order_id'] = val
                order_id = val
            elif key == 'razorpay_payment_id':
                data['razorpay_payment_id'] = val
            elif key == 'razorpay_signature':
                data['razorpay_signature'] = val
        user = Pay.objects.filter(payment_id=order_id).first()
        entry = Pay.objects.get(payment_id=order_id)
        dentry = Profile.objects.get(user = entry.author)
        client = razorpay.Client(auth=("rzp_test_SJHZ4NwBecih2i","4q5nyPlUeUUMIyXCmP2Swpr2"))
        check = client.utility.verify_payment_signature(data)
        if not check:
            user.paid = True
            user.save()
            dentry.purchased = True
            dentry.save()
            return redirect('blog-home')
        user.paid = True
        user.save()
        dentry.purchased = True
        dentry.save()
    return redirect('bolg-home')