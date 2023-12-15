from fastapi import APIRouter, Depends, HTTPException, status, FastAPI, Request, Form,Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from fastapi.responses import RedirectResponse
import app.db.schemas as schemas
from datetime import datetime, timezone
import time
from app.db.models import User, Citizen, Comment, Post, Agency, OTP
import twilio
import pytz
from app.routers import post, user
from twilio.rest import Client
import random
from datetime import datetime, timedelta
from app.config import Settings

setting = get_settings()
print(setting.max_otp_attempts)

# Create a 'now' variable representing the current date and time


# Generate and print a random number between 100 and 9999


templates = Jinja2Templates(
    directory="C:\\Users\\raghu\\Documents\\useful_social\\us\\app\\templates"
)
router = APIRouter()


@router.get("/post/login",name='login')
async def login(request: Request,status:str=Query(None)):
    return templates.TemplateResponse("login.html", {"request": request,"status":status})


@router.post("/post/login/otp")
async def otp(request: Request, phone: str = Form(...)):
    account_sid = "ACb619e4e6639fea826319162fac4e585c"
    auth_token = "2f06e34253eb8005ced48e0893075811"
    client = Client(account_sid, auth_token)
    random_number = random.randint(1000, 9999)

    message = client.messages.create(from_="+12052936739", to=phone, body=random_number)

    # Add 3 minutes to the current time
    print(datetime.now() + timedelta(minutes=3))

    new_data = OTP(
        phone=phone,
        otp=random_number,
        status="New",
        valid_till=datetime.now() + timedelta(seconds=30),
        num_attempts=1,
        created_at=datetime.now(),
    )
    await new_data.save()

    return templates.TemplateResponse("otp.html", {"request": request, "phone": phone,"status":status,"attempts":1})


@router.post("/post/verify_otp/{phone}")
async def verify(request: Request, phone: str, otp: int = Form(...)):
    filtered_data = await OTP.filter(phone=phone).order_by("-id").limit(1).first()

    if filtered_data.num_attempts > 3:
        return templates.TemplateResponse("login.html", {"request": request})
    print(filtered_data.valid_till)
    indian_timezone = pytz.timezone("Asia/Kolkata")

    print(datetime.now(pytz.utc).astimezone(indian_timezone))

    if (filtered_data.valid_till.date()) == (
        (datetime.now(pytz.utc).astimezone(indian_timezone).date())
    ):
        if (filtered_data.valid_till.time()) < (
            (datetime.now(pytz.utc).astimezone(indian_timezone).time())
        ):
            filtered_data.status = "expired"

            await filtered_data.save()
            target_url = router.url_path_for(
            "login")
            target_url+=f"?status={filtered_data.status}"
            response = RedirectResponse(url=target_url,status_code=303)
            return response

    if otp == filtered_data.otp:
        target_url = router.url_path_for(
            "create"
        )  # Use the name of the endpoint function
        response = RedirectResponse(url=target_url, status_code=303)
        return response

    if filtered_data.num_attempts == 3:
        n = filtered_data.num_attempts
        n += 1

        filtered_data.num_attempts = n
        filtered_data.status = "max_attempts"
        await filtered_data.save()

        target_url = router.url_path_for(
            "login"
        )
          # Use the name of the endpoint function
        target_url+=f"?status={filtered_data.status}"
        response = RedirectResponse(url=target_url, status_code=303)
        return response

    """
    account_sid = "ACb619e4e6639fea826319162fac4e585c"
    auth_token = "2f06e34253eb8005ced48e0893075811"
    client = Client(account_sid, auth_token)
   
    message = client.messages.create(from_="+12052936739", to=phone, body=random_number)"""
    n = filtered_data.num_attempts
    n += 1
    print(n)

    filtered_data.num_attempts = n
    await filtered_data.save()

    return templates.TemplateResponse("otp.html", {"request": request, "phone": phone,"attempts":n})


@router.get("/post/test")
async def create(request: Request):
    users = await User.all()
    citizen = await Citizen.all()
    post = await Post.all()
    comment = await Comment.all()
    agency = await Agency.all()
    no_of_comment = await Comment.all().count()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": users,
            "citizen": citizen,
            "post": post,
            "comment": no_of_comment,
            "agency": agency,
        },
    )
