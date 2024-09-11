# generator/views.py
import openai
import os
import json
from django.conf import settings
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages 
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from .models import Image 
from django.core.files.base import ContentFile
from generator.models import *



def generate_comic_image(request):
    if request.method == "POST":
        prompt = request.POST.get('prompt', '')
        comic_style = request.POST.get('comic_style', 'comic style')  # Get the selected comic style

        if prompt:
            try:
                openai.api_key = settings.OPENAI_API_KEY

                # Append the selected comic style to the prompt
                full_prompt = f"{prompt} in {comic_style}"

                # Use the new image generation endpoint
                response = openai.Image.create(
                    prompt=full_prompt,
                    n=1,
                    size="512x512"
                )

                image_url = response['data'][0]['url']

                # Debugging output
                print(f"Image URL: {image_url}")

                return JsonResponse({'image_url': image_url})
            except Exception as e:
                print(f"Error: {str(e)}")
                return JsonResponse({'error': f'Error: {str(e)}'})

    return render(request, 'generate_comic_image.html')



def home(request):
    return render(request, 'home.html')  


def login_user(request):
    if request.POST:
        email=request.POST.get('email')
        password=request.POST.get('password')
        user = authenticate(request,username=email,password=password)

        if user is not None:
            if user.is_superuser:
                login(request,user)
                return redirect('ad_home')
            else:
                login(request,user)
                return redirect('generate_comic_image')
        else:
             messages.error(request, 'Invalid user credentials')
        
    return render(request,'login.html')




def register_user(request):
    if request.POST:
        name=request.POST.get('fullname')
        email=request.POST.get('email')
        password=request.POST.get('password')
        user=User.objects.create_user(username=email,password=password,first_name=name)
        user.save()
        return redirect('login_user')
    return render(request,'register.html')




def gallery_user(request):
    # Directory where images are stored
    image_dir = os.path.join(settings.BASE_DIR, 'image')
    
    # Check if the directory exists, if not, create it
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        print(f"Directory created at {image_dir}")
    else:
        print(f"Directory exists at {image_dir}")
    
    # List of image files
    images = []
    for filename in os.listdir(image_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            print(filename)
            images.append({
                'name': filename,
                'date': '2024-09-01',  # Example date; replace with actual date if available
                'tag': 'example_tag'  # Example tag; replace with actual tag if available
            })   

    return render(request, 'gallery.html', {'Images': images})

# def gallery_user(request):
#     # Directory where images are stored
#     image_dir = os.path.join(settings.BASE_DIR,'image')
#     print(image_dir)
#     # List of image files
#     images = []
#     for filename in os.listdir(image_dir):
#         if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
#             print(filename)
#             images.append({
#                 'name': filename,
#                 'date': '2024-09-01',  # Example date; replace with actual date if available
#                 'tag': 'example_tag'  # Example tag; replace with actual tag if available
#             })   
   
    
#     return render(request, 'gallery.html', {'Images': images})
    


def logout_user(request):
    logout(request)  # This will log the user out
    return redirect('home')  # Redirect to the home page after logout

def save_button(request):
    return render(request, 'generate_comic_image.html')


def save_image(request):
    if request.method == "POST":
        try:
            # Parse JSON body
            data = json.loads(request.body)
            image_url = data.get('image_url', '')

            if image_url:
                # Download the image from the provided URL
                image_response = requests.get(image_url)

                if image_response.status_code == 200:
                    image_data = image_response.content

                    # Ensure the 'image' directory exists
                    images_dir = 'image'
                    if not os.path.exists(images_dir):
                        os.makedirs(images_dir)

                    # Sanitize the file name and enforce PNG extension
                    file_name = os.path.basename(image_url)
                    file_name = file_name.split('?')[0]  # Remove query parameters if any
                    file_name = file_name.replace('%', '_')  # Replace invalid characters
                    file_name = os.path.splitext(file_name)[0] + ".jpeg"  # Ensure the file has a .png extension

                    # Save the image in the 'image' directory
                    image_path = os.path.join(images_dir, file_name)
                    with open(image_path, 'wb') as f:
                        f.write(image_data)

                    return JsonResponse({'success': True, 'message': 'Image saved successfully!', 'file_path': image_path})

                return JsonResponse({'success': False, 'error': 'Failed to download the image from the URL.'})
            else:
                return JsonResponse({'success': False, 'error': 'Image URL is missing.'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def image_saving(request):
    if request.method == 'POST':
        user = request.user
        image_url = request.POST.get('image_url')
        
        if image_url:
            # Assuming images model has a URL field for storing image paths/URLs
            images.objects.create(user=user, image=image_url)
        
        return redirect('generate_comic_image')





def content(request):
    return render(request, 'content.html')


def create(request):
    return render(request, 'create.html')


def approve(request):
    return render(request, 'approve.html')


def ad_home(request):
    return render(request, 'admin_home.html')


@csrf_exempt  # TinyMCE might not send the CSRF token properly, so exempt this view
def upload_image(request):
    if request.method == 'POST':
        if request.FILES.get('file'):
            image = request.FILES['file']

            # Define the path where the image will be stored
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'images/')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            # Save the image file
            image_path = os.path.join(upload_dir, image.name)
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            # Return the URL of the uploaded image
            image_url = f"{settings.MEDIA_URL}images/{image.name}"
            return JsonResponse({'location': image_url})

        return JsonResponse({'error': 'No file provided'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def platform(request):
    return render(request, 'platform.html')

def approve(request):
    return render(request, 'approve.html')

def feedback(request):
    return render(request, 'feedback.html')

def api_use(request):
    return render(request, 'api_use.html')