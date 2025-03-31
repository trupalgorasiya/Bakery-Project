# from django.db import models 
from django.db import models
from django.contrib.auth.hashers import make_password
from decimal import Decimal
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from sweetdelightsapp1.utils import send_status_update_email  # Import the function
#userProfile
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    # last_name = models.CharField(max_length=15)
    dob_date = models.DateField()
    email_id = models.EmailField(max_length=45, unique=True)
    password = models.CharField(max_length=128)
    confirm_password = models.CharField(max_length=128)
    contact_no = models.CharField(max_length=10)
    address = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        # Automatically hash the password if it's not already hashed
        if not self.password.startswith('pbkdf2_'):  # Check if password is already hashed
            self.password = make_password(self.password)
        super().save(*args, **kwargs)  # Call the parent class's save method

    def __str__(self):
        return self.first_name 
    

#Product 

# Main Category (e.g., Cakes, Cupcakes, etc.)
class MainCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)  # Image upload path
    description = models.TextField(blank=True, null=True)  # Optional description

    def __str__(self):
        return self.name
    
# SubCategory (e.g., Vanilla, Red Velvet, etc. for Cakes)
class SubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE)  # Linked to Main Category
    name = models.CharField(max_length=50)
    description = models.TextField()  # Add description field for subcategories
    image = models.ImageField(upload_to='subcategory_images/', blank=True, null=True)  # Image field

    def __str__(self):
        return f"{self.main_category.name} - {self.name}"

class Ingredient(models.Model):
    name = models.CharField(max_length=255)  # e.g., Sugar, Egg, Flour

    def __str__(self):
        return self.name

class Product(models.Model):
    # Auto-generated primary key
    product_id = models.AutoField(primary_key=True)  # Auto-incrementing integer field

    # Define which category the product belongs to (Main or Sub Category)
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True, related_name="products")
    ingredients = models.ManyToManyField(Ingredient, through='ProductIngredient')
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    price_options = models.JSONField(default=list)  # Example: ['1kg , ₹499', '2kg , ₹949', '3kg , ₹1399']
    stock = models.PositiveIntegerField()  # Stock quantity
    
    # A boolean flag to distinguish if the product belongs directly to the main category or a subcategory
    is_main_category_product = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.subcategory:  # If no subcategory, this is a main category product
            self.is_main_category_product = True
        else:
            self.is_main_category_product = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)  # e.g., "60% Egg", "Low Sugar", "Sugar-Free"

    def __str__(self):
        return f"{self.product.name} - {self.ingredient.name}: {self.description}"
    
    
class Discount(models.Model):
    discount_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Optional discount code
    discount_type = models.CharField(max_length=20, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed')])
    value = models.DecimalField(max_digits=10, decimal_places=2)  # Discount amount or percentage
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Minimum order value for discount
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Max discount amount for percentage type
    start_date = models.DateTimeField(null=True, blank=True)  # Discount start time
    end_date = models.DateTimeField(null=True, blank=True)  # Discount expiry time
    is_active = models.BooleanField(default=True)  # If the discount is currently active

    def __str__(self):
        return f"{self.code} - {self.discount_type} ({self.value})"

#cart
class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)  # Unique ID for each cart item
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to user
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Link to product
    selected_price_option = models.CharField(max_length=255)  # Store the selected price option (string from price_options)
    quantity = models.PositiveIntegerField(default=1)  # Number of items
    created_at = models.DateTimeField(auto_now_add=True)  # When added to cart
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)  # Link discount
    
    class Meta:
        unique_together = ('user', 'product', 'selected_price_option')

    def __str__(self):
        return f"{self.user.first_name} - {self.product.name} ({self.quantity})"
    
#wishlist
class Wishlist(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)  # Assuming you have a User model
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # Linking to Product model
    added_at = models.DateTimeField(auto_now_add=True)  # Timestamp when added

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate wishlist entries

    def __str__(self):
        return f"{self.user} - {self.product}"
    
#payment
class ProductPayment(models.Model):
    payment_id = models.CharField(max_length=100, primary_key=True)  # Unique Payment ID
    payment_datetime = models.DateTimeField(auto_now_add=True)  # Auto-filled when created
    payment_method = models.CharField(max_length=50)  # Example: "Credit Card", "UPI", etc.
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total paid amount
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # Ensure ForeignKey is correctly set
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed')
    ], default='Pending')  # Payment status

    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"

# Custom Cake Order Model (Define this first)
class CustomCakeOrder(models.Model):
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('processing', 'Processing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cake_type = models.CharField(max_length=50)
    size = models.CharField(max_length=50)
    shape = models.CharField(max_length=50)
    flavor = models.CharField(max_length=50)
    filling = models.CharField(max_length=50)
    icing = models.CharField(max_length=50)
    cake_layers = models.CharField(max_length=50)
    occasion = models.CharField(max_length=50, null=True, blank=True)
    cake_texture = models.CharField(max_length=50, null=True, blank=True)
    sweetness_level = models.CharField(max_length=50)
    serving_size = models.CharField(max_length=50)
    cake_theme = models.TextField(null=True, blank=True)
    allergy_info = models.TextField(null=True, blank=True)
    egg_preference = models.CharField(max_length=20, choices=[('with_egg', 'With Egg'), ('without_egg', 'Without Egg')])
    dietary_preferences = models.TextField(null=True, blank=True)
    extra_addons = models.TextField(null=True, blank=True)
    packaging = models.TextField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    pickup_date = models.DateField(null=True, blank=True)
    pickup_time = models.TimeField(null=True, blank=True)
    additional_customization = models.TextField(null=True, blank=True)
    hidden_surprise = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='cake_orders/', null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    admin_response = models.TextField(null=True, blank=True)
    order_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    is_different_address = models.BooleanField(default=False)  # If checked, true
    shipping_address = models.TextField(null=True, blank=True)  # Store the new address if checkbox is checked
    # Linking to Payment and Order
    payment = models.ForeignKey('ProductPayment', on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.OneToOneField('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name="custom_cake_order")
    def __str__(self):
        return f"Custom Cake Order by {self.user.first_name} - {self.status}"

    def save(self, *args, **kwargs):
        """Override save method to detect status changes and send email updates."""
        if self.pk:  # Check if the instance already exists
            previous_order = CustomCakeOrder.objects.get(pk=self.pk)
            if previous_order.status != self.status:  # Status has changed
                send_status_update_email(self)  # Send status update email

        super().save(*args, **kwargs)
#order
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)  # Auto-incrementing order ID
    order_datetime = models.DateTimeField(auto_now_add=True)  # Auto-set when order is placed
    delivery_status = models.CharField(
        max_length=20,
        choices=[('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')],
        default='Processing'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total order cost
    payment = models.ForeignKey(ProductPayment, on_delete=models.CASCADE)  # Link to Payment
    # Shipping Address Fields
    is_different_address = models.BooleanField(default=False)  # If checked, true
    shipping_address = models.TextField(null=True, blank=True)  # Store the new address if checkbox is checked
    # Link to User instead of separate customer fields
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0.00))
    

    def __str__(self):
        return f"Order {self.order_id} - {self.delivery_status} - User {self.user.first_name}"

#Orderdetails
class OrderDetails(models.Model):
    order_detail_id = models.AutoField(primary_key=True)  # Unique ID for each order detail
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # Links to Order
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Links to Product
    quantity = models.PositiveIntegerField(default=1)  # Quantity of product in the order
    selected_price_option = models.CharField(max_length=50)  # Stores the selected price option (e.g., "1kg , ₹499")
    cake_customization = models.TextField(blank=True, null=True) 
    
    def __str__(self):
        return f"Order {self.order.order_id} - {self.product.name} ({self.selected_price_option}) x {self.quantity}"


#Order Cancel
class OrderCancel(models.Model):
    cancel_id = models.AutoField(primary_key=True)  # Unique cancel request ID
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # Links to order
    cancel_reason = models.TextField()  # Reason for cancellation
    cancel_datetime = models.DateTimeField(auto_now_add=True)  # When was it canceled?
    

    def __str__(self):
        return f"Cancel Order {self.order.order_id}"

class OrderCancelDetails(models.Model):
    cancel_detail_id = models.AutoField(primary_key=True)
    cancel = models.ForeignKey(OrderCancel, on_delete=models.CASCADE)  # Links to cancellation
    order_detail = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)  # Specific product canceled
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Track which product is canceled
    quantity_canceled = models.PositiveIntegerField(default=1)  # How many units canceled
    cancel_reason = models.TextField(null=True, blank=True)  # Reason for canceling this specific item

    refund_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Processed', 'Processed'), ('Not Applicable', 'Not Applicable')],
        default='Pending'
    )  # Refund processing status
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # 💰 Refundable amount

    def __str__(self):
        return f"Cancel {self.cancel.order.order_id} - {self.product.name} x {self.quantity_canceled}"

#Order Return
class OrderReturn(models.Model):
    return_id = models.AutoField(primary_key=True)  # Unique return request ID
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # Links to order
    return_datetime = models.DateTimeField(auto_now_add=True)  # When return was requested
    

    def __str__(self):
        return f"Return {self.order.order_id}"

#Order Return Details
class OrderReturnDetails(models.Model):
    return_detail_id = models.AutoField(primary_key=True)
    order_return = models.ForeignKey(OrderReturn, on_delete=models.CASCADE)  # Links to return request
    order_detail = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)  # Product being returned
    quantity_returned = models.PositiveIntegerField(default=1)  # How many units returned
    refund_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Processed', 'Processed'), ('Not Applicable', 'Not Applicable')],
        default='Pending'
    )  # Has the refund been processed?
    return_reason = models.TextField()  # Why is the return requested?
    return_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )  # Status of return
    
    def __str__(self):
        return f"Return {self.order_return.order.order_id} - {self.order_detail.product.name} x {self.quantity_returned}"

#Shop Details
class Shop(models.Model):
    shop_name = models.CharField(max_length=255)
    shop_address = models.TextField()
    email_id = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='shop_images/', null=True, blank=True)

    def __str__(self):
        return self.shop_name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Use your custom User model
    rating = models.IntegerField(default=5)  # Rating out of 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)  # Marks verified purchases
    photo = models.ImageField(upload_to="reviews/", blank=True, null=True)  # Image upload


class ProductInquiry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    question = models.TextField()
    response = models.TextField(blank=True, null=True)  # Admin response
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inquiry by {self.user.first_name} - {self.product.name}"
    

