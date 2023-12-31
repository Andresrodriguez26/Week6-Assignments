from werkzeug.security import generate_password_hash  # Generates a unique password hash for extra security 
from flask_sqlalchemy import SQLAlchemy # This is our ORM (Object Relational Mapper)
from flask_login import UserMixin, LoginManager # Helping us load a user as our current_user
from datetime import datetime # Put a timestap on any data we create (Users, Products, etc)
import uuid # Makes a unique id for our data (primary key)
from flask_marshmallow import Marshmallow

from .helpers import get_image 

# Instantiate all our classes
db = SQLAlchemy() # Make database object
login_manager = LoginManager() # Makes login object
ma = Marshmallow()


# Use login_manager to reate a user_loader function
@login_manager.user_loader
def load_user(user_id):
    
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    return User.query.get(user_id) # This is a basic query inside our database to bring back a specific User object



# Think of these as admin (keeping track of what products are available to sell)
class User(db.Model, UserMixin):
    # CREATE TABLE USER, all the columns we create
    user_id = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    username = db.Column(db.String(30), nullable=False, unique=True)
    email =  db.Column(db.String(30), nullable=False, unique=True)
    password =  db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow) # This is going to grab a timestamp as soon as a User object is instantiated

    # INSERT INTO User() Values()
    def __init__(self, username, email, password, first_name="", last_name=""):
        self.user_id = self.set_id()
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = self.set_password(password)

    # Methods for editting our attributes
    def set_id(self):
        return str(uuid.uuid4()) # All this is doing is creating a unique idetification token
    

    def get_id(self):
        return str(self.user_id) # UserMixin using this method to grab the user_id on the object logged in
    

    def set_password(self, password):
        return generate_password_hash(password) # Hashes the password so it is secure (aka no one can see it)
    

    def __repr__(self):
        return f"<user: {self.username}>"
       

class Product(db.Model): # db.Model helps us translate python code to columns in SQL
    prod_id = db.Column(db.String, primary_key="True")
    name = db.Column(db.String(50), nullable="False")
    image = db.Column(db.String)
    description = db.Column(db.String(200))
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Eventually we need to connect this to orders

    def __init__(self, name, price, quantity, image="", description=""):
        self.prod_id = self.set_id()
        self.name = name
        self.image = self.set_image(image, name)
        self.description = description
        self.price = price
        self.quantity = quantity


    def set_id(self):
        return str(uuid.uuid4())
    

    def set_image(self, image, name):

        if not image: # Aka the user didnt give us an image
            image = get_image(name) # Name is going to become search & we are going to use it to make our api call
            # Comeback and add our api call

        return image
    
    # We need a method for when customers buy products to decrement & increment our quantity
    def decrement_quantity(self, quantity):
       
        self.quantity -= int(quantity)
        return self.quantity
    
    def increment_quantity(self, quantity):
        
        self.quantity += int(quantity)
        return self.quantity
    

    def __repr__(self):
        return f"<Product: {self.name}>"
    




# Creating our Schema class (Schema essentially just means what our data "looks" like, and our data needs to look like a dictionary (json) not an object)



class ProductSchema(ma.Schema):

    class Meta:
        fields = ["prod_id", "name", "image", "description", "price", "quantity"]



# Instantiate our ProductSchema class so we can use them in our application
product_schema = ProductSchema() # This is 1 singular product
products_schema = ProductSchema(many="True") # Bringing back all the products in our database & sending to frontend