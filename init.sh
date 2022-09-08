#! bin/sh

db=db.sqlite3
if [ -e "$db" ]; then
    echo "-------------------------------- REMOVING EXISTING DB --------------------------------"
    rm $db
fi
touch .env
echo "Please provide the following details"

echo -n "DATABASE URL (Postgress): "
while [[ $DATABASE_URL = "" ]]; do
    read DATABASE_URL
done
echo "DATABASE_URL=$DATABASE_URL" > .env

echo -n "DJANGO SECRET KEY (Your secret sequence of random characters): "
while [[ $DJANGO_SECRET_KEY = "" ]]; do
    read DJANGO_SECRET_KEY
done
echo "DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY" >> .env

echo -n "SENDGRID EMAIL HOST PASSWORD (From your sendgrid account): "
while [[ $SENDGRID_EMAIL_HOST_PASSWORD = "" ]]; do
    read SENDGRID_EMAIL_HOST_PASSWORD
done
echo "SENDGRID_EMAIL_HOST_PASSWORD=$SENDGRID_EMAIL_HOST_PASSWORD" >> .env

echo -n "CLOUDINARY CLOUD NAME (From your cloudinary account): "
while [[ $CLOUDINARY_CLOUD_NAME = "" ]]; do
    read CLOUDINARY_CLOUD_NAME
done
echo "CLOUDINARY_CLOUD_NAME=$CLOUDINARY_CLOUD_NAME" >> .env

echo -n "CLOUDINARY API KEY (From your cloudinary account): "
while [[ $CLOUDINARY_API_KEY = "" ]]; do
    read CLOUDINARY_API_KEY
done
echo "CLOUDINARY_API_KEY=$CLOUDINARY_API_KEY" >> .env

echo -n "CLOUDINARY API SECRET (From your cloudinary account): "
while [[ $CLOUDINARY_API_SECRET = "" ]]; do
    read CLOUDINARY_API_SECRET
done
echo "CLOUDINARY_API_SECRET=$CLOUDINARY_API_SECRET" >> .env

echo -n "STRIPE PUBLISHABLE KEY (From your stripe account): "
while [[ $STRIPE_PUBLISHABLE_KEY = "" ]]; do
    read STRIPE_PUBLISHABLE_KEY
done
echo "STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE_KEY" >> .env

echo -n "STRIPE_SECRET_KEY (From your stripe account): "
while [[ $STRIPE_SECRET_KEY = "" ]]; do
    read STRIPE_SECRET_KEY
done
echo "STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY" >> .env

echo -n "Admin username: "
while [[ $admin_username = "" ]]; do
    read admin_username
done

echo -n "Admin email: "
while [[ $admin_email = "" ]]; do
    read admin_email
done

echo -n "Admin password: "
while [[ $admin_password = "" ]]; do
    read -s admin_password
done

python manage.py migrate

echo "from django.contri.auth import get_user_model; User=get_user_model(); User.objects.create_superuser('$admin_username','$admin_email','$admin_password')"|python3 manage.py shell