## 📚 LiveStatusAPI: Real-Time Presence Tracking

A real-time presence tracking API that enables applications to monitor user activity, predict response times, and analyze engagement trends.

### 🌟 Key Features

- **Real-Time Presence Tracking**: Monitor user online status across different devices
- **Engagement Analytics**: Analyze user activity patterns and engagement metrics
- **Response Time Prediction**: Smart algorithms to predict user response times
- **Webhook Integration**: Register webhooks for real-time presence updates
- **Role-Based Access Control**: Secure, permission-based API access

## 🚀 API Endpoints

### Presence Management

#### Get User Presence
- **Endpoint**: `GET /users/{userId}/presence`
- **Purpose**: Retrieve a user's current presence data
- **Response**: Returns detailed presence information including:
  - Current status (online, away, offline, busy)
  - Last seen timestamp
  - Device type
  - Predicted response time
  - Engagement score

#### Update User Presence
- **Endpoint**: `PUT /users/{userId}/presence`
- **Purpose**: Update a user's presence status
- **Request Body**: Accepts status updates and device information
- **Response**: Confirms the presence update was successful

### Analytics

#### Get User Analytics
- **Endpoint**: `GET /users/{userId}/analytics`
- **Purpose**: Retrieve analytics about user presence patterns
- **Parameters**: 
  - `timeRange` (day, week, month)
- **Response**: Returns analytics including:
  - Average response time
  - Peak activity hours
  - Engagement trends over time

### Webhooks

#### Register Webhook
- **Endpoint**: `POST /webhooks`
- **Purpose**: Register a webhook for presence updates
- **Request Body**: URL and events to subscribe to
- **Response**: Confirms webhook registration

## 🔒 Authentication & Authorization

### Authentication Flow

- **Login endpoint**: `POST /api/login/`
- **Authentication Method**: JWT (JSON Web Tokens)
- **Token Validation**: All protected endpoints validate the token
- **Refresh Mechanism**: Use refresh tokens to obtain new access tokens

### User Registration
- **Registration endpoint**: `POST /api/register/`
- **Required Fields**: email, username, password
- **Email Verification**: Required before full access
- **Verification endpoint**: `GET /api/verify-email/<token>/`

## 📖 API Documentation

The complete API specification is available through OpenAPI 3.0.0:

- **OpenAPI Specification**: 
  - Access the raw OpenAPI specification at: `/api/schema/`
  
- **Interactive Documentation**: 
  - Swagger UI: `/api/schema/swagger-ui/`
  - ReDoc: `/api/schema/redoc/`

### Schema Components
Our API defines several key schema components:

- **PresenceData**: User presence information
  - Status (online, away, offline, busy)
  - Last seen timestamp
  - Device type
  - Engagement metrics
  
- **PresenceUpdate**: Format for updating presence
  - Status changes
  - Device information

- **AnalyticsData**: User analytics information
  - Response time metrics
  - Activity patterns
  - Engagement trends

- **WebhookRegistration**: Format for registering webhooks
  - Target URL
  - Event subscriptions

## 🧩 Project Components

### Models
- **CustomUser**: Extended user model with presence data
- **PresenceRecord**: Tracks historical presence information
- **WebhookSubscription**: Manages webhook registrations

### Serializers
- **PresenceDataSerializer**
- **PresenceUpdateSerializer**
- **AnalyticsDataSerializer**
- **WebhookRegistrationSerializer**

### Permissions
- JWT authentication
- Role-based access control

## 🚀 Getting Started

To run the project locally:

1. Clone the repository
2. Install requirements: 
   
   ```
   pip install -r requirements.txt

   ```
3. Configure environment variables.

   - Create a .env file in the root directory (see .env.example for reference).
   
4. Run migrations:
   ```
    python manage.py migrate

    ```
5. Start the server:
   ```
    python manage.py runserver

   ```
6. Explore the API docs at: http://localhost:8000/api/schema/swagger-ui/


📋 Complete Endpoints Summary

Action	          Method	                           Endpoint

Get User Presence	  GET	                      /users/{userId}/presence

Update Presence	  PUT	                      /users/{userId}/presence

Get Analytics	     GET	                      /users/{userId}/analytics

Register Webhook	  POST	                   /webhooks

Register User	     POST	                   /api/register/

Login	              POST	                   /api/login/

Verify Email	     GET	                      /api/verify-email/<token>/

Logout	           POST	                  /api/logout/

Profile	           GET/PUT	              /api/profile/

### ✨ Project Benefits

- For Developers: Easy integration with standardized endpoints
- For Businesses: Insights into user engagement and activity patterns
- For Users: Seamless presence sharing with privacy controls
- For Operations: Webhook-based automation for presence events


Feel free to reach out for contributions, feedback, or support!