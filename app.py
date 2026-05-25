# ================= IMPORTS =================
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)

from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

from flask_socketio import SocketIO, emit

from werkzeug.utils import secure_filename

from datetime import datetime

import eventlet
eventlet.monkey_patch()

import random


# ================= APP =================

app = Flask(__name__)

socketio = SocketIO(

    app,

    cors_allowed_origins="*",

    async_mode="eventlet"

)

app.config["SECRET_KEY"] = "secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"

db = SQLAlchemy(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

# ================= USER =================
class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True
    )

    name = db.Column(
        db.String(100)
    )

    bio = db.Column(
        db.String(300)
    )

    email = db.Column(
        db.String(200)
    )

    phone = db.Column(
        db.String(20)
    )

    password = db.Column(
        db.String(100)
    )

    dob = db.Column(
        db.String(100)
    )

    gender = db.Column(
        db.String(50)
    )

    profile_pic = db.Column(
        db.String(300)
    )

    online = db.Column(
        db.Boolean,
        default=False
    )

    last_seen = db.Column(
        db.String(100)
    )

# ================= FOLLOW =================
class Follow(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    follower = db.Column(
        db.String(100)
    )

    following = db.Column(
        db.String(100)
    )

# ================= MESSAGE =================
class Message(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sender = db.Column(
        db.String(100)
    )

    receiver = db.Column(
        db.String(100)
    )

    message = db.Column(
        db.String(1000)
    )

    image = db.Column(
        db.String(300)
    )

    voice = db.Column(
        db.String(300)
    )

    link = db.Column(
        db.String(500)
    )

    document = db.Column(
        db.String(300)
    )

    seen = db.Column(
        db.Boolean,
        default=False
    )

# ================= STORY =================
class Story(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100)
    )

    image = db.Column(
        db.String(300)
    )

# ================= STORY VIEW =================
class StoryView(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    story_id = db.Column(
        db.Integer
    )

    viewer = db.Column(
        db.String(100)
    )

# ================= CREATE DB =================
with app.app_context():

    db.create_all()

# ================= LOGIN LOADER =================
@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )

# ================= FIRST PAGE =================
@app.route("/")
def first_page():

    return redirect("/register")

# ================= HOME =================
@app.route("/home")
@login_required
def home():

    users = User.query.filter(
        User.id != current_user.id
    ).all()

    stories = Story.query.all()

    return render_template(

        "index.html",

        users=users,

        stories=stories

    )

# ================= ACCOUNT =================
@app.route("/account")
@login_required
def account():

    return render_template(
        "account.html"
    )

# ================= PROFILE =================
@app.route("/profile/<username>")
@login_required
def profile(username):

    user = User.query.filter_by(
        username=username
    ).first()

    followers = Follow.query.filter_by(
        following=username
    ).count()

    following = Follow.query.filter_by(
        follower=username
    ).count()

    already_following = Follow.query.filter_by(
        follower=current_user.username,
        following=username
    ).first()

    return render_template(

        "profile.html",

        user=user,

        followers=followers,

        following=following,

        already_following=already_following

    )

# ================= FOLLOW =================
@app.route("/follow/<username>")
@login_required
def follow(username):

    check = Follow.query.filter_by(
        follower=current_user.username,
        following=username
    ).first()

    if not check:

        new_follow = Follow(

            follower=current_user.username,

            following=username

        )

        db.session.add(new_follow)

        db.session.commit()

    return redirect(
        "/profile/" + username
    )

# ================= EDIT PROFILE =================
@app.route(
    "/edit-profile",
    methods=["GET", "POST"]
)
@login_required
def edit_profile():

    if request.method == "POST":

        current_user.name = request.form.get(
            "name"
        )

        current_user.bio = request.form.get(
            "bio"
        )

        profile = request.files.get(
            "profile_pic"
        )

        if profile and profile.filename != "":

            filename = secure_filename(
                profile.filename
            )

            profile.save(
                "static/uploads/" + filename
            )

            current_user.profile_pic = filename

        db.session.commit()

        return redirect(
            "/profile/" +
            current_user.username
        )

    return render_template(
        "edit_profile.html"
    )

# ================= MEDIA =================
@app.route("/media")
@login_required
def media():

    images = Message.query.filter(

        (
            Message.sender ==
            current_user.username
        )

        |

        (
            Message.receiver ==
            current_user.username
        ),

        Message.image != ""

    ).all()

    voices = Message.query.filter(

        (
            Message.sender ==
            current_user.username
        )

        |

        (
            Message.receiver ==
            current_user.username
        ),

        Message.voice != ""

    ).all()

    documents = Message.query.filter(

        (
            Message.sender ==
            current_user.username
        )

        |

        (
            Message.receiver ==
            current_user.username
        ),

        Message.document != ""

    ).all()

    links = Message.query.filter(

        (
            Message.sender ==
            current_user.username
        )

        |

        (
            Message.receiver ==
            current_user.username
        ),

        Message.link != ""

    ).all()

    return render_template(

        "media.html",

        images=images,

        voices=voices,

        documents=documents,

        links=links

    )

# ================= STORIES =================
@app.route(
    "/stories",
    methods=["GET", "POST"]
)
@login_required
def stories():

    if request.method == "POST":

        image = request.files["image"]

        filename = secure_filename(
            image.filename
        )

        image.save(
            "static/stories/" + filename
        )

        new_story = Story(

            username=current_user.username,

            image=filename

        )

        db.session.add(new_story)

        db.session.commit()

    stories = Story.query.all()

    return render_template(

        "stories.html",

        stories=stories

    )

# ================= VIEW STORY =================
@app.route("/view-story/<int:id>")
@login_required
def view_story(id):

    story = Story.query.get(id)

    check = StoryView.query.filter_by(

        story_id=id,

        viewer=current_user.username

    ).first()

    if not check:

        new_view = StoryView(

            story_id=id,

            viewer=current_user.username

        )

        db.session.add(new_view)

        db.session.commit()

    viewers = StoryView.query.filter_by(
        story_id=id
    ).all()

    return render_template(

        "view_story.html",

        story=story,

        viewers=viewers

    )

# ================= REGISTER =================
@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        email = request.form.get("email")

        phone = request.form.get("phone")

        username = request.form.get("username")

        name = request.form.get("name")

        bio = request.form.get("bio")

        dob = request.form.get("dob")

        gender = request.form.get("gender")

        password = request.form.get("password")

        entered_otp = request.form.get("otp")

        profile = request.files[
            "profile_pic"
        ]

        filename = secure_filename(
            profile.filename
        )

        profile.save(
            "static/uploads/" + filename
        )

        if entered_otp != session.get("otp"):

            return "Wrong OTP"

        new_user = User(

            email=email,

            phone=phone,

            username=username,

            name=name,

            bio=bio,

            dob=dob,

            gender=gender,

            password=password,

            profile_pic=filename,

            online=False,

            last_seen="Never"

        )

        db.session.add(new_user)

        db.session.commit()

        return redirect("/login")

    return render_template(
        "register.html"
    )

# ================= SEND OTP =================
@app.route("/send-otp")
def send_otp():

    otp = str(
        random.randint(
            100000,
            999999
        )
    )

    session["otp"] = otp

    return otp

# ================= LOGIN =================
@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        user = User.query.filter_by(
            username=username
        ).first()

        if user and user.password == password:

            user.online = True

            db.session.commit()

            login_user(user)

            return redirect("/home")

    return render_template(
        "login.html"
    )

# ================= LOGOUT =================
@app.route("/logout")
@login_required
def logout():

    current_user.online = False

    current_user.last_seen = str(
        datetime.now()
    )

    db.session.commit()

    logout_user()

    return redirect("/login")

# ================= CHAT =================
@app.route("/chat/<username>")
@login_required
def chat(username):

    user = User.query.filter_by(
        username=username
    ).first()

    messages = Message.query.filter(

        (
            (Message.sender == current_user.username)

            &

            (Message.receiver == username)
        )

        |

        (
            (Message.sender == username)

            &

            (Message.receiver == current_user.username)
        )

    ).all()

    return render_template(

        "chat.html",

        username=username,

        messages=messages,

        user=user

    )

# ================= DELETE MESSAGE =================
@app.route("/delete-message/<int:id>")
@login_required
def delete_message(id):

    msg = Message.query.get(id)

    if msg and msg.sender == current_user.username:

        db.session.delete(msg)

        db.session.commit()

    return redirect(request.referrer)

# ================= SOCKET =================

@socketio.on("send_message")
def handle_message(data):

    new_message = Message(

        sender=data["sender"],

        receiver=data["receiver"],

        message=data["message"],

        image="",

        voice="",

        link="",

        document="",

        seen=False

    )

    db.session.add(new_message)

    db.session.commit()

    emit(

        "receive_message",

        {

            "sender": data["sender"],

            "receiver": data["receiver"],

            "message": data["message"]

        },

        broadcast=True

    )



@socketio.on("typing")
def typing(data):

    emit(

        "show_typing",

        {

            "sender": data["sender"]

        },

        broadcast=True

    )



@socketio.on("stop_typing")
def stop_typing(data):

    emit(

        "hide_typing",

        {

            "sender": data["sender"]

        },

        broadcast=True

    )

# ================= STOP TYPING =================
@socketio.on("stop_typing")
def stop_typing(data):

    emit(

        "hide_typing",

        {

            "sender": data["sender"]

        },

        broadcast=True

    )
# ================= DELETE STORY =================
@app.route("/delete-story/<int:id>")
@login_required
def delete_story(id):

    story = Story.query.get(id)

    if story.username == current_user.username:

        db.session.delete(story)

        db.session.commit()

    return redirect("/stories")

# ================= RUN =================
if __name__ == "__main__":

    socketio.run(

        app,

        host="0.0.0.0",

        port=5001,

        debug=True,

        allow_unsafe_werkzeug=True

    )