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

3. **Activate Virtual environment**
    - On macOs and Linux
    ```
    source venv/bin/activate  
    ```

    - On Windows
    ```
    venv\Scripts\activate
    ```

3. **Install required packages**
    ```
    pip install -r requirements.txt
    ```

4. **Setup your PostgreSQL database**

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

5. **Create .env File on root directory**
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

6. **Apply migrations**
    ```
    python manage.py migrate
    ```

7. **Create Superuser**
    ```
    python manage.py createsuperuser
    ```

8. **Run Application**
    ```
    python manage.py runserver
    ```

    Access the application on your web browser and go to your defined host:port (localhost:8000)


## Code Explanation
*Note: API details will be provided on postman collection*

1. **Authentication system**
    
    - **User Registration:**
        [Registration View](https://github.com/suryahangam/mnk-banking-system/blob/main/authentication/views.py#L23)
        [Registration Serializer](https://github.com/suryahangam/mnk-banking-system/blob/main/authentication/serializers.py#L5)

    ```
    class UserRegistrationView(CreateAPIView):
        ...

    class UserRegistrationSerializer(serializers.ModelSerializer):
        ...
    ```

    Endpoints:
    ```
    api/auth/register/
    ```

    **UserRegistrationView**

    **Purpose:** 
    This view manages user registration through a POST request. It enables new users to create accounts in your application.

    **Inheritance:** 
    Inherits from CreateAPIView, which provides built-in methods for handling creation requests.

    **Serializer:** Uses UserRegistrationSerializer to validate input data and create user instances.

    **POST Method:** The post() method handles incoming registration requests, validates the data, and creates a new user if the        validation succeeds. It returns a response with the user data upon successful registration.


    **UserRegistrationSerializer**

    **Purpose:** 
    This serializer validates the data submitted during user registration and manages the creation of user instances.

    **Fields:**
        - password and confirm_password: Used to ensure the user sets a valid password, with confirmation for accuracy.
        - email: The unique email address for the user.
        - mobile_number: Stores the user's mobile number(Optional).

    **Validation Methods:**
    **create():** Handles user creation logic, including password hashing.
    **validate():** Ensures that the password and confirmation match.
    **validate_email():** Checks for the uniqueness of the email address in the database, raising an error if it already exists.

    These components collectively enable a secure and validated user registration process, ensuring that user data is correctly handled and stored in your Django application.


    - **Login**    
        [Login API](https://github.com/suryahangam/mnk-banking-system/blob/main/authentication/views.py#L62)
        [Token Verification](https://github.com/suryahangam/mnk-banking-system/blob/main/authentication/views.py#L157)

    ```
    class CustomTokenObtainPairView(TokenObtainPairView):
        ...

    class TwoFactorVerifyView(APIView):
        ...
    ```

    Endpoints:
    ```
    1. api/auth/token/
    2. api/auth/token/verify-2fa/
    ```

    **Custom Token Obtain Pair View (JWT Integration with 2FA)**
    This view extends the standard token generation functionality provided by Simple JWT to incorporate an additional layer of security with Two-Factor Authentication (2FA).

    - **JWT Token Generation:** 
    Using Simple JWT, this view allows users to log in by providing their email and password to obtain an access token and a refresh token.

    -**Two-Factor Authentication (2FA):** 
    If the user has 2FA enabled, the system generates a One-Time Password (OTP) via the pyotp library. The OTP is sent to the user through their preferred method (email or SMS).

    -**Modified Token Response:** 
    When 2FA is required, the response omits the token pair (access and refresh tokens) and instead informs the user that they need to verify their OTP. This adds an extra security step.


    **Two-Factor Verify View (OTP Verification)**
    This view allows users to verify the One-Time Password (OTP) they received via their selected 2FA method (email or SMS). After successful verification, a new JWT access token and refresh token are provided, granting full access to protected resources.

    -**OTP Verification:** 
    Users submit their user ID and the OTP they received. The system verifies the OTP using the same time-based OTP mechanism (TOTP) with a 5-minute validity window.

    -**Token Issuance:** 
    If the OTP is correct, the user is provided with a valid JWT access token and refresh token.

    -**Error Handling:** 
    If the OTP is incorrect, the system responds with an error message, indicating that the verification failed.

    **Key Features:**
    - **JWT (Simple JWT):** Provides stateless authentication with token generation for user sessions.
    - **Two-Factor Authentication (2FA):** Adds an additional security layer by requiring users to verify their identity with an OTP.
    - **Time-based OTP:** Using the pyotp library, the OTP is valid for a short window (5 minutes).
    - **Token Refresh:** After successful OTP verification, the user is issued a new JWT refresh token for maintaining their session.

2. **Account Management**

    - **Account Creation (Single + Bulk)**
        [Account Create View](https://github.com/suryahangam/mnk-banking-system/blob/main/accounts/views.py#L14)
        [Account Create Serializer](https://github.com/suryahangam/mnk-banking-system/blob/main/accounts/serializers.py#L10)

    ```
    class AccountCreateView(generics.CreateAPIView):
        ...

    class AccountSerializer(serializers.ModelSerializer):
        ...
    ```

    Endpoints:
    ```
    api/accounts/create-account/
    ```


    **AccountCreateView:**
    
    This view is responsible for handling the creation of new accounts, specifically for users with admin privileges. Here are the key points:

    - **Inherits from CreateAPIView:** This is a built-in Django REST framework class-based view used for creating model instances.

    - **Permissions:**

        The view enforces two permissions:
            **IsAuthenticated:** Ensures that only authenticated users can access this endpoint.
            **IsAdmin:** Ensures that only users with admin rights can create new accounts.
            **serializer_class:** This specifies the serializer to be used for validating the incoming data and serializing the response, in this case, AccountSerializer.

    - **post method:**

    - Handles POST requests for creating accounts.
    - Supports both single and bulk account creation based on whether the incoming request data is a single object in a list or multiple objects.
    - Once validated through the serializer, the method saves the account(s) and returns a success message along with the created   account IDs.


    **AccountSerializer:**
    The serializer is responsible for validating and serializing data related to the account model. It ensures that the data conforms to the necessary constraints before being saved in the database.

    - **user_details:** This is a nested serializer (UserListSerializer) that is used to include user information when retrieving account details.

    - **transactions:** This is a custom field defined by SerializerMethodField to display a list of all transactions associated with the account (both sent and received).

    - **Fields:**

        - The Meta class defines the fields that will be serialized for the Account model, including attributes like first_name, last_name, balance, and currency.
        - Several fields like balance, currency, and account_number are read-only, meaning they cannot be updated directly by users.

    - **Custom Validation:**

        - validate_date_of_birth: Ensures that the user's date of birth is a past date.
        - validate_postal_code: Checks if the postal code conforms to the UK postal code format using a regular expression.
        - validate_currency: Ensures that only valid currencies (USD, GBP, EUR) are accepted.
        - validate_interest_rate: Ensures that the interest rate is not negative.
        
    - **create method:**

    Supports both single account creation and bulk creation. If multiple accounts are provided, it uses bulk_create() for efficient database insertion.

    **update method:**
    *(This is for update account functionality)*

    Handles the updating of existing account data by iterating over the provided fields and updating the corresponding account attributes. Finally, it saves the instance.

    Together, the view and serializer work to handle the creation of new accounts, with the necessary validation and data handling. The AccountCreateView ensures that only admins can create accounts, while AccountSerializer ensures the data being provided is valid, such as correct postal codes and non-negative interest rates.

    - **Account Update**
        [Account Update View](https://github.com/suryahangam/mnk-banking-system/blob/main/accounts/views.py#L37)
        *both create and update uses same serializer*

    ```
    class AccountUpdateView(generics.UpdateAPIView):
        ...
    ```

    Endpoints:
    ```
    api/accounts/<int:account_pk>/update-account/
    ```

    **AccountUpdateView:**

    This view is designed for updating an account. It allows authenticated users to update their account information, while admin users have additional permissions to update any account.

    **Who can update?:**

    - Admins can update any account.
    - Regular users can only update their own account.
    - Partial updates are supported, meaning users can update only a subset of the fields.
    - Permissions are strictly enforced to ensure security:
    - Regular users cannot access or update accounts they do not own.

    **Key Components:**
    1. **permission_classes:**

        The view uses two permission classes:
        - IsAuthenticated: Ensures that only logged-in users can access this view.
        - IsAccountOwnerOrAdmin: A custom permission class that allows either the account owner or admin users to update the account.
        
    2. **queryset:**

        The queryset is set to ```Account.objects.all()```, meaning it will retrieve all account objects from the database. This is used internally for retrieving the objects based on conditions.

    3. **serializer_class:**

        The view uses AccountSerializer to handle the serialization of data and validation when updating account information.
        
    4. **get_object method:**

        - This method customizes how the specific account object is retrieved based on the authenticated user's role:

            - **Admin users:** They can update any account. The view gets the account_id from the URL (via self.kwargs.get('pk')) to fetch the desired account.
            - **Regular users:** They can only update their own account. The view fetches the account where the user is the owner (user=user).

        - The method uses Django's get_object_or_404 helper to retrieve the account object. If the account doesn't exist, it will return a 404 Not Found response.

    5. **put method:**

        put(request, *args, **kwargs) is responsible for handling HTTP PUT requests to update the account data. This is where the actual update happens:

        - Retrieve the account: It calls get_object() to retrieve the correct account, ensuring that only the appropriate account is updated.
        - Serializer for validation: A serializer (AccountSerializer) is initialized with the account instance and the incoming request data. The argument partial=True allows partial updates, meaning the user doesn't need to provide all fields — only the ones they want to update.
        - Validation: The serializer's is_valid() method checks whether the provided data is valid. If not, it raises a ValidationError.
        - Save changes: Once validated, the serializer.save() method updates the account object in the database.
        - Response: A success message is returned with a 200 OK status, along with the account_id of the updated account.

    - **Account Listing (Search & Filtering)**
        [Account List View](https://github.com/suryahangam/mnk-banking-system/blob/main/accounts/views.py#L77)

    ```
    class AccountListView(generics.ListAPIView):
        ...
    ```

    Endpoints:
    ```
    api/accounts/list-accounts/
    ```

    **Account Listing and Filtering Features**

    1. **AccountListView (Account Listing View):**

    The AccountListView is an API view designed to list all account records. It includes advanced features like pagination, search, and filtering to allow users to view and filter account data efficiently.

    - Permissions:
        Users must be authenticated (IsAuthenticated) and either the account owner or an admin (IsAccountOwnerOrAdmin) to access the view.

    - Pagination:
        The results are paginated using ListPagination to handle large datasets, allowing users to retrieve records in manageable chunks.

    - Filtering:
        The view supports filtering based on account attributes like account_type, user, and balance using DjangoFilterBackend and a custom AccountFilter.

    2. **AccountSerializer (Serializer for Account Data):**

    The AccountSerializer is responsible for converting Account model instances to a format suitable for API responses (serialization) and for validating incoming data when creating or updating accounts.

    - Fields:
        It serializes important fields related to user and account details, including:
            - Personal information (first_name, last_name, etc.)
            - Account-specific details (balance, currency, account_number, etc.)
            - Related transactions (using the get_transactions method).

    - Methods:
        - get_transactions(obj): Retrieves a list of all transactions (sent and received) associated with the account.
        - Validation Methods:
            - validate_date_of_birth: Ensures the date of birth is in the past.
            - validate_postal_code: Ensures the postal code follows the UK format.
            - validate_currency: Ensures the currency is one of the accepted options (e.g., USD, GBP, EUR).
            - validate_interest_rate: Ensures the interest rate is non-negative.

    - Customization:
        - The serializer supports bulk account creation when a list of data is provided.
        - Read-only fields include balance, currency, date_opened, account_number, and transactions.

    3. **ListPagination (Custom Pagination Class):**

    The ListPagination class is a custom paginator for handling API responses that list multiple items (e.g., accounts). It controls the number of items per page and allows users to customize the page size using query parameters.

    - Attributes:
        - page_size: Default number of items per page is 10.
        - page_size_query_param: Allows users to set a custom page size using a query parameter (e.g., page_size=20).
        - max_page_size: Limits the maximum number of items per page to 100.
        
    4. **AccountFilter (Custom Filter for Account Queries):**
        The AccountFilter class defines several filters that allow users to filter account records based on various fields when making API requests. This enhances the querying capabilities of the API.

    - Filter Fields:
        - account_type: Filters by account type (e.g., Savings, Current).
        - user: Filters by the associated user's ID.
        - date_opened: Filters by the date the account was opened.
        - balance_min: Filters accounts with a balance greater than or equal to a specified value.
        - balance_max: Filters accounts with a balance less than or equal to a specified value.


    - **Account Detail with related transaction history**
        [Account Detail View](https://github.com/suryahangam/mnk-banking-system/blob/main/accounts/views.py#L89)
        *both create and update uses same serializer*

    ```
    class AccountDetailView(generics.RetrieveAPIView):
        ...
    ```

    Endpoints:
    ```
    api/accounts/<int:account_pk>/account-detail
    ```

    **AccountDetailView:**

    The AccountDetailView is designed to retrieve and display the details of a specific account, including the account’s transaction history. It uses Django REST framework's RetrieveAPIView, which provides an efficient way to fetch a single resource based on its primary key.

    **Key Components of AccountDetailView:**

    1. **Permission Classes:**
        The view uses IsAuthenticated and IsAccountOwnerOrAdmin permissions, ensuring that:
        
        - Authenticated users can access the view.
        - Users can only view their own account details unless they are an admin.
        - Admins have permission to view any user's account details.
    
  
    2. **Serializer:**

    - The view utilizes the AccountSerializer to transform the account data into JSON format.

    - Since this serializer includes a transactions field (using the get_transactions method), it also retrieves transaction histories related to the account, both sent and received transactions.


    3. **get_serializer_context Method:**

    - This method ensures that the request context is passed into the serializer.

    - By updating the context with {"request": self.request}, it ensures that when serializing the account data (including related transactions), the request object is available, allowing for customization in serialization (like dynamic URL generation or permissions checks).

    **How It Works:**

    - When an authenticated user sends a GET request to retrieve an account’s details, the get_object() method (inherited from RetrieveAPIView) fetches the specific account using the primary key passed in the URL.

    - The AccountSerializer processes this account and returns the details, including related transactions, in the response.
    
3. **Banking Operation**

    - **ThirdParty services used**

        1. **ClickSend Service**
            - Used ClickSend free API plan using clicksend-client in order to send SMS for OTP verification

            *Documentation: https://developers.clicksend.com/docs/messaging/sms/#operation/send-sms*

        2. **ExchangeratesAPI**
            - Used ExchangeRates API (free plan) in order to get latest exchange rates.
            (Since, free plan does not allow some base currencies so 
            Local exchange_rates.json has been used for the fallback options)

            *Documentation: https://exchangeratesapi.io/documentation/*

            - Fallback json:
            ```
            {
                "USD": {
                    "EUR": 0.85,
                    "GBP": 0.75
                },
                "EUR": {
                    "USD": 1.18,
                    "GBP": 0.88
                },
                "GBP": {
                    "USD": 1.33,
                    "EUR": 1.14
                }
            }

            ```


    - **Fund Transfer (Transcation creation)**

        [Transaction Create View](https://github.com/suryahangam/mnk-banking-system/blob/main/transactions/views.py#L19)

    ```
    class TransactionCreateView(generics.CreateAPIView):
        ...

    TransactionCreateSerializer(serializers.ModelSerializer):
        ...
    ```

    Endpoints:
    ```
    api/transactions/create/
    ```

    **Fund Transfer (Transaction Creation) Module**

    The Fund Transfer module allows authenticated users to create and manage transactions securely between accounts. This module is designed to handle various aspects of a transaction, including validation, currency conversion, and updating account balances.

    1. **TransactionCreateView:**

    - **Purpose:** 
    This class handles the creation of new transactions from one account to anoter. It is responsible for creating transaction 
    records and also updates the balance of respective user accounts.

    - **Attributes:**
        - queryset: Retrieves all transaction objects from the database.
        - serializer_class: Utilizes the TransactionCreateSerializer to validate incoming data.
        - permission_classes: Only allows authenticated users to access this view.

    - **Method:**
        **create(request, *args, kwargs):
        - Receives the transaction data, validates it, and creates a transaction.
        - Sets the transaction status to 'COMPLETED' immediately after creation due to no external processing delays.
        - Returns a JSON response indicating the status of the transaction.

    2. **TransactionCreateSerializer**

    Responsible for validating the transaction data and creating transaction instances.

    - **Fields:**

        - receiver_account_number: (write-only) the account number of the recipient.
        - amount: the amount to be transferred.
        - description: a brief description of the transaction.
        - to_currency: specifies the currency in which the recipient expects to receive funds.
    
    - **Methods:**
        - validate_to_currency: Ensures the provided currency is one of the supported options (USD, EUR, GBP).
        - validate_amount: Checks that the transfer amount is greater than zero.
        - validate: Validates overall transaction conditions including:
            - Sender and receiver accounts cannot be the same.
            - The sender must have sufficient funds.
            - Currency compatibility between sender and receiver accounts.

        - create: Handles the creation of the transaction, including any necessary currency conversion.

    3. **Currency Conversion**

        ```
        def convert_currency(self, amount, from_currency, to_currency):
            ...
        ```

        - Function: convert_currency(amount, from_currency, to_currency)
        - Purpose: Converts amounts between different currencies, applying a spread for fluctuation risks.

        - Method:
            - Retrieves the current exchange rate from a third-party API.
            - Calculates the total amount after conversion and applies a predefined spread.

    4. **Helper Function for Exchange Rate Retrieval**

        ```
        def get_latest_exchange_rate(from_currency, to_currency):
            ...
        ```

        - Function: get_latest_exchange_rate(from_currency, to_currency)
        - Purpose: Fetches the latest exchange rate from an external API or falls back to a cached JSON file if the API call fails.
        - Usage:
            - This function ensures that the transaction's conversion rates are accurate, enhancing the reliability of the fund transfer process.

    - **List Transactions**

        [List Transaction View](https://github.com/suryahangam/mnk-banking-system/blob/main/transactions/views.py#L67)

    ```
    class ListTransactionView(generics.ListAPIView):
        ...

    class TransactionSerializer(serializers.ModelSerializer):
        ...
    ```

    Endpoints:
    ```
    api/transactions/list/
    ```

    **List Transaction Feature**

    The List Transaction feature enables authenticated users to view their transaction history. This functionality includes search and filter capabilities, as well as pagination, making it easier for users to navigate through potentially large datasets. Below is a breakdown of the key components involved in this feature.


    1. **ListTransactionView**

    - Purpose: This view class handles the retrieval and presentation of transaction data to the user.

    - Attributes:

        - queryset: Retrieves all transaction objects from the database.
        - serializer_class: Specifies the TransactionSerializer to serialize transaction data into JSON format.
        - pagination_class: Utilizes ListPagination to paginate the transaction list, ensuring manageable chunks of data are sent to the client.
        - filterset_class: Uses TransactionFilter to apply filters based on user input.
        - filter_backends: Combines Django Filter and SearchFilter to allow filtering and searching of transactions.
        - permission_classes: Ensures that only authenticated users or users with specific permissions can access the view.

    2. **TransactionSerializer**

    - Purpose: This serializer converts Transaction model instances to and from JSON format. It defines the fields to be included in the serialized output and provides methods for custom serialization.

    - Attributes:

        - id: The unique identifier for the transaction.
        - sender_email: The email address of the sender, retrieved from the sender's user account.
        - receiver_email: The email address of the receiver, retrieved from the receiver's user account.
        - amount: The amount involved in the transaction.
        - timestamp: The date and time when the transaction occurred.
        - status: The current status of the transaction (e.g., completed, pending).
        - description: A brief description of the transaction.
        - transaction_type: The type of transaction based on the user making the request.

    - Methods:
        - get_transaction_type: Returns the type of transaction based on the current authenticated user.

    - **Transaction Detail View**
    [Detail Transaction View](https://github.com/suryahangam/mnk-banking-system/blob/main/transactions/views.py#L76)

    ```
    class DetailTransactionView(generics.RetrieveAPIView):
        ...

    class TransactionSerializer(serializers.ModelSerializer):
        ...
    ```

    Endpoints:
    ```
    api/transactions/<int:transaction_pk>/detail
    ```

    **DetailTransactionView**

    The DetailTransactionView is an API endpoint for retrieving detailed information about a specific transaction. It extends Django REST Framework's RetrieveAPIView to fetch a single transaction instance from the database.

    **Key Features**
        - Transaction Retrieval: The view fetches transactions using Transaction.objects.all(), allowing users to access their transaction details.

        - Serializer Usage: It uses TransactionSerializer to convert transaction data into a user-friendly JSON format.

        - Permission Control: Access is restricted to authenticated users, specifically the transaction owner or an admin, ensuring data privacy and security.

    - **Currency conversion API endpoint**
    [Currency convert Endpoint](https://github.com/suryahangam/mnk-banking-system/blob/main/transactions/views.py#L85)

    ```
    class CurrencyConverterView(APIView):
        ...
    ```

    API endpoint to display the currency conversion rate before making a transaction.

    This view allows authenticated users to input an amount and a target currency
    for conversion. The API calculates the converted amount based on real-time 
    exchange rates and adds a conversion spread, displaying the total converted amount.

    **Key Features**

    - **Authentication Requirement:** Access to this view is restricted to authenticated users. This ensures that only authorized users can perform currency conversions based on their account details.

    - **Input Validation:** The view utilizes the CurrencyConverterSerializer to validate incoming data. This includes checks to ensure that the user is not attempting to convert funds into the same currency they currently hold, which would be redundant.

    - **Real-time Exchange Rates:**

        - The view fetches the latest exchange rates using a helper function, get_latest_exchange_rate().
        - It applies these rates to calculate the converted amount from the user's account currency to the target currency.
    
    - **Conversion Spread:** A predefined conversion spread is added to the converted amount. This spread accounts for fluctuations in currency rates and ensures that users are informed about the actual costs associated with their currency conversions.

    - **Response Structure:** Upon successful conversion, the view returns a JSON response containing:

        - Original Amount: The amount being converted.
        - Converted Amount: The total amount after conversion and spread adjustments.
        - Exchange Rate: The rate applied for the conversion, providing transparency to users.

    **Use Cases**

    Transaction Preparation: Users planning to transfer funds in different currencies can utilize this endpoint to understand the conversion implications on their funds before proceeding with a transaction.

## contributing
## license
## Contact information

**Email**: limbusuryapratap14@gmail.com
**Phone**: +44-7887638302
**LinkedIn**: https://www.linkedin.com/in/suryahangam/  
