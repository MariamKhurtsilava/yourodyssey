from extensions import app, db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import login_manager


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    file = db.Column(db.String)
    price_kutaisi = db.Column(db.Float, nullable=False)
    price_london = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))

    def __str__(self):
        return f"{self.name}"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    products = db.relationship('Product', backref='category', lazy=True)  

    def __str__(self):
        return f"{self.name}"

    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password_hash = db.Column(db.String)
    role = db.Column(db.String)

    def __init__(self, username, password, role="guest"):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return f"{self.username}"

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        georgia = Category(name='Georgia')
        switzerland = Category(name='Switzerland')
        italy = Category(name='Italy')
        france = Category(name='France')

        admin = User(username="admin", password="password123", role="admin")
        user = User(username="test1", password="pass123")

        db.session.add_all([georgia, switzerland, italy, france, user, admin])
        db.session.commit()

        products = [
            Product(name='Samegrelo', file='samegrelo.jpg', price_kutaisi=1000, price_london=1500, category=georgia),
            Product(name='Tbilisi', file='tbilisi.jpg', price_kutaisi=1500, price_london=2000, category=georgia),
            Product(name='Zurich', file='zurich.jpg', price_kutaisi=2000, price_london=3000, category=switzerland),
            Product(name='Zermatt', file='zermatt.jpg', price_kutaisi=2500, price_london=3500, category=switzerland),
            Product(name='Rome', file='rome.jpg', price_kutaisi=3000, price_london=4000, category=italy),
            Product(name='Milan', file='milan.jpg', price_kutaisi=3500, price_london=4500, category=italy),
            Product(name='Paris', file='paris.jpg', price_kutaisi=4000, price_london=5000, category=france),
            Product(name='Nice', file='nice.jpg', price_kutaisi=4500, price_london=5500, category=france)
        ]

        db.session.add_all(products)
        db.session.commit()
