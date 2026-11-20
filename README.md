# 🚀 SaaS Platform for Automated Docker Container Deployment

A cloud-hosted SaaS web platform designed to simplify, automate, and secure the deployment and management of software containers through an intuitive user interface. Developed as part of an engineering internship project at the **National Office of Airports (ONDA)**[cite: 136].

---

## 📋 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Key Features](#2-key-features)
3. [System Architecture](#3-system-architecture)
4. [Technologies Used](#4-technologies-used)
5. [Project Structure](#5-project-structure)
6. [Screenshots](#6-screenshots)
7. [Installation & Setup](#7-installation--setup)
8. [Environment Variables](#8-environment-variables)
9. [Docker Deployment](#9-docker-deployment)
10. [Future Improvements](#10-future-improvements)

---

## 1. 📌 Project Overview
Managing containerized applications manually via CLI can be complex for non-specialist technical teams[cite: 147]. This project delivers a centralized **SaaS platform** that abstracts infrastructure complexities, allowing users to securely deploy, monitor, and manage Docker containers via a web browser[cite: 147].

---

## 2. ✨ Key Features
* **Secure Authentication:** User registration, secure login, and session management protected by **JSON Web Tokens (JWT)**.
* **Container Lifecycle Management:** Full CRUD operations (Create, Read, Start, Stop, Delete) for Docker containers.
* **Real-time Monitoring:** Live tracking of container statuses (`running`, `stopped`, etc.) and log inspection.
* **User Isolation:** Multi-tenant architecture ensuring users securely manage only their own deployed resources.

---

## 3. 🏗️ System Architecture
The platform follows a modular **Client-Server REST architecture** structured into isolated tiers:
* **Frontend Layer:** Built with Vite & JavaScript for a responsive, fast user interface.
* **Backend Layer:** Powered by **Flask (Python)** acting as a stateless REST API, utilizing **Docker SDK for Python** to control the Docker Engine.
* **Persistence Layer:** **PostgreSQL** database managed via **SQLAlchemy ORM** to store user profiles and container metadata securely.

---

## 4. 🛠️ Technologies Used
- **Backend:** Python, Flask, Flask-JWT-Extended, SQLAlchemy, Alembic (Migrations), Marshmallow[cite: 44, 155]
- **Frontend:** React, Vite, Tailwind CSS, JavaScript, HTML5, CSS3, Nginx[cite: 58, 157]
- **Database:** PostgreSQL[cite: 20]
- **Containerization & Reverse Proxy:** Docker, Docker Compose, Traefik[cite: 25, 158]

---

## 5. 🗂️ Project Structure
```text
├── backend/                     # Flask REST API & business logic
│   ├── logs/                    # Application execution & error logs
│   ├── migrations/              # Alembic database migration versions
│   ├── routes/                  # API Blueprint endpoints
│   │   ├── auth_routes.py       # Authentication & JWT routes
│   │   └── container_routes.py  # Docker container CRUD & control routes
│   ├── services/                # Modular service layer
│   │   ├── docker_service.py    # Docker Engine SDK integration
│   │   ├── email_service.py     # Email notification service
│   │   └── user_service.py      # User management logic
│   ├── app.py                   # Flask application entry point
│   ├── config.py                # Environment & app configurations
│   ├── database.py              # SQLAlchemy database setup
│   ├── models.py                # User & Container relational models
│   ├── schemas.py               # Marshmallow serialization/validation schemas
│   ├── Dockerfile               # Backend container build instructions
│   └── requirements.txt         # Python dependencies
├── frontend/vite-project/       # React + Vite + Tailwind CSS SPA
│   ├── public/                  # Static assets
│   ├── src/                     # React components, pages & API services
│   ├── Dockerfile               # Frontend multi-stage container build
│   ├── nginx.conf               # Nginx web server configuration
│   ├── tailwind.config.js       # Tailwind CSS configuration
│   ├── vite.config.js           # Vite bundler configuration
│   └── package.json             # Frontend dependencies
├── migrations/                  # Root database migration scripts
├── traefik/                     # Traefik reverse proxy configuration
│   └── traefik.yml              # Traefik routing & entrypoint rules
├── docker-compose.yml           # Multi-container orchestration file
├── container_data.json          # Container metadata reference
└── container_startup_logs.txt   # Container initialization logs
