#!/bin/bash

echo "========== Project running started =========="

env_activation_file=.venv/bin/activate

function activate_venv() {
    echo "Activating virtual environment"
    source .venv/bin/activate
}

if [[ -e $env_activation_file ]]; then
    echo "Creating virtual environment"
    python -m venv .venv
    sleep 4
    activate_venv
else
    activate_venv
fi

echo "Installing project requirements from requirements.txt"
pip install --upgrade pip && pip install -r requirements.txt

echo "Running makemigrations ...."
python manage.py makemigrations
echo "Applying migrations ...."
python manage.py migrate


echo "Using default database ..."
echo "DATABASE_URL='sqlite:///db.sqlite3'" > .env

echo "===== Please provide the following env variables ====="

echo -e "Django secret key: (random string, no spaces)\n"
read DJANGO_SECRET_KEY
echo "DJANGO_SECRET_KEY='$DJANGO_SECRET_KEY'" >> .env

echo -e "Input your sendgrid host password\n"
read SENDGRID_EMAIL_HOST_PASSWORD
echo "SENDGRID_EMAIL_HOST_PASSWORD='$SENDGRID_EMAIL_HOST_PASSWORD'" >> .env

echo -e "Input your cloudinary cloud name\n"
read CLOUDINARY_CLOUD_NAME
echo "CLOUDINARY_CLOUD_NAME='$CLOUDINARY_CLOUD_NAME'" >> .env

echo -e "Input your cloudinary api key\n"
read CLOUDINARY_API_KEY
echo "CLOUDINARY_API_KEY='$CLOUDINARY_API_KEY'" >> .env

echo -e "Input your cloudinary api secret key\n"
read CLOUDINARY_API_SECRET
echo "CLOUDINARY_API_SECRET='$CLOUDINARY_API_SECRET'" >> .env

echo -e "Input your stripe publishable key\n"
read STRIPE_PUBLISHABLE_KEY
echo "STRIPE_PUBLISHABLE_KEY='$STRIPE_PUBLISHABLE_KEY'" >> .env

echo -e "Input your stripe secret key\n"
read STRIPE_SECRET_KEY
echo "STRIPE_SECRET_KEY='$STRIPE_SECRET_KEY'" >> .env

echo "===== Creating the admin (superuser) ====="
read -p "Admin username: " admin_username
read -p "Admin email: " admin_email
read -ps "Admin password: " admin_password

echo "from django.contri.auth import get_user_model;User=get_user_model();User.objects.create_superuser('$admin_username','$admin_email','$admin_password')"|python3 manage.py shell

echo "FINI"

echo "===== Running the application ====="
python manage.py runserver