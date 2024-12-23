# CollabSphere Authentication System Documentation


## Overview

The CollabSphere Authentication System is a comprehensive user authentication and authorization solution built with Django REST Framework. It provides secure email-based authentication, role-based access control, and real-time user status tracking.


### API Endpoints

- Authentication Endpoints

1. User Registration

- Endpoint: `/register/`
- Method: POST
- Purpose: Register new users in the system
- Request Body:

```
{
    "email": "user@example.com",
    "username": "username",
    "full_name": "Full Name",
    "password": "securepassword",
    "password2": "securepassword"
}

```

Success Response (201 Created):

```
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "username",
        "full_name": "Full Name"
    },
    "tokens": {
        "refresh": "refresh_token",
        "access": "access_token"
    },
    "message": "Verification email sent"
}

```

2. User Login

- Endpoint: `/login/`
- Method: POST
- Purpose: Authenticate users and provide access tokens
- Request Body:

```
{
    "email": "user@example.com",
    "password": "securepassword",
    "device_token": "fcm_token",
    "device_type": "web"
}

```

- Success Response (200 OK):
  
```

{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "username"
    },
    "tokens": {
        "refresh": "refresh_token",
        "access": "access_token"
    },
    "permissions": {
        "can_moderate": false,
        "can_manage_users": false
    }
}

```

3. User Logout

- Endpoint: `/logout/`
- Method: POST
- Purpose: Log out users and invalidate tokens
- Headers Required: Authorization: Bearer <access_token>
- Request Body:
```

{
    "device_type": "web",
    "device_token": "fcm_token"
}

```

- Success Response (200 OK):

```
{
    "message": "Successfully logged out"
}

```

- Email Verification Endpoints
  
4. Verify Email

- Endpoint: `/verify-email/<token>/`
- Method: GET
- Purpose: Verify user's email address

- Success Response (200 OK):
  
```

{
    "message": "Email successfully verified"
}

```
5. Resend Verification Email

- Endpoint: `/resend-verification/`
- Method: POST
- Purpose: Resend verification email to user
- Headers Required: Authorization: Bearer <access_token>
  
- Success Response (200 OK):

```
{
    "message": "Verification email sent"
}

```

- Token Management Endpoints

6. Obtain Token Pair

- Endpoint: `/api/token/`
- Method: POST
- Purpose: Obtain new access and refresh tokens
- Request Body:

{
    "email": "user@example.com",
    "password": "securepassword"
}

Success Response (200 OK):

```
{
    "refresh": "refresh_token",
    "access": "access_token"
}

```

7. Refresh Token

- Endpoint: /api/token/refresh/
- Method: POST
- Purpose: Obtain new access token using refresh token
  
- Request Body:
```

{
    "refresh": "refresh_token"
}

```
- Success Response (200 OK):

```
{
    "access": "new_access_token"
}

```
- Profile Management
  
8. User Profile

- Endpoint: /profile/
- Method: GET, PUT, PATCH
- Purpose: Retrieve and update user profile
- Headers Required: Authorization: Bearer <access_token>
- Request Body `(PUT/PATCH)`:

```
{
    "username": "new_username",
    "full_name": "New Name",
    "bio": "User bio",
    "current_password": "current_password",
    "new_password": "new_password"
}

```

- Success Response (200 OK):

```
{
    "id": 1,
    "email": "user@example.com",
    "username": "new_username",
    "full_name": "New Name",
    "bio": "User bio"
}

```
### Authentication Flow

### Registration

- User submits registration form
- System creates user account
- Verification email is sent
- JWT tokens are generated and returned


### Email Verification:

- User clicks verification link in email
- System verifies token and activates account
- User can now log in


### Login:

- User submits credentials
- System validates email verification status
- JWT tokens are generated
- User's online status is updated
- Device token is stored (for notifications)


### Token Refresh:

- Client uses refresh token to obtain new access token
- Previous access token is invalidated
- New access token is returned


### Logout:

- Client sends logout request
- User's online status is updated
- Device token is removed
- Tokens are invalidated



### Security Features

### Password Security:

- Password hashing using Django's default hasher
- Password validation rules enforced
- Secure password reset flow


### Email Verification:

- Required email verification
- Time-limited verification tokens
- Secure token generation


### JWT Authentication:

- Short-lived access tokens
- Refresh token rotation
- Token blacklisting support


### Role-Based Access Control:

- Custom user roles
- Granular permissions
- Role hierarchy support



### Error Handling
- All endpoints follow a consistent error response format:
  
```
{
    "error": "Error message",
    "detail": "Detailed error description"
}

```
### Common HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error


### Dependencies

- Django REST Framework
- Simple JWT
- Django CORS Headers


### Testing

- Run tests using:
  
```
python manage.py test

```