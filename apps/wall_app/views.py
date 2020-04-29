from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Message, Comment
import bcrypt

# Create your views here.
def index(request):
    return render(request, "wall_app/index.html")

def register(request):
    errors = User.objects.basic_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags='reg')
        return redirect("/")
    else:
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        pw = request.POST["password"]
        pw_hash = bcrypt.hashpw(pw.encode(), bcrypt.gensalt())
        new_user = User.objects.create(first_name=first_name, last_name=last_name, email=email, password=pw_hash)
        request.session["user_id"] = new_user.id
        return redirect("/wall")

def login(request):
    email = request.POST["email"]
    pw = request.POST["password_login"]
    users = User.objects.filter(email = email)
    if len(users) == 0:
        messages.error(request, "Invalid login.", extra_tags='login')
        return redirect("/")

    user = users[0]
    if bcrypt.checkpw(pw.encode(), user.password.encode()):
        request.session["user_id"] = user.id
        return redirect("/wall")
    messages.error(request, "Invalid login.", extra_tags='login')
    return redirect("/")

def wall(request):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session["user_id"])
        messages = Message.objects.all().order_by("-created_at")
        comments = Comment.objects.all().order_by("-created_at")
        context = {
            "user" : user,
            "messages" : messages,
            "comments" : comments
        }
        return render(request, "wall_app/wall.html", context)
    return redirect("/")

def post_message(request):
    user = User.objects.get(id=request.session["user_id"])
    message = request.POST["message"]
    Message.objects.create(user=user, message=message)
    return redirect("/wall")

def post_comment(request):
    user = User.objects.get(id=request.session["user_id"])
    comment = request.POST["comment"]
    message = Message.objects.get(id=request.POST["message_id"])
    Comment.objects.create(user=user, message=message, comment=comment)
    return redirect("/wall")

def logout(request):
    request.session.clear()
    return redirect("/")