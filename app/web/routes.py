from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse

from app import crud
from app.web.forms import (
    LoginForm, RegistrationForm, ItemForm, 
    CategoryForm, TagForm, UserProfileForm
)

# Create web blueprint
web_bp = Blueprint('web', __name__)

# Home page
@web_bp.route('/')
def index():
    """Render the home page."""
    # Get recent items for display
    recent_items = crud.get_items(limit=5)
    categories = crud.get_categories()
    
    return render_template(
        'index.html', 
        recent_items=recent_items,
        categories=categories
    )

# Authentication routes
@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Check credentials
        user = crud.get_user_by_username(form.username.data)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('web.login'))
        
        # Log user in
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to the page the user was trying to access
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('web.index')
        
        flash('You have been logged in successfully!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user
        user = crud.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('web.login'))
    
    return render_template('auth/register.html', form=form)

@web_bp.route('/logout')
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('web.index'))

# Item routes
@web_bp.route('/items')
def item_list():
    """Display a list of items with optional filtering."""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', type=int)
    tag_ids = request.args.getlist('tag_id', type=int)
    
    # Get items
    offset = (page - 1) * per_page
    if search or category_id or tag_ids:
        items = crud.search_items(search, category_id, tag_ids)
    else:
        items = crud.get_items(limit=per_page, offset=offset)
    
    # Get total count for pagination
    total_items = crud.count_items(category_id)
    total_pages = (total_items + per_page - 1) // per_page
    
    # Get categories and tags for filtering
    categories = crud.get_categories()
    tags = crud.get_tags()
    
    return render_template(
        'items/list.html',
        items=items,
        search=search,
        category_id=category_id,
        tag_ids=tag_ids,
        categories=categories,
        tags=tags,
        page=page,
        total_pages=total_pages
    )

@web_bp.route('/items/<int:item_id>')
def item_view(item_id):
    """Display details of a specific item."""
    item = crud.get_item_by_id(item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('web.item_list'))
    
    return render_template('items/view.html', item=item)

@web_bp.route('/items/create', methods=['GET', 'POST'])
@login_required
def item_create():
    """Create a new item."""
    form = ItemForm()
    
    # Set form choices
    categories = crud.get_categories()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    form.category_id.choices.insert(0, (0, 'No Category'))
    
    tags = crud.get_tags()
    form.tag_ids.choices = [(t.id, t.name) for t in tags]
    
    if form.validate_on_submit():
        # Process category_id (handle the "No Category" option)
        category_id = form.category_id.data if form.category_id.data > 0 else None
        
        # Create item
        item = crud.create_item(
            name=form.name.data,
            description=form.description.data,
            owner_id=current_user.id,
            category_id=category_id,
            tag_ids=form.tag_ids.data
        )
        
        flash('Item created successfully!', 'success')
        return redirect(url_for('web.item_view', item_id=item.id))
    
    return render_template('items/create.html', form=form)

@web_bp.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def item_edit(item_id):
    """Edit an existing item."""
    # Get item
    item = crud.get_item_by_id(item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('web.item_list'))
    
    # Check if user is the owner or an admin
    if item.owner_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this item.', 'danger')
        return redirect(url_for('web.item_view', item_id=item.id))
    
    # Create form
    form = ItemForm(obj=item)
    
    # Set form choices
    categories = crud.get_categories()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    form.category_id.choices.insert(0, (0, 'No Category'))
    
    tags = crud.get_tags()
    form.tag_ids.choices = [(t.id, t.name) for t in tags]
    
    # Set initial values
    if request.method == 'GET':
        form.category_id.data = item.category_id or 0
        form.tag_ids.data = [tag.id for tag in item.tags]
    
    if form.validate_on_submit():
        # Process category_id (handle the "No Category" option)
        category_id = form.category_id.data if form.category_id.data > 0 else None
        
        # Update item
        updated_item = crud.update_item(
            item_id=item.id,
            name=form.name.data,
            description=form.description.data,
            category_id=category_id,
            tag_ids=form.tag_ids.data
        )
        
        flash('Item updated successfully!', 'success')
        return redirect(url_for('web.item_view', item_id=item.id))
    
    return render_template('items/edit.html', form=form, item=item)

@web_bp.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
def item_delete(item_id):
    """Delete an item."""
    # Get item
    item = crud.get_item_by_id(item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('web.item_list'))
    
    # Check if user is the owner or an admin
    if item.owner_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this item.', 'danger')
        return redirect(url_for('web.item_view', item_id=item.id))
    
    # Delete item
    crud.delete_item(item.id)
    
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('web.item_list'))

# Category routes (admin only)
@web_bp.route('/categories')
def category_list():
    """Display a list of categories."""
    categories = crud.get_categories()
    return render_template('categories/list.html', categories=categories)

@web_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def category_create():
    """Create a new category (admin only)."""
    # Check if user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to create categories.', 'danger')
        return redirect(url_for('web.category_list'))
    
    form = CategoryForm()
    if form.validate_on_submit():
        # Create category
        category = crud.create_category(
            name=form.name.data,
            description=form.description.data
        )
        
        flash('Category created successfully!', 'success')
        return redirect(url_for('web.category_list'))
    
    return render_template('categories/create.html', form=form)

# User profile
@web_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    """Edit user profile."""
    form = UserProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check current password if changing email or password
        if form.new_password.data or form.email.data != current_user.email:
            if not current_user.check_password(form.current_password.data):
                flash('Current password is incorrect.', 'danger')
                return render_template('auth/profile.html', form=form)
        
        # Update user
        user = crud.update_user(
            user_id=current_user.id,
            username=form.username.data,
            email=form.email.data,
            password=form.new_password.data if form.new_password.data else None
        )
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('web.user_profile'))
    
    return render_template('auth/profile.html', form=form)