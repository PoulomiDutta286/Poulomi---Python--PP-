import os
import json
import functools
import logging
from datetime import datetime
from flask import Flask, jsonify, request
#3 components-Flask,jsonify,request from the Flask framework.
# Flask is a lightweight web framework written in Python that is used to develop web applications and APIs.
#We use request to access incoming HTTP request data from the client,such as JSON data, while jsonify converts Python data into a JSON-formatted HTTP response.
#Jsonify and request can be imported in any order.
import mysql.connector
#mysql.connector allows Python to connect to a mysql database and execute SQL queries.
from mysql.connector import Error, IntegrityError # helps handle certain database constraint violations such as registering a user name that already exists.
# Error helps handle database errors
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
# flask_jwt_extended= It is a Python package that helps us implement JWT(Json Web Token) authentication in Flask applications.
# ============================================================
# CONFIGURATION & LOGGING SETUP
# ============================================================
load_dotenv()
#load_dotenv() is a function from the python-dotenv package that loads environment variables from a .env file into the environment.
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)# When we call the Flask class, Python internally executes its constructor(__intit__)to initialize the new object.                                                                                                                        
                 
# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
jwt = JWTManager(app) 
#config stores different settings and options that determine how your Flask application should work.
#JWT_SECRET_KEY= The value stored under this key is the secret key you should use for signing and verifying JWT tokens.

# ============================================================
# CORE PYTHON: CUSTOM EXCEPTIONS
# ============================================================
class InventoryError(Exception):# By writing (Exception), we tell Python that InventoryError should behave like a proper Python exception
    """Base exception for inventory domain errors."""
    pass #pass means we are not adding any additional code inside the class for now.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          

class ItemNotFoundError(InventoryError):# creating another custom exception class(these classes are called custom exception classes because we the programmers create these classes ourselves to represent specific errors in our application)
    """Raised when an inventory item does not exist."""
    pass

class InvalidDataError(InventoryError):
    """Raised provided inventory data fails validation."""
    pass

class AuthenticationError(InventoryError):
    """Raised when user authentication fails."""
    pass


# ============================================================
# ADVANCED PYTHON: DECORATORS & GENERATORS
# ============================================================
def log_and_time_transaction(func):# We are defining a function called log_and_time_transaction that takes another function as an argument.
    """Decorator to log execution and trace errors."""
    #log_and_time_transaction takes another function and adds extra functionality to that function without modifying its original code. Therefore, it's called a decorator.
    @functools.wraps(func)# func is the original function.
    def wrapper(*args, **kwargs):#kwargs is used to collect the number of keyword arguments. It collects the arguments passed in the form of key=value pairs into a dictionary.
        logging.info(f"-> Starting execution: {func.__name__}")# func._name_ is the name of the function.
     #This statement is here because we want the log message to be generated every time the decorated function is called,just before the original function starts executing.   
        try:
            result = func(*args, **kwargs) 
            # Writing func(*args,**kwargs)actually calls and executes the original functio
            #result stores whatever value the original function returns after executing.
            logging.info(f"<- Successfully completed: {func.__name__}")
            return result
#We want to send the original function's returned value back to whoever called the decorated function.        
        except Exception as e:
            logging.error(f"X Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

def inventory_batch_generator(records, batch_size=5):# records=['A','B','C','D','E','F']
    #batch_size=5 means there will be 5 records in each batch.
    """Generator to yield inventory records in controlled batches."""
    for i in range(0, len(records), batch_size):
        yield records[i:i + batch_size]
#Programmer has written the generator function but has never actually called it.

# ============================================================
# OBJECT-ORIENTED PROGRAMMING: DATABASE HANDLERS
# ============================================================
class MySQLDatabaseManager: #db=MySQLDatabaseManager then db is an object only because whenever there is a class name followed by a parentheses() then Python is instructed to create a new object using that class.
    """Encapsulates all MySQL relational operations (Inventory & Users)."""
    def __init__(self):#self object is not defined anywhere it is passed as parameter to def_init_(self)
        self.host = os.getenv("MYSQL_HOST", "localhost")
#os.getenv() is a Python function used to get the value of an environment variable.        
        self.port = int(os.getenv("MYSQL_PORT", 3306))
        self.user = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD", "Ankhi@1234")
        self.database = os.getenv("MYSQL_DATABASE", "inventory_management")
        self._initialize_tables()
#


    def get_connection(self):# Because it's the function's job to connect to mysql.
        return mysql.connector.connect(
            host=self.host, port=self.port, user=self.user,
            password=self.password, database=self.database
        )

    def _initialize_tables(self):#define a function initialize that takes in the parameter self.: colon indicates that the body of the method begins on the next indented line. 
        #Because _initialize_tables() must first create the database if it doesn't exist.

#Therefore, _initialize_tables() connects without specifying a database, creates it, and then selects it.
        """Initializes MySQL database, inventory table, and users table if not exist."""
        try:
            #try: is used to attempt the database operations (connecting, creating the database and tables) while allowing the program to handle any errors through the corresponding except block.
            conn = mysql.connector.connect(
                host=self.host, port=self.port, user=self.user, password=self.password
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}`")
           #Creates a new database in MySQL. The purpose of this code is to connect to MySQL, create the required database if it doesn't exist, create two tables (inventory and users), and then close the connection.
            conn.database = self.database
            
            # Inventory Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    inventory_date DATE NOT NULL,
                    material_type VARCHAR(150) NOT NULL,
                    quantity INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # Users Table for Authentication
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            logging.error(f"MySQL Initialization Failed: {e}")

    @log_and_time_transaction
    def register_user(self, username, password):
        try:
            hashed_pw = generate_password_hash(password)
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed_pw)
            )
            conn.commit()
            user_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return user_id
        except IntegrityError:
            raise InvalidDataError("Username already exists.")

    @log_and_time_transaction
    def verify_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            raise AuthenticationError("Invalid username or password.")
        return user

    @log_and_time_transaction
    def fetch_all(self):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, inventory_date, material_type, quantity FROM inventory ORDER BY id DESC")
        rows = cursor.fetchall()
        for row in rows:
            if row.get("inventory_date"):
                row["inventory_date"] = row["inventory_date"].strftime("%d/%m/%y")
        cursor.close()
        conn.close()
        return rows

    @log_and_time_transaction
    def insert_record(self, date_text, material, quantity):
        try:
            date_val = datetime.strptime(date_text, "%d/%m/%y").date()
            qty = int(quantity)
            if qty < 0:
                raise ValueError("Quantity cannot be negative.")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO inventory (inventory_date, material_type, quantity) VALUES (%s, %s, %s)",
                (date_val, material, qty)
            )
            conn.commit()
            new_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return new_id
        except ValueError as ve:
            raise InvalidDataError(f"Invalid input data. Details: {ve}")

    @log_and_time_transaction
    def update_record(self, record_id, material, quantity):
        try:
            qty = int(quantity)
            if qty < 0:
                raise ValueError("Quantity cannot be negative.")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE inventory SET material_type = %s, quantity = %s WHERE id = %s",
                (material, qty, record_id)
            )
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            conn.close()
            if affected == 0:
                raise ItemNotFoundError(f"Record with ID {record_id} not found.")
            return True
        except ValueError as ve:
            raise InvalidDataError(f"Invalid update data. Details: {ve}")

    @log_and_time_transaction
    def delete_record(self, record_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = %s", (record_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        if affected == 0:
            raise ItemNotFoundError(f"Record with ID {record_id} not found.")
        return True


class MongoAuditManager:
    """Encapsulates MongoDB operations for auditing and logging."""
    def __init__(self):
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(uri)
        self.db = self.client["inventory_audit_db"]
        self.collection = self.db["system_logs"]

    def log_event(self, action, payload, user="system"):
        log_doc = { 
            "action": action,
            "performed_by": user,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.collection.insert_one(log_doc)


# Instantiate Managers
db_mysql = MySQLDatabaseManager()
db_mongo = MongoAuditManager()


# ============================================================
# FILE I/O OPERATIONS
# ============================================================
def export_inventory_to_json(filepath="inventory_backup.json"):
    """Exports inventory records to a local JSON file."""
    records = db_mysql.fetch_all()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4)
    return filepath


# ============================================================
# RESTFUL API DEVELOPMENT (AUTH & INVENTORY ENDPOINTS)
# ============================================================

# 1. Authentication Endpoints
@app.route("/api/auth/register", methods=["POST"])
def api_register():
    try:
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise InvalidDataError("Username and password are required.")

        user_id = db_mysql.register_user(username, password)
        db_mongo.log_event("REGISTER_USER", {"username": username}, user=username)
        return jsonify({"status": "success", "message": "User registered successfully", "id": user_id}), 201
    except InventoryError as ie:
        return jsonify({"status": "fail", "message": str(ie)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise InvalidDataError("Username and password are required.")

        user = db_mysql.verify_user(username, password)
        access_token = create_access_token(identity=user["username"])
        db_mongo.log_event("LOGIN_USER", {"username": username}, user=username)
        
        return jsonify({"status": "success", "access_token": access_token}), 200
    except AuthenticationError as ae:
        return jsonify({"status": "fail", "message": str(ae)}), 401
    except InventoryError as ie:
        return jsonify({"status": "fail", "message": str(ie)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 2. Inventory Endpoints (Protected by JWT)
@app.route("/api/inventory", methods=["GET"])
def api_get_inventory():
    try:
        items = db_mysql.fetch_all()
        categories = tuple({item["material_type"] for item in items})
        return jsonify({
            "status": "success",
            "unique_categories": categories,
            "count": len(items),
            "data": items
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/inventory", methods=["POST"])
@jwt_required()
def api_add_inventory():
    try:
        current_user = get_jwt_identity()
        req_data = request.get_json() or {}
        date_text = req_data.get("date")
        material = req_data.get("material")
        quantity = req_data.get("quantity")

        if not all([date_text, material, quantity]):
            raise InvalidDataError("Missing required fields: date, material, quantity.")

        new_id = db_mysql.insert_record(date_text, material, quantity)
        db_mongo.log_event("INSERT", {"id": new_id, "material": material, "quantity": quantity}, user=current_user)

        return jsonify({"status": "success", "message": "Record created successfully", "id": new_id}), 201
    except InventoryError as ie:
        return jsonify({"status": "fail", "message": str(ie)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/inventory/<int:record_id>", methods=["PUT"])
@jwt_required()
def api_update_inventory(record_id):
    try:
        current_user = get_jwt_identity()
        req_data = request.get_json() or {}
        material = req_data.get("material")
        quantity = req_data.get("quantity")

        if not material or quantity is None:
            raise InvalidDataError("Missing update fields: material, quantity.")

        db_mysql.update_record(record_id, material, quantity)
        db_mongo.log_event("UPDATE", {"id": record_id, "material": material, "quantity": quantity}, user=current_user)

        return jsonify({"status": "success", "message": f"Record {record_id} updated successfully"}), 200
    except ItemNotFoundError as infe:
        return jsonify({"status": "fail", "message": str(infe)}), 404
    except InventoryError as ie:
        return jsonify({"status": "fail", "message": str(ie)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/inventory/<int:record_id>", methods=["DELETE"])
@jwt_required()
def api_delete_inventory(record_id):
    try:
        current_user = get_jwt_identity()
        db_mysql.delete_record(record_id)
        db_mongo.log_event("DELETE", {"id": record_id}, user=current_user)

        return jsonify({"status": "success", "message": f"Record {record_id} deleted successfully"}), 200
    except ItemNotFoundError as infe:
        return jsonify({"status": "fail", "message": str(infe)}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/export", methods=["GET"])
@jwt_required()
def api_export_file():
    try:
        path = export_inventory_to_json()
        return jsonify({"status": "success", "file_path": path}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# AUTOMATED TESTING SUITE (PYTEST)
# ============================================================
def test_flask_endpoints():
    app.config["TESTING"] = True
    client = app.test_client()

    # Test Public GET Inventory Endpoint
    response = client.get("/api/inventory")
    assert response.status_code == 200
    json_data = response.get_json()
    assert "data" in json_data


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
