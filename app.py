import sqlite3
from flask import Flask, render_template, request, redirect, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def get_database():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_database()
    cursor = conn.cursor()

    cursor.execute("""
    create table if not exists users(
        id integer primary key autoincrement,
        fname text not null,
        lname text not null,
        email unique not null,
        password text not null,
        role text default 'user',
        created_date timestamp default current_timestamp,
        created_at timestamp default current_timestamp
                         
    
    );""")

    cursor.execute("""
    create table if not exists product_type(
        id integer primary key autoincrement,
        name text unique not null);""")

    cursor.execute("""
    create table if not exists product(
        id integer primary key autoincrement,
        type_id integer  not null,
        name text not null,
        detail text not null,
        price real not null,
        image text not null,
        foreign key (type_id) references product_type(id)
    );""")

    cursor.execute("""
    create table if not exists message(
         id integer primary key autoincrement,
         sender_email not null,
         receiver_email not null,
         content text not null,
         is_read integer not null default 0,
         sent_date timestamp not null,
         sent_at timestamp not null
         
    );""")

    cursor.execute("""
    create table if not exists cart_item(
        id integer primary key autoincrement,
        user_id integer,
        item_name text not null,
        item_price real not null,
        added_date timestamp default current_timestamp,
        added_at timestamp default current_timestamp,
        foreign key(user_id) references users(id)

        );""")

    created_at = datetime.now().strftime("%H:%M")
    created_date = datetime.now().strftime("%d-%m-%Y")

    cursor.execute("insert or ignore into users(fname,lname,email,password,role,created_date, created_at) values('Admin', 'User', 'admin@test', ?, 'Admin', ?, ?)", (generate_password_hash('admin123'), created_date, created_at))

    cursor.execute("insert or ignore into users(fname,lname,email,password,role,created_date,created_at) values('Admin', 'User', 'send@support', ?, 'Admin', ?,?)", (generate_password_hash('admin123'), created_date, created_at))
    conn.commit()





app = Flask(__name__)
app.secret_key = "super-secret-key"
init_db()



@app.route("/home/")
@app.route("/home")
@app.route("/")
def home():


    conn=get_database()
    cursor=conn.cursor()

    products = cursor.execute("select * from product").fetchall()
    current_email = session.get('user_email')
    current_id = session.get('user_id')
   
    user_in_cart = cursor.execute("select 1 from cart_item where user_id=?", (current_id,)).fetchone()

    

    if "user_id" in session:

        unreadCount  = cursor.execute("select count(*) from message where receiver_email=? and is_read = 0", (current_email,)).fetchone()[0]
        
        user = cursor.execute("select * from users where email=?", (current_email,)).fetchone()

        

        welcome_message=f"Welcome! We are very glad that you are here. If you ever need a support, feel free to reach out at this email (send@support). Thank you. Best regard your support team"

        welcomed_user=cursor.execute("select * from message where sender_email='send@support' and receiver_email=? and content=?",(current_email, welcome_message)).fetchone()
        conn.commit()

        if welcomed_user is None:
            sent_at = datetime.now().strftime(" %H:%M")
            sent_date = datetime.now().strftime("%d-%m-%Y")
            cursor.execute("insert into message(sender_email, receiver_email, content,sent_date, sent_at) values('send@support', ?,?,?,?)", (current_email, welcome_message,sent_date, sent_at))
            conn.commit()
        
        if user_in_cart:

            items=cursor.execute("select * from cart_item where user_id=?", (current_id,)).fetchall()
            itemCount=cursor.execute("select count(*) from cart_item where user_id=? ", (current_id,)).fetchone()[0]
            conn.commit()

            if itemCount > 0:
                return render_template("home.html",logged_in=True,is_user=True, products=products, user=user,itemCount=itemCount )

        if unreadCount > 0:

            return render_template("home.html", logged_in=True,is_user=True, products=products, user=user, unreadCount=unreadCount)
        
        if unreadCount > 0 and itemCount > 0:
            return render_template("home.html", logged_in=True,is_user=True, products=products, user=user, unreadCount=unreadCount, itemCount=itemCount)


        headMessage=f"Welcome {user['fname']}"
        return render_template("home.html", logged_in=True,is_user=True, products=products, user=user, headMessage=headMessage)
    
    headMessage=f"Hello there!"
    return render_template("home.html", products=products, headMessage=headMessage )



@app.route("/search/product/", methods=["GET", "POST"])
@app.route("/search/product", methods=["GET", "POST"])

def search_product():

    if request.method == "POST":
        user_input = request.form["product_name"]
        product_name = f"%{user_input}%"
        email_address = session.get('user_email')

        conn = get_database()
        cursor = conn.cursor()

        user = cursor.execute("select * from users where email=?", (email_address,)).fetchone()
        unreadCount  = cursor.execute("select count(*) from message where receiver_email=? and is_read = 0", (email_address,)).fetchone()[0]

        search = cursor.execute("select * from product where name like? or  detail like? ", (product_name, product_name)).fetchall()
        conn.commit()

        if "user_id" in session:

            if search:
                return render_template("home.html",logged_in=True, user=user, is_user=True, unreadCount=unreadCount, search=search)

            noResult=f"No Result for {user_input}"
            return render_template("home.html",logged_in=True, user=user, is_user=True, unreadCount=unreadCount, search=search, noResult=noResult)

        if search and not "user_id" in session:

            return render_template("home.html", search=search)

        noResult=f"No Result for {user_input}"
        return render_template("home.html", noResult=noResult, search=search)
    return render_template("home.html")


@app.route("/view/product/", methods=["GET", "POST"])
@app.route("/view/product", methods=["GET", "POST"])

def view_product():

    if "user_id" in session:

        conn = get_database()
        cursor = conn.cursor()
        current_email = session.get('user_email')
        user = cursor.execute("select * from users where email=?", (current_email,)).fetchone()
        conn.commit()


        if request.method == "POST":

            product_image=request.form["product_image"]
            product_name=request.form["product_name"]
            product_detail=request.form["product_detail"]
            product_price=request.form["product_price"]
            current_email = session.get('user_email')

            conn = get_database()
            cursor = conn.cursor()

            product=cursor.execute("select * from product where name =? and detail=? and price=? and image=?", (product_name,product_detail,product_price, product_image)).fetchone()
            user = cursor.execute("select * from users where email=?", (current_email,)).fetchone()
            conn.commit()

            headMessage=f"Product view"
            return render_template("home.html", logged_in=True, user=user, product=product, view_product=True, headMessage=headMessage)
        return redirect(url_for("home"))
            
       
    return redirect(url_for("login")) 

@app.route("/add/item/to/cart/", methods=["GET", "POST"])
@app.route("/add/item/to/cart", methods=["GET", "POST"])

def add_to_cart():

    if "user_id" in session:

        if request.method == "POST":

            
            itemName=request.form["product_name"]
            itemPrice=request.form["product_price"]
            added_at = datetime.now().strftime("%H:%M")
            added_date = datetime.now().strftime("%d-%m-%Y")


            current_email = session.get('user_email')
            current_id=session.get('user_id')

            conn = get_database()
            cursor = conn.cursor()

            cursor.execute("insert into cart_item(user_id, item_name, item_price, added_date,added_at) values(?,?,?,?,?)", (current_id, itemName, itemPrice, added_date, added_at))
            
            conn.commit()

            flash("Item Added", "success")
            return redirect(url_for('home'))
        return redirect(url_for("home"))

    return redirect(url_for('login'))

@app.route("/view/cart/items/")
@app.route("/view/cart/items")
def view_items():

    if "user_id" in session:
        conn = get_database()
        cursor = conn.cursor()

        current_email = session.get('user_email')
        current_id = session.get('user_id')

        
        user = cursor.execute("select * from users where email=?", (current_email,)).fetchone()
        user_in_cart = cursor.execute("select 1 from cart_item where user_id =?", (current_id,))

        if user_in_cart:


            view_items = cursor.execute("select * from cart_item where user_id =?", (current_id,)).fetchall()
            
            row=cursor.execute("select sum(item_price) as total_price from cart_item where user_id=?", (current_id,)).fetchone()
            if row:
                totalPrice =row[0]
            else:
                totalPrice = 0

            conn.commit()

            headMessage=f"My Cart"
            return render_template("home.html", logged_in=True, view_items=view_items, user=user, totalPrice=totalPrice, headMessage=headMessage)
        
        return render_template("home.html", logged_in=True, user=user)
    return redirect(url_for("login"))


@app.route("/remove/from/cart/", methods=["GET", "POST"])
@app.route("/remove/from/cart", methods=["GET", "POST"])

def remove_from_cart():

    if "user_id" in session:

        if request.method == "POST":

            
            itemName=request.form["itemName"]
            itemPrice=request.form["itemPrice"]
            itemId=request.form["itemId"]

            current_id=session.get('user_id')
            conn = get_database()
            cursor = conn.cursor()

            cursor.execute("delete from cart_item where id=? and user_id=?", (itemId, current_id))
            conn.commit()

            flash("Item removed", "success")
            return redirect(url_for('view_items'))
        return redirect(url_for("view_items"))

    return redirect(url_for('login'))
            

@app.route("/signup/", methods=["GET", "POST"])
@app.route("/signup", methods=["GET", "POST"])
def signup():

    conn = get_database()
    cursor = conn.cursor()
    products = cursor.execute("select * from product").fetchall()
    conn.commit()

    if request.method == "POST":
        fname = request.form["fname"]
        lname = request.form["lname"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        created_at = datetime.now().strftime("%H:%M")
        created_date = datetime.now().strftime("%d-%m-%Y")


        conn = get_database()
        cursor = conn.cursor()
        cursor.execute("Select 1 from users where email = ?", (email,))
        

        exist_email = cursor.fetchone()
        
        if exist_email:
            flash("Email Aready Exist", "error")
            return redirect(url_for("signup"))

        if len(password) < 5:
            flash("You password is short. Use atleast 5 characters", "warning")
            return redirect(url_for("signup"))

        if fname.casefold() in password.casefold() or lname.casefold() in password.casefold():
            flash("Password should not be similar to your name", "warning")
            return redirect(url_for("signup"))

        cursor.execute("Insert into users(fname, lname, email, password,created_date, created_at) values(?,?,?,?,?,?);", (fname, lname,email,hashed_password,created_date, created_at))
        conn.commit()
        conn.close()
        flash("Account Created Successfully", "success")
        return redirect(url_for("login"))

    return render_template("home.html", signup=True, products=products)



@app.route("/login/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])

def login():

    conn = get_database()
    cursor = conn.cursor()
    products = cursor.execute("select * from product").fetchall()
    conn.commit()

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_database()
        cursor = conn.cursor()
        products = cursor.execute("select * from product").fetchall()
        cursor.execute("select * from users where email = ?", (email,))
        user = cursor.fetchone()
        conn.commit()

        if user is None:
            flash("User not found", "error")
            return redirect(url_for("login"))

        stored_hash = user["password"]
        if not check_password_hash(stored_hash, password):
            flash("Password incorrect", "error")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["user_name"] = user["fname"]
        session["user_lname"] = user["lname"]
        session["user_email"] = user["email"]
        session["user_role"] = user["role"]

        flash("Logged in succefully", "success")
        return redirect(url_for("home"))

    

    return render_template("home.html", login=True, products=products)


@app.route("/password/new", methods=["GET", "POST"])
@app.route("/password/new/", methods=["GET", "POST"])

def newPassword():
    if request.method == "POST":

        email = request.form["email"]
        newPassword = request.form["password"]
        new_hashed_password = generate_password_hash(newPassword)

        conn = get_database()
        cursor = conn.cursor()

        cursor.execute("select * from users where email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            flash("Invalid email", "error")
            return redirect(url_for("newPassword"))

        if len(newPassword) < 5:
            flash("Entered password is short. Use atleast 5 characters", "error")
            return redirect(url_for("newPassword"))

        if user:
            conn = get_database()
            cursor = conn.cursor()
            cursor.execute("update users set password =? where email=?", (new_hashed_password, email))
            
            conn.commit()
            conn.close()

            flash("Password Created Successfully", "success")
            return redirect(url_for("login"))
        




    return render_template("passwordReset.html", passwordReset=True)


@app.route("/logout/")
@app.route("/logout")
def logout():
    session.clear()
    flash("Come Back Soon!", "warning")
    return redirect(url_for("home"))

@app.route("/user/account/delete/")
@app.route("/user/account/delete/")

def delete_user_account():
    if "user_id" in session:
        current_email = session.get("user_email")
        current_id = session.get("user_id")
        if current_id:
            conn=get_database()
            cursor=conn.cursor()

            cursor.execute("delete from users where id =?", (current_id,))
            cursor.execute("delete from message where sender_email =? or receiver_email=?", (current_email,current_email))

            products=cursor.execute("select * from product").fetchall()
            conn.commit()
            flash("Account deleted successfull", "warning")
            return render_template("home.html", products=products)
    return redirect(url_for("login"))

@app.route("/admin/")
@app.route("/admin")

def admin():

    if "user_id" not in session:
        flash("Log in first", "error")
        return redirect(url_for("login"))


    if session.get("user_role") != "Admin":
        flash("Success, first login with your email address", "warning")
        return redirect(url_for("login"))

    return render_template("admin.html", logged_in=True, letter=session["user_name"][0].upper(), role=session["user_role"], name = session["user_name"], is_admin=True)



@app.route("/admin/login/", methods=["GET", "POST"])
@app.route("/admin/login", methods=["GET", "POST"])

def admin_login():

    conn = get_database()
    cursor = conn.cursor()
    products = cursor.execute("select * from product").fetchall()
    conn.commit()

    if request.method == "POST":

        email = request.form["email"]
        conn = get_database()
        cursor = conn.cursor()

        cursor.execute("select * from users where email = ? and role ='Admin' ", (email,))
        user = cursor.fetchone()

        
        if user and session.get("user_id") == user['id']:
            flash("Verified! Welcome Back ", "success")
            return redirect(url_for("admin"))

        if user and not session.get("user_id") == user['id'] or user and not session.get("user_role") != user['role']:
            flash("You are currently not logged in. Login first", "warning")
            return redirect(url_for("login"))
        
            
        else:
            flash("Not allowed", "error")
            return redirect(url_for("admin_login"))
           
    return render_template("home.html", admin_login=True, products=products)



    
@app.route("/admin/user/", methods=["POST"])
@app.route("/admin/user", methods=["POST"])

def get_user():

    if session.get("user_role") != "Admin":
        return redirect(url_for("admin_login")), 403

    email = request.form["email"]

    conn = get_database()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    

    if not user:
        flash("User not found", "error")
        return redirect("/admin")
    view_user = "User Details"

    letter = session["user_name"][0].upper()

    return render_template("admin.html", found_user=user, view_user = view_user, logged_in=True, letter=letter, name = session["user_name"],role=session["user_role"])
    
@app.route("/admin/display/users/", methods=["GET", "POST"])
@app.route("/admin/display/users", methods=["GET", "POST"])

def get_users():

    if "user_id" in session and session.get("user_role") == "Admin":

        conn = get_database()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        if users:
            conn.close()
            view_user="Users Registered"
            return render_template("admin.html", logged_in=True, users=users, view_user=view_user, letter=session["user_name"][0].upper(), name = session["user_name"],role=session["user_role"])
        else:
            flash("No Users In Database", "warning")
            return redirect(url_for("admin"))
    else:
        return redirect(url_for("admin_login"))



@app.route("/admin/display/products/", methods=["GET","POST"])
@app.route("/admin/display/products", methods=["GET", "POST"])

def get_products():

    if "user_id" in session and session.get("user_role") == "Admin":
        conn = get_database()
        cursor = conn.cursor()
        
        cursor.execute("SELECT *  FROM product")
        products = cursor.fetchall()
        conn.close()
        view_product="Products Stored In the System"

        if products:
            return render_template("admin.html", logged_in=True, products=products, view_product=view_product, letter=session["user_name"][0].upper(), name = session["user_name"],role=session["user_role"])
        else:
            flash("No Products Stored", "warning")
            return redirect(url_for("admin"))
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/display/messages/", methods=["GET", "POST"])
@app.route("/admin/display/messages", methods=["GET", "POST"])

def get_messages():

    if "user_id" in session and session.get("user_role") == "Admin":

        conn = get_database()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM message")
        messages = cursor.fetchall()
        
        conn.close()
        view_message="Messages"

        if messages:
            return render_template("admin.html", logged_in=True, messages=messages, view_message=view_message, letter=session["user_name"][0].upper(), name = session["user_name"],role=session["user_role"])
        else:
            flash("No Messages", "warning")
            return redirect(url_for("admin"))
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/display/product/type/", methods=["GET", "POST"])
@app.route("/admin/display/product/type", methods=["GET", "POST"])

def get_type():

    if "user_id" in session and session.get("user_role") == "Admin":

        conn = get_database()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM product_type")
        product_type = cursor.fetchall()
        
        conn.close()
        view_type="Product Type"

        if product_type:
            return render_template("admin.html", logged_in=True, product_type=product_type, view_type=view_type, letter=session["user_name"][0].upper(), name = session["user_name"],role=session["user_role"])
        else:
            flash("No Data Stored", "warning")
            return redirect(url_for("admin"))
    else:
        return redirect(url_for("admin_login"))


@app.route("/admin/remove/user/", methods=["GET", "POST"])
@app.route("/admin/remove/user", methods=["GET","POST"])

def remove_user():

    if "user_id" in session and session.get("user_role") == "Admin":

        if request.method == "POST":
            email = request.form["email"]
            conn = get_database()
            cursor = conn.cursor()

            cursor.execute("select * from users where email = ?", (email,))

            user = cursor.fetchone()
            
            if user:
                cursor.execute("delete from users where email = ?", (email,))
                conn.commit()
                conn.close()
                flash(f"User with email '{email} Removed Successfully'", "success")
                return redirect(url_for("admin"))
            else:
                flash(f"User with email '{email}' doesn't exist", "error")
                return redirect(url_for("remove_user"))
    else:
        return redirect(url_for("admin_login"))

    return render_template("admin.html", logged_in=True, letter=session["user_name"][0].upper(), name = session["user_name"],role=session["user_role"])


@app.route("/admin/grant/admin/access", methods=["GET","POST"])
@app.route("/admin/grant/admin/access", methods=["GET","POST"])

def grant_admin():

    if "user_id" in session and session.get("user_role") == "Admin":
        if request.method == "POST":

            email = request.form["email"]
            conn = get_database()
            cursor = conn.cursor()

            cursor.execute("select email, fname from users where email = ?", (email,))

            user = cursor.fetchone()
            if user:
                cursor.execute("update users set role =? where email = ?", ('Admin', email,))
                conn.commit()
                conn.close()
                flash(f"Admin access granted to user with email '{email} '", "success")
                redirect(url_for("admin"))
            else:
                flash(f"User with email '{email}' doesn't exist", "error")
                return redirect(url_for("grant_admin"))
    else:
        return redirect(url_for("admin_login"))

    return render_template("admin.html", logged_in=True, letter=session["user_name"][0].upper(), name = session["user_name"],role=session["user_role"])

@app.route("/admin/revoke/admin/access", methods=["GET","POST"])
@app.route("/admin/revoke/admin/access", methods=["GET","POST"])

def revoke_admin():

    if "user_id" in session and session.get("user_role") == "Admin":

        if request.method == "POST":

            email = request.form["email"]
            conn = get_database()
            cursor = conn.cursor()

            cursor.execute("select email, fname from users where email = ?", (email,))

            user = cursor.fetchone()
            if user:
                cursor.execute("update users set role =? where email = ?", ('user', email,))
                conn.commit()
                conn.close()
                flash(f"Admin access revoked from user with email '{email} '", "success")
                redirect(url_for("admin"))
            else:
                flash(f"User with email '{email}' doesn't exist", "error")
                return redirect(url_for("revoke_admin"))
    else:
        return redirect(url_for("admin_login"))
    return render_template("admin.html", logged_in=True, letter=session["user_name"][0].upper(), name = session["user_name"],role=session["user_role"])

@app.route("/admin/add/product/")
@app.route("/admin/add/product")

def add_product():
    if "user_id" in session and session.get("user_role") == "Admin":
            
        return render_template("admin.html", logged_in=True, letter=session["user_name"][0].upper(), role=session["user_role"], name = session["user_name"], add_product=True)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/add/product/detail/", methods=["GET", "POST"])
@app.route("/admin/add/product/detail", methods=["GET", "POST"])

def product_detail():

    if "user_id" in session and session.get("user_role") == "Admin":

        if request.method == "POST":

            typeId = request.form["typeId"]
            productName = request.form["productName"]
            productDetail = request.form["productDetail"]
            productPrice = request.form["productPrice"]
            productImage = request.form["productImage"]

            

            conn=get_database()
            cursor = conn.cursor()

            product_type=cursor.execute("select 1 from product_type where id =?", (typeId)).fetchone()

            if product_type:

                cursor.execute("Insert into product (type_id, name,detail,price,image) values(?,?,?,?,?)", (typeId,productName,productDetail,productPrice, productImage))

                conn.commit()
                flash("Product Added Successfully", "success")
                return redirect(url_for("add_product"))

            flash("Foreign Key constraint Failed. Unknow Product Type ID", "warning")
            return redirect(url_for("add_product"))
            

        return render_template("admin.html", logged_in=True, letter=session["user_name"][0].upper(), role=session["user_role"], name = session["user_name"], add_product=True)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/add/product/type/", methods=["GET", "POST"])
@app.route("/admin/add/product/type", methods=["GET", "POST"])

def add_type():

    if "user_id" in session and session.get("user_role") == "Admin":

        if request.method == "POST":

            typeName = request.form["typeName"]


            conn=get_database()
            cursor = conn.cursor()

            cursor.execute("Insert into product_type (name) values(?)", (typeName,))

            conn.commit()
            flash("Type Added Successfully", "success")
            return redirect(url_for("add_type"))

        return render_template("admin.html", logged_in=True, letter=session["user_name"][0].upper(), role=session["user_role"], name = session["user_name"], add_type=True)
    else:
        return redirect(url_for("admin_login"))


@app.route("/admin/update/product/detail/", methods=["GET", "POST"])
@app.route("/admin/update/product/detail", methods=["GET", "POST"])

def update_product():

    if "user_id" in session and session.get("user_role") == "Admin":

        if request.method == "POST":

            productId = request.form["productId"]
            typeId = request.form["typeId"]
            productName = request.form["productName"]
            productDetail = request.form["productDetail"]
            productPrice = request.form["productPrice"]
            productImage = request.form["productImage"]

            conn=get_database()
            cursor = conn.cursor()

            product_type=cursor.execute("select 1 from product_type where id =?", (typeId)).fetchone()

            product_Id=cursor.execute("select 1 from product where id =?", (productId,)).fetchone()

            if product_Id is None:
                flash("Product id not found", "warning")
                return redirect(url_for("add_product"))

            if product_type and product_Id:
                cursor.execute("update product set name=?,detail=?,price=?, image=? where id=?", (productName,productDetail,productPrice, productImage, productId))

                conn.commit()
                flash("Product Updated Successfully", "success")
                return redirect(url_for("update_product"))

            flash("Foreign Key constraint Failed. Unknow New Product Type ID ", "warning")
            return redirect(url_for("update_product"))

        return render_template("admin.html", logged_in=True, letter=session["user_name"][0].upper(), role=session["user_role"], name = session["user_name"], add_product=True, update_product=True)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/update/product/type/", methods=["GET", "POST"])
@app.route("/admin/update/product/type", methods=["GET", "POST"])

def update_product_type():

    if "user_id" in session and session.get("user_role") == "Admin":

        if request.method == "POST":

            typeId = request.form["typeId"]
            typeName = request.form["typeName"]
            
            conn=get_database()
            cursor = conn.cursor()

            cursor.execute("update product_type set name=? where id=?", (typeName,typeId))

            conn.commit()
            flash("Type Updated Successfully", "success")
            return redirect(url_for("update_type"))
        

        return render_template("admin.html", logged_in=True, letter=session["user_name"][0].upper(), role=session["user_role"], name = session["user_name"], update_type=True)
    else:
        return redirect(url_for("admin_login"))

@app.route("/new/message/")
@app.route("/new/message")

def new_message():

    if "user_id" in session:

        conn=get_database()
        cursor=conn.cursor()

        cursor.execute("select * from product")
        products = cursor.fetchall() 

        email_address = session.get('user_email')
        user_id=session.get("user_id")

        unreadCount  = cursor.execute("select count(*) from message where receiver_email=? and is_read = 0", (email_address,)).fetchone()[0]
        unreads = cursor.execute("select * from message where receiver_email=? and is_read = 0", (email_address,)).fetchall()
        conn.commit()
        user = cursor.execute("select 1 from users where email=?", (email_address,)).fetchone()
        

        conn.commit()

        return render_template("inbox.html",logged_in=True, is_user=True, unreads=unreads, unreadCount=unreadCount, user_id=user_id, user=user, leaveMessage=True)

    return redirect(url_for("login"))

    
@app.route("/send/message/", methods=["GET", "POST"])
@app.route("/send/message", methods=["GET", "POST"])

def send_message():

    if "user_id" in session:
    
        if request.method == "POST":

            message_content = request.form["content"]
            send_to_email = request.form["receiver_email"]

            conn=get_database()
            cursor = conn.cursor()


            is_email_exist = cursor.execute("select * from users where email =?", (send_to_email,)).fetchone()
            conn.commit()

            sent_at = datetime.now().strftime("%H:%M")
            sent_date = datetime.now().strftime("%d-%m-%Y")
            current_email = session.get('user_email')

            unreadCount  = cursor.execute("select count(*) from message where receiver_email=? and is_read = 0", (current_email,)).fetchone()[0]


            unreads = cursor.execute("select * from message where receiver_email=? and is_read = 0", (current_email,)).fetchall()
            conn.commit()

        

            if not session.get("user_email"):
                flash("You are currently not loggen. Login first in", "error")
                return redirect(url_for("login"))

            if not is_email_exist:

                flash("Something went wrong.", "warning")
                return redirect(url_for("inbox"))

            if is_email_exist:
                cursor.execute("insert into message (sender_email, receiver_email, content, sent_date,sent_at) values(?,?,?,?,?)", (current_email,send_to_email, message_content,sent_date, sent_at))
                conn.commit()

            flash("Message sent", "success")
            return redirect(url_for("inbox"))
        return redirect(url_for("new_message"))
        

    return redirect(url_for("login"))
    



@app.route("/inbox/")
@app.route("/inbox")

def inbox():

    if "user_id" in session:

        conn=get_database()
        cursor = conn.cursor()

        current_email = session.get('user_email') 
        unreads = cursor.execute("select * from message where receiver_email=? and is_read = 0", (current_email,)).fetchall()
        conn.commit()

        unreadCount  = cursor.execute("select count(*) from message where receiver_email=? and is_read = 0", (current_email,)).fetchone()[0]

        return render_template("inbox.html", unreads=unreads, logged_in=True,unreadCount=unreadCount)

    return redirect(url_for("login"))


@app.route("/reply/", methods=["GET", "POST"])
@app.route("/reply", methods=["GET", "POST"])

def reply():

    if "user_id" in session:

        if request.method == "POST":

            message_to_reply = request.form["message_to_reply"]
            message_content = request.form["content"]
            reply_to_email = request.form["receiver_email"]
            sent_at = datetime.now().strftime("%H:%M")
            sent_date = datetime.now().strftime("%d-%m-%Y")
            current_email = session.get('user_email')

            conn=get_database()
            cursor = conn.cursor()

            reply_to_message = cursor.execute("select * from message where content=?", (message_to_reply,)).fetchone()
            conn.commit()

            if reply_to_message:

                cursor.execute("update message set is_read = 1 where sender_email=? and receiver_email=? and content=?", (reply_to_email, current_email, message_to_reply))

                cursor.execute("insert into message (sender_email, receiver_email, content,sent_date, sent_at) values(?,?,?,?,?)", (current_email,reply_to_email,message_content,sent_date, sent_at))


                conn.commit()


                flash("Message sent", "success")
                return redirect(url_for("inbox"))

    return redirect(url_for("login"))


@app.route("/message/read/one/", methods=["POST", "GET"])
@app.route("/message/read/one", methods=["POST", "GET"])

def read():


    if "user_id" in session:

        if request.method == "POST":

            sender_email = request.form["sender_email"]
            message_to_read = request.form["message_to_read"]
            receiver_email = session.get('user_email') 

            conn=get_database()
            cursor = conn.cursor()

            unread_message=cursor.execute("select * from message where content=? and is_read=0",(message_to_read,)).fetchone()
            conn.commit()

            if unread_message:

                cursor.execute("update message set is_read = 1 where sender_email=? AND receiver_email =? AND content=?", (sender_email, receiver_email, message_to_read))
                conn.commit()

                return redirect(url_for("inbox"))

    return redirect(url_for("login"))




@app.route("/inbox/message/read/all/")
@app.route("/inbox/message/read/all")

def readAll():


    if "user_id" in session:
        conn=get_database()
        cursor = conn.cursor()

        email_address = session.get('user_email') 
        
        cursor.execute("update message set is_read = 1 where receiver_email = ? ", (email_address,))
        conn.commit()
        flash("Marked successfully", "warning")
        return redirect(url_for("inbox"))

    return redirect(url_for("login"))






if __name__ == "__main__":
    app.run()