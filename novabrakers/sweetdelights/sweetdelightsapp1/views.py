from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.shortcuts import *
from .models import *
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import re
import razorpay
from django.contrib.admin.views.decorators import staff_member_required
from decimal import Decimal, InvalidOperation
from django.utils.timezone import now
from django.urls import reverse
from django.core.files.base import ContentFile
import base64
from django.db.models import F
from django.http import JsonResponse
from datetime import datetime
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import json
from django.core.files.storage import FileSystemStorage
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
import uuid
from django.core.paginator import Paginator
from django.template.loader import get_template
import pdfkit
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from .forms import *  # ✅ Ensure you have a ReviewForm
from django.utils.timezone import now
from django.conf import settings

# Create your views here.
# -------------------------------------------------------------------------------------------USER AUTHENTICATION
def registration(request):
    if request.method == 'POST':
        first_name = request.POST.get('username')
        dob_date = request.POST.get('dob')
        email_id = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        contact_no = request.POST.get('mobile')
        address = request.POST.get('address_details')

        
        if User.objects.filter(email_id=email_id).exists():  
            messages.error(request, "This email is already registered. Please log in.")
            return redirect('registration')  

        
        error_messages = []
        is_valid = True

        if not first_name:
            is_valid = False
            error_messages.append("Full Name is required.")

        if not email_id or '@' not in email_id or '.' not in email_id:
            is_valid = False
            error_messages.append("Enter a valid email address.")

        if password != confirm_password:
            is_valid = False
            error_messages.append("Passwords do not match.")
        elif len(password) < 8:
            is_valid = False
            error_messages.append("Password must be at least 8 characters long.")
        elif not re.match(r'^[A-Za-z0-9]*$', password):
            is_valid = False
            error_messages.append("Password must contain at least one letter and one number.")
        elif not re.search(r'[A-Z]', password):
            is_valid = False
            error_messages.append("Password must contain at least one uppercase letter.")
        elif re.search(r'[^\w]', password):
            is_valid = False
            error_messages.append("Password must not contain special characters.")

        if len(contact_no) != 10 or not contact_no.isdigit():
            is_valid = False
            error_messages.append("Enter a valid 10-digit mobile number.")

        if not dob_date:
            is_valid = False
            error_messages.append("Date of Birth is required.")
        else:
            today = datetime.today()
            dob = datetime.strptime(dob_date, '%Y-%m-%d')
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 16:
                is_valid = False
                error_messages.append("You must be at least 16 years old to register.")

        if not address:
            is_valid = False
            error_messages.append("Address is required.")

        if is_valid:
            # Generate and send OTP
            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp  # Store OTP in session
            request.session['temp_user'] = {
                'first_name': first_name,
                'dob_date': dob_date,
                'email_id': email_id,
                'password': password,
                'contact_no': contact_no,
                'address': address
            }

            send_mail(
                'Welcome! Verify Your Registration',
                f'Hello,\n\nThank you for signing up! To complete your registration, please use the following One-Time Password (OTP):\n\n🔑 {otp}\n\nThis OTP is valid for 10 minutes. Please do not share it with anyone.\n\nBest regards,\nNova Bakers',
                'trupalgorasiya510.com',  
                [email_id],
                fail_silently=False,
            )

            messages.success(request, "OTP sent to your email. Please verify.")
            return redirect('registrationverify')  # Redirect to OTP verification page

        else:
            for message in error_messages:
                messages.error(request, message)

    return render(request, 'Registration.html')


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('otp')

        if not entered_otp:
            messages.error(request, "OTP is required.")
            return redirect('registrationverify') 

        if len(entered_otp) != 6 or not entered_otp.isdigit():
            messages.error(request, "OTP must be a 6-digit number.")
            return redirect('registrationverify')  

        if entered_otp == saved_otp:
            temp_user = request.session.get('temp_user')

            if temp_user:
                user = User(
                    first_name=temp_user['first_name'],
                    dob_date=temp_user['dob_date'],
                    email_id=temp_user['email_id'],
                    password=temp_user['password'],  # Secure password in production
                    contact_no=temp_user['contact_no'],
                    address=temp_user['address']
                )
                user.save()

                del request.session['otp']
                del request.session['temp_user']

                messages.success(request, "OTP verified successfully! Registration completed.")
                return redirect('Login')  

        messages.error(request, "Invalid OTP. Please try again.")  # Error message if OTP is incorrect
        return redirect('registrationverify')

    return render(request, 'registrationverify.html')

def Login(request):
    if request.method == "POST":
        email = request.POST.get('email_id')  # Get email from form
        password = request.POST.get('password')  # Get password from form

        try:
            user = User.objects.filter(email_id=email).first()  # Fetch user by email
            if user:
                
                if check_password(password, user.password):
                    
                    request.session['user_id'] = user.user_id  # Save user ID in session
                    messages.success(request, f"Welcome, {user.first_name}!")
                    return redirect('Homepage') 
                else:
                    messages.error(request, "Invalid email OR password.")
            else:
                messages.error(request, "User with this email does not exist.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, "Login.html")  

def Logout(request):
    # Clear the session to log out the user
    request.session.flush()  
    return redirect('Login')  

def change_password(request):
    # Get user_id from session
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "You must be logged in to change your password.")
        return redirect('Login')  # Redirect if user_id is missing

    # Fetch the user from the database
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('Login')

    if request.method == 'POST':
        current_password = request.POST.get('current-password')
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')

        # Check if the current password is correct
        if not check_password(current_password, user.password):
            messages.error(request, "Current password is incorrect.")
            return render(request, 'Changepassword.html')

        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, 'Changepassword.html')

        # ✅ Validate password strength using regex
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'Changepassword.html')

        if not re.search(r'[A-Za-z]', new_password):  # Check at least one letter
            messages.error(request, "Password must contain at least one letter.")
            return render(request, 'Changepassword.html')

        if not re.search(r'[0-9]', new_password):  # Check at least one number
            messages.error(request, "Password must contain at least one number.")
            return render(request, 'Changepassword.html')

        if not re.search(r'[A-Z]', new_password):  # Check at least one uppercase letter
            messages.error(request, "Password must contain at least one uppercase letter.")
            return render(request, 'Changepassword.html')

        if re.search(r'[^A-Za-z0-9]', new_password):  # Check special characters
            messages.error(request, "Password must not contain special characters.")
            return render(request, 'Changepassword.html')

        # Update and hash the new password
        user.password = make_password(new_password)
        user.save()

        # Logout the user after changing password
        logout(request)  # Fix: Changed 'Logout' to 'logout'
        messages.success(request, "Password successfully updated. Please log in again.")
        return redirect('Login')

    return render(request, 'Changepassword.html')

def Forgotpassword(request):
    if request.method == "POST":
        email = request.POST.get("email")

        # Check if email exists in the database
        user = User.objects.filter(email_id=email).first()
        if not user:
            messages.error(request, "Email not found!")
            return redirect("Forgotpassword")

        # Generate OTP
        otp = str(random.randint(100000, 999999))
       
        # Store OTP in session (or in DB if needed)
        request.session["reset_email"] = email
        request.session["otp"] = otp
        
        # Send OTP to email
        send_mail(
        "Reset Your Password Securely",
        f"Hello,\n\nWe've received a request to reset your password. Your One-Time Password (OTP) is: {otp}\n\nPlease use this OTP within 2 minutes to proceed. Do not share it with anyone.\n\nIf you didn't request this, you can ignore this email.\n\nBest regards,\nNova Bakers",
        "trupalgorasiya510@gmail.com",
        [email],
        fail_silently=False,
        )

        messages.success(request, "OTP Send on your email. please verify!")
        return redirect("Verifyotp")  # Redirect to OTP verification page

    return render(request, "Forgotpassword.html")

def Verifyotp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")  # Get OTP from user input
        stored_otp = request.session.get("otp")  # Get OTP from session

        # Validation: OTP must be exactly 6 digits
        if not entered_otp or not entered_otp.isdigit() or len(entered_otp) != 6:
            messages.error(request, "OTP must be a 6-digit number.")
            return render(request, "Verifyotp.html")

        # Check if OTP exists in session
        if not stored_otp:
            messages.error(request, "Session expired! Please request a new OTP.")
            return redirect("Forgotpassword")  # Redirect to re-enter email for OTP

        # Compare entered OTP with stored OTP
        if entered_otp == stored_otp:
            request.session["otp_verified"] = True  # Store verification flag
            del request.session["otp"]  # Remove OTP from session for security
            messages.success(request, "OTP verified successfully!")
            return redirect("Forgotpasswordupdate")  # Redirect to password reset page
        else:
            messages.error(request, "Invalid OTP! Please try again.")

    return render(request, "Verifyotp.html")

def Forgotpasswordupdate(request):
    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("Forgotpasswordupdate")

        # Get user email from session
        email = request.session.get("reset_email")
        user = User.objects.filter(email_id=email).first()

        if not user:
            messages.error(request, "User not found!")
            return redirect("ForgotPassword")

        # Update password (hashed)
        user.password = make_password(new_password)
        user.save()

        # Clear session
        request.session.pop("reset_email", None)
        request.session.pop("otp", None)

        messages.success(request, "Password updated successfully! Please log in.")
        return redirect("Login")

    return render(request, "Forgotpasswordupdate.html")

def UserDetails(request):
    # Get the user_id from the session to check if the user is logged in
    user_id = request.session.get('user_id')

    if user_id:
        try:
            # Fetch the user based on user_id
            user = User.objects.get(user_id=user_id)  
            # Pass the user details to the template
            return render(request, 'UserDetails.html', {'user': user})
        except User.DoesNotExist:
            # Handle case if user does not exist
            messages.error(request, "User not found.")
            return redirect('Login')  # Redirect to login page if user is not found
    else:
        # If the user is not logged in, redirect to login page
        messages.error(request, "You must log in to view your details.")
        return redirect('Login')  # Redirect to login page

def UserDetailsUpdate(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "You need to log in first!")
        return redirect("Login")  # Redirect to login if session is missing

    user = User.objects.filter(user_id=user_id).first()
    if not user:
        messages.error(request, "User not found!")
        return redirect("Login")

    if request.method == "POST":
        # Get user input
        first_name = request.POST.get("fullName", "").strip()
        email_id = request.POST.get("email", "").strip()
        contact_no = request.POST.get("mobile", "").strip()
        dob_date = request.POST.get("dob_date", "").strip()
        address = request.POST.get("address", "").strip()

        # Validation
        is_valid = True
        error_messages = []

        # 1. Full Name Validation
        if not first_name:
            is_valid = False
            error_messages.append("Full Name is required.")

        # 2. Email Validation (Ensure it contains '@' and '.')
        if not email_id or '@' not in email_id or '.' not in email_id:
            is_valid = False
            error_messages.append("Enter a valid email address.")

        # 3. Mobile Number Validation (Must be 10 digits)
        if len(contact_no) != 10 or not contact_no.isdigit():
            is_valid = False
            error_messages.append("Enter a valid 10-digit mobile number.")

        # 4. Date of Birth Validation (Ensure user is 16+ years old)
        if not dob_date:
            is_valid = False
            error_messages.append("Date of Birth is required.")
        else:
            today = datetime.today()
            try:
                dob = datetime.strptime(dob_date, "%Y-%m-%d").date()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                if age < 16:
                    is_valid = False
                    error_messages.append("You must be at least 16 years old to register.")
            except ValueError:
                is_valid = False
                error_messages.append("Invalid date format. Please select a valid date.")

        # 5. Address Validation
        if not address:
            is_valid = False
            error_messages.append("Address is required.")

        # If validation fails, show errors and stay on the same page
        if not is_valid:
            for error in error_messages:
                messages.error(request, error)
            return render(request, "UserDetailsUpdate.html", {"user": user})

        # Update user details
        user.first_name = first_name
        user.email_id = email_id
        user.contact_no = contact_no
        user.dob_date = dob
        user.address = address

        user.save()
        messages.success(request, "Information updated successfully!")

        # Redirect to UserDetails.html after successful update
        return redirect("UserDetails")

    return render(request, "UserDetailsUpdate.html", {"user": user})

#--------------------------------------------------------------------------------------------------- PRODUCTS

def Cakes(request):
    # Get the "Cakes" main category
    cakes_category = get_object_or_404(MainCategory, name="Cakes")

    # Get only subcategories related to "Cakes"
    subcategories = SubCategory.objects.filter(main_category=cakes_category)

    # Get products categorized under those subcategories
    products_by_subcategory = {}
    for subcategory in subcategories:
        products_by_subcategory[subcategory.id] = Product.objects.filter(subcategory=subcategory)

    return render(request, 'Cakes.html', {
        'cakes_category': cakes_category,
        'subcategories': subcategories,
        'products_by_subcategory': products_by_subcategory,
    })

def cakes_by_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    products = Product.objects.filter(subcategory=subcategory)

    return render(request, 'Cakes.html', {
        'selected_subcategory': subcategory,  # Pass selected subcategory to hide list
        'products': products,  # Only show related products
    })

def Pastries(request):
    main_category = MainCategory.objects.get(name='Pastries')
    subcategories = SubCategory.objects.filter(main_category=main_category)
    products = Product.objects.filter(main_category=main_category)  # Fetch products for the 'Breads' category
    for product in products:
        product.price_options = [option.strip() for option in product.price_options]
    return render(request, 'Pastries.html', {'subcategories': subcategories,'products': products})

def Cookies(request):
    main_category = MainCategory.objects.get(name='Cookies')
    subcategories = SubCategory.objects.filter(main_category=main_category)
    products = Product.objects.filter(main_category=main_category)

    # Ensure product.price_options is cleaned
    for product in products:
        product.price_options = [option.strip() for option in product.price_options]

    return render(request, 'Cookies.html', {'subcategories': subcategories, 'products': products})

def Donuts(request):
    main_category = MainCategory.objects.get(name='Donuts')
    subcategories = SubCategory.objects.filter(main_category=main_category)
    products = Product.objects.filter(main_category=main_category)  # Fetch products for the 'Breads' category
    for product in products:
        product.price_options = [option.strip() for option in product.price_options]


    return render(request, 'Donuts.html', {'subcategories': subcategories,'products': products})

def Cupcakes(request):
    main_category = MainCategory.objects.get(name='Cupcakes')
    subcategories = SubCategory.objects.filter(main_category=main_category)
    products = Product.objects.filter(main_category=main_category)  # Fetch products for the 'Breads' category
    for product in products:
        product.price_options = [option.strip() for option in product.price_options]


    return render(request, 'Cupcakes.html', {'subcategories': subcategories,'products': products})

def Waffles(request):
    main_category = MainCategory.objects.get(name='Waffles')
    subcategories = SubCategory.objects.filter(main_category=main_category)
    products = Product.objects.filter(main_category=main_category)  # Fetch products for the 'Breads' category
    for product in products:
        product.price_options = [option.strip() for option in product.price_options]


    return render(request, 'Waffles.html', {'subcategories': subcategories,'products': products})


def Breads(request):
    main_category = MainCategory.objects.get(name='Breads')
    subcategories = SubCategory.objects.filter(main_category=main_category)
    products = Product.objects.filter(main_category=main_category)  # Fetch products for the 'Breads' category
    for product in products:
        product.price_options = [option.strip() for option in product.price_options]


    return render(request, 'Breads.html', {'subcategories': subcategories,'products': products})

def Others(request):
    # Get the "Others" main category
    main_category = get_object_or_404(MainCategory, name="Others")

    # Get all subcategories under "Others"
    subcategories = SubCategory.objects.filter(main_category=main_category)

    # Get products grouped by subcategory
    subcategory_products = {subcategory: Product.objects.filter(subcategory=subcategory) for subcategory in subcategories}

    return render(request, 'others.html', {
        'main_category': main_category,
        'subcategories': subcategories,
        'subcategory_products': subcategory_products
    })

#--------------------------------------------------------------------------------------------------- DISPLAY PAGES
def Homepage(request):
    categories = MainCategory.objects.all()  # Fetch all categories
    return render(request, "Homepage.html", {"categories": categories})

def PartipationForm(request):
    return render(request,"PartipationForm.html")

def PartyProps(request):
    return render(request,"PartyProps.html")

def FAQ(request):
    return render(request,"FAQ.html")

def Gallery(request):
    return render(request,"Gallery.html")

def Ourservices(request):
    return render(request,"Ourservices.html")

def about(request):
    return render(request, 'about.html')

#------------------------------------------------------------------------------------ ADD TO CART 
def clean_price(price_option):
    # Remove non-numeric characters, except the comma and decimal point
    cleaned_price = re.sub(r'[^0-9.,]', '', price_option)
    
    # Check if the cleaned price is a valid number
    try:
        # Handle both commas and decimal points
        if ',' in cleaned_price:
            cleaned_price = cleaned_price.replace(',', '.')  # Convert commas to decimal points

        # Try converting to float
        price = float(cleaned_price)
        
        # If the price is valid and positive, return it
        if price <= 0:
            raise ValueError("Price cannot be zero or negative.")
        return price
    except ValueError:
        return None  # Invalid price

def add_to_cart(request, id):
    user_ide = request.session.get('user_id')

    if not user_ide:
        messages.error(request, "You must be logged in to add items to your cart.")
        return redirect('Login')

    users = User.objects.get(user_id=user_ide)
    product = get_object_or_404(Product, product_id=id)

    # ✅ Check if the product is out of stock
    if product.stock <= 0:
        messages.error(request, f"Sorry, {product.name} is out of stock.")
        return redirect(request.META.get('HTTP_REFERER', 'Breads'))

    selected_price_option = request.POST.get("selected_price_option", "").strip()
    print(selected_price_option)
    cleaned_price = clean_price(selected_price_option)

    if cleaned_price is None:
        messages.error(request, "Invalid price selection. Please try again.")
        return redirect('cart_view')

    # ✅ Get the total quantity of the product in the cart (across all price options)
    total_cart_quantity = Cart.objects.filter(user=users, product=product).aggregate(total_qty=models.Sum('quantity'))['total_qty'] or 0

    # ✅ Check if adding another one will exceed stock
    if total_cart_quantity >= product.stock:
        messages.error(request, f"Only {product.stock} {product.name}(s) are available in stock. You already have {total_cart_quantity} in your cart.")
        return redirect(request.META.get('HTTP_REFERER', 'Breads'))

    # ✅ Check if this exact price option already exists in the cart
    cart_item, created = Cart.objects.get_or_create(
        user=users,
        product=product,
        selected_price_option=str(selected_price_option),
        defaults={"quantity": 1}
    )

    if not created:
        # ✅ If the item already exists in the cart, increase its quantity
        if cart_item.quantity + 1 > product.stock:
            messages.error(request, f"Only {product.stock} {product.name}(s) are available in stock. You already have {cart_item.quantity} in your cart.")
            return redirect(request.META.get('HTTP_REFERER', 'Breads'))
        
        cart_item.quantity += 1
        cart_item.save()
    else:
        messages.success(request, f"{product.name} added to cart successfully!")

    return redirect('cart_view')


from django.utils.timezone import now

def cart_view(request):
    user_id = request.session.get('user_id')  # Get user ID from session

    if not user_id:
        messages.info(request, "Please log in to view your cart.")
        return redirect('Login')

    user = get_object_or_404(User, user_id=user_id)
    cart_items = Cart.objects.filter(user=user)

    subtotal = Decimal(0)
    shipping_cost = Decimal(50)  # Static shipping cost
    total_cart_items = sum(item.quantity for item in cart_items)  # Calculate total items in cart

    for item in cart_items:
        try:
            # Clean up the selected price option and remove the ₹ symbol
            price_weight_str = item.selected_price_option.replace("₹", ",").strip()

            # Check if the price_weight_str contains a comma
            if ',' in price_weight_str:
                price_weight = price_weight_str.split(',')

                if len(price_weight) == 2:
                    # Clean up and process price and weight
                    cleaned_price = Decimal(price_weight[0].strip())
                    item.product.cleaned_price = cleaned_price  # Store cleaned price
                    item.product.cleaned_weight = price_weight[1].strip()  # Store cleaned weight
                    
                    # Calculate the subtotal
                    item.subtotal = cleaned_price * item.quantity
                    subtotal += item.subtotal
                else:
                    raise ValueError(f"Error: The price_weight string '{price_weight_str}' does not have exactly two parts (price and weight).")
            else:
                raise ValueError(f"Error: The selected price option '{price_weight_str}' doesn't contain a comma to separate price and weight.")

        except Exception as e:
            print(f"Error processing item: {e}")

    # 🛠 FIX: Only fetch discount if it's NOT removed and NOT expired
    discount = None
    discount_amount = Decimal(0)
    is_discount_applied = False  # Track if discount is applied

    if 'discount_removed' not in request.session:  # Check if discount is removed
        cart = Cart.objects.filter(user=user).first()
        discount = cart.discount if cart and cart.discount else None

        if discount:
            # ✅ Check if the discount is expired
            if discount.end_date and discount.end_date < now():
                messages.warning(request, "This discount has expired and cannot be applied.")
                discount = None  # Remove discount since it is expired
            elif discount.min_order_amount and subtotal < discount.min_order_amount:
                messages.warning(request, f"Minimum order amount for this discount is ₹{discount.min_order_amount}.")
                discount = None  # Remove discount since it is not eligible
            else:
                if discount.discount_type == "percentage":
                    discount_amount = (subtotal * discount.value) / 100
                    if discount.max_discount:
                        discount_amount = min(discount_amount, discount.max_discount)
                else:
                    discount_amount = discount.value
                
                is_discount_applied = True  # Discount successfully applied

    total_price = max(subtotal - discount_amount + shipping_cost, 0)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'discount': discount if is_discount_applied else None,  # Only pass discount if applied
        'discount_amount': discount_amount if is_discount_applied else None,
        'total_price': total_price,
        'total_cart_items': total_cart_items,  # Pass total cart items to template
        'loggedin': True
    })

def remove_from_cart(request, id):
    # Get user from session
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "You must be logged in to remove items from your cart.")
        return redirect('Login')

    user = get_object_or_404(User, user_id=user_id)
    product_item = get_object_or_404(Product, product_id=id)

    print(f"User for cart: {user}")

    # Retrieve the selected price option from request (sent as a query parameter)
    selected_price_option_id = request.GET.get('price_option_id')

    # Filter cart items based on product and selected price option
    cart_items = Cart.objects.filter(user=user, product=product_item)

    if selected_price_option_id:
        cart_items = cart_items.filter(selected_price_option_id=selected_price_option_id)  # Match selected price

    if cart_items.exists():
        cart_items.first().delete()  # Delete only one matching item
        messages.success(request, "Item removed from cart successfully!")
    else:
        messages.error(request, "Item not found in your cart.")
    
    return redirect('cart_view')

def update_cart_quantity(request, product_id, selected_price_option, action):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "You must be logged in to update your cart.")
        return redirect('Login')

    user = get_object_or_404(User, user_id=user_id)  

    try:
        # ✅ Fetch the cart item for the specific price option
        cart_item = get_object_or_404(Cart, product__product_id=product_id, selected_price_option=selected_price_option, user=user)
        product = cart_item.product

        # ✅ Get total quantity of this product in the cart across all price options
        total_cart_quantity = Cart.objects.filter(product=product, user=user).aggregate(Sum('quantity'))['quantity__sum'] or 0

        # ✅ Extract and clean the price from `selected_price_option`
        try:
            price_weight_str = selected_price_option.replace("₹", "").strip()
            price_weight = price_weight_str.split(",")

            if len(price_weight) == 2:
                cleaned_price = Decimal(price_weight[0].strip())
            else:
                raise ValueError("Invalid price format in selected_price_option.")
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('cart_view')

        # ✅ Handle quantity update safely
        if action == 'increase':
            if total_cart_quantity < product.stock:  # ✅ Prevent exceeding stock
                cart_item.quantity += 1
            else:
                messages.error(request, f"Only {product.stock} items available in Stock .")
                return redirect('cart_view')

        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                messages.error(request, "Quantity can't be less than 1.")
                return redirect('cart_view')

        # ✅ Update subtotal correctly
        cart_item.subtotal = cleaned_price * cart_item.quantity
        cart_item.save()

        messages.success(request, "Cart updated successfully.")

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('cart_view')


def cet(request):
    return render(request,'cart.html')

# ------------------------------------------------------------------------------------ADD TO WISHLIST

def get_session_user_id(request):
    """Helper function to get session-based user ID."""
    if 'user_id' not in request.session:
        request.session['user_id'] = request.session.session_key or request.session.create()
    return request.session['user_id']

def add_to_wishlist(request, product_id):
    """Add a product to the wishlist using session-based user ID."""
    user_id = get_session_user_id(request)  

    if not user_id:
        messages.info(request, "Please log in to add items to your wishlist.")
        return redirect('Login')  # Change 'login' to your actual login page name
    product = get_object_or_404(Product, product_id=product_id)  

    wishlist_item, created = Wishlist.objects.get_or_create(user_id=user_id, product=product)  

    if created:
        messages.success(request, "Product added to wishlist!")  # ✅ Success message
    else:
        messages.warning(request, "This product is already in your wishlist!")  # ✅ Warning message

    return redirect('view_wishlist')  # Redirect to wishlist page

def view_wishlist(request):
    """Display the wishlist items for the session-based user."""
    user_id = get_session_user_id(request)
    wishlist_items = Wishlist.objects.filter(user_id=user_id)
    for item in wishlist_items:
        price_weight = item.product.price_options[0].split(',')
        item.product.cleaned_price = price_weight[0]  # "490"
        item.product.cleaned_weight = price_weight[1]  # "1kg"

    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

def remove_from_wishlist(request, product_id):
    """Remove a product from the wishlist."""
    user_id = get_session_user_id(request)
    product = get_object_or_404(Product, pk=product_id)

    Wishlist.objects.filter(user_id=user_id, product=product).delete()
    messages.success(request, "Product removed from wishlist!")  # Optional success message

    return redirect('view_wishlist')  # Redirect back to wishlist page

# ------------------------------------------------------------------------------------ORDER
from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import format_html

def send_order_confirmati_email(user, order):
    subject = "Order Confirmation - Your Order Has Been Placed!"
    
    html_message = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f8f9fa;
                padding: 20px;
            }}
            .container {{
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
            }}
            h2 {{
                color: #333;
                text-align: center;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #c2a1a0;
                color: white;
            }}
            .footer {{
                margin-top: 20px;
                text-align: center;
                font-size: 14px;
                color: #555;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Thank You for Your Order, {user.first_name}!</h2>
            <p>Your order has been successfully placed. Below are the details:</p>
            <table>
                <tr>
                    <th>Order ID</th>
                    <td>{order.order_id}</td>
                </tr>
                <tr>
                    <th>Total Amount</th>
                    <td>₹{order.total_amount}</td>
                </tr>
                <tr>
                    <th>Payment Method</th>
                    <td>{order.payment.payment_method}</td>
                </tr>
                 <tr>
                    <th>Payment Status</th>
                    <td>{order.payment.status}</td>
                </tr>
                <tr>
                    <th>Shipping Address</th>
                    <td>{order.shipping_address if order.shipping_address else 'Default Address'}</td>
                </tr>
                <tr>
                    <th>Order Status</th>
                    <td>{order.delivery_status}</td>
                </tr>
            </table>

            <p class="footer">
                Your order is being processed, and we will notify you once it is shipped.<br>
                <strong>Nova Bakers</strong> | Contact: support@novabakers.com
            </p>
        </div>
    </body>
    </html>
    """

    send_mail(
        subject,
        "",
        settings.DEFAULT_FROM_EMAIL,
        [user.email_id],
        fail_silently=False,
        html_message=html_message,  # ✅ Sends HTML-formatted email
    )


RAZORPAY_KEY_ID = "rzp_test_QRvsdEFaC3EA6l"
RAZORPAY_KEY_SECRET = "buLoHaDp2eHNGuASj4jWwfmx"

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))  # Initialize Razorpay
def Checkout(request):
    user_id = request.session.get('user_id')  
    if not user_id:
        messages.info(request, "Please log in to proceed with checkout.")
        return redirect('Login')

    user = get_object_or_404(User, user_id=user_id)  
    cart_items = Cart.objects.filter(user=user)  

    if not cart_items.exists():
        messages.error(request, "Your cart is empty. Add items before proceeding.")
        return redirect('cart_view')

    subtotal = Decimal(0)
    shipping_cost = Decimal(50)  

    is_cake_in_cart = any(
        (item.product.subcategory and item.product.subcategory.main_category.name == "Cakes") or 
        (item.product.main_category and item.product.main_category.name == "Cakes")
        for item in cart_items
    )

    for item in cart_items:
        try:
            price_str = item.selected_price_option.split(',')[0]  
            price_str = price_str.replace("₹", "").strip()  
            cleaned_price = Decimal(price_str)
            item.subtotal = cleaned_price * item.quantity
            subtotal += item.subtotal
        except:
            messages.error(request, f"Invalid price for {item.product.name}.")
            return redirect('cart_view')

    cart = Cart.objects.filter(user=user).first()
    discount = cart.discount if cart and cart.discount else None
    discount_amount = Decimal(0)

    if discount:
        if discount.end_date and discount.end_date < now():
            messages.warning(request, "This discount has expired and will not be applied.")
            discount = None
        elif discount.min_order_amount and subtotal < discount.min_order_amount:
            messages.warning(request, f"Minimum order amount for discount: ₹{discount.min_order_amount}")
        else:
            discount_amount = (subtotal * discount.value) / 100 if discount.discount_type == "percentage" else discount.value
            if discount.max_discount:
                discount_amount = min(discount_amount, discount.max_discount)

    total_price = max(subtotal - discount_amount + shipping_cost, 0)  

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")  
        is_different_address = request.POST.get("different_address_checkbox") == "on"
        shipping_address = request.POST.get("address2") if is_different_address else user.address  
        cake_customization_text = request.POST.get("cake_customization", "").strip()

        if payment_method == "COD":
            payment = ProductPayment.objects.create(
                payment_id="COD-" + str(uuid.uuid4()),  
                payment_method="COD",
                total_amount=total_price,
                status="Pending"  
            )
        else:
            razorpay_order = client.order.create({
                "amount": int(total_price * 100),
                "currency": "INR",
                "receipt": str(uuid.uuid4()),
                "payment_capture": "1"
            })

            payment = ProductPayment.objects.create(
                payment_id=razorpay_order['id'],
                payment_method="Razorpay",
                total_amount=total_price,
                status="Complete"
            )

        order = Order.objects.create(
            user=user,
            total_amount=total_price,
            payment=payment,
            discount=discount,
            discount_amount=discount_amount,
            is_different_address=is_different_address,
            shipping_address=shipping_address
        )
        order.save() 
        order_details_list = []
        for item in cart_items:
            product = item.product
            if product.stock >= item.quantity:
                product.stock = F('stock') - item.quantity
                product.save(update_fields=['stock'])  

                order_details_list.append(OrderDetails(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    selected_price_option=item.selected_price_option,
                    cake_customization=cake_customization_text if is_cake_in_cart else None  # ✅ Save only for cakes
                ))
            else:
                messages.error(request, f"Insufficient stock for {product.name}.")
                return redirect('cart_view')

        OrderDetails.objects.bulk_create(order_details_list)

        cart_items.delete()

        if payment_method == "COD":
            messages.success(request, "Your COD order has been placed successfully!")
            send_order_confirmati_email(user, order)  # ✅ Pass the user object, not just the email
            return redirect("order_success")
        
        send_order_confirmati_email(user, order)  # ✅ Pass the user object, not just the email
        return render(request, 'razorpay_payment.html', {
            "razorpay_order_id": razorpay_order['id'],
            "razorpay_key": RAZORPAY_KEY_ID,
            "amount": total_price,
            "order_id": order.order_id
        })

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'subtotal': round(subtotal, 2),
        'discount': discount,
        'discount_amount': discount_amount,
        'shipping_cost': shipping_cost,
        'total_price': total_price,
        'user': user, 
        'loggedin': True
    })

#-------------------------------------------------------------------------------------------------CUSTOMIZE ORDER
def send_order_confirmation_email(user, order):
    subject = "🎂 Your Custom Cake Order Confirmation 🎉"

    # Email body in HTML format
    message = f"""
    <html>
        <body>
            <h2 style="color: #d63384;">Hello {user.first_name},</h2>
            <p>Thank you for placing your custom cake order! Here are the details of your order:</p>
            
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th style="background-color: #d63384; color: white;">Order Number</th>
                    <td>{order.id}</td>
                </tr>
                <tr>
                    <th style="background-color: #d63384; color: white;">Cake Type</th>
                    <td>{order.cake_type}</td>
                </tr>
                <tr>
                    <th style="background-color: #d63384; color: white;">Size</th>
                    <td>{order.size}</td>
                </tr>
                <tr>
                    <th style="background-color: #d63384; color: white;">Shape</th>
                    <td>{order.shape}</td>
                </tr>
                <tr>
                    <th style="background-color: #d63384; color: white;">Flavor</th>
                    <td>{order.flavor}</td>
                </tr>
                <tr>
                    <th style="background-color: #d63384; color: white;">Icing</th>
                    <td>{order.icing}</td>
                </tr>
                <tr>
                    <th style="background-color: #d63384; color: white;">Layers</th>
                    <td>{order.cake_layers}</td>
                </tr>
                <tr>
                    <th style="background-color: #d63384; color: white;">Sweetness Level</th>
                    <td>{order.sweetness_level}</td>
                </tr>
                <tr>
                    <th style="background-color: #d63384; color: white;">Serving Size</th>
                    <td>{order.serving_size}</td>
                </tr>
                <tr>
                    <th style="background-color: #d63384; color: white;">Total Price</th>
                    <td>₹{order.total_price}</td>
                </tr>
                <tr>
                    <th style="background-color: #d63384; color: white;">Pickup Date</th>
                    <td>{order.pickup_date}</td>
                </tr>
                <tr>
                    <th style="background-color: #d63384; color: white;">Pickup Time</th>
                    <td>{order.pickup_time}</td>
                </tr>
            </table>

            <p>If you have any special requests or modifications, feel free to contact us.</p>
            <p style="color: #d63384;"><strong>🎉 Thank you for choosing us! 🎂</strong></p>
        </body>
    </html>
    """

    send_mail(
        subject,
        "Your email client does not support HTML emails.",
        settings.DEFAULT_FROM_EMAIL,
        [user.email_id],
        html_message=message  # Send HTML email
    )

def CustomCakeCheckout(request, order_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.info(request, "Please log in to proceed with checkout.")
        return redirect('Login')

    user = get_object_or_404(User, user_id=user_id)
    order = get_object_or_404(CustomCakeOrder, id=order_id, user=user)

    subtotal = Decimal(order.total_price)
    shipping_cost = Decimal(50)
    discount_code = order.discount_code or ""
    discount_amount = Decimal(order.discount_amount or 0)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        is_different_address = request.POST.get("different_address_checkbox") == "on"
        shipping_address = request.POST.get("address2") if is_different_address else user.address

        if payment_method == "COD":
            payment = ProductPayment.objects.create(
                payment_id="COD-" + str(uuid.uuid4()),
                payment_method="COD",
                total_amount=subtotal - discount_amount + shipping_cost,
                status="Pending"
            )
            order.payment = payment
            order.shipping_address = shipping_address
            order.save()
            send_order_confirmation_email(user, order)
            messages.success(request, "Your custom cake order has been placed successfully!")
            return redirect("order_success")

        else:
            razorpay_order = client.order.create({
                "amount": int((subtotal - discount_amount + shipping_cost) * 100),
                "currency": "INR",
                "receipt": str(uuid.uuid4()),
                "payment_capture": "1"
            })

            payment = ProductPayment.objects.create(
                payment_id=razorpay_order['id'],
                payment_method="Razorpay",
                total_amount=subtotal - discount_amount + shipping_cost,
                status="Complete"
            )
            send_order_confirmation_email(user, order)

        order.payment = payment
        order.shipping_address = shipping_address
        order.save()

        return render(request, 'razorpay_payment.html', {
            "razorpay_order_id": razorpay_order['id'],
            "razorpay_key": RAZORPAY_KEY_ID,
            "amount": subtotal - discount_amount + shipping_cost,
            "order_id": order.id
        })

    return render(request, 'checkout.html', {
        'subtotal': round(subtotal, 2),
        'discount_amount': round(discount_amount, 2),
        'shipping_cost': round(shipping_cost, 2),
        'total_price': subtotal - discount_amount + shipping_cost,
        'user': user,
        'custom_order': order
    })


def payment_success(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('razorpay_payment_id')

    try:
        order = Order.objects.get(order_id=order_id)
        order.payment.status = "Completed"
        order.payment.payment_id = payment_id
        order.payment.save()
        messages.success(request, "Payment successful! Your order has been placed.")
    except Order.DoesNotExist:
        messages.error(request, "Order not found!")

    return redirect('order_success')

def order_success(request):
    return render(request, 'order_success.html')  # Ensure you have this templat


#--------------------------------------------------------------------------------------DISPLAY ORDER RELATED PAGES
def Myorder(request):
    user_id = request.session.get('user_id')  # Get logged-in user ID

    if not user_id:
        messages.info(request, "Please log in to view your orders.")
        return redirect('Login')

    orders = Order.objects.filter(user_id=user_id).order_by('-order_datetime')  # Get orders in descending order

    # ✅ Check if all items in an order are returned
    for order in orders:
        total_items = OrderDetails.objects.filter(order=order).aggregate(total=Sum("quantity"))["total"] or 0
        returned_items = OrderReturnDetails.objects.filter(order_return__order=order).aggregate(returned=Sum("quantity_returned"))["returned"] or 0

        order.is_fully_returned = returned_items >= total_items and total_items > 0  # ✅ Hide return button only if all items are returned

    paginator = Paginator(orders, 5)  # Show 5 orders per page
    page_number = request.GET.get('page')  # Get current page number from URL
    page_orders = paginator.get_page(page_number)  # Get orders for the current page

    return render(request, 'Myorder.html', {'orders': page_orders})

def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if order.delivery_status == "Shipped":
        messages.error(request, "This order has already been shipped and cannot be canceled.")
        return redirect('Myorder')

    # Create a cancellation entry
    OrderCancel.objects.create(order=order, cancel_reason="User requested cancellation")

    # Update order status
    order.delivery_status = "Cancelled"
    order.save()

    messages.success(request, "Your order has been successfully canceled.")
    return redirect('Myorder')

def track_order(request, order_id):
    order = Order.objects.get(order_id=order_id)
    return render(request, 'track_order.html', {'order': order})

def extract_price(price_option):
    """Extracts the numeric price from the selected_price_option field."""
    try:
        # Use regex to find the numeric part before any unit (kg, packet, etc.)
        match = re.search(r"(\d+[\.,]?\d*)", price_option)  # Capture the price before the unit
        if match:
            # Replace comma with dot for decimals and return as Decimal
            price = match.group(0).replace(',', '.')
            return Decimal(price)
        return Decimal(0)  # Return 0 if no valid price found
    except (ValueError, AttributeError):
        return Decimal(0)  # Return 0 if there's an error in parsing

def order_details(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    # ✅ Get all order items, excluding fully canceled ones
    order_items = OrderDetails.objects.filter(order=order, quantity__gt=0)

    # ✅ Fetch canceled & returned orders
    canceled_orders = OrderCancel.objects.filter(order=order)
    returned_orders = OrderReturn.objects.filter(order=order)

    canceled_items = []
    returned_items = []

    total_canceled_refund = Decimal(0)
    total_returned_refund = Decimal(0)

    # ✅ Fetch canceled order details correctly
    for cancel in canceled_orders:
        cancel_details = OrderCancelDetails.objects.filter(cancel=cancel)

        for detail in cancel_details:
            if detail.quantity_canceled == 0:
                continue  # Skip fully returned items

            cleaned_price = extract_price(detail.order_detail.selected_price_option)  # Extract numeric price for calculation
            cancel_reason = detail.cancel_reason or cancel.cancel_reason

            # ✅ Calculate refundable amount & subtotal **ONLY IF REFUND IS NOT 'Not Applicable'**
            refundable_amount = cleaned_price * detail.quantity_canceled if detail.refund_status != "Not Applicable" else Decimal(0)
            if detail.refund_status != "Not Applicable":
                total_canceled_refund += refundable_amount
            subtotal = cleaned_price * detail.quantity_canceled

            canceled_items.append({
                'product': detail.order_detail.product,
                'product_id': detail.order_detail.product.product_id,
                'image': detail.order_detail.product.image.url if detail.order_detail.product.image else None,
                'cancel_reason': cancel_reason,
                'cancel_datetime': cancel.cancel_datetime,
                'quantity': detail.quantity_canceled,
                'selected_price_option': detail.order_detail.selected_price_option,  # Display the raw price with unit
                'refund_status': detail.refund_status,
                'subtotal': subtotal,
                'refund_amount': refundable_amount,
            })

    # ✅ Fetch returned order details
    for return_order in returned_orders:
        return_details = OrderReturnDetails.objects.filter(order_return=return_order)

        for detail in return_details:
            if detail.quantity_returned == 0:
                continue  # Skip fully returned items

            cleaned_price = extract_price(detail.order_detail.selected_price_option)  # Extract numeric price for calculation
            return_reason = detail.return_reason

            # ✅ Calculate refundable amount & subtotal **ONLY IF REFUND IS NOT 'Not Applicable'**
            returnable_amount = cleaned_price * detail.quantity_returned if detail.refund_status != "Not Applicable" else Decimal(0)
            if detail.refund_status != "Not Applicable":
                total_returned_refund += returnable_amount
            subtotal = cleaned_price * detail.quantity_returned

            returned_items.append({
                'product': detail.order_detail.product,
                'product_id': detail.order_detail.product.product_id,
                'image': detail.order_detail.product.image.url if detail.order_detail.product.image else None,
                'return_reason': return_reason,
                'return_datetime': return_order.return_datetime,
                'quantity': detail.quantity_returned,
                'selected_price_option': detail.order_detail.selected_price_option,  # Display the raw price with unit
                'refund_status': detail.refund_status,
                'subtotal': subtotal,
                'refund_amount': returnable_amount,
            })

    # ✅ Calculate subtotal for ordered items, use raw price with unit in the template
    subtotal = sum(
        extract_price(item.selected_price_option) * item.quantity  # Extract numeric price for calculation
        for item in order_items
    )

    # ✅ Add the rest of the calculations for shipping cost, discount, etc.
    shipping_cost = Decimal(50)
    discount_amount = order.discount_amount or Decimal(0)  # ✅ Fetch applied discount
    total_price = max(subtotal - discount_amount + shipping_cost, Decimal(0))  # ✅ Ensure non-negative total
    for item in order_items:
        item.subtotal = extract_price(item.selected_price_option) * item.quantity
    # ✅ Add separated totals
    context = {
        'order': order,
        'order_items': order_items,
        'canceled_items': canceled_items,
        'returned_items': returned_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'discount': order.discount,  # ✅ Pass discount object
        'discount_amount': discount_amount,  # ✅ Pass discount amount
        'total_price': total_price,
        'total_canceled_refund': total_canceled_refund,
        'total_returned_refund': total_returned_refund,
        'total_refundable_amount': total_canceled_refund + total_returned_refund,
    }

    return render(request, 'order_details.html', context)

def view_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    shop = Shop.objects.first()
    order_items = OrderDetails.objects.filter(order=order)

    # Calculate subtotal for each item and for the whole order
    for item in order_items:
        item.subtotal = extract_price(item.selected_price_option.split("₹")[-1].strip()) * item.quantity

    subtotal = sum(item.subtotal for item in order_items)
    shipping_cost = 50
    total_price = subtotal + shipping_cost

    # Render the invoice as HTML
    html_content = render_to_string('invoice_template.html', {
        'order': order,
        'shop': shop,
        'order_items': order_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total_price': total_price,
    })

    # Generate PDF from HTML
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=r"C:\Users\Trupal\wkhtmltopdf\bin\wkhtmltopdf.exe")
    options = {
        'enable-local-file-access': '',
        'page-size': 'A4',
        'encoding': 'UTF-8',
    }

    try:
        pdf = pdfkit.from_string(html_content, False, configuration=pdfkit_config, options=options)
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", content_type="text/plain")

    # Return the PDF inline so it can be viewed directly in the browser
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Invoice_{order.order_id}.pdf"'  # 'inline' for viewing
    return response

def download_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    shop = Shop.objects.first()
    order_items = OrderDetails.objects.filter(order=order)

    # Calculate subtotal for each item and for the whole order
    for item in order_items:
        item.subtotal = extract_price(item.selected_price_option.split("₹")[-1].strip()) * item.quantity

    subtotal = sum(item.subtotal for item in order_items)
    shipping_cost = 50
    total_price = subtotal + shipping_cost

    # Render the invoice as HTML
    html_content = render_to_string('invoice_template.html', {
        'order': order,
        'shop': shop,
        'order_items': order_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total_price': total_price,
    })

    # Generate PDF from HTML
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=r"C:\Users\Trupal\wkhtmltopdf\bin\wkhtmltopdf.exe")
    options = {
        'enable-local-file-access': '',
        'page-size': 'A4',
        'encoding': 'UTF-8',
    }

    try:
        pdf = pdfkit.from_string(html_content, False, configuration=pdfkit_config, options=options)
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", content_type="text/plain")

    # Return the PDF with the 'attachment' disposition for download
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.order_id}.pdf"'  # 'attachment' for download
    return response


def cancel_order_page(request, order_id):
    """Display cancel order page where users can select items to cancel"""
    order = get_object_or_404(Order, order_id=order_id)
    order_items = OrderDetails.objects.filter(order=order)
    return render(request, "cancel_order.html", {"order": order, "order_items": order_items})

def process_cancel_order(request, order_id):
    """Process order cancellation (entire order or selected items)"""
    order = get_object_or_404(Order, order_id=order_id)

    if request.method == "POST":
        cancel_reason = request.POST.get("cancel_reason", "").strip()  # Get cancellation reason
        cancel_items = request.POST.getlist("cancel_items")  # List of selected item IDs

        # ✅ Ensure an OrderCancel entry exists OR create a new one
        cancel_order, created = OrderCancel.objects.get_or_create(
            order=order,
            defaults={"cancel_reason": cancel_reason}  
        )

        # ✅ Update cancellation reason even if entry already exists
        if not created and cancel_reason:
            cancel_order.cancel_reason = cancel_reason
            cancel_order.save()

        refundable_amount = 0  # Initialize refund amount

        # ✅ Function to extract price correctly
        def extract_price(selected_price_option):
            """Extracts numeric price from a formatted price string."""
            try:
                if not selected_price_option:
                    return 0.00
                
                match = re.search(r"₹(\d+\.?\d*)", selected_price_option)
                return float(match.group(1)) if match else 0.00
            except ValueError:
                return 0.00

        # ✅ Cancel entire order
        if "cancel_all" in request.POST:
            for order_item in OrderDetails.objects.filter(order=order):
                item_price = extract_price(order_item.selected_price_option)
                item_subtotal = item_price * order_item.quantity  

                refund_status = "Pending" if item_price > 0 else "Not Applicable"

                cancel_item_reason = request.POST.get(f"cancel_reason_{order_item.order_detail_id}", "").strip() or cancel_reason

                # ✅ Store cancellation details per item
                OrderCancelDetails.objects.create(
                    cancel=cancel_order,
                    order_detail=order_item,
                    product=order_item.product,
                    quantity_canceled=order_item.quantity,
                    cancel_reason=cancel_item_reason,  # ✅ Fix: Store reason per item
                    refund_status=refund_status,  
                    refund_amount=item_subtotal  
                )

                if refund_status == "Pending":
                    refundable_amount += item_subtotal

                # ✅ Mark item as canceled
                order_item.quantity = 0
                order_item.status = "Cancelled"
                order_item.save()

            # ✅ Update order status
            order.delivery_status = "Cancelled"
            order.save()

            messages.success(request, "Your entire order has been canceled successfully.")

        # ✅ Cancel selected items
        elif "cancel_selected" in request.POST and cancel_items:
            for item_id in cancel_items:
                try:
                    order_item = OrderDetails.objects.get(order_detail_id=int(item_id))
                    quantity_canceled = int(request.POST.get(f"cancel_quantity_{item_id}", 1))

                    cancel_item_reason = request.POST.get(f"cancel_reason_{item_id}", "").strip()

                    if 1 <= quantity_canceled <= order_item.quantity:
                        item_price = extract_price(order_item.selected_price_option)
                        item_subtotal = item_price * quantity_canceled

                        refund_status = "Pending" if item_price > 0 else "Not Applicable"

                        # ✅ Store cancellation details per item
                        OrderCancelDetails.objects.create(
                            cancel=cancel_order,
                            order_detail=order_item,
                            product=order_item.product,
                            quantity_canceled=quantity_canceled,
                            cancel_reason=cancel_item_reason,  # ✅ Storing reason for selected item
                            refund_status=refund_status,  
                            refund_amount=item_subtotal  
                        )

                        if refund_status == "Pending":
                            refundable_amount += item_subtotal

                        # ✅ Update quantity (remove if fully canceled)
                        order_item.quantity -= quantity_canceled
                        if order_item.quantity == 0:
                            order_item.status = "Cancelled"
                        
                        order_item.save()

                        messages.success(request, f"Successfully canceled {quantity_canceled} items of {order_item.product.name}.")
                    else:
                        messages.error(request, "Invalid cancellation quantity.")
                except (ValueError, OrderDetails.DoesNotExist):
                    messages.error(request, "Invalid item selected for cancellation.")

        # ✅ Check if all items in the order are canceled
        remaining_items = OrderDetails.objects.filter(order=order, quantity__gt=0).exists()

        if not remaining_items:  # If no items left, cancel the entire order
            order.delivery_status = "Cancelled"
            order.save()
            messages.success(request, "Your entire order has been canceled because all items were removed.")

        # ✅ Save total refundable amount in OrderCancel
        cancel_order.refund_amount = refundable_amount
        cancel_order.save()

        return redirect("Myorder")

    return redirect("cancel_order_page", order_id=order_id)


def return_order_page(request, order_id):
    """Display the return order page with order details."""
    order = get_object_or_404(Order, order_id=order_id)

    # ✅ Show only items with quantity left to return
    order_items = OrderDetails.objects.filter(order=order, quantity__gt=0)

    return render(request, "return_order.html", {
        "order": order,
        "order_items": order_items
    })

def process_return_order(request, order_id):
    """Process order return (entire order or selected items)"""
    order = get_object_or_404(Order, order_id=order_id)

    if request.method == "POST":
        return_items = request.POST.getlist("return_items")  # ✅ Selected return items
        return_reason_entire_order = request.POST.get("return_reason_entire_order", "").strip()

        # ✅ Get or create the return order record
        return_order, created = OrderReturn.objects.get_or_create(order=order)

        # ✅ Handle entire order return
        if "return_all" in request.POST:
            if not return_reason_entire_order:
                messages.error(request, "Please provide a reason for returning the entire order.")
                return redirect("return_order_page", order_id=order_id)

            for order_item in OrderDetails.objects.filter(order=order):
                if order_item.quantity > 0:
                    OrderReturnDetails.objects.create(
                        order_return=return_order,
                        order_detail=order_item,
                        quantity_returned=order_item.quantity,
                        return_reason=return_reason_entire_order,
                        refund_status="Pending",
                        return_status="Pending"
                    )
                    order_item.quantity = 0  # ✅ Set quantity to 0 (fully returned)
                    order_item.status = "Returned"
                    order_item.save()

            order.delivery_status = "Returned"
            order.save()
            messages.success(request, "Entire order has been returned successfully.")
            return redirect("Myorder")

        # ✅ Handle selected item return
        elif "return_selected" in request.POST and return_items:
            for item_id in return_items:
                order_item = get_object_or_404(OrderDetails, order_detail_id=int(item_id))
                quantity_returned = int(request.POST.get(f"return_quantity_{item_id}", 1))
                return_reason = request.POST.get(f"return_reason_{item_id}", "").strip()

                if quantity_returned > 0 and quantity_returned <= order_item.quantity:
                    OrderReturnDetails.objects.create(
                        order_return=return_order,
                        order_detail=order_item,
                        quantity_returned=quantity_returned,
                        return_reason=return_reason,
                        refund_status="Pending",
                        return_status="Pending"
                    )

                    # ✅ Decrease quantity or remove item
                    order_item.quantity -= quantity_returned
                    if order_item.quantity == 0:
                        order_item.status = "Returned"
                    order_item.save()

                    messages.success(request, f"Returned {quantity_returned} x {order_item.product.name}.")
                else:
                    messages.error(request, "Invalid return quantity.")

        return redirect("Myorder")

#---------------------------------------------------------------------------------------PRODUCT DETAILS
def get_logged_in_user(request):
    user_id = request.session.get("user_id")  
    if user_id:
        try:
            return User.objects.get(user_id=user_id)  
        except ObjectDoesNotExist:
            return None
    return None  

def has_purchased_product(user, product_id):
    return Order.objects.filter(user=user, orderdetails__product__product_id=product_id).exists()

def product_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    reviews = Review.objects.filter(product=product)

    total_reviews = reviews.count()
    average_rating = round(sum([review.rating for review in reviews]) / total_reviews) if total_reviews > 0 else 0

    current_user = get_logged_in_user(request)
    user_can_review = has_purchased_product(current_user, product_id) if current_user else False

    inquiries = ProductInquiry.objects.filter(product=product)

 
    similar_products = Product.objects.filter(subcategory=product.subcategory).exclude(product_id=product_id)[:4]

 
    inquiries = ProductInquiry.objects.filter(product=product)
    product_ingredients = ProductIngredient.objects.filter(product=product)
    return render(request, "product_detail.html", {
        "product": product,
        "reviews": reviews,
        "average_rating": average_rating,
        "total_reviews": total_reviews,
        "current_user": current_user,
        "user_can_review": user_can_review,
        "inquiries": inquiries,
        "similar_products": similar_products,  
        "product_ingredients": product_ingredients,  
    })

#---------------------------------------------------------------------------------------------------REVIEW
def submit_review(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, product_id=product_id)
        rating = int(request.POST.get("rating", 5))
        comment = request.POST.get("comment")
        photo = request.FILES.get("photo") 

       
        user = get_logged_in_user(request)
        if not user:
            messages.error(request, "You must be logged in to submit a review.")
            return redirect("login")

        if not comment.strip():
            messages.error(request, "Comment cannot be empty.")
            return redirect("product_detail", product_id=product_id)

        
        has_purchased = Order.objects.filter(user=user, orderdetails__product=product).exists()

        if not has_purchased:
            messages.error(request, "You can only review products you have purchased.")
            return redirect("product_detail", product_id=product_id)

        # ✅ Save Review
        Review.objects.create(
            product=product,
            user=user,
            rating=rating,
            comment=comment,
            photo=photo  
        )

        messages.success(request, "Review submitted successfully!")
        return redirect("product_detail", product_id=product_id)

    return redirect("product_detail", product_id=product_id)


def edit_review(request, review_id):
    """Allow users to edit their review."""
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, "You must be logged in to edit your review.")
        return redirect("login")

    
    review = get_object_or_404(Review, id=review_id, user=user)

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been updated successfully!")
            return redirect("product_detail", product_id=review.product.product_id)
    else:
        form = ReviewForm(instance=review)

    return render(request, "edit_review.html", {"form": form, "review": review})


def delete_review(request, review_id):
    """Allow users to delete their own review."""
    user = get_logged_in_user(request)
    if not user:
        return JsonResponse({"error": "You must be logged in to delete a review."}, status=403)

    review = get_object_or_404(Review, id=review_id, user=user)
    product_id = review.product.product_id 
    review.delete()

    return JsonResponse({"success": True, "message": "Your review has been deleted successfully!"})

#-----------------------------------------------------------------------------------------------------DISCOUNT


def apply_discount(request):
    """Applies a discount code if valid."""
    if request.method == "POST":
        discount_code = request.POST.get("discount_code", "").strip()
        user_id = request.session.get("user_id")

        if not user_id:
            messages.error(request, "You need to log in to apply a discount.")
            return redirect("Login")

        user = get_object_or_404(User, user_id=user_id)
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect("cart_view")

        # Fetch the discount
        try:
            discount = Discount.objects.get(code=discount_code, is_active=True)
        except Discount.DoesNotExist:
            messages.error(request, "Invalid discount code.")
            return redirect("cart_view")

        # ✅ Check if the discount has expired
        if discount.end_date and discount.end_date < now():
            messages.error(request, "This discount has expired.")
            return redirect("cart_view")

        # ✅ Calculate subtotal properly
        subtotal = Decimal(0)

        for item in cart_items:
            try:
                # Extract price from selected_price_option
                price_weight_str = item.selected_price_option.replace("₹", "").strip()
                price_weight = price_weight_str.split(",")

                if len(price_weight) == 2:
                    cleaned_price = Decimal(price_weight[0].strip())  # Convert price to Decimal
                    subtotal += cleaned_price * item.quantity
                else:
                    messages.error(request, "Invalid price format in cart item.")
                    return redirect("cart_view")

            except Exception as e:
                messages.error(request, f"Error processing item price: {e}")
                return redirect("cart_view")

        # ✅ Check if subtotal meets discount requirements
        if discount.min_order_amount and subtotal < discount.min_order_amount:
            messages.error(
                request,
                f"Minimum order amount for this discount is ₹{discount.min_order_amount}.",
            )
            return redirect("cart_view")

        # ✅ Calculate discount amount
        discount_amount = Decimal(0)
        if discount.discount_type == "percentage":
            discount_amount = (subtotal * Decimal(discount.value)) / 100
            if discount.max_discount:
                discount_amount = min(discount_amount, Decimal(discount.max_discount))
        else:
            discount_amount = Decimal(discount.value)

        # ✅ Apply the discount
        for item in cart_items:
            item.discount = discount  # Assign discount to all cart items
            item.save()

        # ✅ Store discount details in session
        request.session["discount_applied"] = {
            "code": discount.code,
            "value": str(discount.value),
            "discount_type": discount.discount_type,
            "max_discount": str(discount.max_discount or 0),
        }

        # ✅ Remove discount_removed flag if previously removed
        request.session.pop("discount_removed", None)

        messages.success(request, f"Discount '{discount.code}' applied successfully!")

    return redirect("cart_view")

def discount_list(request):
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.error(request, "Please log in to apply a discount.")
        return redirect('Login')

    # Fetch only active discounts
    discounts = Discount.objects.filter(is_active=True)
    
    return render(request, "discount_list.html", {"discounts": discounts, "now": now()})

def remove_discount(request):
    """Removes the applied discount from the session and cart."""
    user_id = request.session.get('user_id')
    
    if user_id:
        user = get_object_or_404(User, user_id=user_id)
        cart = Cart.objects.filter(user=user).first()
        
        if cart:
            cart.discount = None  # Remove discount from DB
            cart.save()

    request.session['discount_removed'] = True  # Store in session
    return redirect('cart_view')

#-----------------------------------------------------------------------------------------------INQUIRY
def submit_inquiry(request, product_id):
    if "user_id" not in request.session:
        messages.error(request, "Please log in to ask a question.")
        return redirect("Login")  # Redirect to login if user is not logged in

    user_id = request.session.get("user_id")  # Get the user ID from the session
    user = get_object_or_404(User, user_id=user_id)  # Fetch user from your custom User model
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == "POST":
        question = request.POST.get("question")
        ProductInquiry.objects.create(user=user, product=product, question=question)
        messages.success(request, "Your inquiry has been submitted.")

    return redirect("product_detail", product_id=product_id)

#-----------------------------------------------------------------------------------------------------SEARCH
def search_results(request):
    query = request.GET.get("q")  # Get user search input

    if query:
        # ✅ Redirect if query matches a main category
        main_category_mapping = {
            "Cakes": "Cakes",
            "Pastries": "Pastries",
            "Cupcakes": "Cupcakes",
            "Cookies": "Cookies",
            "Donuts": "Donuts",
            "Waffles": "Waffles",
            "Breads": "Breads",
            "Others": "Others",
        }

        main_category = MainCategory.objects.filter(name__icontains=query).first()
        if main_category and main_category.name in main_category_mapping:
            return redirect(f"/{main_category_mapping[main_category.name]}.html")

        # ✅ Redirect if query matches a subcategory
        subcategory = SubCategory.objects.filter(name__icontains=query).first()
        if subcategory:
            if subcategory.main_category.name == "Cakes":
                return redirect("cakes_by_subcategory", subcategory_id=subcategory.id)
            elif subcategory.main_category.name == "Others":
                return redirect("/Others.html")

        # ✅ Redirect if query matches a product
        product = Product.objects.filter(name__icontains=query).first()
        if not product:
            product = Product.objects.filter(description__icontains=query).first()
        if product:
            return redirect("product_detail", product_id=product.product_id)
        

    # ✅ If no match, show a "No results found" page
    return render(request, "search_results.html", {"query": query, "no_results": True})


#-------------------------------------------------------------------------------------------CART COUNT LIKE(4)
def cart_count(request):
    total_cart_items = 0
    if request.session.get('user_id'):
        user_id = request.session.get('user_id')
        cart_items = Cart.objects.filter(user_id=user_id)
        total_cart_items = sum(item.quantity for item in cart_items)

    return {'total_cart_items': total_cart_items}

#-------------------------------------------------------------------------------------------CUSTOMIZEORDER RELATED 

def order_confirmation(request, order_id):
    # Get the order by its ID
    order = get_object_or_404(CustomCakeOrder, id=order_id)

    # Render the confirmation page with the order details
    return render(request, "order_confirmation.html", {"order": order})

def Customizeorder(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "You must be logged in to place a custom order.")
        return redirect('Login')

    user = get_object_or_404(User, user_id=user_id)
    total_price = Decimal(1500)  # Base price
    discount_code = request.POST.get("discount_coupon", "").strip()
    discount_amount = Decimal(0)

    # Apply Discount if coupon is provided
    if discount_code:
        discount_amount, discount_message = calculate_discount(total_price, discount_code)
        total_price = max(total_price - discount_amount, Decimal(0))  # Ensure it doesn't go negative
        messages.success(request, discount_message)

    if request.method == "POST":
        # Extract form data
        cake_data = {
            "cake_type": request.POST.get("cake_type", ""),
            "size": request.POST.get("size", ""),
            "shape": request.POST.get("shape", ""),
            "flavor": request.POST.get("flavor", ""),
            "filling": request.POST.get("filling", ""),
            "icing": request.POST.get("icing", ""),
            "cake_layers": request.POST.get("cake_layers", ""),
            "occasion": request.POST.get("occasion", ""),
            "sweetness_level": request.POST.get("sweetness_level", ""),
            "serving_size": request.POST.get("serving_size", ""),
            "cake_theme": request.POST.get("cake_theme", ""),
            "allergy_info": request.POST.get("allergy_info", ""),
            "egg_preference": request.POST.get("egg", ""),
            "extra_addons": request.POST.get("extra_addons", ""),
            "packaging": request.POST.get("packaging", ""),
            "message": request.POST.get("message", ""),
            "pickup_date": request.POST.get("pickup_date", ""),
            "pickup_time": request.POST.get("pickup_time", ""),
            "additional_customization": request.POST.get("additional_customization", ""),
            "hidden_surprise": request.POST.get("hidden_surprise", ""),
            "notes": request.POST.get("notes", ""),
            "photo": request.FILES.get("photo", None),
        }

        # Create order and store applied discount
        order = CustomCakeOrder.objects.create(
            user=user,
            total_price=total_price,
            discount_code=discount_code,  # Store applied discount code
            discount_amount=discount_amount,  # Store applied discount amount
            **cake_data
        )

        messages.success(request, "Your custom cake order has been placed successfully!")
        return redirect("CustomCakeCheckout", order_id=order.id)

    return render(request, "Customizeorder.html", {
        "user": user,
        "total_price": total_price,
        "discount_code": discount_code
    })


def calculate_discount(total_price, discount_code):
    try:
        discount = Discount.objects.get(
            code=discount_code, is_active=True,
            start_date__lte=now(), end_date__gte=now()
        )

        # Ensure minimum order amount condition
        if discount.min_order_amount and total_price < discount.min_order_amount:
            return Decimal(0), f"Minimum order amount for this coupon is ₹{discount.min_order_amount}."

        # Calculate discount amount
        if discount.discount_type == "percentage":
            discount_amount = (total_price * discount.value) / 100
            if discount.max_discount:
                discount_amount = min(discount_amount, discount.max_discount)
        else:
            discount_amount = discount.value  # Fixed discount amount

        return discount_amount, f"Coupon applied! You saved ₹{discount_amount:.2f}."
    
    except Discount.DoesNotExist:
        return Decimal(0), "Invalid or expired discount code."

def check_coupon(request):
    """AJAX View to check if a coupon code is valid."""
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code", "").strip()

        try:
            discount = Discount.objects.get(code=coupon_code, is_active=True, start_date__lte=now(), end_date__gte=now())

            return JsonResponse({
                "status": "valid",
                "discount_type": discount.discount_type,
                "value": float(discount.value),
                "min_order_amount": float(discount.min_order_amount) if discount.min_order_amount else None,
                "max_discount": float(discount.max_discount) if discount.max_discount else None,
            })

        except Discount.DoesNotExist:
            return JsonResponse({"status": "invalid", "message": "Invalid or expired discount code."})

    return JsonResponse({"status": "error", "message": "Invalid request."})


def Customorderhis(request):
    user_id = request.session.get('user_id')  
    if not user_id:
        return redirect('Login')  

    user = User.objects.get(user_id=user_id)  
    orders_list = CustomCakeOrder.objects.filter(user=user).order_by('-created_at')  

    # Apply pagination (5 orders per page)
    paginator = Paginator(orders_list, 5)  
    page_number = request.GET.get('page')  # Get current page number from URL
    orders = paginator.get_page(page_number)  

    return render(request, 'Customorderhis.html', {'orders': orders})
def Trackcustomorder(request, order_id):
    order = get_object_or_404(CustomCakeOrder, id=order_id)
    return render(request, 'Trackcustomorder.html', {'custom_order': order})



def custom_order_details(request, order_id):
    print(f"Received request for order ID: {order_id}")
    custom_order = CustomCakeOrder.objects.get(id=order_id)
    print(f"Order found: {custom_order}")
    return render(request, 'custom_order_details.html', {"custom_order": custom_order})

def invoice_view(request, order_id):
    # Fetch the order object
    order = get_object_or_404(CustomCakeOrder, id=order_id)
    shop = Shop.objects.first()  # Assuming your shop information is linked with the order

    # Check if the 'download' parameter is present in the request
    if request.GET.get('download') == 'TRUE':  # Make sure we check for 'true'
        # Generate PDF for download
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Invoice_{order.id}.pdf"'

        # Create a buffer to write to
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Add content to the PDF (customize this part as needed)
        p.setFont("Helvetica", 12)
        p.drawString(100, 750, f"Invoice - Order #{order.id}")
        p.drawString(100, 730, f"From: {shop.shop_name}")
        p.drawString(100, 710, f"To: {order.user.first_name} ")
        p.drawString(100, 690, f"Total: ₹{order.total_price}")
        
        # Add more details from the order as needed
        p.drawString(100, 670, f"Order Date: {order.created_at.strftime('%d-%b-%Y')}")
        p.drawString(100, 650, f"Status: {order.status}")  # Use 'status' instead of 'payment_status'
        
        # Finalize PDF
        p.showPage()
        p.save()

        # Get the PDF content from the buffer and return it as a response
        buffer.seek(0)
        response.write(buffer.read())
        return response
    else:
        # For regular view, render the HTML invoice
        context = {
            'order': order,
            'shop': shop,
        }
        return render(request, 'invoicetemplate.html', context)
