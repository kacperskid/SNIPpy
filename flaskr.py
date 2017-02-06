import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash



app = Flask(__name__)
app.config.from_object(__name__)


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
    
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def get_permission():
    db = get_db ()
    user_id = session.get('user_id')
    permission = db.execute('select id_perm from user where id==?',[str(user_id)])
    permission = permission.fetchall()
    return permission    
    
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        

@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        db = get_db()
        user_login = db.execute('select id from user where Login==? and Password==?', [request.form['username'], request.form['password']])
        user_credentials=user_login.fetchall()
        
        if  len(user_credentials) == 1:
            
            session['logged_in'] = True
            session['user_id'] = user_credentials[0][0]
            flash('Login succesful')
            db.close()
            return redirect(url_for('home'))

        else:
            error = 'Invalid username or password'
            
    db.close()        
    return render_template('login.html', error=error)
    
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))
    
@app.route('/register')
def register():
    if session.get('logged_in'):
        db = get_db()
        cur = db.execute('select * from permissions')
        permissions = cur.fetchall()
        db.close()
        return render_template('register.html',permissions=permissions)
    else:
        abort(401)    
    
@app.route('/add_user',methods=['POST']) 
def add_user():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    
    cursor = db.execute('select * from permissions where Permission==?',[request.form['perm']])
    column = cursor.fetchall()
    permission_id = column[0][0]
    
    db.execute('insert into user (Login, Password, id_perm) values (?, ?, ?)',
                 [request.form['login'], request.form['password'], permission_id])
    db.commit()

    flash('New user registered!')
    db.close()
    return redirect(url_for('register'))

@app.route('/snp_form')    
def snp_form():
    if session.get('logged_in'):
        return render_template("add_snip.html")
    else:
        abort(401)
    
@app.route('/add_snp',methods=['POST'])    
def add_snp():
    if not session.get('logged_in'):
        abort(401)  
    db = get_db ()
    db.execute('insert into SNP (name, seq5, seq3, alleles, chrom, pos, Gene_name) values (?, ?, ?, ?, ?, ?, ?)',
                [request.form['snp_name'], request.form['sequence5'],request.form['sequence3'],request.form['alleles'],request.form['chromosome'], request.form['position'],request.form['gene_name']])
    db.commit()
    flash('New SNP was added!')
    db.close()
    return redirect(url_for('snp_form'))
       
    
@app.route('/show_snp')
def show_snp():
    db = get_db()
    cur = db.execute('select * from SNP order by id_snp desc')
    entries = cur.fetchall()
    db.close()
    return render_template('show_snp.html', entries=entries)    

@app.route('/disease')
def disease_form():
    if session.get('logged_in'):
        return render_template("disease.html")
    else:
        abort (401)
        
@app.route('/add_disease', methods=['POST'])
def add_disease():
    if session.get('logged_in'):
        db = get_db ()
        db.execute('insert into disease (disease_name,description,effect) values (?, ?, ?)', [request.form ['disease_name'],
            request.form['description'], request.form['effect']])
        db.commit()
        flash('New disease was added!')
        db.close()
        return redirect(url_for('disease_form'))
    else:
        abort (401)
        
@app.route('/show_disease')
def show_disease():
    db = get_db()
    cur = db.execute('select * from disease')
    entries = cur.fetchall()
    db.close()
    return render_template('show_disease.html', entries=entries)    

@app.route('/join_disease')
def join_disease():
    db = get_db()
    cur = db.execute('select * from disease')
    disease_list = cur.fetchall()
    
    cur = db.execute('select * from SNP')
    snp_list = cur.fetchall()
    db.close()
    return render_template('join_disease.html', disease_list=disease_list, snp_list=snp_list)     
    
@app.route ('/join_disease_snp', methods=['POST'])
def join_disease_snp():
     print request.form
     db =get_db()
     db.execute ('insert into disease_snp (disease_snp_id_disease,disease_snp_snp_id) values (?,?)',[request.form['disease'],request.form['snp']])
     db.commit()
     flash('SNP connected with disease!')
     db.close()
     return redirect(url_for('join_disease'))
     
@app.route('/show_connections')
def show_connections():
    db = get_db()
    cur = db.execute('select distinct name, disease_name, effect from disease_snp join snp on disease_snp_snp_id==id_snp join disease on disease_snp_id_disease==id_disease')
    entries = cur.fetchall()
    db.close()
    return render_template('show_connections.html', entries=entries)   
     
    
@app.route('/home')
def home():
    return render_template('layout.html')
    
app.run()
    
