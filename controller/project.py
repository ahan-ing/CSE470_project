from flask import Blueprint, render_template, redirect, request, url_for, current_app, send_from_directory, flash,abort
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user,login_manager,LoginManager, UserMixin
import os
from models import db
from models.tables import *
from models.cart import *
from forms.form import *
import traceback
from models.tables import Event, User, db
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import delete
from models.tables import Participant


project = Blueprint('project', __name__)
bcrypt = Bcrypt()
cart_items = {}





@project.route('/')
def index():
    return render_template('index.html')




@project.route('/items')
def item_listing():
    if current_user.is_authenticated:
        if current_user.user_type == 'seller':
            items = Item.query.filter_by(seller_id=current_user.id, is_approved=True).all()
        else:
            items = Item.query.filter_by(is_approved=True).all()
    else:
        items = Item.query.filter_by(is_approved=True).all()


    return render_template('items.html', items=items)






@project.route('/imgages/<image_name>')
def get_image(image_name):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], image_name)






@project.route('/sell', methods=['GET', 'POST'])
@login_required
def sell_item():
    form = SellItemForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        price = form.price.data
        quantity=form.quantity.data
        image = form.image.data
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            is_approved = current_user.is_admin
            new_item = Item(title=title, description=description, price=price, quantity=quantity, image_path=filename, seller_id=current_user.id,is_approved=is_approved)
            db.session.add(new_item)
            db.session.commit()
            flash('Item added successfully. Awaiting admin approval.', 'success')
            return redirect(url_for('project.index'))
    return render_template('sell.html', form=form), 200






def view_item(item_id):
    item = Item.query.get_or_404(item_id)
    if current_user.is_authenticated and item.seller_id == current_user.id:
        return render_template('view_item.html', item=item)
    else:
        flash('You do not have permission to view this item.', 'danger')
        return redirect(url_for('project.index'))






@project.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.seller_id != current_user.id:
        abort(403)  
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('project.items'))






@project.route('/update_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.seller_id != current_user.id:
        abort(403)
    form = UpdateItemForm()
    if form.validate_on_submit():
            item.title = form.title.data
            item.description = form.description.data
            item.price = form.price.data
            item.quantity=form.quantity.data
            item.image_path = form.image_path.data
            db.session.commit()
            flash('Item successfully updated!', 'success')
            return redirect(url_for('project.items', item_id=item.id))
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







@project.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    item = Item.query.get(item_id)

    if item:
        if item.quantity is not None and cart_items.get(item.id, 0) >= item.quantity:
            flash(f'Cannot add more of {item.title} to the cart. Available quantity: {item.quantity}', 'error')
        else:
            cart_items[item.id] = cart_items.get(item.id, 0) + 1
            flash(f'Item {item.title} added to cart!', 'success')
    else:
        flash('Item not found', 'error')

    return redirect(url_for('project.item_listing'))






@project.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    item = Item.query.get(item_id)
    if item:
        if item.id in cart_items:
            cart_items[item.id] -= 1
            if cart_items[item.id] == 0:
                del cart_items[item.id]  
            flash(f'Removed one {item.title} from the cart!', 'success')
        else:
            flash('Item not found in the cart', 'error')
    else:
        flash('Item not found', 'error')


    return redirect(url_for('project.view_cart'))






@project.route('/cart')
def view_cart():
    items_in_cart = []


    print(f"cart_items type: {type(cart_items)}")  


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
        return render_template('payment_confirmation.html', items_in_cart=items_in_cart, total_price=total_price)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
        flash('An error occurred during payment confirmation. Please try again later.', 'error')
        return redirect(url_for('project.view_cart'))  






@project.route('/checkout', methods=['GET', 'POST'])
def checkout():
    try:
        if request.method == 'POST':
            return redirect(url_for('project.payment_confirmation'))
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
        is_approved = current_user.is_admin
        new_article = Article(title=title, content=content, is_approved=is_approved)
        db.session.add(new_article)
        db.session.commit()
        flash('Blog added successfully. Awaiting admin approval.', 'success')
    return render_template('upload_article.html')






@project.route('/remove_article/<int:article_id>', methods=['POST'])
def remove_article(article_id):
    try:
        article = Article.query.get_or_404(article_id)
        db.session.delete(article)
        db.session.commit()
        flash('Blog removed successfully!', 'success')
        return redirect(url_for('project.articles'))
    except Exception as e:
        flash('An error occurred while removing the article. Please try again later.', 'error')
        return redirect(url_for('project.articles'))





@project.route('/events')

def events():
    events = Event.query.filter_by(is_approved=True).all()
    return render_template('events.html', events=events)


@project.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    form = CreateEventForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        date = form.date.data
        image = form.image.data
        location = form.location.data
        is_approved = current_user.is_admin
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            is_approved = current_user.is_admin
            new_event = Event( title=title, description=description, date=date,image_path=filename, location=location,is_approved=is_approved)
            history_event = HistoryEvent(title=title,description=description,date=date,image_path=filename,location=location)
            db.session.add(new_event)
            db.session.add(history_event)
            db.session.commit()

            flash('Event created successfully. Awaiting admin approval.', 'success')
            return redirect(url_for('project.index'))

    return render_template('create_event.html', form=form)





@project.route('/events/<int:event_id>')
def view_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        abort(404)  
    return render_template('event_details.html', event=event)




@project.route('/historyevents')
def historyevents():
    events = HistoryEvent.query.all()
    return render_template('historyevents.html', history_event=events)


@project.route('/historyevents/<int:history_event_id>')
def view_historyevent(history_event_id):
    event = HistoryEvent.query.get(history_event_id)
    reviews = EventReview.query.filter_by(history_event_id=history_event_id).all()

    return render_template('view_historyevent.html', event=event, reviews=reviews)















@project.route('/modify_event/<int:event_id>', methods=['GET', 'POST'])
def modify_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('project.events'))
    form = ModifyEventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        db.session.commit()
        flash('Event modified successfully!', 'success')
        return redirect(url_for('project.events'))
    return render_template('modify_event.html', event=event, form=form)





@project.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get(event_id)
    if event:
        delete_stmt = delete(volunteer_event_association).where(volunteer_event_association.c.event_id == event_id)
        db.session.execute(delete_stmt)

        db.session.delete(event)

        try:
            db.session.commit()
            flash(f'Event "{event.title}" deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting the event.', 'error')

        return redirect(url_for('project.events'))
    else:
        flash('Event not found', 'error')
        return redirect(url_for('project.events'))




############$$$$$$$$$$$$$$$$$$VOLUNTEER PART$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

@project.route('/join_event/<int:event_id>', methods=['POST'])
@login_required
def join_event(event_id):
    print("Attempting to join event", event_id)  # Debug print

    try:
        event = Event.query.get_or_404(event_id)

        # Check if the current user is not already associated with the event
        if current_user not in event.volunteers:
            # Add the current user to the event's list of volunteers
            event.volunteers.append(current_user)
            
            # Create a new participant record and add it to the session
            participant = Participant(user_id=current_user.id, event_id=event_id)
            db.session.add(participant)

            # Commit the session to save changes to the database
            db.session.commit()
            print("Joined event successfully")  # Debug print

            flash('You have successfully joined the event!', 'success')
        else:
            flash('You are already joined to this event.', 'warning')

    except Exception as e:
        db.session.rollback()  # Roll back the session in case of error
        print("Error joining event:", e)  # Debug print
        flash('An error occurred while joining the event.', 'danger')

    return redirect(url_for('project.joined_events'))





@project.route('/joined_events')
@login_required
def joined_events():
    # Get the joined events for the current user
    joined_events = current_user.joined_events
    return render_template('joined_events.html', title='Joined Events', joined_events=joined_events)




@project.route('/cancel_event/<int:event_id>', methods=['POST'])
@login_required
def cancel_event(event_id):
    # Get the event
    event = Event.query.get_or_404(event_id)

    # Check if the user has joined the event
    if current_user in event.volunteers:
        # Remove the user from the event's volunteers
        event.volunteers.remove(current_user)
        db.session.commit()
        flash('You have successfully canceled your attendance to the event.', 'success')
    else:
        flash('You are not currently joined to this event.', 'danger')

    return redirect(url_for('project.joined_events'))

# In controller/project.py


@project.route('/volunteer_dashboard')
@login_required
def volunteer_dashboard():
    # Fetch all events
    all_events = Event.query.all()
    return render_template('volunteer_dashboard.html', all_events=all_events)


# In controller/project.py


@project.route('/volunteer_join_event/<int:event_id>', methods=['POST'])
@login_required
def volunteer_join_event(event_id):
    event = Event.query.get_or_404(event_id)


    # Check if the user has already joined the event
    if event not in current_user.joined_events:
        current_user.joined_events.append(event)
        db.session.commit()
        flash('Successfully joined the event!', 'success')
    else:
        flash('You have already joined this event.', 'warning')


    return redirect(url_for('project.volunteer_dashboard'))






#####################################################################################################


#@project.route('/search', methods=['GET'])
#def search():
#    query = request.args.get('query')  # Get the search query from the URL parameter
#    if query:
        # Assuming 'Item' is your model for products
        #results = Item.query.filter(Item.title.contains(query)).all()
        #return render_template('search_results.html', results=results)
    #else:
        #return render_template('search_results.html', results=[])


@project.route('/vlogs')
def vlogs():
    vlogs = Vlog.query.all()
    return render_template('vlogs.html', vlogs=vlogs)






@project.route('/upload_vlog', methods=['GET', 'POST'])
def upload_vlog():
    form = UploadVlogForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        youtube_link = form.youtube_link.data
        is_approved = current_user.is_admin
        new_vlog = Vlog(title=title, description=description, youtube_link=youtube_link, is_approved=is_approved)
        db.session.add(new_vlog)
        db.session.commit()
        flash('Vlog added successfully. Awaiting admin approval.', 'success')
        return redirect(url_for('project.vlogs'))
    return render_template('upload_vlog.html', form=form)








@project.route('/remove_vlog/<int:vlog_id>', methods=['POST'])
def remove_vlog(vlog_id):
    vlog = Vlog.query.get_or_404(vlog_id)
    db.session.delete(vlog)
    db.session.commit()
    flash('Vlog removed successfully!', 'success')
    return redirect(url_for('project.vlogs'))








@project.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    if not query:
        flash('Please enter a search query.', 'warning')
        return redirect(url_for('project.item_listing'))
    items = Item.query.filter(Item.title.ilike(f"%{query}%")).all()
    return render_template('search_results.html', query=query, items=items)
from flask_bcrypt import Bcrypt












@project.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)    
            flash('Login successful!', 'success')
            return redirect(url_for('project.index'))
        else:
            flash('Login unsuccessful. Check username and password.', 'danger')
    return render_template('login.html')






@project.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        user_type = request.form.get('user_type')  
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('project.signup'))
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username is already taken. Please choose a different one.', 'danger')
            return redirect(url_for('project.signup'))
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email is already registered. Please use a different email.', 'danger')
            return redirect(url_for('project.signup'))
        hashed_password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')


        new_user = User(username=username, email=email, password=hashed_password, user_type=user_type,is_admin=False)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Account created successfully!', 'success')
        return redirect(url_for('project.login'))
    return render_template('signup.html', form=form)






@project.route('/dashboard')
@login_required
def dashboard():
    items = current_user.items
    return render_template('dashboard.html', items=items)




@project.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('project.login'))






@project.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)  
    pending_items = Item.query.filter_by(is_approved=False).all()
    pending_events = Event.query.filter_by(is_approved=False).all()
    pending_blogs = Article.query.filter_by(is_approved=False).all()
    pending_vlogs = Vlog.query.filter_by(is_approved=False).all()
    return render_template('admin_dashboard.html', items=pending_items, events=pending_events,blogs=pending_blogs, vlogs=pending_vlogs)




@project.route('/approve_item/<int:item_id>', methods=['POST'])
@login_required
def approve_item(item_id):
    if not current_user.is_admin:
        abort(403)  
    item = Item.query.get_or_404(item_id)
    item.is_approved = True
    db.session.commit()
    flash('Item approved successfully.', 'success')
    return redirect(url_for('project.index'))






@project.route('/reject_item/<int:item_id>', methods=['POST'])
@login_required
def reject_item(item_id):
    if not current_user.is_admin:
        abort(403)  
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item rejected successfully.', 'success')
    return redirect(url_for('project.index'))






@project.route('/approve_event/<int:event_id>', methods=['POST'])
@login_required
def approve_event(event_id):
    if not current_user.is_admin:
        abort(403)  
    event = Event.query.get_or_404(event_id)
    event.is_approved = True
    history_event = HistoryEvent(
            title=event.title,
            description=event.description,
            date=event.date,
            image_path=event.image_path,
            location=event.location
        )
    db.session.add(event)
    db.session.add(history_event)

    db.session.commit()
    flash('Event approved successfully.', 'success')
    return redirect(url_for('project.admin_dashboard'))






@project.route('/reject_event/<int:event_id>', methods=['POST'])
@login_required
def reject_event(event_id):
    if not current_user.is_admin:
        abort(403)  
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event rejected successfully.', 'success')
    return redirect(url_for('project.index'))






@project.route('/approve_blog/<int:blog_id>', methods=['POST'])
@login_required
def approve_blog(blog_id):
    if not current_user.is_admin:
        abort(403)  
    blog = Article.query.get_or_404(blog_id)
    blog.is_approved = True
    db.session.commit()
    flash('Blog approved successfully.', 'success')
    return redirect(url_for('project.admin_dashboard'))






@project.route('/reject_blog/<int:blog_id>', methods=['POST'])
@login_required
def reject_blog(blog_id):
    if not current_user.is_admin:
        abort(403)  
    blog = Article.query.get_or_404(blog_id)
    db.session.delete(blog)
    db.session.commit()
    flash('Blog rejected successfully.', 'success')
    return redirect(url_for('project.admin_dashboard'))






@project.route('/approve_vlog/<int:vlog_id>', methods=['POST'])
@login_required
def approve_vlog(vlog_id):
    if not current_user.is_admin:
        abort(403)  
    vlog = Vlog.query.get_or_404(vlog_id)
    vlog.is_approved = True
    db.session.commit()
    flash('Vlog approved successfully.', 'success')
    return redirect(url_for('project.admin_dashboard'))




@project.route('/reject_vlog/<int:vlog_id>', methods=['POST'])
@login_required
def reject_vlog(vlog_id):
    if not current_user.is_admin:
        abort(403)  
    vlog = Vlog.query.get_or_404(vlog_id)
    db.session.delete(vlog)
    db.session.commit()
    flash('Vlog rejected successfully.', 'success')
    return redirect(url_for('project.admin_dashboard'))


@project.route('/review/<int:history_event_id>', methods=['GET', 'POST'])
@login_required
def review(history_event_id):
    event = HistoryEvent.query.get(history_event_id)
    form = ReviewForm()

    if form.validate_on_submit():
        rating = form.rating.data
        review_text = form.review_text.data

        # Create a new EventReview instance
        review = EventReview(
            rating=rating,
            review_text=review_text,
            user_id=current_user.id,
            history_event_id=history_event_id,
            usertype=current_user.user_type,
            name=current_user.username 
        )

        db.session.add(review)
        db.session.commit()

        flash('Review submitted successfully!', 'success')

    return render_template('review.html', event=event, form=form)


def get_event_reviews(event_id):
    reviews = EventReview.query.filter_by(history_event_id=event_id).all()
    return reviews



@project.route('/view_reviews/<int:event_id>')
def view_reviews(event_id):
    # Assuming you have a function to query reviews for a specific event
    reviews = get_event_reviews(event_id)

    return render_template('view_reviews.html', event_id=event_id, reviews=reviews)

