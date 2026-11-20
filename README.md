# 🚀 SaaS Platform for Automated Docker Container Deployment

A web-based SaaS platform designed to simplify, automate, and secure Docker container deployment and management through an intuitive user interface.

Developed as an engineering internship project at **ONDA – National Office of Airports (Marrakech Menara Airport)**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Application Screenshots](#application-screenshots)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Docker Deployment](#docker-deployment)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## 📌 Overview

Managing containerized applications manually through command-line interfaces can be complex and time-consuming.

This project provides a centralized SaaS platform that simplifies Docker container management through a user-friendly web interface.

The platform enables technical teams to deploy, monitor, and manage Docker containers while benefiting from secure authentication and centralized management.

The application combines a React frontend, a Flask REST API, PostgreSQL database, and Docker-based infrastructure.

---

## ✨ Key Features

### 🔐 Authentication & Security
- User registration and secure login.
- JWT-based authentication.
- User profile and security settings.
- Session management.

### 🚀 Container Management
- Create and deploy Docker containers.
- Start and stop existing containers.
- Inspect and delete containers.
- Manage container lifecycle operations through a web interface.

### 📊 Monitoring & Dashboard
- Centralized dashboard for container management.
- Container status tracking.
- Container log inspection.
- Overview of deployed resources.

### 🏗️ Infrastructure & Deployment
- Docker-based application containerization.
- Multi-service orchestration using Docker Compose.
- Traefik reverse proxy integration.
- PostgreSQL database persistence.

---

## 🏗️ System Architecture

The platform follows a modular Client-Server REST architecture.

### Architecture Diagram

```mermaid
flowchart TD
    A[User / Web Browser] --> B[Traefik Reverse Proxy]
    B --> C[React Frontend]
    C --> D[Flask REST API]
    D --> E[PostgreSQL Database]
    D --> F[Docker SDK]
    F --> G[Docker Engine]
    G --> H[Managed Containers]
```

### Architecture Components

| Component | Description |
|---|---|
| Frontend | React and Vite-based user interface |
| Backend | Flask REST API and business logic |
| Database | PostgreSQL for persistent data storage |
| ORM | SQLAlchemy for database interactions |
| Container Engine | Docker Engine managed through Docker SDK |
| Reverse Proxy | Traefik for traffic routing |
| Web Server | Nginx for frontend delivery |

---

## 🛠️ Technologies Used

### Backend & API

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)

- Python
- Flask
- Flask-JWT-Extended
- SQLAlchemy
- Alembic
- Marshmallow
- Docker SDK for Python

### Frontend

![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat&logo=tailwindcss&logoColor=white)

- React
- Vite
- JavaScript
- HTML5
- CSS3
- Tailwind CSS

### DevOps & Infrastructure

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=flat&logo=docker&logoColor=white)
![Traefik](https://img.shields.io/badge/Traefik-24A1C1?style=flat&logo=traefikproxy&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat&logo=nginx&logoColor=white)

- Docker
- Docker Compose
- Traefik
- Nginx

---

## 📂 Project Structure

```text
plateforme-saaS/
│
├── backend/
│   ├── logs/
│   ├── migrations/
│   ├── routes/
│   │   ├── auth_routes.py
│   │   └── container_routes.py
│   ├── services/
│   │   ├── docker_service.py
│   │   ├── email_service.py
│   │   └── user_service.py
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   └── vite-project/
│       ├── public/
│       ├── src/
│       ├── Dockerfile
│       ├── nginx.conf
│       └── package.json
│
├── images/
│   ├── login.png
│   ├── dashboard.png
│   ├── deploy.png
│   ├── profile.png
│   └── security.png
│
├── migrations/
├── traefik/
│   └── traefik.yml
│
├── docker-compose.yml
└── README.md
```

---

## 📸 Application Screenshots

Explore the main interfaces of the platform.

### 🔐 Login & Authentication

<p align="center">
  <img src="images/login.png" alt="Login Interface" width="850"/>
</p>

### 📊 Dashboard & Container Monitoring

<p align="center">
  <img src="images/dashboard.png" alt="Dashboard Interface" width="850"/>
</p>

### 🚀 Container Deployment

<p align="center">
  <img src="images/deploy.png" alt="Container Deployment Interface" width="850"/>
</p>

### 👤 User Profile

<p align="center">
  <img src="images/profile.png" alt="User Profile Interface" width="850"/>
</p>

### 🔒 Security Settings

<p align="center">
  <img src="images/security.png" alt="Security Settings Interface" width="850"/>
</p>

---

## ⚙️ Installation & Setup

### Prerequisites

Make sure the following tools are installed:

- Git
- Docker
- Docker Compose

### 1. Clone the Repository

```bash
git clone https://github.com/Ghitaa444/plateforme-saaS.git

cd plateforme-saaS
```

### 2. Configure Environment Variables

Create a `.env` file in the project root directory.

Configure the required environment variables as described in the next section.

### 3. Build and Start the Application

```bash
docker compose up --build
```

### 4. Access the Application

Open your browser and navigate to the local address configured in your Docker Compose and Traefik configuration.

---

## 🔑 Environment Variables

Create a `.env` file in the root directory.

Example configuration:

```env
SECRET_KEY=your_flask_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URL=postgresql://username:password@db-service:5432/saas_db
FLASK_ENV=development
```

**Security Note:** Replace the example values with your own configuration. Never commit real credentials, secret keys, or sensitive environment variables to GitHub.

---

## 🐳 Docker Deployment

The application is containerized and orchestrated using Docker Compose.

### Main Services

| Service | Responsibility |
|---|---|
| Frontend | Serves the React application through Nginx |
| Backend | Runs the Flask REST API |
| Database | Handles PostgreSQL data persistence |
| Traefik | Manages reverse proxy and traffic routing |

### Start the Application

```bash
docker compose up -d --build
```

### Check Running Containers

```bash
docker compose ps
```

### View Application Logs

```bash
docker compose logs -f
```

### Stop the Application

```bash
docker compose down
```

---

## 🔮 Future Improvements

Potential enhancements for future versions include:

- **Advanced Monitoring:** Integrating Prometheus and Grafana for container resource monitoring.
- **CI/CD Automation:** Implementing automated testing and deployment pipelines using GitHub Actions.
- **Resource Management:** Adding advanced CPU and memory usage monitoring.
- **Scalability:** Improving infrastructure to support larger deployment workloads.
- **Deployment Management:** Expanding container deployment configuration and management capabilities.

---

## 👩‍💻 Author

**Ghita EL Finou**

AI Engineering & Data Science Student

Backend Development | Artificial Intelligence | DevOps

- GitHub: [@Ghitaa444](https://github.com/Ghitaa444)
- LinkedIn: [Connect with me](YOUR_LINKEDIN_URL)

---

<p align="center">
  <b>Built with Python, React, Docker, and a passion for engineering.</b>
</p>
