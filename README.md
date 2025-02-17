# LiveStatusAPI 🚀  

LiveStatusAPI is an **open-source real-time presence tracking and engagement analytics API**. It enables developers to integrate **real-time user status, analytics, and webhooks** into their applications.  

## 📌 **Features**  
✅ Track user presence (`Online, Offline, Away, Busy`)  
✅ Retrieve historical engagement analytics  
✅ Webhooks for real-time updates  
✅ Predictive engagement scoring  
✅ Multi-device presence tracking  

## 🚀 **Getting Started**  

### 1️⃣ Clone the Repository**  

```
git clone https://github.com/YOUR_GITHUB_USERNAME/LiveStatusAPI.git
cd LiveStatusAPI

```
### 2️⃣ Set Up the Virtual Environment & Install Dependencies

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

### 3️⃣ Run Migrations & Start Server

```
python manage.py migrate
python manage.py runserver

```
### 4️⃣ API Documentation

The API is documented using OpenAPI 3.0. View it locally:

```
python manage.py runserver

```

Then visit: http://127.0.0.1:8000/docs

### 🔄 Endpoints Overview

User Presence

📌 GET /users/{userId}/presence - Retrieve user presence
📌 PUT /users/{userId}/presence - Update presence status

Analytics
📌 GET /users/{userId}/analytics?timeRange=day|week|month - Retrieve analytics

Webhooks
📌 POST /webhooks - Register webhook for presence updates

Full API reference available in openapi.yaml.

🛠️ Contributing
We welcome contributions! 🎉 See CONTRIBUTING.md for details on how to get started.

## ✅ **How to Contribute**  

1. **Fork the Repository**  
   - Click the **Fork** button at the top of the repository.  
  
2. **Clone Your Fork Locally**  
 
 ```
   git clone https://github.com/YOUR_GITHUB_USERNAME/LiveStatusAPI.git
   cd LiveStatusAPI

```
3. **Create a New Branch**

```
git checkout -b feature-branch

```
4. **Make Your Changes & Commit**

```
git add .
git commit -m "Added feature X"

```
5. **Push & Create a Pull Request**

```
git push origin feature-branch

```
- Go to GitHub → Open a Pull Request from your branch.

- Follow the PR template and describe your changes.

### ⚙️ Project Setup

### 1️⃣ Set Up Virtual Environment

```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

```
### 2️⃣ Run Migrations & Start Server

```
python manage.py migrate
python manage.py runserver
```

### 3️⃣ Run Tests Before Submitting PR


```
pytest tests/

```
### 📝 Coding Guidelines

🔹 Follow PEP8 for Python code formatting.
🔹 Use docstrings and meaningful variable names.
🔹 Write unit tests for new features.


### 🏷 Issue Tracking

Check out the Issues tab for tasks you can work on.