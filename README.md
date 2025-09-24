**📚 Library Service API**

Library Service API is a web-based system designed to simplify and digitize the process of managing a library.
It provides tools for both users (borrowing books, managing accounts, making payments) and administrators (tracking inventory, controlling borrowings, monitoring payments).

The project is built with Django REST Framework and integrates Stripe for handling payments and fines.
Documentation is automatically generated with drf-spectacular, ensuring a clean and developer-friendly API interface.

**✨ Features**

📖 Book management — browse available books in the library.
Each book includes title, image, author, cover type (hard or soft), current inventory, and a daily rental fee.
Admins can add, update, or remove books from the catalog.

🔐 Authentication — secure registration and login with email-based authentication.
Passwords are stored securely, and user roles (regular user vs. admin) determine API access.

📅 Borrowings — users can borrow books via API, with automatic tracking of borrowing date, expected return date, and actual return date.
The system prevents duplicate returns and updates inventory upon return. Borrowings are managed via API or admin panel.

💳 Payments — integrated with Stripe Checkout to process rental fees and fines.
Users are redirected to a secure payment session, while the system stores session IDs and statuses.

🔔 Stripe Webhooks — ensures reliable payment updates.
Once a checkout session is completed, the system automatically marks the payment as paid and syncs it with borrowing data.

🤖 Telegram notifications - The Telegram bot is a microservice that instantly notifies administrators about key events in the system: 
successful payments for borrowed books and reports on overdue borrowings.
It is integrated with Django signals and Celery tasks, ensuring reliable message delivery even under high load.

📜 API Documentation — auto-generated via drf-spectacular.
Both Swagger and ReDoc UIs are available for testing endpoints and exploring schemas.

🛠 Admin panel — Django’s admin interface extended for library models.
Full CRUD for Books, Borrowings, Payments, Users. Includes quick actions like marking a borrowing as returned.

**🛠 Tech Stack**

Backend: Python, Django, Django REST Framework, drf-spectacular
Database: PostgreSQL
Payments: Stripe API
Auth: Custom Django user model (email-based login)
Tools: Docker, Git, GitHub
Integrations: Telegram notification bot

**Access project**

API root → http://127.0.0.1:8000/api/
Swagger UI → http://127.0.0.1:8000/api/doc/swagger/
ReDoc → http://127.0.0.1:8000/api/doc/redoc/
Django Admin → http://127.0.0.1:8000/admin/

**Endpoints**

Category      | Endpoint(s)                                | Description
--------------------------------------------------------------------------------------------
Books         | GET /api/library/books/                     | List all books (accessible to authenticated users)
              | GET /api/library/books/{id}/                | Retrieve details of a single book
              | POST /api/library/books/                    | Add new book (admin only)
              | PUT/PATCH /api/library/books/{id}/          | Update book details (admin only)
              | DELETE /api/library/books/{id}/             | Remove a book (admin only)

Borrowings    | POST /api/library/borrowings/               | Borrow a book (authenticated users)
              | GET /api/library/borrowings/                | List borrowings (own for users, all for admins)
              | GET /api/library/borrowings/{id}/           | Borrowing details
              | POST /api/library/borrowings/{id}/return/   | Return a borrowed book

Payments      | GET /api/library/payments/                  | List payments (own for users, all for admins)
              | GET /api/library/payments/{id}/             | Payment details
              | GET /api/library/payments/{id}/success/     | Confirm successful payment (Stripe)
              | GET /api/library/payments/{id}/cancel/      | Payment canceled or expired
              | POST /api/library/stripe/webhook/           | Stripe webhook for session updates

Auth & Users  | POST /api/user/register/                    | User registration
              | POST /api/user/token/                       | Obtain JWT token
              | POST /api/user/token/refresh/               | Refresh JWT token
              | POST /api/user/token/verify/                | Verify JWT token
              | GET /api/user/me/                           | Get current user profile
              | PUT/PATCH /api/user/me/                     | Update current user profile

Docs          | GET /api/schema/                            | OpenAPI schema (JSON)
              | GET /api/doc/swagger/                       | Swagger UI
              | GET /api/doc/redoc/                         | ReDoc UI

Admin Panel   | /admin/                                     | Django Admin site (full model management)



**Telegram Bot Notifications**

The project includes a microservice that sends real-time Telegram messages to administrators when key events occur:

Borrowing Payment Alerts - administrators receive instant confirmation whenever a user successfully pays for a borrowing. This ensures full visibility over all completed transactions.
Overdue Borrowings Report - admins can trigger a command to receive a summary of all borrowings that are overdue, making it easier to monitor and follow up on late returns.
Reliable Delivery - the system leverages Django signals and Celery tasks to guarantee that messages are delivered reliably, even under high load.

1. Add @library_borrowings_bot in your Telegram chat

2. Write /start

3. For check current overdue write /overdue

Now you will receive notifications!

🚀 Getting Started
Before starting, it’s recommended to fork the repository to your own GitHub account so you can safely make changes and push updates.

1. Clone the repository

`git clone git@github.com:SensibleN00B/library-service-api.git
cd library-service-api`


2. Create .env file – copy from .env.sample

3. Run with Docker

`docker compose up -d --build
`

4. Create superuser

`docker-compose exec app python manage.py createsuperuser
`

5. Access the project

Open http://127.0.0.1:8000/
 in your browser 🎉
