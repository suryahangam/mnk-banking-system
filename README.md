# Banking System Project

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Code Explanation](#code-explanation)
- [Contributing](#contributing)
- [License](#license)
- [Contact Information](#contact-information)

## Project Overview
The Banking System REST API is a robust backend application designed to facilitate comprehensive banking operations without a direct user interface. Developed using Django and PostgreSQL, this API provides essential functionalities for user management, multi-currency transactions, and secure authentication, making it suitable for integration into various client applications.

## Features
- User authentication and authorization
- Two Factor authentication(2FA) using OTP via Email and SMS
- First user automatically set as admin
- Account/s creation (intial 10,000 USD) and management (Automatic account number generation, by default user activation)
- Multi currency fund transfer (USD, GBP, EUR)
- Currency conversion with real time exchange rates for (USD, GBP, EUR)
- Transaction handling (Listing, filtering)
- Notification system via email and SMS

## Technologies Used
- Django: Web framework for building the application
- PostgreSQL: Database management system
- Django REST Framework: For building the API
- clicksend-client: A library for sending SMS and email notifications using the ClickSend service.
- ExchangeratesAPI: API for real time currency exchange rates
- django-otp: For one time and time sensitive 2FA code generation
- djangorestframework-simplejwt: JSON Web Tokens (JWT) for secure user authentication.
- requests: A simple HTTP library for Python, used for making network requests.
- psycopg2-binary: A PostgreSQL adapter for Python that allows Django to connect to the PostgreSQL database.

## Setup Instructions
Follow these steps to install and run the project:

### Prerequisites
- Python 3.8 or higher
- PostgreSQL
- Virtual Environment (optional but recommended)
- All packages listed on requirements.txt

### Installation Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/banking_system.git
   cd banking_system
   ```


2. **Set up a Virtual environment(Optional):**
    ```
    python3 -m venv venv
    ```
    If you don't have venv installed, you can install it by running the following command:
    ```
    python3 -m pip install venv
    ```

    ### Activate Virtual environment
    - On macOs and Linux
    ```
    source venv/bin/activate  
    ```

    - On Windows
    ```
    venv\Scripts\activate
    ```

2. **Install required packages**
    ```
    pip install -r requirements.txt
    ```

3. **Setup your PostgreSQL database**

    Create a database and user in PostgreSQL.
    Example:

    - Connect to PostgreSQL database
    ```
    psql -d postgres -U your-username
    ```   

    - Once connected, create database and user
    ```
    CREATE DATABASE database_name;
    CREATE USER username WITH PASSWORD 'yourpassword';
    GRANT ALL PRIVILEGES ON DATABASE database_name TO username;
    ```

4. **Create .env File on root directory**
    (Will be provided)
    Add following environment variables on .env:
    ```    
    SECRET_KEY='project-security-key'
    DEBUG= True or False

    ALLOWED_HOSTS='localhost'


    # Email Configuration
    EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST='smtp.gmail.com'
    EMAIL_PORT=587
    EMAIL_USE_TLS=True
    EMAIL_HOST_USER='your-email-host'
    EMAIL_HOST_PASSWORD='your-email-app-password'  

    # JWT Configuration
    JWT_ACCESS_TOKEN_LIFETIME='5'  # Minutes
    JWT_REFRESH_TOKEN_LIFETIME='1440'  # Days (1 day)

    # ClickSend Configuration
    CLICKSEND_API_KEY='clicksend-api-key'
    CLICKSEND_USERNAME='clicksend-username'


    # Currency exchange API
    EXCHANGE_RATE_API_KEY='your-exchange-rate-api-key'
    EXCHANGE_RATE_API_URL='https://api.exchangeratesapi.io/v1/latest'

    CURRENCY_CONVERSION_SPREAD=0.01

    # DATABASE CONFIGURATION
    DATABASE_ENGINE = 'django.db.backends.postgresql'
    DATABASE_NAME = 'your-database-name'
    DATABASE_USER = 'your-database-user'
    DATABASE_PASSWORD = 'your-database-password'
    DATABASE_HOST = 'your-database-host (localhost)'
    DATABASE_PORT = '5432'
    ```

5. **Apply migrations**
    ```
    python manage.py migrate
    ```

5. **Create Superuser**
    ```
    python manage.py createsuperuser
    ```

    Access the application on your web browser and go to your defined host:port (localhost:8000)


## Code Explanation

1. **Authentication system**
- ### User Registration & Login:

## Contact information