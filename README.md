# Fitbit Device Linking Dashboard
![image](https://github.com/user-attachments/assets/2b9f24e7-29c4-4f7a-b693-48fc0ea7b6e6)

A Flask-based web application for linking and reassigning Fitbit devices to users. This project provides a user-friendly interface to manage Fitbit device associations, including features like device reassignment, user confirmation, and secure token handling.

---

## Features ✨

- **Device Linking**: Link Fitbit devices to users via OAuth 2.0.
- **Reassignment Confirmation**: Confirm reassignment of devices to new users.
- **Secure Token Handling**: Store and manage access and refresh tokens securely.
- **Dynamic UI**: Interactive and responsive user interface with animations.
- **Countdown Timer**: A countdown timer for enabling the "Return to Home" button.

---

## Technologies Used 🛠️

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL (or any SQL database)
- **OAuth 2.0**: Fitbit API integration
- **Animations**: CSS animations for a smooth user experience

---

## Getting Started 🚀

### Prerequisites

Before running the project, ensure you have the following installed:

- Python 3.8 or higher
- Flask (`pip install flask`)
- A Fitbit Developer account (for OAuth credentials)
- PostgreSQL (or any SQL database)

### Installation

# Setup Instructions 🛠️

## 1. Clone the repository
```bash
git clone https://github.com/your-username/fitbit-device-linking.git
cd fitbit-device-linking
```

## 2. Set up a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Set up the database
- Create a PostgreSQL database and update the connection details in `config.py`.
- Run the database migrations (if applicable).

## 5. Configure Fitbit OAuth
Update the `CLIENT_ID` and `REDIRECT_URI` in `config.py` with your Fitbit Developer credentials.

## 6. Run the application
```bash
python app.py
```

## 7. Access the application
Open your browser and go to [http://localhost:5000](http://localhost:5000).


   # Usage 🖥️
## Linking a Device
- Navigate to the **Link Device** page.
- Select an email from the dropdown or enter a new one.
- If the email is already in use, confirm the reassignment.
- If the email is new, enter the user's name and proceed to Fitbit OAuth authorization.

## Reassigning a Device
- If an email is already associated with a user, you'll be prompted to confirm reassignment.
- Enter the new user's name and proceed.

## Confirmation Page
- After successful linking or reassignment, you'll be redirected to a **confirmation page** with a countdown timer.
- Once the countdown ends, the **Return to Home** button becomes clickable and expands to fill the container.

---

# Project Structure 📂
```
fitbit-device-linking/
├── app.py                # Main Flask application
├── config.py             # Configuration file (OAuth credentials, database settings)
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── confirmation.html # Confirmation page
│   ├── link_device.html  # Device linking page
│   └── reassign_confirmation.html # Reassignment confirmation page
├── static/               # Static files (CSS, JS, images)
│   └── styles.css        # Custom styles
└── README.md             # Project documentation
```

---

# Contributing 🤝
Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/YourFeatureName
   ```
5. Open a pull request.



# Acknowledgments 🙏
- **Fitbit API**: For providing the OAuth 2.0 integration.
- **Flask**: For making backend development simple and efficient.
- **Bootstrap**: For the responsive and clean UI components.

---

# Screenshots 📸

## Device Linking Page  
**Device Linking Page**  
<!-- Add a screenshot of the link device page -->

## Confirmation Page  
**Confirmation Page**  
<!-- Add a screenshot of the confirmation page -->

---



