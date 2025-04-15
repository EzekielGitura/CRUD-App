from flask import current_app
import click
import os

from app import create_app

app = create_app()

@app.cli.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.password_option()
def create_admin(username, email, password):
    """Create an admin user."""
    from app.crud import create_user
    
    user = create_user(
        username=username,
        email=email,
        password=password,
        is_admin=True
    )
    
    click.echo(f'Admin user {username} created successfully!')

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database."""
    from app.db.database import init_db
    
    init_db()
    click.echo('Database initialized successfully!')

def main():
    """Run the application."""
    # Check if running with Flask CLI
    if os.environ.get('FLASK_APP'):
        return
    
    # Otherwise, run the development server
    app.run(debug=True)

if __name__ == '__main__':
    main()