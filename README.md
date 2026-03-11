# Hisaab Backend

A backend service for the Hisaab application, built with FastAPI and SQLAlchemy.

## Getting Started

### 1. Setup Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Environment Variables

Copy `.env.example` to `.env` and fill in the required values.

```powershell
cp .env.example .env
```

### 4. Run the Application

```powershell
python -m app.main
```

### 5. Run Tests

```powershell
python -m pytest
```

## Project Structure

```text
hisaab-backend/
├── alembic/              # Database migration files and configurations
├── app/
│   ├── constants/        # Application-wide constants (e.g., endpoints, error messages)
│   ├── db/               # Database connection and common base models
│   ├── exceptions/       # Custom HTTP exception handling and logic
│   ├── models/           # SQLAlchemy ORM models (User, Budget, Expense, etc.)
│   ├── routers/          # FastAPI route definitions and business logic connecting endpoints
│   ├── schemas/          # Pydantic models for request/response validation
│   ├── settings/         # Configuration and environment variables management
│   ├── utils/            # Helper functions and reusable utilities
│   └── main.py           # FastAPI application entry point, app initialization
├── .env.example          # Template for environment variables
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Database Models & Thoughts

### User

- `first_name`
- `last_name`
- `email`
- `password`
- `country`
- `is_verified`
- `auth_provider`
- `provider_id`

### Expense

- `id`
- `user_id` (foreign key)
- `category_id` (foreign key)
- `name`
- `description`
- `amount`
- `expense_date`

### Budget

- `id`
- `user_id` (foreign key)
- `category_id` (foreign key)
- `total_amount`
- `amount_spent`
- `amount_left`
  **NOTE:** Budget is linked to a category.

### Category

- `id`
- `user_id` (foreign key)
- `name`
- `description`
- `color`
- `icon`

## API Endpoints List

Below is the complete list of REST API endpoints that will be necessary to cover the features described.

### Authentication (`/api/auth`)

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Authenticate user and return an access token (JWT)
- `POST /api/auth/verify-account` - Verify the user's account
- `POST /api/auth/forgot-password` - Forgot password
- `POST /api/auth/reset-password` - Reset password
- `POST /api/auth/refresh` - Refresh the access token (JWT)
- `POST /api/auth/resend-otp` - Resend OTP for email verification or password reset
- `POST /api/auth/google` - Login with Google
- `POST /api/auth/guest` - Login as a guest (No body required)

### User (`/api/users`)

- `GET /api/users/profile` - Get the current logged-in user profile
- `PATCH /api/users/profile` - Update the user profile (e.g., update `country`, update name)
- `DELETE /api/users/profile` - Delete user account and associated data

### Category (`/api/categories`)

- `GET /api/categories` - List all available categories
- `GET /api/categories/{id}` - Get a specific category's details
- `POST /api/categories` - Create a new category
- `PUT /api/categories/{id}` - Update a category (name, color, icon, description)
- `DELETE /api/categories/{id}` - Delete a category

### Expense (`/api/expenses`)

- `GET /api/expenses` - List expenses (Query params: `month`, `year`)
- `GET /api/expenses/{id}` - Get details of a single expense
- `POST /api/expenses` - Add a new expense
- `PUT /api/expenses/{id}` - Update an existing expense
- `DELETE /api/expenses/{id}` - Delete an expense

### Budget (`/api/budgets`)

- `GET /api/budgets` - List all budgets for the user (Query params: `month`, `year`)
- `GET /api/budgets/{id}` - Get budget details by ID
- `POST /api/budgets` - Set a new budget for a category
- `PUT /api/budgets/{id}` - Update the budget amount
- `DELETE /api/budgets/{id}` - Delete a budget
