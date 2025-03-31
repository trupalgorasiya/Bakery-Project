# 🎂 Bakery Management and Custom Cake Order System

## 📌 Description
A dynamic **Bakery Custom Order System** built with Django, allowing users to customize their cake orders and 
receive real-time updates via email. The system includes an admin panel where orders can be managed, and users 
are notified of order status updates through email notifications. Users can also browse and purchase various 
bakery products, including cakes, pastries, and breads, cupcakes, waffls.

## 🚀 Features
- 🎂 **Custom Cake Orders**: Users can customize cake flavors, sizes, designs, and messages.
- 🍰 **Bakery Products**: Browse and purchase a variety of bakery items such as cakes, pastries, breads, and cookies.
- 📩 **Email Notifications**: Users receive email updates for order submission, processing, and status changes.
- 🔄 **Order Tracking**: Customers can check order status in real-time.
- 🎟️ **Discount & Offers System**: Customers can apply discounts during checkout.
- 🛒 **Cart Management**: Users can add cakes and other bakery items to the cart before placing orders.
- 📊 **Admin Panel (Jazzmin UI)**: Manage orders, customers, and generate reports.
- 💳 **Payment Integration**: Secure online payments using Razorpay.
- 📂 **Database**: Uses **MySQL** for storing user orders, products, and transactions.

## 🛠️ Technologies Used
- **Backend**: Django, Python
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: MySQL
- **Payment Gateway**: Razorpay API
- **Admin Panel**: Django Jazzmin

## 📥 Installation
Follow these steps to set up the project on your local machine:

1. **Clone the repository:**  
   ```sh
   git clone https://github.com/yourusername/bakery-order-system.git
   cd bakery-order-system
   ```

2. **Create a virtual environment:**  
   ```sh
   python -m venv venv
   ```

3. **Activate the virtual environment:**  
   - Windows: `venv\Scripts\activate`  
   - Mac/Linux: `source venv/bin/activate`

4. **Install dependencies:**  
   ```sh
   pip install -r requirements.txt
   ```

5. **Configure MySQL Database:**  
   Update `settings.py` with your MySQL credentials:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'your_database_name',
           'USER': 'your_database_user',
           'PASSWORD': 'your_database_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

6. **Apply migrations:**  
   ```sh
   python manage.py migrate
   ```

7. **Run the development server:**  
   ```sh
   python manage.py runserver
   ```

8. **Open in the browser:**  
   ```
   http://127.0.0.1:8000/
   ```


## 🤝 Contribution
Contributions are welcome! Feel free to fork the repository and submit a pull request.

## 📜 License
This project is licensed under the **MIT License**.

## 📧 Contact
For any queries, reach out at [trupalgorasiya510@gmail.com](trupalgorasiya510@gmail.com).


