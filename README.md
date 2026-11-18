# AI-Enabled Inventory Management REST API

A production-grade, secure RESTful backend API built with Flask, featuring dual-database architecture (MySQL for transactional inventory/users and MongoDB for system audit logs), JWT authentication, automated test suites, and an LLM-powered natural language query endpoint.

---

## 🚀 Tech Stack

* **Core Backend:** Python, Flask, RESTful APIs
* **Databases:** MySQL (Inventory & Auth), MongoDB (Audit Logs & Telemetry)
* **Security & Auth:** JWT (`Flask-JWT-Extended`), Werkzeug Password Hashing
* **AI Integration:** OpenAI API (`gpt-4.1-mini`) with Prompt Grounding
* **Testing & Quality:** Pytest, Custom Exception Hierarchies

---

## 🛠️ Key Architectural Features

1. **Separation of Concerns (Dual-Database):** 
   * **MySQL** manages relational, ACID-compliant stock records, categories, and user accounts.
   * **MongoDB** handles unstructured system audit logs, tracking user actions and AI queries asynchronously.
2. **AI Prompt Grounding:** 
   * The `POST /api/inventory/ai` endpoint injects a live snapshot of MySQL inventory records directly into the LLM prompt with strict constraints, eliminating hallucinations and ensuring accurate data retrieval.
3. **Defensive Validation & Security:** 
   * Protected endpoints secured with JWT tokens, parameterized SQL queries to prevent injections, and custom exception handling for robust error management.

---

## 📌 API Endpoints Overview

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/auth/register` | Register a new user account | Public |
| **POST** | `/api/auth/login` | Authenticate and receive a JWT token | Public |
| **GET** | `/api/inventory` | Retrieve all inventory items | Protected (JWT) |
| **POST** | `/api/inventory` | Add a new inventory item | Protected (JWT) |
| **PUT** | `/api/inventory/<id>` | Update an existing inventory item | Protected (JWT) |
| **DELETE** | `/api/inventory/<id>` | Delete an inventory item | Protected (JWT) |
| **POST** | `/api/inventory/ai` | Query live stock data using natural language | Protected (JWT) |

---

## ⚙️ Local Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/PoulomiDutta286/inventory-management-api.git](https://github.com/PoulomiDutta286/inventory-management-api.git)
cd inventory-management-api
