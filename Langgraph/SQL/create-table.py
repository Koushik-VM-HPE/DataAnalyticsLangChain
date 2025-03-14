from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Table, MetaData

# Step 1: Set up SQLite database
DATABASE_URL = "sqlite:///example.db"  # Using SQLite for simplicity

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

# Step 2: Define the 'products', 'orders', and 'order_items' tables

class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price = Column(Float)

class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer)
    order_date = Column(String)

class OrderItem(Base):
    __tablename__ = 'order_items'

    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))
    quantity = Column(Integer)
    price = Column(Float)

# Step 3: Create the tables in the database
Base.metadata.create_all(engine)

# Step 4: Insert some example data into the tables
Session = sessionmaker(bind=engine)
session = Session()

# Example products
product1 = Product(name="Product 1", price=10.0)
product2 = Product(name="Product 2", price=20.0)
product3 = Product(name="Product 3", price=30.0)

# Example orders
order1 = Order(customer_id=1, order_date="2025-03-12")
order2 = Order(customer_id=2, order_date="2025-03-13")

# Example order items
order_item1 = OrderItem(order_id=1, product_id=1, quantity=2, price=10.0)
order_item2 = OrderItem(order_id=1, product_id=2, quantity=1, price=20.0)
order_item3 = OrderItem(order_id=2, product_id=3, quantity=3, price=30.0)

# Add all the data to the session and commit
session.add_all([product1, product2, product3, order1, order2, order_item1, order_item2, order_item3])
session.commit()

# Verify by querying the products and orders tables
products = session.query(Product).all()
orders = session.query(Order).all()

print("Products:")
for product in products:
    print(f"{product.product_id}: {product.name}, Price: {product.price}")

print("\nOrders:")
for order in orders:
    print(f"{order.order_id}: Customer {order.customer_id}, Date: {order.order_date}")

# Close the session
session.close()
