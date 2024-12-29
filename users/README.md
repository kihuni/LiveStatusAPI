# CollabSphere Authentication System Documentation


## User Data Flow in the application

This document provides a comprehensive overview of how user data flows through the system—from registration to accessing protected resources. This flow ensures a seamless, secure, and structured experience for all users.


### User Registration Process

**_Endpoint: POST /register/_**

- Purpose: Allows a new user to create an account.

Steps:

**_Data Input: The user submits the following fields:_** 

- email

- username

- full_name

- password

- password2

- (Optional) bio

**_Validation:_**

- Password confirmation (password == password2).

- Password strength is validated using Django’s built-in password validators.

**_User Creation:_**

- A new user is created with the provided details.

- The email_verified field is set to False.

- A verification_token is generated.

**_Default Role Assignment:_**

- The user is assigned a default role (user).

**_Email Verification:_**

- A verification email is sent to the user with a link containing the verification_token.

**_Response:_**

- Returns user details (via UserSerializer).

- Returns access and refresh tokens for the user.

### Email Verification Process

**_Endpoint: GET /verify-email/<token>/_**

- Purpose: Verifies the user’s email address.

Steps:

**_Token Validation:_**

- The verification_token is checked for validity.

- If valid, email_verified is set to True.

**_Response:_**

- On success: Confirms that the email has been verified.

- On failure: Provides an error message (e.g., token expired or invalid).


### User Login Process

**_Endpoint: POST /login/_**

- Purpose: Authenticates the user and generates access tokens.

Steps:

**_Data Input: The user provides:_**

- email

- password

- (Optional) device_token (used for push notifications).

**_Validation:_**

- Credentials are validated using Django’s authenticate() function.

- If the user’s email is not verified, an error is returned.

**_Session Updates:_**

- is_online is set to True.

- last_seen is updated.

- device_token is stored (if provided).

**_Response:_**

- Returns access and refresh tokens.


## Accessing Protected Resources

### Token-Based Authentication

- Purpose: Ensures that only authenticated users can access protected resources.

**_Mechanism:_**

- Access tokens are validated using the Django REST Framework’s SimpleJWT.

- Tokens are passed in the Authorization header as Bearer <token>.

Steps:

**_Authentication Middleware:_**

- Verifies the token’s validity.

- Decodes the token to identify the user.

- Denies access if the token is invalid or expired.

**_Role-Based Permissions:_**

- Role permissions are validated using the RolePermission class.

- Each endpoint defines the required permission, which is checked against the user’s role.

**_Example Endpoints:_**

**_Profile: GET /profile/_**

- Returns user-specific details (e.g., username, email, avatar).

- **_Resource Management:_** Protected endpoints (e.g., managing users, deleting messages) are guarded by role-based permissions.

## Role and Permission Management

### Role Assignment:

- Default Role: All new users are assigned the user role by default.

- Admin Assignment: Admins can assign or modify roles via the manage_roles endpoint.

**_Permissions:_**

- Permissions are defined in the Role model (e.g., can_manage_users, can_delete_messages).

- Custom permissions are stored in the custom_permissions JSON field.

**_Access Control Example:_**

**_Moderator Accessing Chat Moderation:_**

- Checks the can_moderate permission.

**_Admin Managing Users:_**

- Checks the can_manage_users permission.

### Profile Updates

**_Endpoint: PUT /profile/_**

- Purpose: Allows users to update their profile.

Steps:

- Data Input: The user submits updates for fields like bio, avatar, or password.

**_Password Updates:_**

- Requires the current password for verification before setting a new password.

**_Validation and Save:_**
  
- Validates the input and saves the changes.

### Logout Process

**_Endpoint: POST /logout/_**

- Purpose: Logs the user out by invalidating their tokens.

Steps:

** Access Token Blacklisting:_**

- The user’s refresh token is blacklisted to prevent further usage.

**_Online Status Update:_**

- Sets is_online to False.

## Key Components

### Models:

- CustomUser: Core user model.

- Role: Defines roles and associated permissions.

### Serializers:

- UserRegistrationSerializer

- UserLoginSerializer

- UserSerializer

- UserProfileUpdateSerializer

- RoleSerializer

### Permissions:

- RolePermission: Maps roles to endpoint-specific permissions.

### Endpoints:

Action        Method      Endpoint    

Register       POST       /register/

Login          POST       /login/

Verify Email   GET        /verify-email/<token>/

Logout         POST       /logout/

Profile        GET/PUT    /profile/

Manage Roles   GET/POST   /roles/ (Admin only)





