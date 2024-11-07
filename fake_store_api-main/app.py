from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# MySQL connection setup (use this function to create a new connection each time)
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",      # Change to your MySQL host if necessary
        user="root",           # MySQL user (default is 'root' for localhost)
        password="",           # MySQL password (leave blank if none)
        database="ma"          # The name of your database ('ma' in this case)
    )
    return conn

# Root route
@app.get('/')
def home():
    return jsonify({"message": "Welcome to the API"})


# Route to get all products
@app.get('/products')
def getProducts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM product''')
    data = cursor.fetchall()
    conn.close()

    product_list = []
    for item in data:
        product_list.append(
            {
                "id": item[0],
                "title": item[1],
                "price": item[4],
                "description": item[3],
                "category": item[2],
                "image": item[5],
                "rating": {
                    "rate": 3.9,  # Placeholder, you can replace with actual rating logic
                    "count": 120  # Placeholder for rating count
                }
            }
        )
    return jsonify(product_list)


# Route to get a single product by its ID
@app.get('/products/<int:product_id>')
def getProduct(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM product WHERE id = %s''', (product_id,))
    data = cursor.fetchone()
    conn.close()

    if data:
        product = {
            "id": data[0],
            "title": data[2],
            "price": data[4],
            "description": data[6],
            "category": data[3],
            "image": data[5],
            "rating": {
                "rate": 3.9,  # Placeholder
                "count": 120  # Placeholder
            }
        }
        return jsonify(product)
    else:
        return jsonify({"error": "Product not found"}), 404


# Route to get user details by their ID
@app.get('/users/<int:user_id>')
def getUser(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE id = %s''', (user_id,))
    data = cursor.fetchone()
    conn.close()

    if data:
        user = {
            "id": data[0],
            "name": data[1],
            "email": data[2],
            "password": data[3],  # Note: Ideally, do not expose passwords
        }
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404


# New login route
@app.post('/login')
def login():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE name = %s"
    cursor.execute(query, (name,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[3], password):  # Check password hash
        user_data = {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "imgURL": user[4],
        }
        return jsonify({"message": "Login successful", "user": user_data}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


# Route to add a product to the user's cart
@app.post('/add_to_cart')
def add_to_cart():
    data = request.get_json()
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)  # Default quantity is 1

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the user exists
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    # Check if the product exists
    cursor.execute("SELECT * FROM product WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    if not product:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    try:
        cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                       (user_id, product_id, quantity))
        conn.commit()
        conn.close()
        return jsonify({"message": "Product added to cart successfully"}), 201
    except mysql.connector.Error as err:
        conn.close()
        return jsonify({"error": str(err)}), 400


if __name__ == '__main__':
    app.run(debug=True)
