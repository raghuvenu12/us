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
    Response,
    File,
)
import secrets
from typing import Annotated
from fastapi_login import LoginManager
import collections
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import requests
import socket

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from fastapi.responses import RedirectResponse
import re
from app.utils.crypto import create_hash
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
from urllib.request import urlopen
import ipdata

'''
s=urlopen('http://checkip.dyndns.com')
d=str(s.read())
print(d)'''

setting = get_settings()
payload = {'key': 'CE87A75E625D2A14A870CAFC5D7022B2', 'ip': '101.0.63.227', 'format': 'json'}
api_result = requests.get('https://api.whatismyip.com/ip.php?key=52ba3649a96c23a93aa973a3f0ab9d38')
print(api_result.text)


SECRET = "9c44d829edc3d3096e940dcf62a9c09fdd30a084ebe535dc"

manager = LoginManager(
    SECRET, '/post/verify_otp',
    use_cookie=True,use_header=False,
    default_expiry=timedelta(hours=5768)
)


   

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

@manager.user_loader()
async def query_user(phone: str):
    return phone


@router.get('/')
def protected_route(request:Request):
    cookies=(request.cookies)
    if cookies.get("access-token") is None:
        target_url = f"/post"

        print(target_url)
        resp = RedirectResponse(url=target_url, status_code=307)
        return resp
    else:
        target_url = f"/post/test"
        response = RedirectResponse(url=target_url, status_code=303)
        return response



    



@router.get("/post", name="login")
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
        otp=await OTP.all().order_by('-id').limit(1).first()
        print(otp.id)
        return templates.TemplateResponse(
            "otp.html",
            {"request": request, "id":otp.id, "status": status, "attempts": 1},
        )
    except Exception as e:
        # Handle other exceptions
        print(f"Unexpected Exception: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Add similar try-except blocks to other routes and functions as needed.
@router.get("/post/map")
async def map(request:Request,phone:str=Depends(manager)):
    distinct_user_ids = await Post.all()
    posts=await Post.all()
    lat=[]
    long=[]
    s=set()
    seen = set()
    result = []
    for item in distinct_user_ids:
        if (item.latitude,item.longitude) not in seen:
            seen.add((item.latitude,item.longitude))
            result.append((item.latitude,item.longitude))
    
    
    print(result)
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
    all_post=await Post.all()
    post_mentions=[]
    for i in range(len(all_post)):
        for j in range(len(all_post[i].mentions)):

            post_mentions.append(all_post[i].mentions[j])
    post_mentions=collections.Counter(post_mentions)


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
    top_mentions=[]
    print(top_mentions)
    for i,j in post_mentions.items():
        top_mentions.append(i)

    media = await Media.all().order_by("-id").limit(3)
    n = len(usernames)

    return templates.TemplateResponse(
        "map.html",
        {
            "top_mentions":top_mentions,
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
            "comment_image": comment_image,"distinct_posts":result,"post":posts
        },
    )


    



@router.post("/post/verify_otp/{id}")
async def verify(response:Response,request: Request, id:int,otp: int = Form(...)):
    
    try:
        otp_data = await OTP.get(id=id)
        
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
            token = manager.create_access_token(
            data=dict(sub=otp_data.phone)
                    )
            
            print(query_user( otp_data.phone))

            # Use the name of the endpoint function
            user_exist = await User.filter(phone=otp_data.phone).exists()
            if user_exist:
                target_url = f"/post/test"

                response = RedirectResponse(url=target_url, status_code=303)
                manager.set_cookie(response, token)
                return response
            else:
                new_data = User(
                    phone=otp_data.phone,
                )
                await new_data.save()

                target_url = f"/post/user_login"

                print(target_url)
                resp = RedirectResponse(url=target_url, status_code=303)
                manager.set_cookie(resp, token)
                return resp
                

            
            
           
            
           
            
    

            # Use the name of the endpoint function
           
            
           

            target_url = f"/post/user_login"

           
            

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
            "otp.html", {"request": request, "id":id,"attempts": n}
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Not found")
    


@router.get("/post/user_login")
async def user_login(request: Request):
    
    return templates.TemplateResponse(
        "user_login.html", {"request": request}
    )
@router.get("/post/comment")
async def comment(request:Request) :
    return templates.TemplateResponse("comment.html",{"request":request})

@router.post("/post/user")
async def get_user(
    request: Request,
   phone :str=Depends(manager),
    name: str = Form(...),
    username: str = Form(...),
    file: UploadFile = File(...),
    
):
    
    
    user_id = await User.get(phone=phone)
   
    id = user_id.id
    img = await file.read()
    img = Image.open(BytesIO(img))
    img=img.resize((200, 200))
    output = BytesIO()
    img.convert("RGB").save(output, format="JPEG")

    # Replace with your actual file name

    bucket = storage_client.bucket("sueful_social_profile")

    # Create a Google Cloud Storage client

    # Define the destination blob name (file name in the bucket)
    destination_blob_name = f"profiles/{id}_thumb.jpg"

    # Upload the file to GCS
    blob = bucket.blob(destination_blob_name)
    blob.cache_control = 'no-store, no-cache, must-revalidate'
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
    target_url = f"/post/test"
    response = RedirectResponse(url=target_url, status_code=303)
    return response


@router.post("/post/posts")
async def post(
    request: Request,
    phone :str=Depends(manager),
    text: str = Form(...),
    files: list[UploadFile] = File(...),
    latitude:str=Form(...),longitude:str=Form(...)
):
    
    user= await User.get(phone=phone)
    print(user.id)
    id = user.id
    mention_pattern = r"@([A-Za-z0-9_]+)"
    

    # Regular expression pattern for hashtags (e.g., #example)
    hashtag_pattern = r"#([A-Za-z0-9_]+)"
    
    video_file_extensions = ["mp4", "avi", "mkv"]  # Add more as needed

# Extract mentions and hashtags from the text
   
    video_file_extensions = ["mp4", "avi", "mkv"]  # Add more as needed
    citizen=await Citizen.get(user_id=user.id)
    print(citizen.id)
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
        latitude=float(latitude),
        longitude=float(longitude),
       


    )
    await new_data.save()
    post= (
        await Post.filter(user_id=user.id).order_by("-id").limit(1).first()
    )

    # Initialize the list to store image and video URLs
    media_urls = []
    bucket = storage_client.bucket("sueful_social_profile")

    # Process and upload each file (image or video)
    v=1
    g=1
    for file in files:
        file_extension = file.filename.split('.')[-1].lower()

        if file_extension in video_file_extensions:
            # Handle video file
            video_blob_name = f"posts/post_{post.id}_video_{v}.{file_extension}"

            # Upload video to Blob Storage
            blob = bucket.blob(video_blob_name)
            blob.upload_from_file(file.file, content_type=file.content_type)
            v+=1

            media_urls.append(blob.public_url)
        else:              
            # Handle image file
            img = await file.read()
            img = Image.open(BytesIO(img))
            img = img.resize((200, 200))
            output = BytesIO()
            img.convert("RGB").save(output, format="JPEG")
            image_blob_name = f"posts/post_{post.id}_{g}.jpg"
            g += 1

            # Upload the image file to Blob Storage
            blob = bucket.blob(image_blob_name)
            blob.upload_from_file(BytesIO(output.getvalue()), content_type="image/jpeg")

            media_urls.append(blob.public_url)
        

    # Extract mentions and hashtags from the text
  
    
    

    ipdata.api_key = "262c735de4858cc850b8309d2de3091efbd439641ae16854e3e8fc02"   
    
    
   
    
    
   

  
    new_data = Media(media_thumbnail_url=media_urls, post_id=post.id,Citizen_id=citizen.id)
    await new_data.save()

    # Create a Google Cloud Storage client

    # Define the destination blob name (file name in the bucket)
    target_url = f"/post/test"
    response = RedirectResponse(url=target_url, status_code=303)
    return response


@router.post("/post/{id}/comment")
async def comment(request: Request, id: int, phone: str=Depends(manager),comment: str = Form(...)):
    user_id = await User.get(phone=phone)
    new_data = Comment(
        text=comment, ip_address=request.client.host, post_id=id, user_id=user_id.id
    )
    await new_data.save()
    target_url = f"/post/test"
    response = RedirectResponse(url=target_url, status_code=303)
    return response


@router.get("/post/test")
async def create(request: Request,phone:str=Depends(manager)):
   
    print(phone)
    user_id = await User.get(phone=phone)
    citizen = await Citizen.get(user_id=user_id.id).first()
    username = citizen.username
    image = citizen.image_url
    users = await User.all()
    all_citizen = await Citizen.all()
   
    media_with_post = await Media.all().order_by('-id').limit(3).prefetch_related(
        'post','Citizen'
    )
    print(media_with_post[0])
    #print(media_with_post[0].Citizen.username)

 
   
    
    
    
    

    # Option 2: Iterate over the queryset and print each user
    
    
    
    
    
    post = await Post.all().order_by("-id").limit(3)
    usernames = []
    images = []
    comments = []
    comment_post = []
    comment_username_per_post = []
    comment_username = []
    comment_image_per_post = []
    comment_image = []
    all_post=await Post.all()
    post_mentions=[]
    for i in range(len(all_post)):
        for j in range(len(all_post[i].mentions)):

            post_mentions.append(all_post[i].mentions[j])
    post_mentions=collections.Counter(post_mentions)


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
    top_mentions=[]
    print(top_mentions)
    for i,j in post_mentions.items():
        top_mentions.append(i)

    media = await Media.all().order_by("-id").limit(3)
    n = len(usernames)

    return templates.TemplateResponse(
        "index.html",
        {
            "top_mentions":top_mentions,
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
