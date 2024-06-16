import requests
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

from scrapping import extract_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://killercoseru:SCFt4ja2ougp@ep-holy-surf-a2elkdep.eu-central-1.aws.neon.tech/DIALDIVER?sslmode=require'
db = SQLAlchemy(app)
auth = HTTPTokenAuth(scheme='Bearer')
old_products = []

# Define the User model
class Users(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    firstname = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<Users %r>' % self.username

# Define the Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer)
    brand = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    specs = db.Column(db.String(2000))
    new = db.Column(db.Boolean, default=True, nullable=False)
    shop = db.Column(db.String(255))

    def __repr__(self):
        return '<Product %r>' % self.name

# Dummy token generator function
def generate_token():
    return secrets.token_urlsafe(16)

@auth.verify_token
def verify_token(token):
    user = Users.query.filter_by(token=token).first()
    return user

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    data = request.json
    user = Users.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        if not user.token:
            user.token = generate_token()
            db.session.commit()
        return jsonify({'token': user.token, 'firstname': user.firstname, 'lastname': user.lastname})
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Token is missing or invalid'}), 400

    token = auth_header.split(' ')[1]
    user = Users.query.filter_by(token=token).first()
    if user:
        user.token = None
        db.session.commit()
        return jsonify({'message': 'Logged out successfully'}), 200

    return jsonify({'error': 'Invalid token'}), 401


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    firstname = data.get('firstname')
    lastname = data.get('lastname')

    # Check if username and password are provided
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Check if the username already exists
    if Users.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    # Create a new user
    hashed_password = generate_password_hash(password)
    token = generate_token()
    new_user = Users(username=username, password=hashed_password, token=token, firstname= firstname, lastname=lastname)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Users created successfully'}), 201

# Define the UserPreferences model
class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'), nullable=False)
    id_product = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    user = db.relationship('Users', backref=db.backref('preferences', lazy=True))
    product = db.relationship('Product', backref=db.backref('preferences', lazy=True))

    def __repr__(self):
        return f'<UserPreferences {self.id_user} - {self.id_product}>'

# Define the ProductPrices model
class ProductPrices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_product = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    product = db.relationship('Product', backref=db.backref('prices', lazy=True))

    def __repr__(self):
        return f'<ProductPrices {self.id_product} - {self.price}>'

@app.route('/prices/query/<string:id_user>', methods=['GET'])
@auth.login_required
def query_prices(id_user):
    # Query the user preferences
    preferences = UserPreferences.query.filter_by(id_user=id_user).all()

    if not preferences:
        return jsonify({'error': 'No preferences found for this user'}), 404

    # Fetch the product prices based on preferences
    prices = []
    for preference in preferences:
        product_prices = ProductPrices.query.filter_by(id_product=preference.id_product).order_by(ProductPrices.timestamp.desc()).all()
        if product_prices:
            latest_price = product_prices[0]
            prices.append({
                'product_id': preference.id_product,
                'price': latest_price.price,
                'timestamp': latest_price.timestamp,
                'product_name': preference.product.name
            })

    return jsonify({'prices': prices})


@app.route('/filter/categories', methods=['GET'])
@auth.login_required
def filter_categories():
    # Fetch categories from Product table
    categories = db.session.query(Product.category).group_by(Product.category).all()

    # Format the response
    category_list = [category[0] for category in categories]

    return jsonify({'categories': category_list})

@app.route('/filter/brands', methods=['GET'])
@auth.login_required
def filter_brands():
    # Fetch categories from Product table
    brands = db.session.query(Product.brand).group_by(Product.brand).all()

    # Format the response
    brand_list = [brand[0] for brand in brands]

    return jsonify({'brands': brand_list})

@app.route('/preferences', methods=['GET'])
@auth.login_required
def preferences():
    user = auth.current_user()

    # Fetch user preferences from UserPreferences table
    preferences = UserPreferences.query.filter_by(id_user=user.id_user).all()

    if not preferences:
        return jsonify({'error': 'No preferences found for this user'}), 404

    # Collect preferred products
    preferred_products = []
    for preference in preferences:
        product = Product.query.filter_by(id=preference.id_product).first()
        if product:
            preferred_products.append({
                'product_id': product.id,
                'name': product.name,
                'category': product.category,
                'brand': product.brand
            })

    return jsonify({'preferences': preferred_products})


@app.route('/filter/category/<string:category>/brands', methods=['GET'])
@auth.login_required
def filter_brands_by_category(category):
    # Fetch brands from Product table based on category
    brands = db.session.query(Product.brand).filter_by(category=category).group_by(Product.brand).all()

    # Format the response
    brand_list = [brand[0] for brand in brands]

    return jsonify({'brands': brand_list})

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get the URL of the website to scrape from the request
    url = request.json.get('url')

    # Check if URL is provided
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {e}'}), 500

    # Extract product data
    products = extract_data(url,"div",'product')

    return jsonify({'products': products})

@app.route('/prices/all', methods=['GET'])
@auth.login_required
def get_all_prices():
    # Fetch all records from Product table
    all_products = Product.query.all()

    # Format the response
    product_list = [
        {
            'id': product.id,
            'name': product.name,
            'brand': product.brand,
            'model': product.model,
            'link': product.link,
            'price': product.price,
            'discount': product.discount,
            'disc': product.discount,  # Assuming 'disc' is another name for 'discount'
            'new': product.new,
            'category': product.category
        } for product in all_products
    ]

    return jsonify({'products': product_list})

@app.route('/preferences', methods=['POST'])
@auth.login_required
def add_preferences():
    user = auth.current_user()
    data = request.json

    id_product = data.get('id_product')
    category = data.get('category')
    brand = data.get('brand')

    if not id_product and not category and not brand:
        return jsonify({'error': 'Product ID, category, or brand is required'}), 400

    preferences_added = 0

    if id_product:
        # Check if the product exists
        product = Product.query.filter_by(id=id_product).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Check if the preference already exists
        existing_preference = UserPreferences.query.filter_by(id_user=user.id_user, id_product=id_product).first()
        if not existing_preference:
            # Create a new user preference
            new_preference = UserPreferences(id_user=user.id_user, id_product=id_product)
            db.session.add(new_preference)
            preferences_added += 1

    if category:
        # Fetch all products in the specified category
        products_in_category = Product.query.filter_by(category=category).all()
        for product in products_in_category:
            existing_preference = UserPreferences.query.filter_by(id_user=user.id_user, id_product=product.id).first()
            if not existing_preference:
                # Create a new user preference
                new_preference = UserPreferences(id_user=user.id_user, id_product=product.id)
                db.session.add(new_preference)
                preferences_added += 1

    if brand:
        # Fetch all products of the specified brand
        products_by_brand = Product.query.filter_by(brand=brand).all()
        for product in products_by_brand:
            existing_preference = UserPreferences.query.filter_by(id_user=user.id_user, id_product=product.id).first()
            if not existing_preference:
                # Create a new user preference
                new_preference = UserPreferences(id_user=user.id_user, id_product=product.id)
                db.session.add(new_preference)
                preferences_added += 1

    if preferences_added > 0:
        db.session.commit()
        return jsonify({'message': f'{preferences_added} preferences added successfully'}), 201
    else:
        return jsonify({'message': 'No new preferences were added'}), 200

# Define the PricesMW model
class PricesMW(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer)
    disc = db.Column(db.Integer)  # Assuming 'disc' is another name for 'discount'
    new = db.Column(db.Boolean, default=True, nullable=False)
    category = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<PricesMW {self.id}>'

@app.route('/top_prices_mw', methods=['GET'])
@auth.login_required
def get_top_prices_mw():
    try:
        # Query to select the top 10 rows from the PricesMW table
        top_prices_mw = PricesMW.query.order_by(PricesMW.disc.desc()).limit(10).all()
        # Convert the results to a list of dictionaries
        top_prices_mw_dict = [{'id': price.id,
                               'name': price.name,
                               'brand': price.brand,
                               'model': price.model,
                               'link': price.link,
                               'price': price.price,
                               'discount': price.discount,
                               'disc': price.disc,
                               'new': price.new,
                               'category': price.category} for price in top_prices_mw]
        return jsonify({'top_prices_mw': top_prices_mw_dict})
    except Exception as e:
        return jsonify({'error': f'Failed to fetch top prices: {str(e)}'}), 500

@app.route('/top_discount_products/brand/<string:brand>', methods=['GET'])
@auth.login_required
def get_top_discount_products(brand):
    try:
        # Write a SQL query to select the top 10 products with the highest discount based on brand
        top_discount_products = db.session.query(PricesMW).filter_by(brand=brand).order_by(PricesMW.disc.desc()).limit(10).all()

        # Convert the results to a list of dictionaries
        top_discount_products_dict = [{'id': product.id,
                                       'name': product.name,
                                       'brand': product.brand,
                                       'model': product.model,
                                       'link': product.link,
                                       'price': product.price,
                                       'discount': product.discount,
                                       'disc': product.disc,
                                       'new': product.new,
                                       'category': product.category} for product in top_discount_products]

        return jsonify({'top_discount_products': top_discount_products_dict})
    except Exception as e:
        return jsonify({'error': f'Failed to fetch top discount products: {str(e)}'}), 500

@app.route('/top_discount_products/<string:category>', methods=['GET'])
@auth.login_required
def get_top_discount_products_by_category(category):
    try:
        # Write a SQL query to select the top 10 products with the highest discount based on category
        top_discount_products = db.session.query(PricesMW).filter_by(category=category).order_by(PricesMW.disc.desc()).limit(10).all()

        # Convert the results to a list of dictionaries
        top_discount_products_dict = [{'id': product.id,
                                        'name': product.name,
                                        'brand': product.brand,
                                        'model': product.model,
                                        'link': product.link,
                                        'price': product.price,
                                        'discount': product.discount,
                                        'disc': product.disc,
                                        'new': product.new,
                                        'category': product.category} for product in top_discount_products]

        return jsonify({'top_discount_products': top_discount_products_dict})
    except Exception as e:
        return jsonify({'error': f'Failed to fetch top discount products: {str(e)}'}), 500

import requests

EMAIL_SERVICE_URL = 'http://localhost:5001/send_email'

def send_email(subject, recipient, body):
    payload = {
        'subject': subject,
        'recipient': recipient,
        'body': body
    }
    try:
        response = requests.post(EMAIL_SERVICE_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send email: {e}")
        return None


@app.route('/notify_new_products', methods=['GET'])
@auth.login_required
def notify_new_products():
    global old_products
    new_products = db.session.query(PricesMW).filter_by(category="PHONE").order_by(PricesMW.disc.desc()).limit(10).all()

    if not new_products:
        return jsonify({'error': 'No products provided'}), 400

    existing_products = old_products
    existing_product_links = {product.link for product in existing_products}

    new_product_links = {product.link for product in new_products}
    new_links = new_product_links - existing_product_links

    new_product_details = [product for product in new_products if product.link in new_links]

    old_products = new_products

    if new_product_details:
        subject = "New Products Notification"
        recipient = auth.current_user().username  # Assuming the username is the email
        body = "New products have been added:\n\n" + "\n".join(
            [f"Name: {product.name}, Brand: {product.brand}, Price: {product.price}" for product in
             new_product_details]
        )
        send_email(subject, recipient, body)

        new_products_dict = [{'id': product.id,
                                       'name': product.name,
                                       'brand': product.brand,
                                       'model': product.model,
                                       'link': product.link,
                                       'price': product.price,
                                       'discount': product.discount,
                                       'disc': product.disc,
                                       'new': product.new,
                                       'category': product.category} for product in new_product_details]

        return jsonify({'message': f'{len(new_product_details)} new products added and notifications sent.', 'data':new_products_dict}), 201
    else:
        return jsonify({'message': 'No new products found'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
