
# ReadRealm

**ReadRealm** is a web application that provides users with a platform to explore books, manage user profiles, view book details, and interact with followers. The app utilizes a database to manage user and book data and provides a simple interface for book enthusiasts to connect and explore.

## Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Database Setup](#database-setup)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/harshitha0923/ReadRealm.git
   ```

2. Navigate to the project directory:

   ```bash
   cd ReadRealm_SourceCode
   ```

3. Create and activate a virtual environment (optional but recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # For Linux/Mac
   .venv\Scripts\activate     # For Windows
   ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Set up the database configuration by modifying the `db.yaml` file to match your database settings.

## Project Structure

```
ReadRealm/
│
├── app.py                   # Main application file
├── db.yaml                  # Database configuration
├── static/                  # Static assets (CSS, images, JavaScript)
│   ├── images/              # Image files
│   ├── styles/              # CSS stylesheets
│   └── scripts/             # JavaScript files
├── templates/               # HTML templates for the web pages
│   ├── home.html            # Home page
│   ├── book_details.html    # Book details page
│   ├── user_profile.html    # User profile page
│   ├── register.html        # User registration page
│   └── login.html           # Login page
├── ReadMe.txt               # Basic project documentation
└── database_project_v1.sql  # SQL script to initialize the database
```

## Usage

1. Start the application by running the following command:

   ```bash
   python app.py
   ```

2. Open a web browser and go to `http://localhost:5000` to access the app.

## Database Setup

1. Use the `database_project_v1.sql` script located in the root directory to set up the database.
2. Ensure that the database credentials match those specified in the `db.yaml` file.

## Features

- User registration and login
- User profile management
- Viewing book details
- Interacting with other users (following/unfollowing)

## Technologies Used

- **Python**: Main programming language
- **Flask**: Web framework
- **SQLite/MySQL**: Database (configured via `db.yaml`)
- **HTML/CSS/JavaScript**: Frontend technologies
- **YAML**: For database configuration
- **SQL**: For database schema

## Contributing

Feel free to contribute to this project by forking the repository and submitting pull requests.
