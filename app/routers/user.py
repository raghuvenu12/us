from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    FastAPI,
    Request,
    Form,
    Query,
    UploadFile,
    File,
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from fastapi.responses import RedirectResponse
import re
import app.db.schemas as schemas
from datetime import datetime, timezone
import time
from app.db.models import User, Citizen, Comment, Post, Agency, OTP, Media
import twilio
import pytz
from app.routers import post, user
from twilio.rest import Client
import random
from datetime import datetime, timedelta
from google.cloud import storage
import os
from PIL import Image
from io import BytesIO
from app.config import Settings

setting = get_settings()


# Create a 'now' variable representing the current date and time


# Generate and print a random number between 100 and 9999


templates = Jinja2Templates(
    directory="app/templates"
)
router = APIRouter()
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "molten-complex-408603-13e3b41bd520.json"
Path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
storage_client = storage.Client(Path)



@router.get("/", name="login")
async def login(request: Request, status: str = Query(None)):
    return templates.TemplateResponse(
        "login.html", {"request": request, "status": status}
    )


@router.post("/post/login/otp")
async def otp(request: Request, phone: str = Form(...)):
    try:
        '''account_sid = "ACe6eed746ebf574cded13a432021f1665"
        auth_token = "224cea1e9b2294738fb8a8ad23cc4783"
        client = Client(account_sid, auth_token)
        random_number = random.randint(1000, 9999)
        phone = "+91" + phone
        message = client.messages.create(
            from_="+13214210602", to=phone, body=random_number
        )'''
        phone = "+91" + phone

        # Add 3 minutes to the current time
       

        new_data = OTP(
            phone=phone,
            otp="1234",
            status="New",
            valid_till=datetime.now() + timedelta(minutes=5),
            num_attempts=1,
            created_at=datetime.now(),
        )
        await new_data.save()

        return templates.TemplateResponse(
            "otp.html",
            {"request": request, "phone": phone, "status": status, "attempts": 1},
        )

    except Exception as e:
        # Handle other exceptions
        print(f"Unexpected Exception: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Add similar try-except blocks to other routes and functions as needed.


@router.post("/post/verify_otp/{phone}")
async def verify(request: Request, phone: str, otp: int = Form(...)):
    try:
        otp_data = await OTP.filter(phone=phone).order_by("-id").limit(1).first()
        if otp_data.num_attempts > 3:
            return templates.TemplateResponse("login.html", {"request": request})
        
        indian_timezone = pytz.timezone("Asia/Kolkata")
        if (otp_data.valid_till.date()) == (
            (datetime.now(pytz.utc).astimezone(indian_timezone).date())
        ):
            if (otp_data.valid_till.time()) < (
                (datetime.now(pytz.utc).astimezone(indian_timezone).time())
            ):
                otp_data.status = "expired"

                await otp_data.save()
                target_url = router.url_path_for("login")
                target_url += f"?status={otp_data.status}"
                response = RedirectResponse(url=target_url, status_code=303)
                return response

        if otp == otp_data.otp:
            otp_data.status = "successfull"

            await otp_data.save()

            # Use the name of the endpoint function
            user_exist = await User.filter(phone=phone).exists()
            if user_exist:
                target_url = f"/post/test/{phone}"

                response = RedirectResponse(url=target_url, status_code=303)
                return response
            else:
                new_data = User(
                    phone=phone,
                )
                await new_data.save()

                target_url = f"/post/user_login/{phone}"

                print(target_url)
                response = RedirectResponse(url=target_url, status_code=303)
                return response

        if otp_data.num_attempts == 3:
            n = otp_data.num_attempts
            n += 1

            otp_data.num_attempts = n
            otp_data.status = "max_attempts"
            await otp_data.save()

            target_url = router.url_path_for("login")
            # Use the name of the endpoint function
            target_url += f"?status={otp_data.status}"
            response = RedirectResponse(url=target_url, status_code=303)
            return response
        n = otp_data.num_attempts
        n += 1
        otp_data.num_attempts = n
        await otp_data.save()
        return templates.TemplateResponse(
            "otp.html", {"request": request, "phone": phone, "attempts": n}
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Not found")
    


@router.get("/post/user_login/{phone}")
async def user_login(request: Request, phone: str):
    print(phone)
    return templates.TemplateResponse(
        "user_login.html", {"request": request, "phone": phone}
    )


@router.post("/post/user/{phone}")
async def get_user(
    request: Request,
    phone: str,
    name: str = Form(...),
    username: str = Form(...),
    file: UploadFile = File(...),
):
    
    user_id = await User.get(phone=phone)
   
    id = user_id.id
    img = await file.read()
    img = Image.open(BytesIO(img))
    img.thumbnail((200, 200))
    output = BytesIO()
    img.convert("RGB").save(output, format="JPEG")

    # Replace with your actual file name

    bucket = storage_client.bucket("sueful_social_profile")

    # Create a Google Cloud Storage client

    # Define the destination blob name (file name in the bucket)
    destination_blob_name = f"profiles/{id}_thumb.jpg"

    # Upload the file to GCS
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(BytesIO(output.getvalue()), content_type="image/jpeg")
    image_url = blob.public_url
    new_data = Citizen(
        name=name,
        username=username,
        user_id=id,
        image_url=image_url,
    )
    await new_data.save()

    """ target_url = router.url_path_for(
            "create" ,
        ) 
    target_url+=f"/{phone}" """
    target_url = f"/post/test/{phone}"
    response = RedirectResponse(url=target_url, status_code=303)
    return response


@router.post("/post/posts/{phone}")
async def post(
    request: Request,
    phone: str,
    text: str = Form(...),
    files: list[UploadFile] = File(...),
):
    user= await User.get(phone=phone)
    id = user.id
    mention_pattern = r"@([A-Za-z0-9_]+)"

    # Regular expression pattern for hashtags (e.g., #example)
    hashtag_pattern = r"#([A-Za-z0-9_]+)"

    # Extract mentions and hashtags from the text
    mentions = re.findall(mention_pattern, text)
    hashtags = re.findall(hashtag_pattern, text)
    new_data = Post(
        text=text,
        mentions=mentions,
        hashtags=hashtags,
        ip_address=request.client.host,
        address="Bangalore",
        city="Bangalore",
        state="Karnataka",
        country="India",
        user_id=user.id,
    )
    await new_data.save()
    post= (
        await Post.filter(user_id=user.id).order_by("-id").limit(1).first()
    )
    image_url = []
    bucket = storage_client.bucket("sueful_social_profile")
    g=1
    for file in files:
        img = await file.read()
        img = Image.open(BytesIO(img))
        img.thumbnail((200, 200))
        output = BytesIO()
        img.convert("RGB").save(output, format="JPEG")
        destination_blob_name = f"posts/post_{post.id}_{g}.jpg"
        g+=1
        

        # Upload the file to GCS
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_file(BytesIO(output.getvalue()), content_type="image/jpeg")

        image_url.append(blob.public_url)
    new_data = Media(media_thumbnail_url=image_url, post_id=post.id)
    await new_data.save()

    # Create a Google Cloud Storage client

    # Define the destination blob name (file name in the bucket)
    target_url = f"/post/test/{phone}"
    response = RedirectResponse(url=target_url, status_code=303)
    return response


@router.post("/post/{id}/comment/{phone}")
async def comment(request: Request, phone: str, id: int, comment: str = Form(...)):
    user_id = await User.get(phone=phone)
    new_data = Comment(
        text=comment, ip_address=request.client.host, post_id=id, user_id=user_id.id
    )
    await new_data.save()
    target_url = f"/post/test/{phone}"
    response = RedirectResponse(url=target_url, status_code=303)
    return response


@router.get("/post/test/{phone}")
async def create(request: Request, phone: str):
    print(phone)
    user_id = await User.get(phone=phone)
    citizen = await Citizen.get(user_id=user_id.id).first()
    username = citizen.username
    image = citizen.image_url
    users = await User.all()
    all_citizen = await Citizen.all()
    

    post = await Post.all().order_by("-id").limit(3)
    usernames = []
    images = []
    comments = []
    comment_post = []
    comment_username_per_post = []
    comment_username = []
    comment_image_per_post = []
    comment_image = []
    for i in range(len(post)):
        id = post[i].user_id
        print(id)
        citizen = await Citizen.get(user_id=id).first()
        usernames.append(citizen.username)
        images.append(citizen.image_url)
        comment = await Comment.filter(post_id=post[i].id).order_by("-id").limit(3)
        for i in comment:
            comment_post.append(i.text)
            citizen_details = await Citizen.get(user_id=i.user_id).first()
            comment_username_per_post.append(citizen_details.username)
            comment_image_per_post.append(citizen_details.image_url)

        comments.append(comment_post.copy())
        comment_username.append(comment_username_per_post.copy())
        comment_image.append(comment_image_per_post.copy())
        comment_post.clear()
        comment_username_per_post.clear()
        comment_image_per_post.clear()

    media = await Media.all().order_by("-id").limit(3)
    n = len(usernames)

    return templates.TemplateResponse(
        "index.html",
        {
            "image": image,
            "request": request,
            "user": users,
            "citizen": all_citizen,
            "phone": phone,
            "media": media,
            "username": username,
            "post": post,
            "media": media,
            "usernames": usernames,
            "images": images,
            "n": n,
            "comments": comments,
            "comment_username": comment_username,
            "comment_image": comment_image,
        },
    )
