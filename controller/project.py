from flask import Blueprint, render_template, redirect, request, url_for,current_app, send_from_directory,flash, session
from werkzeug.utils import secure_filename  
import os
from models import db
from models.tables import Item
from forms.form import SellItemForm,UpdateItemForm
#from flask_login import UserMixin, login_user, login_required, logout_user,current_user

#from app import image_path

project = Blueprint('project',__name__)

cart_items = []

@project.route('/')
def index():
    return render_template('index.html')


@project.route('/items')
def item_listing():
    items = Item.query.all()  
    return render_template('items.html', items=items)  

@project.route('/imgages/<image_name>')
def get_image(image_name):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],image_name)


@project.route('/sell', methods=['GET', 'POST'])
def sell_item():
    form = SellItemForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        price = form.price.data
        image = form.image.data

        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

            new_item = Item(title=title, description=description, price=price, image_path=filename)

            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for('project.item_listing'))

    return render_template('sell.html', form=form)



@project.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash(f'Item {item.title} deleted successfully!', 'success')
    else:
        flash('Item not found', 'error')
    return redirect(url_for('project.item_listing'))


@project.route('/update/<int:item_id>', methods=['GET', 'POST'])
def update_item(item_id):
    item = Item.query.get(item_id)

    if not item:
        abort(404)  # Not Found: Item doesn't exist

    form = UpdateItemForm(obj=item)  # Create a form and pre-fill with item data

    if form.validate_on_submit():
        # Update the item with the form data
        form.populate_obj(item)
        db.session.commit()

        flash(f'Item {item.title} updated successfully!', 'success')

        return redirect(url_for('project.item_listing'))

    return render_template('update.html', form=form, item=item)



#@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@project.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, phone_number=form.phone_number.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@project.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.email == form.email.data) | (User.phone_number == form.email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard'))
        flash('Login failed. Please check your credentials.', 'danger')
    return render_template('login.html', form=form)


@project.route("/logout")
#@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@project.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    item = Item.query.get(item_id)

    if item:
        cart_items.append(item)  # Assuming `cart_items` is a list where you store the items in the cart
        flash(f'Item {item.title} added to cart!', 'success')
    else:
        flash('Item not found', 'error')

    return redirect(url_for('project.item_listing'))

@project.route('/cart')
def view_cart():
    return render_template('cart.html', cart_items=cart_items)
