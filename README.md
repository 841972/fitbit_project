# Fitbit Health Tracker API

![Fitbit Logo]([https://upload.wikimedia.org/wikipedia/commons/8/8e/Fitbit_logo_2016.svg](https://getvectorlogo.com/wp-content/uploads/2022/05/fitbit-vector-logo-2022.png]))

A Python-based application that collects health data from Fitbit devices using the Fitbit Web API. Designed for tracking the health metrics of elderly users in a residence, this project automates data collection, stores it in a PostgreSQL database, and provides a simple interface for monitoring.

---

## Features

- **Automated Data Collection**: Fetches daily health metrics (steps, heart rate, sleep) from Fitbit devices.
- **User Management**: Supports multiple users with individual Fitbit accounts.
- **Database Integration**: Stores collected data in a PostgreSQL database for easy access and analysis.
- **Docker Support**: Easy deployment using Docker and Docker Compose.

---

## Technologies Used

- **Python**: Core programming language.
- **Fitbit Web API**: For fetching health data.
- **PostgreSQL**: Database for storing health metrics.
- **Docker**: Containerization for easy deployment.
- **Docker Compose**: Orchestration of multi-container applications.

---

## Getting Started

### Prerequisites

- Docker and Docker Compose installed.
- Fitbit API credentials (`CLIENT_ID` and `CLIENT_SECRET`).

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/tu-usuario/fitbit-project.git
   cd fitbit-project
2. Create a .env file with your credentials:
        ADMIN_MAIL=your_email@gmail.com
        ADMIN_PSSW=your_password
        CLIENT_ID=your_client_id
        CLIENT_SECRET=your_client_secret
        DB_HOST=your_db_host
        DB_USER=your_db_user
        DB_PASSWORD=your_db_password
        DB_PORT=your_db_port
        DB_NAME=your_db_name
   3. Build and run the application:
      docker-compose up --build
   4. Access the application at http://localhost:5000.
