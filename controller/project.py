from flask import Blueprint, render_template, redirect, request, url_for, current_app, send_from_directory, flash
from werkzeug.utils import secure_filename
import os
from models import db
from models.tables import Item
from forms.form import SellItemForm, UpdateItemForm
import traceback
from flask import render_template
from models.tables import Article
from models.tables import Event
from forms.form import CreateEventForm, ModifyEventForm



project = Blueprint('project', __name__)
cart_items = {}

@project.route('/')
def index():
    return render_template('index.html')

@project.route('/items')
def item_listing():
    items = Item.query.all()
    return render_template('items.html', items=items)

@project.route('/imgages/<image_name>')
def get_image(image_name):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], image_name)

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
def logout():
    logout_user()
    return redirect(url_for('login'))

@project.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    item = Item.query.get(item_id)

    if item:
        # Add the item to the cart or increment its quantity if already in the cart
        cart_items[item.id] = cart_items.get(item.id, 0) + 1
        flash(f'Item {item.title} added to cart!', 'success')
    else:
        flash('Item not found', 'error')

    return redirect(url_for('project.item_listing'))

@project.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    item = Item.query.get(item_id)

    if item:
        # Remove the item from the cart or decrease its quantity
        if item.id in cart_items:
            cart_items[item.id] -= 1
            if cart_items[item.id] == 0:
                del cart_items[item.id]  # Remove the item from the cart if quantity is zero
            flash(f'Removed one {item.title} from the cart!', 'success')
        else:
            flash('Item not found in the cart', 'error')
    else:
        flash('Item not found', 'error')

    return redirect(url_for('project.view_cart'))

@project.route('/cart')
def view_cart():
    items_in_cart = []

    print(f"cart_items type: {type(cart_items)}")  # Debug print

    for item_id, quantity in cart_items.items():
        item = Item.query.get(item_id)
        if item:
            items_in_cart.append({'item': item, 'quantity': quantity})

    total_price = sum(int(cart_item['item'].price) * int(cart_item['quantity']) for cart_item in items_in_cart)

    return render_template('cart.html', items_in_cart=items_in_cart, total_price=total_price)

@project.route('/payment_confirmation')
def payment_confirmation():
    try:
        items_in_cart = []

        for item_id, quantity in cart_items.items():
            item = Item.query.get(item_id)
            if item:
                items_in_cart.append({'item': item, 'quantity': quantity})

        total_price = sum(int(cart_item['item'].price) * int(cart_item['quantity']) for cart_item in items_in_cart)

        return render_template('payment_confirmation.html', total_price=total_price)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
        flash('An error occurred during payment confirmation. Please try again later.', 'error')
        return redirect(url_for('project.view_cart'))  # Redirect to the cart if an error occurs

@project.route('/checkout', methods=['GET', 'POST'])
def checkout():
    try:
        if request.method == 'POST':
            # No payment processing logic here, as we are not assuming payment success

            # Redirect to a confirmation page without clearing the cart
            return redirect(url_for('project.payment_confirmation'))

        # Calculate total_price here
        total_price = sum(int(cart_items.get(item_id, 0)['item'].price) * int(cart_items.get(item_id, 0)['quantity']) for item_id in cart_items)

        return render_template('checkout.html', total_price=total_price)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
        flash('An error occurred during checkout. Please try again later.', 'error')
        return redirect(url_for('project.view_cart'))

@project.route('/articles')
def articles():
    articles = Article.query.all()
    return render_template('articles.html', articles=articles)

@project.route('/upload_article', methods=['GET', 'POST'])
def upload_article():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')


        new_article = Article(title=title, content=content)
        db.session.add(new_article)
        db.session.commit()


        flash('Article uploaded successfully!', 'success')


    return render_template('upload_article.html')


## Event Part
@project.route('/events')
def events():
    # Display a list of events
    events = Event.query.all()
    return render_template('events.html', events=events)

@project.route('/create_event', methods=['GET', 'POST'])
def create_event():
    # Route to create a new event
    form = CreateEventForm()

    if form.validate_on_submit():
        # Create a new event and add it to the database
        new_event = Event(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            location=form.location.data
        )
        db.session.add(new_event)
        db.session.commit()

        flash('Event created successfully!', 'success')
        return redirect(url_for('project.events'))

    return render_template('create_event.html', form=form)

@project.route('/events/<int:event_id>')
def view_event(event_id):
    # Display details of a specific event
    event = Event.query.get(event_id)
    if not event:
        abort(404)  # Not Found: Event doesn't exist

    return render_template('event_details.html', event=event)

@project.route('/modify_event/<int:event_id>', methods=['GET', 'POST'])
def modify_event(event_id):
    # Get the event details from the database
    event = Event.query.get(event_id)

    if not event:
        # Handle the case where the event doesn't exist
        flash('Event not found', 'error')
        return redirect(url_for('project.events'))

    form = ModifyEventForm(obj=event)

    if form.validate_on_submit():
        # Update the event details in the database
        form.populate_obj(event)
        db.session.commit()

        flash('Event modified successfully!', 'success')
        return redirect(url_for('project.events'))

    return render_template('modify_event.html', event=event, form=form)

@project.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    # Delete an event from the database
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        flash(f'Event "{event.title}" deleted successfully!', 'success')
    else:
        flash('Event not found', 'error')

    return redirect(url_for('project.events'))