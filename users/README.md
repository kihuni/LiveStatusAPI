# 📚 User Data Flow in the Application

This document provides a detailed overview of how user data flows through the application—from registration to accessing resources. It highlights the key endpoints, models, serializers, and permissions that ensure a seamless and secure experience for users.

---

## 🚀 **1. User Registration Process**

### **Endpoint:** `POST /register/`

- **Purpose:** Creates a new user account.
- **Flow:**
  1. **Input Data:** Users provide:
     - `email`, `username`, `full_name`, `password`, `password2` (optional: `bio`).
  2. **Validation:** Ensures:
     - Passwords match and meet strength criteria.
  3. **User Creation:** 
     - Generates a user with `email_verified = False` and assigns the default role (`user`).
     - Sends an email with a verification link containing a `verification_token`.
  4. **Response:** Returns user details and access tokens.

---

## ✅ **2. Email Verification Process**

### **Endpoint:** `GET /verify-email/<token>/`

- **Purpose:** Activates a user’s email address.
- **Steps:**
  - Validates the `verification_token`.
  - Sets `email_verified = True` on success.
- **Response:** Confirms email verification or provides error messages for invalid tokens.

---

## 🔑 **3. User Login Process**

### **Endpoint:** `POST /login/`

- **Purpose:** Authenticates users and issues access tokens.
- **Flow:**
  1. **Input Data:** Users submit `email`, `password` (optional: `device_token`).
  2. **Validation:** Verifies credentials and ensures the email is verified.
  3. **Session Management:** Updates `is_online` and `last_seen`.
  4. **Response:** Returns access and refresh tokens.

---

## 🔒 **4. Accessing Protected Resources**

### **Mechanism: Token-Based Authentication**
- **Purpose:** Secures endpoints using JWT (JSON Web Tokens).
- **Flow:**
  1. Tokens are validated via Django REST Framework’s `SimpleJWT`.
  2. Role-based permissions are enforced using the `RolePermission` class.

### **Example Protected Endpoints:**
- **User Profile:** `GET /profile/`
- **Resource Management:** Guarded by permissions (e.g., managing users, deleting messages).

---

## 🛡️ **5. Role and Permission Management**

### **Roles:**
- **Default Role:** New users are assigned `user`.
- **Custom Roles:** Admins can assign specific roles with defined permissions.

### **Permissions:**
- Permissions are mapped to roles (e.g., `can_manage_users`, `can_moderate`).

### **Access Control Examples:**
1. **Moderator Managing Chats:** Requires `can_moderate` permission.
2. **Admin Managing Users:** Requires `can_manage_users` permission.

---

## 🛠️ **6. Profile Updates**

### **Endpoint:** `PUT /profile/`

- **Purpose:** Allows users to update profile information.
- **Steps:**
  1. Input fields like `bio`, `avatar`, or `password`.
  2. Validate and save updates.
  3. Password updates require current password verification.

---

## 🚪 **7. Logout Process**

### **Endpoint:** `POST /logout/`

- **Purpose:** Ends the user session securely.
- **Steps:**
  1. Blacklists the user’s refresh token.
  2. Sets `is_online` to `False`.

---

## 🧩 **Key Components**

### **Models:**
- `CustomUser`: Core user model.
- `Role`: Defines roles and permissions.

### **Serializers:**
- `UserRegistrationSerializer`
- `UserLoginSerializer`
- `UserProfileUpdateSerializer`
- `RoleSerializer`

### **Permissions:**
- `RolePermission`: Enforces role-based access control.

---

## 📋 **Endpoints Summary**

| **Action**         | **Method** | **Endpoint**              |
|---------------------|------------|---------------------------|
| **Register**        | `POST`     | `/register/`              |
| **Login**           | `POST`     | `/login/`                 |
| **Verify Email**    | `GET`      | `/verify-email/<token>/`  |
| **Logout**          | `POST`     | `/logout/`                |
| **Profile**         | `GET/PUT`  | `/profile/`               |
| **Manage Roles**    | `GET/POST` | `/roles/` (Admin only)    |

---

## ✨ **Project Highlights**
- Comprehensive user data flow management.
- Robust authentication and email verification.
- Role-based access control for secure resource management.
- Clean and user-friendly APIs powered by Django.

---

Feel free to reach out for contributions, feedback, or support!
