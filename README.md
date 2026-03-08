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
  **NOTE:** A `country` field can be added which can help with setting the currency from a UI perspective.

### Expense

- `name`
- `description`
- `amount`
  **NOTE:** Date tracking is crucial since the expenses or budget need to be displayed per month, and users must be able to view expenses for previous months/years. I'll use an explicit `expense_date` field to allow manual entry and querying, instead of relying purely on a `created_at` timestamp.

### Budget

- `category_id` (foreign key)
- `amount_spent`
- `total_amount`
  **NOTE:** Budget is linked to a category.
  **TODO:** `amount_spent` needs to be removed and calculated manually in our business logic.

### Category

- `name`
- `description`
- `color`
  _(Used to categorize expenses and link against budgets)_

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

### User (`/api/user`)

- `GET /api/user/me` - Get the current logged-in user profile
- `POST /api/user/me` - Create a new user profile
- `PATCH /api/user/me` - Update the user profile (e.g., add `country`, update name)
- `DELETE /api/user/me` - Delete user account and associated data

### Category (`/api/category`)

- `GET /api/category` - List all available categories
- `GET /api/category/{id}` - Get a specific category's details
- `POST /api/category` - Create a new category
- `PATCH /api/category/{id}` - Update a category (name, color, description)
- `DELETE /api/category/{id}` - Delete a category

### Expense (`/api/expense`)

- `GET /api/expense` - List expenses (Query params: `month`, `year`, `category_id` for filtering)
- `GET /api/expense/{id}` - Get details of a single expense
- `POST /api/expense` - Add a new expense
- `PATCH /api/expense/{id}` - Update an existing expense
- `DELETE /api/expense/{id}` - Delete an expense

### Budget (`/api/budget`)

- `GET /api/budget` - List all budgets for the user (Query params: `month`, `year`)
- `GET /api/budget/summary` - Get aggregate budget summary (Calculated dynamically: total budget vs. total spent from Expenses)
- `GET /api/budget/{id}` - Get budget details by ID
- `POST /api/budget` - Set a new budget for a category
- `PATCH /api/budget/{id}` - Update the budget amount
- `DELETE /api/budget/{id}` - Delete a budget
