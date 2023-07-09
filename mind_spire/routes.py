from flask import Blueprint,render_template,session,request,redirect,current_app,url_for,flash
from mind_spire.forms import BlogForm, RegisterForm, LoginForm
import uuid
from mind_spire.models import Blog, User
from dataclasses import asdict
from datetime import datetime
from bson.objectid import ObjectId
from passlib.hash import pbkdf2_sha256
import functools

pages=Blueprint("pages",__name__,template_folder="templates", static_folder="static")

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))

        return route(*args, **kwargs)

    return route_wrapper



@pages.route("/")
def home():
    return render_template("home.html",title="MindSpire")

#THEN THIS
#Here we are showing the blogs in a table , retrieving from database
@pages.route("/index")
@login_required
def index():
    user_data = current_app.db.user.find_one({"email": session["email"]})
    user = User(**user_data)

    blog_data=current_app.db.blogs.find({"_id":{"$in":user.written_blogs}})
    blog=[Blog(**blog) for blog in blog_data]
    return render_template("index.html", title="MindSpire",blog_data=blog)


@pages.get("/blog/<string:_id>")
@login_required
def blog_details(_id: str):
    blog = Blog(**current_app.db.blogs.find_one({"_id": _id}))
    blog.shared = current_app.db.blogshare.find_one({"_id": _id}) is not None  # Check if shared
    return render_template("details.html", blog=blog)





#@pages.route("/share")
#def share():
    #blog_data1 = current_app.db.blogshare.find({})
    #blog1 = [Blog(_id=blog['_id'], title=blog['title'], post=blog['post']) for blog in blog_data1]
    #return render_template("share.html", title="MindSpire", blog_data1=blog1)

@pages.route("/share")
def share():
    blog_data1 = current_app.db.blogshare.find({})
    blog1 = []
    
    user_data = current_app.db.user.find_one({"email": session["email"]})
    user = User(**user_data)

    for blog in blog_data1:
        blog_id = blog["_id"]
        likes_count = blog.get("likes", 0)
        liked_by = blog.get("liked_by", [])
        blog["likes"] = likes_count
        blog["liked_by"] = list(blog.get("liked_by", []))
        blog1.append(Blog(**blog))

    return render_template("share.html", title="MindSpire", blog_data1=blog1, user=user)





@pages.route("/add_share/<string:_id>")
@login_required
def add_share(_id: str):
    blog = current_app.db.blogs.find_one({"_id": _id})
    if blog:
        blog["shared"] = True  # Update the shared field
        current_app.db.blogshare.insert_one(blog)
    return redirect(url_for(".blog_details", _id=_id))  # Redirect to details page



#FIRST THIS  , adding to database
@pages.route("/add", methods=["GET", "POST"])
@login_required
def add_post():
    form = BlogForm()

    if form.validate_on_submit():
        current_date = datetime.now().date()
        if form.submit1.data:  # Check if button 1 was clicked
            blogs = Blog(
                _id= uuid.uuid4().hex,
                title= form.title.data,
                post= form.post.data,
                created_at=current_date.strftime('%Y-%m-%d')
            )
            current_app.db.blogs.insert_one(asdict(blogs))  # Insert into database 1
            current_app.db.user.update_one(
            {"_id": session["user_id"]}, {"$push": {"written_blogs": blogs._id}}
        )
        elif form.submit2.data:  # Check if button 2 was clicked
            current_date = datetime.now().date()

            blogs = Blog(
                _id= uuid.uuid4().hex,
                title= form.title.data,
                post= form.post.data,
                created_at=current_date.strftime('%Y-%m-%d'),
                shared=True  
            )
            current_app.db.blogshare.insert_one(asdict(blogs))  # Insert into database 2

        return redirect(url_for(".home"))

    return render_template("new_post.html", title="MindSpire-Add what's on your mind", form=form)




@pages.route("/add_like/<string:_id>")
@login_required
def add_like(_id: str):
    user_data = current_app.db.user.find_one({"email": session["email"]})
    user = User(**user_data)

    blogshare = current_app.db.blogshare.find_one({"_id": _id})
    if blogshare:
        likes_count = blogshare.get("likes", 0)

        # Check if the user has already liked the post
        if user._id not in blogshare.get("liked_by", []):
            updated_likes_count = likes_count + 1
            current_app.db.blogshare.update_one({"_id": _id}, {"$set": {"likes": updated_likes_count}})
            
            # Add the user to the list of users who liked the post
            current_app.db.blogshare.update_one({"_id": _id}, {"$push": {"liked_by": user._id}})

    return redirect(url_for(".share"))



@pages.route("/register", methods=["POST", "GET"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = current_app.db.user.find_one({"email": form.email.data})
        if existing_user:
            flash("User with this email already exists", "danger")
            return redirect(url_for(".register"))

        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data),
        )

        current_app.db.user.insert_one(asdict(user))

        flash("User registered successfully", "success")

        return redirect(url_for(".login"))

    return render_template(
        "register.html", title="MindSpire - Register", form=form
    )



@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = LoginForm()

    if form.validate_on_submit():
        user_data = current_app.db.user.find_one({"email": form.email.data})
        if not user_data:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".login"))
        user = User(**user_data)

        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session["user_id"] = user._id
            session["email"] = user.email

            return redirect(url_for(".index"))

        flash("Login credentials not correct", category="danger")

    return render_template("login.html", title="MindSpire - Login", form=form)


@pages.route("/logout")
def logout():
    #current_theme=session.get("theme")
    session.clear()
   # session["theme"]=current_theme

    return redirect(url_for(".login"))



@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    return redirect(request.args.get("current_page"))