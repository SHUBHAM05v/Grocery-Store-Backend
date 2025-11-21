🛒 Grocery Store Backend (Django REST Framework)

A fully functional backend system for an online grocery store, built using Django REST Framework, with MySQL as the database,
Supports customers and store managers with full role-based functionality.

🚀 Features
👤 User Features
Register / Login using JWT authentication
Browse products by:
Category
Popularity
Stock availability
Add items to cart
Update / Remove items from cart
Wishlist functionality
Checkout with bill summary
Apply promo codes during checkout

🧑‍💼 Store Manager Features
Add / Edit / Delete Products
View Sales Reports:
Most sold
Least sold
Category-wise analytics
Create / Update / Delete Promo Codes
Low-stock Alerts (Products below threshold)
Manager-only APIs (secured)

🏗️ Tech Stack
Python 3.x
Django 4.x
Django REST Framework
MySQL
Simple JWT Authentication

⚙️ Installation & Setup
cd grocery

📦 Create Virtual Environment
python -m venv env

📥 Install Dependencies
pip install -r requirements.txt

🛢️ Configure Database
Update your settings.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'grocery',
        'USER': 'root',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': 3306,
    }
}

🔄 Run Migrations
python manage.py makemigrations
python manage.py migrate

▶️ Run Server
python manage.py runserver

🔐 Authentication
System uses JWT authentication:
/auth/register/
/auth/login/
/auth/me/ (get current user)

Include token in headers:
Authorization: Bearer <your_token>
