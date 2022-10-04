from django.shortcuts import render,redirect
from .models import Contact,User,Design,Inquery,Transaction
from django.conf import settings
from django.core.mail import send_mail
import random
from .paytm import generate_checksum,verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.

def initiate_payment(request,pk):
    user=User.objects.get(email=request.session['email'])
    try:
        amount = int(request.POST['amount'])
    except:
        return render(request, 'payments/pay.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user,amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        #('EMAIL', user.email),
        #('MOBILE_N0', '9549056974'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()
    
    designer=User.objects.get(pk=pk)
    inquery=Inquery.objects.get(sender=user,receiver=designer)
    inquery.payment_status=True
    inquery.save()



    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request,'redirect.html',context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)


def index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=="user":
			return render(request,'index.html')
		else:
			return render(request,'designer_index.html')
	except:
		return render(request,'index.html')

def designer_index(request):
	return render(request,'designer_index.html')	

def about(request):
	return render(request,'about.html')

def contact(request):
	if request.method=="POST":
		Contact.objects.create(
				name=request.POST['name'],
				email=request.POST['email'],
				mobile=request.POST['mobile'],
				message=request.POST['message']
			)
		msg="contact saved"
		return render(request,'contact.html',{'msg':msg})
	else:
		return render(request,'contact.html')

def signup01(request):
	if request.method=="POST":
		try:
			User.objects.get(email=request.POST['email'])
			msg="email is already registered "
			return render(request,'signup01.html',{'msg':msg})
		except:
			email=request.POST['email']
			otp=int(1230)
			subject = 'OTP for forgot password'
			message = 'hello there , your OTP is '+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [email,]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'otp.html',{'otp':otp,'email':email})

	else:
		return render(request,'signup01.html')

def verify_otp(request):
	otp=request.POST['otp']
	uotp=request.POST['uotp']
	email=request.POST['email']
	if otp==uotp:
		return render(request,'signup.html',{'email':email})
	else:
		msg="otp does not match"
		return render(request,'otp.html',{'msg':msg,'otp':otp,'email':email})

def signup(request):
	try:
			User.objects.get(email=request.POST['email'])
			msg="email is already registered "
			return render(request,'signup.html',{'msg':msg,'email':email})
	except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
						usertype=request.POST['usertype'],
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						address=request.POST['address'],
						password=request.POST['password'],
						profile_pic=request.FILES['profile_pic']
					)
				msg="User Signup successful"
				return render(request,'login.html',{'msg':msg})

def login(request):
	if request.method=='POST':
		try:
			user=User.objects.get(
					email=request.POST['email'],
					password=request.POST['password']
				)
			if user.usertype=="user":
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['profile_pic']=user.profile_pic.url
				return render(request,'index.html')
			else:
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['profile_pic']=user.profile_pic.url
				return render(request,'designer_index.html')

		except:
			msg="Email or password is incorrect"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['profile_pic']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			otp=random.randint(1000,9999)
			subject = 'OTP for forgot password'
			message = 'hello '+user.fname+', your OTP is '+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email,]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'otppassword.html',{'otp':otp,'email':user.email})
		except:			
			msg="Email is not registered"
			return render(request,'forgot_password.html',{'msg':msg})
	else:
		return render(request,'forgot_password.html')

def verify_otppassword(request):
	otp=request.POST['otp']
	uotp=request.POST['uotp']
	email=request.POST['email']
	if otp==uotp:
		return render(request,'new_password.html',{'email':email})
	else:
		msg="otp does not match"
		return render(request,'otppassword.html',{'msg':msg,'otp':otp,'email':email})

def new_password(request):
	if request.method=="POST":
		if request.POST['new_password']==request.POST['cnew_password']:
				user=User.objects.get(email=request.POST['email'])	
				user.password=request.POST['new_password']
				user.save()
				msg="password updated successfully"
				return render(request,'login.html',{'msg':msg})
		else:
				msg="new password and conform new password does not match"
				return render(request,'new_password.html',{'msg':msg,'email':request.POST['email']})
	else:
		return render(request,'new_password.html')

def profile(request):
	user=User.objects.get(email=request.session['email'])
	if user.usertype=="user":
		if request.method=="POST":
			user.fname=request.POST['fname']
			user.lname=request.POST['lname']
			user.mobile=request.POST['mobile']
			user.address=request.POST['address']
			try:
				user.profile_pic=request.FILES['profile_pic']
			except:
				pass
			user.save( )
			request.session['profile_pic']=user.profile_pic.url
			return render(request,'profile.html',{'user':user})
		else:
			return render(request,'profile.html',{'user':user})
	else:
		if request.method=="POST":
			user.fname=request.POST['fname']
			user.lname=request.POST['lname']
			user.mobile=request.POST['mobile']
			user.address=request.POST['address']
			try:
				user.profile_pic=request.FILES['profile_pic']
			except:
				pass
			user.save( )
			request.session['profile_pic']=user.profile_pic.url
			return render(request,'designer_profile.html',{'user':user})
		else:
			return render(request,'designer_profile.html',{'user':user})

def change_password(request):
	user=User.objects.get(email=request.session['email'])
	if user.usertype=="user":
		if request.method=="POST":
			if request.POST['new_password']==request.POST['cnew_password']:			
				if request.POST['new_password']==user.password:
					msg="new password and old password are same"
					return render(request,'change_password.html',{'msg':msg})
				else:	
					user.password=request.POST['new_password']
					user.save()
					msg="password updated successfully"
					return redirect('logout')
			else:
					msg="new password and conform new password does not match"
					return render(request,'change_password.html',{'msg':msg})
		else:
			return render(request,'change_password.html')
	else:
		if request.method=="POST":
			if request.POST['new_password']==request.POST['cnew_password']:			
				if request.POST['new_password']==user.password:
					msg="new password and old password are same"
					return render(request,'designer_change_password.html',{'msg':msg})
				else:	
					user.password=request.POST['new_password']
					user.save()
					msg="password updated successfully"
					return redirect('logout')
			else:
					msg="new password and conform new password does not match"
					return render(request,'designer_change_password.html',{'msg':msg})
		else:
			return render(request,'designer_change_password.html')

def your_design_details(request,cat):
	designer=User.objects.get(email=request.session['email'])
	designs=Design.objects.get(designer=designer,design_category=cat)
	return render(request,'your_design_details.html',{'cat':cat,'designs':designs})

def update_design(request,cat):
	designer=User.objects.get(email=request.session['email'])
	designs=Design.objects.get(designer=designer,design_category=cat)
	if request.method=="POST":
		try:
			designs.pic1=request.FILES['pic1']
		except:
			pass
		try:
			designs.pic2=request.FILES['pic2']
		except:
			pass
		try:
			designs.pic3=request.FILES['pic3']
		except:
			pass
		try:
			designs.pic4=request.FILES['pic4']
		except:
			pass
		designs.save( )
		msg="Design Updated successfully"
		return render(request,'your_design_details.html',{'cat':cat,'designs':designs,'msg':msg})		
	else:
		return render(request,'update_design.html',{'designs':designs})

def add_your_designs(request):
	SPACEADAPTATION_flag=False
	RETAILDESIGN_flag=False
	RESIDENTAL_flag=False
	designer=User.objects.get(email=request.session['email'])
	try:			
		Design.objects.get(designer=designer,design_category='RESIDENTAL')
		RESIDENTAL_flag=True
	except:
		pass
	try:			
		Design.objects.get(designer=designer,design_category='RETAILDESIGN')
		RETAILDESIGN_flag=True
	except:
		pass
	try:			
		Design.objects.get(designer=designer,design_category='SPACEADAPTATION')
		SPACEADAPTATION_flag=True
	except:
		pass
	if request.method=="POST":
		

		Design.objects.create(
				designer=designer,
				design_category=request.POST['design_category'],
				pic1=request.FILES['pic1'],
				pic2=request.FILES['pic2'],
				pic3=request.FILES['pic3'],
				pic4=request.FILES['pic4'],
			)
		try:			
			Design.objects.get(designer=designer,design_category='RESIDENTAL')
			RESIDENTAL_flag=True
		except:
			pass
		try:			
			Design.objects.get(designer=designer,design_category='RETAILDESIGN')
			RETAILDESIGN_flag=True
		except:
			pass
		try:			
			Design.objects.get(designer=designer,design_category='SPACEADAPTATION')
			SPACEADAPTATION_flag=True
		except:
			pass
		msg="Designs added successfully"
		return render(request,'add_your_designs.html',{'msg':msg,'SPACEADAPTATION_flag':SPACEADAPTATION_flag,'RETAILDESIGN_flag':RETAILDESIGN_flag,'RESIDENTAL_flag':RESIDENTAL_flag})
	else:
		return render(request,'add_your_designs.html',{'SPACEADAPTATION_flag':SPACEADAPTATION_flag,'RETAILDESIGN_flag':RETAILDESIGN_flag,'RESIDENTAL_flag':RESIDENTAL_flag})

def services(request):
	designers=User.objects.filter(usertype="designer")
	return render(request,'services.html',{'designers':designers})

def design_details(request,cat,pk):
	designer=User.objects.get(pk=pk)
	designs=Design.objects.get(designer=designer,design_category=cat)
	return render(request,'design_details.html',{'cat':cat,'designs':designs,'designer':designer})

def estimate(request,pk):
	designer=User.objects.get(pk=pk)
	return render(request,'estimate.html',{'designer':designer})

def inquery(request,pk):
	designer=User.objects.get(pk=pk)
	sender=User.objects.get(email=request.session['email'])
	

	if request.method=="POST":
		try:
			Inquery.objects.get(sender=sender,receiver=designer)
			msg="inquery already sent"
			return render(request,'inquery.html',{'msg':msg,'designer':designer})
		except:
			Inquery.objects.create(
					sender=sender,
					receiver=designer,
					description=request.POST['description'],		
				)
			msg="inquery has been send"
			return render(request,'payment01.html',{'msg':msg,'designer':designer})
	else:
		return render(request,'inquery.html',{'designer':designer})

def inquery_for_you(request):
	designer=User.objects.get(email=request.session['email'])
	inquery=Inquery.objects.filter(receiver=designer)[::-1]
	return render(request,'inquery_for_you.html',{'inquery':inquery})