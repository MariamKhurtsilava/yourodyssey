from flask import Flask, render_template, request, redirect, flash,  url_for, session
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash
from extensions import app, db
from forms import RegisterForm, LoginForm, UpdatePasswordForm, AddProductForm
from werkzeug.utils import secure_filename
from models import Product, Category, User
import os


products = [
    {"name": "Samegrelo", "file": "samegrelo.jpg", "price": 1000, "id": "1"},
    {"name": "Tbilisi", "file": "tbilisi.jpg", "price": 1500, "id": "2"},
    {"name": "Zurich", "file": "zurich.jpg", "price": 2000, "id": "3"},
    {"name": "Zermatt", "file": "zermatt.jpg", "price": 2500, "id": "4"},
    {"name": "Rome", "file": "rome.jpg", "price": 3000, "id": "5"},
    {"name": "Milan", "file": "milan.jpg", "price": 3500, "id": "6"},
    {"name": "Paris", "file": "paris.jpg", "price": 4000, "id": "7"},
    {"name": "Nice", "file": "nice.jpg", "price": 4500, "id": "8"},
]


@app.route("/populate_data")
def populate_data():
    for product in products:
        product_to_add = Product(name=product["name"], price=product["price"], file=product["file"])
        db.session.add(product_to_add)
    db.session.commit()
    print(Product.query.all())
    return redirect("/")

@app.route("/")
def home():
    products = Product.query.all()
    return render_template("index.html", products=products)

@app.route("/start_your_journey", methods=['GET', 'POST'])
def start_your_journey():
    products = Product.query.all()
    price = None
    origin = 'kutaisi'
    destination = None
    adults = 1
    children = 0
    package = 'basic'
    
    london_prices = {
        "Samegrelo": 1500,
        "Tbilisi": 2000,
        "Zurich": 2500,
        "Zermatt": 3000,
        "Rome": 3500,
        "Milan": 4000,
        "Paris": 4500,
        "Nice": 5000
    }


    if request.method == 'POST':
        if 'check_price' in request.form:
            origin = request.form['origin']
            destination_id = int(request.form['destination'])
            destination = Product.query.get(destination_id)

            adults = int(request.form['adults'])
            children = int(request.form['children'])
            package = request.form['package']

            if origin == 'london':
                base_price = london_prices.get(destination.name, destination.price_london)
            else:
                base_price = destination.price_kutaisi

            adult_price = base_price * adults
            child_price = (base_price / 2) * children

            price = adult_price + child_price

            if package == 'pack_and_save':
                price += 200
            elif package == 'all_in_full_flex':
                price += 500

    return render_template("start_your_journey.html", products=products, price=price, origin=origin, destination=destination, adults=adults, children=children, package=package, london_prices=london_prices)


@app.route("/inspire")
def inspire():
    return render_template("inspire.html")


@app.route('/detail/<int:id>')
def detail(id):
    current = Product.query.get(id)
    return render_template("details.html", product=current)




@app.route("/delete/<int:id>")
@login_required
def delete_product(id):
    if current_user.role == "admin":
        current = Product.query.get(id)
        db.session.delete(current)
        db.session.commit()
        flash("Product deleted successfully", category="success")
    else:
        flash("You are not authorized to delete products.", category="danger")
    return redirect("/")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_product(id):
   
    if current_user.role == "admin":
        
        current_product = Product.query.get(id)
        
      
        form = AddProductForm(
            name=current_product.name,
            price_kutaisi=current_product.price_kutaisi,
            price_london=current_product.price_london
        )
        
        if form.validate_on_submit():
         
            current_product.name = form.name.data
            current_product.price_kutaisi = form.price_kutaisi.data
            current_product.price_london = form.price_london.data
            
            
            db.session.commit()
            
            flash("Product updated successfully", category="success")
            return redirect("/")
        
       
        if form.errors:
            flash("Error updating product. Please check your inputs.", category="danger")
        
       
        return render_template("addproduct.html", form=form)
    
    else:
       
        return "You are not authorized to edit products.", 404

@app.route("/category/<int:category_id>")
def category_select(category_id):
    current_category = Category.query.get(category_id)
    products = current_category.products  
    return render_template("start_your_journey.html", category=current_category, products=products)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("You successfully registered", category="success")
        return redirect("/")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("You successfully logged in", category="success")
            return redirect("/")
        else:
            flash("Invalid username or password", category="danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", category="success")
    return redirect("/")


@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    if request.method == 'POST':
    
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        adults = request.form.get('adults')
        children = request.form.get('children')
        package = request.form.get('package')
        price = request.form.get('price')
        
        
        session['booking_details'] = {
            'origin': origin,
            'destination': destination,
            'adults': adults,
            'children': children,
            'package': package,
            'price': price
        }
        
        
        return redirect(url_for('profile'))
    else:
       
        return redirect(url_for('index')) 


@app.route('/update_password', methods=['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect", category="danger")
        elif form.new_password.data != form.confirm_password.data:
            flash("New passwords do not match", category="danger")
        else:
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Password updated successfully", category="success")
            return redirect(url_for("profile"))

    return render_template("update_password.html", form=form)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UpdatePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect", category="danger")
        elif form.new_password.data != form.confirm_password.data:
            flash("New passwords do not match", category="danger")
        else:
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Password updated successfully", category="success")
            return redirect(url_for("profile")) 

    return render_template("profile.html", form=form, user=current_user) 

if __name__ == '__main__':
    app.run(debug=True)  