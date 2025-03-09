from flask import Flask, render_template, request, redirect, session, url_for, flash
from auth import generate_state, get_tokens, generate_code_verifier, generate_code_challenge, generate_auth_url
from db import connect_to_db, add_user
from config import CLIENT_ID, REDIRECT_URI
import os
from flask_login import current_user, login_user, logout_user, login_required
from flask_login import LoginManager, UserMixin

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
# Obtener el modo de ejecución
FLASK_ENV = os.getenv('FLASK_ENV', 'development')  # Por defecto, modo desarrollo
USERNAME = os.getenv('log_USERNAME')  
PASSWORD = os.getenv('PASSWORD')


# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Ruta para el inicio de sesión


if FLASK_ENV == 'production':
    # Modo producción: usar IP pública y HTTPS
    HOST = os.getenv('PRODUCTION_HOST')
    PORT = int(os.getenv('PRODUCTION_PORT'))
    SSL_CONTEXT = (
        os.getenv('SSL_CERT'),  # Ruta al certificado
        os.getenv('SSL_KEY')     # Ruta a la clave privada
    )
    DEBUG = False
else:
    # Modo desarrollo: usar localhost y HTTP
    HOST = os.getenv('HOST')
    PORT = int(os.getenv('PORT'))
    SSL_CONTEXT = None
    DEBUG = os.getenv('DEBUG').lower() == 'true'
# Modelo de usuario
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Cargar el usuario
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Si ya está autenticado, redirige al inicio

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username)
        print(USERNAME)
        print(password)
        print(PASSWORD)
        if username == USERNAME and password == PASSWORD:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

# Ruta de cierre de sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Proteger todas las rutas con @login_required
@app.before_request
def require_login():
    if not current_user.is_authenticated and request.endpoint != 'login':
        return redirect(url_for('login'))
# Route: Homepage (Dashboard)
@app.route('/')
@login_required
def index():
    """
    Render the dashboard homepage.
    This will display the Fitbit data stored in the database.
    """
    # TODO: Fetch data from the database and pass it to the template
    return render_template('dashboard.html')

# Route: Link a new Fitbit device
@app.route('/link', methods=['GET', 'POST'])
@login_required
def link_device():
    """
    Handle the linking of a new Fitbit device.
    Generates an authorization URL and redirects the user to Fitbit's OAuth page.
    """
    if request.method == 'POST':
        # Get the selected email from the dropdown
        email = request.form['email']
        
        # Check if the email is already in use
        conn = connect_to_db()
        if conn:
            try:
                with conn.cursor() as cur:
                    # Query to get the current user associated with the email, ordered by the most recent linked_at timestamp
                    cur.execute("""
                        SELECT name, linked_at 
                        FROM users 
                        WHERE email = %s 
                        ORDER BY linked_at DESC 
                        LIMIT 1
                    """, (email,))
                    existing_user = cur.fetchone()
                    
                    if existing_user and existing_user[0]:
                        # If the email is already in use, show a confirmation page with the most recent user
                        current_user_name = existing_user[0]
                        last_linked_at = existing_user[1]
                        return render_template('reassign_confirmation.html', 
                                              email=email, 
                                              current_user_name=current_user_name,
                                              last_linked_at=last_linked_at)
                    else:
                        # If the email is not in use assign user name and proceed to authorization
                        session['pending_email'] = email
                        return redirect(url_for('assign_user'))
            except Exception as e:
                print(f"Error checking email in database: {e}")
                return "Error: No se pudo verificar el correo.", 500
            finally:
                conn.close()
        else:
            return "Error: No se pudo conectar a la base de datos.", 500
    
    else:
        # If it's a GET request, fetch the list of emails from the database
        conn = connect_to_db()
        if conn:
            try:
                with conn.cursor() as cur:
                    # Query to get the oldest email entries from the users table
                    cur.execute("""
                        SELECT email 
                        FROM users 
                        WHERE (email, linked_at) IN (
                            SELECT email, MIN(linked_at)
                            FROM users
                            GROUP BY email
                        )
                    """)
                    emails = [row[0] for row in cur.fetchall()]  # Extract emails from the query result
            except Exception as e:
                print(f"Error fetching emails from database: {e}")
                emails = []  # Fallback to an empty list in case of error
            finally:
                conn.close()
        
        # Render the link_device.html template with the list of emails
    return render_template('link_device.html', emails=emails)
@app.route('/assign', methods=['GET', 'POST'])
@login_required
def assign_user():
    """
    Handle the assignment of a new user.
    """
    if request.method == 'POST':
        user_name = request.form['user_name']
        
        # Check if the user name already exists in the database (case-insensitive)
        conn = connect_to_db()
        if conn:
            try:
                with conn.cursor() as cur:
                    # Query to check if the user name already exists (case-insensitive)
                    cur.execute("SELECT name FROM users WHERE LOWER(name) = LOWER(%s)", (user_name,))
                    existing_user = cur.fetchone()
                    
                    if existing_user:
                        # If the user name already exists, show an error message
                        error = f"El nombre de usuario '{user_name}' ya está en uso."
                        return render_template('assign_user.html', error=error)
                    else:
                        # If the user name is not in use, proceed to authorization
                        #Store the new name in the session for later use
                        session['new_user_name'] = user_name
                        code_verifier = generate_code_verifier()
                        code_challenge = generate_code_challenge(code_verifier)
                        state = generate_state()
                        print(f"Generated valid state: {state}")
                        print(f"Generated code verifier: {code_verifier}")
                        print(f"Generated code challenge: {code_challenge}")
                        auth_url = generate_auth_url(code_challenge, state)
                        print(f"Generated auth URL: {auth_url}")
                        session['pending_user_name'] = user_name
                        session['code_verifier'] = code_verifier
                        session['state'] = state
                        return render_template('link_auth.html', auth_url=auth_url)
            except Exception as e:
                print(f"Error checking user name in database: {e}")
                return "Error: No se pudo verificar el nombre de usuario.", 500
            finally:
                conn.close()
        else:
            return "Error: No se pudo conectar a la base de datos.", 500
    
    else:
        # If it's a GET request, render the assign_user.html template
        return render_template('assign_user.html')
# Route: Fitbit OAuth callback
@app.route('/callback')
@login_required
def callback():
    """
    Handle the callback from Fitbit after the user authorizes the app.
    This route captures the authorization code and exchanges it for access and refresh tokens.
    """
    # Get the authorization code from the query parameters
    code = request.args.get('code')
    returned_state = request.args.get('state')
     # Get the stored state from the session
    stored_state = session.get('state')
    #Verify that the returned state matches the stored state
    if returned_state != stored_state:
        return "Error: Invalid state parameter. Possible CSRF attack.", 400
    
    # Get the pending email and new user name from the session
    email = session.get('pending_email')
    new_user_name = session.get('new_user_name')
    code_verifier = session.get('code_verifier')
    
    if email:
        conn = connect_to_db()
        if conn:
            try:
                with conn.cursor() as cur:
                    # Query to check if the email is already in use
                    cur.execute("SELECT id, access_token, refresh_token FROM users WHERE email = %s", (email,))
                    existing_user = cur.fetchone()
                    
                    if existing_user:
                        user_id, existing_access_token, existing_refresh_token = existing_user
                        
                        # Flow 2: Reassign the device to a new user
                        if new_user_name:
                            if not existing_access_token or not existing_refresh_token:
                                # If tokens are missing, require reauthorization
                                if code:
                                    # Exchange the authorization code for new tokens
                                    access_token, refresh_token = get_tokens(code, code_verifier)
                                    # Add a new user with the same email and new name
                                    add_user(new_user_name, email, access_token, refresh_token)
                                    print(f"Dispositivo reasignado a {new_user_name} ({email}) con nuevos tokens:: {access_token} y refresh ::{refresh_token}")
                                else:
                                    return "Error: Se requiere autorización para reasignar el dispositivo.", 400
                            else:
                                # If tokens are valid, simply add a new user with the same email and new name
                                add_user(new_user_name, email, existing_access_token, existing_refresh_token)
                                print(f"Dispositivo reasignado a {new_user_name} ({email}) sin necesidad de reautorización.")
                        else:
                            return "Error: Se requiere un nombre de usuario para reasignar el dispositivo.", 400
                    else:
                        # Flow 1: Link a new email to a user
                        if new_user_name:
                            if code:
                                # Exchange the authorization code for new tokens
                                access_token, refresh_token = get_tokens(code)
                                # Add a new user with the new email and name
                                add_user(new_user_name, email, access_token, refresh_token)
                                print(f"Nuevo usuario {new_user_name} ({email}) añadido.")
                            else:
                                return "Error: Se requiere autorización para vincular un nuevo correo.", 400
                        else:
                            return "Error: Se requiere un nombre de usuario para vincular un nuevo correo.", 400
                    
                    # Clear the session data
                    session.pop('pending_email', None)
                    session.pop('new_user_name', None)
                    session.pop('code_verifier', None)
                    session.pop('state', None)
                    
                    # Redirect to the confimation page
                    return render_template('confirmation.html', user_name=new_user_name, email=email)
            except Exception as e:
                # Handle errors during token exchange
                return f"Error: {e}", 400
            finally:
                conn.close()
        else:
            return "Error: No se pudo conectar a la base de datos.", 500
    else:
        # Handle missing email
        return "Error: No se proporcionó un correo electrónico.", 400
    
@app.route('/reassign', methods=['POST'])
@login_required
def reassign_device():
    """
    Handle the reassignment of a Fitbit device to a new user.
    """
    email = request.form['email']
    new_user_name = request.form['new_user_name']
    
    # Store the email and new user name in the session for later use
    session['pending_email'] = email
    session['new_user_name'] = new_user_name
    
    # Check if reauthorization is needed
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cur:
                # Query to check if the email is already in use and has valid tokens
                cur.execute("SELECT access_token, refresh_token FROM users WHERE email = %s", (email,))
                existing_user = cur.fetchone()
                
                if existing_user:
                    existing_access_token, existing_refresh_token = existing_user
                    if not existing_access_token or not existing_refresh_token:
                        # If tokens are missing, require reauthorization
                        code_verifier = generate_code_verifier()
                        code_challenge = generate_code_challenge(code_verifier)
                        state = generate_state()
                        print(f"Generated valid state: {state}")
                        print(f"Generated code verifier: {code_verifier}")
                        print(f"Generated code challenge: {code_challenge}")
                        auth_url = generate_auth_url(code_challenge, state)
                        print(f"Generated auth URL: {auth_url}")
                        session['code_verifier'] = code_verifier
                        session['state'] = state
                        return render_template('link_auth.html', auth_url=auth_url)
                    else:
                        # If tokens are valid, proceed to add the new user without reauthorization
                        add_user(new_user_name, email, existing_access_token, existing_refresh_token)
                        print(f"Dispositivo reasignado a {new_user_name} ({email}) sin necesidad de reautorización.")
                        return redirect('/')
                else:
                    return "Error: El correo no está en uso.", 400
        except Exception as e:
            return f"Error: {e}", 400
        finally:
            conn.close()
    else:
        return "Error: No se pudo conectar a la base de datos.", 500# Run the Flask app
if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG, ssl_context=SSL_CONTEXT)