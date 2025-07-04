# Kidnap-children – Social Platform for Finding Missing Children

Kidnap-children is a Laravel-based web application and social platform designed to help find and report missing children. The system uses artificial intelligence to analyze and compare images, recognizing faces and finding similarities even across different ages. Users can create posts about missing or found children, upload and share images, comment, chat privately, and receive real-time notifications. By combining AI-powered image recognition with social media features, the platform enables easy communication, community engagement, and maximizes the chances of reuniting families.

---

## 🧠 AI Image Comparison Service (Python + Flask)

### Purpose & Integration

The system integrates a Python Flask API as an AI microservice for image recognition and matching. This service enables the platform to:
- Analyze uploaded images of children
- Recognize faces and find similarities, even across different ages
- Suggest possible matches and related cases to users

### How It Works

1. **Image Upload:** Users upload images of missing or found children via the web app.
2. **API Request:** The Laravel backend sends these images to the Flask API using a POST request (multipart/form-data).
3. **AI Model:** The Flask service uses a deep learning face recognition model (e.g., FaceNet, ArcFace, or a custom CNN) that is robust to age variation. It extracts facial embeddings and compares them to stored embeddings in the database.
4. **Similarity Search:** The API finds and returns the IDs of images/users with the highest similarity scores, even if the photos are from different ages.
5. **Result Integration:** The Laravel app uses these IDs to suggest possible matches, notify users, or link related cases.

#### Example Flask Endpoint
```python
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/api/detect_image', methods=['POST'])
def detect_image():
    # Receive images, run AI model, return related image IDs
    # ... (AI logic here)
    return jsonify([related_image_id1, related_image_id2, ...])
```

#### Tech Stack
- Python 3.x
- Flask
- Deep learning libraries (TensorFlow, PyTorch, or Keras)
- Face recognition models (with age-invariance)
- REST API

---

## 🌍 Project Purpose

Kidnap-children is a social good project that connects people to help locate missing children. Users can:
- Report missing or found children with detailed posts and images
- Comment and discuss on posts
- Chat privately with other users
- Receive real-time notifications about relevant activity
- Get matched with similar cases using image recognition

---

## 🏗️ Architecture & Main Features

- **Backend:** Laravel (PHP)
  - **Models:** User, Post, Comment, Notification, Chat, PostImage, Region, City, Country, History
  - **Controllers:**
    - Frontend: Home, Post, Comment, Profile, Notification, Chat
    - API: Auth, Registration, Password Reset, Verification
    - Old controllers for legacy support
  - **Repositories & Services:**
    - PostRepository, CommentRepository for data access
    - PostServices, CommentServices, UploaderService for business logic and file uploads
  - **Events & Broadcasting:**
    - Real-time notifications for likes, comments, posts, and chat using Laravel Echo
  - **Middleware:**
    - Authentication, CORS, CSRF, Localization, HTTPS enforcement
  - **Validation:**
    - Form requests for posts and comments
- **Frontend:**
  - Blade templates in `/front` for home, profile, chat, notifications, and post management
  - Image upload and preview, responsive design
- **Database:**
  - Migrations for users, posts, comments, images, notifications, chats, and more
  - Factories and seeders for test data

---

## 🧩 Key Features

- **User Registration & Authentication:** Secure login, registration, password reset, and email verification
- **Post Management:** Create, update, and delete posts about missing/found children, with multiple images
- **Image Recognition:** Integrates with external API to match images and suggest related cases
- **Commenting System:** Threaded comments with real-time updates
- **Chat:** Private messaging between users, with image/file support
- **Notifications:** Real-time alerts for likes, comments, new posts, and chat messages
- **Profile Management:** User info, profile and background images, found/missed person lists
- **Admin Tools:** (if enabled) for managing users and content
- **Localization:** Middleware for language support

---

## 📁 Project Structure

- `/app`
  - `Http/Controllers/` – Main controllers for frontend and API
  - `Http/Repository/` – Data access layers
  - `Http/Services/` – Business logic and file uploads
  - `Events/` – Broadcasting events for real-time features
  - `Models/` – Eloquent models for all entities
  - `Providers/` – Service providers for auth, events, routes
  - `Middleware/` – Security, localization, and request handling
- `/front`
  - Blade templates for all user-facing pages (home, chat, profile, notifications, posts)
  - Uploads directory for user and post images
- `/database`
  - `migrations/` – Table definitions for all entities
  - `factories/` – Model factories for seeding
  - `seeds/` – Seeders for test/demo data

---

## 🚦 Getting Started

### Prerequisites
- PHP 7.4+
- Composer
- Node.js & npm (for frontend assets)
- MySQL or compatible database
- Python 3.x (for Flask AI service)

### Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd Kidnap-children
   ```
2. Install PHP dependencies:
   ```bash
   composer install
   ```
3. Install JS dependencies and build assets:
   ```bash
   npm install && npm run dev
   ```
4. Copy `.env.example` to `.env` and configure your database and broadcasting settings.
5. Run migrations and seeders:
   ```bash
   php artisan migrate --seed
   ```
6. Start the queue worker (for jobs):
   ```bash
   php artisan queue:work
   ```
7. Serve the application:
   ```bash
   php artisan serve
   ```
8. **Start the Flask AI service** (in its directory):
   ```bash
   python app.py
   ```

### Usage
- Register or log in as a user
- Create posts for missing or found children, upload images
- Comment, chat, and receive notifications in real time
- Use the dashboard to manage your profile and posts
- The AI service will automatically analyze uploaded images and suggest possible matches

---

## 📚 Extending & Customization
- **Integrate new image recognition APIs** for better matching
- **Add new notification types** or real-time features
- **Customize UI** in `/front` for branding or accessibility
- **Add admin features** for moderation if needed
- **Improve or retrain the AI model** for higher accuracy

---

## 📝 License
This project is open-source and available under the MIT License. 
