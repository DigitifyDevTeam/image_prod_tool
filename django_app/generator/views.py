from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import ProductSubmissionForm, get_horizontal_files_for_category
from .models import ProductSubmission, BatchSubmission
import os
import sys
import json
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO


class ProductIconGenerator:
    def __init__(self):
        self.background_width = 800
        self.background_height = 800
        # Base directory for data files
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.data_dir = os.path.join(self.base_dir, 'Data')
        self.vertical_dir = os.path.join(self.data_dir, 'Vertical_pictos')
        self.horizontal_dir = os.path.join(self.data_dir, 'horizantal_Pictos')
    
    def create_background(self):
        """Load the background image file from multiple possible locations"""
        base_dir = os.path.dirname(os.path.dirname(__file__))  # django_app/
        root_dir = os.path.dirname(base_dir)  # micro/
        possible_paths = [
            os.path.join(base_dir, 'backgrounds', 'background.jpg'),
            os.path.join(base_dir, 'backgrounds', 'background.png'),
            os.path.join(root_dir, 'background.jpg'),
            os.path.join(root_dir, 'background.png'),
            os.path.join(root_dir, 'backgrounds', 'background.jpg'),
            os.path.join(root_dir, 'backgrounds', 'background.png'),
            os.path.join(root_dir, 'img', 'background.jpg'),
            os.path.join(root_dir, 'img', 'background.png')
        ]
        
        for path in possible_paths:
            try:
                background = Image.open(path)
                print(f"✅ Loaded background from: {path}")
                if background.size != (self.background_width, self.background_height):
                    background = background.resize((self.background_width, self.background_height), Image.Resampling.LANCZOS)
                return background
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"❌ Error loading {path}: {e}")
                continue
        
        print("⚠️  No background image found. Creating a simple white background.")
        background = Image.new('RGB', (self.background_width, self.background_height), (255, 255, 255))
        return background
    
    def center_product(self, product_image, background):
        """Center the product image directly on the background image without frame"""
        max_size = 350
        product_width, product_height = product_image.size
        
        if product_width > product_height:
            new_width = max_size
            new_height = int((product_height * max_size) / product_width)
        else:
            new_height = max_size
            new_width = int((product_width * max_size) / product_height)
        
        product_image = product_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Ensure product image has transparency (RGBA)
        if product_image.mode != 'RGBA':
            product_image = product_image.convert('RGBA')
        
        # Ensure background is in RGBA mode for proper alpha blending
        if background.mode != 'RGBA':
            background = background.convert('RGBA')
        
        product_x = (self.background_width - product_image.size[0]) // 2
        product_y = (self.background_height - product_image.size[1]) // 2
        
        # Paste product image with alpha channel to blend naturally (no white frame)
        background.paste(product_image, (product_x, product_y), product_image)
        
        return background
    
    def load_picto(self, picto_path, max_size=100):
        """Load a picto image, convert to RGBA, and resize preserving aspect ratio"""
        try:
            picto = Image.open(picto_path)
            if picto.mode != 'RGBA':
                picto = picto.convert('RGBA')
            
            # Resize preserving aspect ratio
            width, height = picto.size
            if width > height:
                new_width = max_size
                new_height = int((height * max_size) / width)
            else:
                new_height = max_size
                new_width = int((width * max_size) / height)
            
            picto = picto.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return picto
        except Exception as e:
            print(f"❌ Error loading picto {picto_path}: {e}")
            return None
    
    def add_vertical_pictos(self, background, vertical_selections):
        """Add vertical pictos on the left side of the image
        Position 1 = BOTTOM, Position 5 = TOP
        """
        picto_max_size = 130  # Increased size for better visibility
        x_pos = 20  # X position (left side)

        
        # Fixed Y positions maintaining same visual spacing between pictos
        # Original: 100px pictos with 115px spacing between top edges = 15px visual gap
        # New: 130px pictos, maintaining 15px visual gap = 145px spacing between top edges
        # Position 1 at BOTTOM, Position 5 at TOP
       
        vertical_positions = [
            575,   # Position 1 - BOTTOM (keep same reference point)
            430,   # Position 2 (575 - 145 = 430)
            285,   # Position 3 (430 - 145 = 285)
            140,   # Position 4 (285 - 145 = 140)
            5,     # Position 5 - TOP (140 - 145 = -5, but keep at 5 for safety)
        ]
        
        for i, filename in enumerate(vertical_selections):
            if filename and i < len(vertical_positions):
                picto_path = os.path.join(self.vertical_dir, filename)
                picto = self.load_picto(picto_path, picto_max_size)
                if picto:
                    y_pos = vertical_positions[i]
                    
                    if background.mode != 'RGBA':
                        background = background.convert('RGBA')
                    
                    background.paste(picto, (x_pos, y_pos), picto)
        
        return background
    
    def add_horizontal_pictos(self, background, horizontal_selections):
        """Add horizontal pictos vertically on the right side of the image
        Position 1 = BOTTOM, Position 5 = TOP (same Y positions as left vertical pictos)
        """
        picto_max_size = 130  # Increased size for better visibility
        x_pos = self.background_width - 120  # X position (right side, 120px from right edge)
        
        # Same Y positions as left vertical pictos (maintaining same visual spacing)
        # Original: 100px pictos with 115px spacing between top edges = 15px visual gap
        # New: 130px pictos, maintaining 15px visual gap = 145px spacing between top edges
        # Position 1 at BOTTOM, Position 5 at TOP
        vertical_positions = [
            575,   # Position 1 - BOTTOM (keep same reference point)
            430,   # Position 2 (575 - 145 = 430)
            285,   # Position 3 (430 - 145 = 285)
            140,   # Position 4 (285 - 145 = 140)
            5,     # Position 5 - TOP (140 - 145 = -5, but keep at 5 for safety)
        ]
        
        for i, (category, filename) in enumerate(horizontal_selections):
            if category and filename and i < len(vertical_positions):
                picto_path = os.path.join(self.horizontal_dir, category, filename)
                picto = self.load_picto(picto_path, picto_max_size)
                if picto:
                    y_pos = vertical_positions[i]
                    
                    if background.mode != 'RGBA':
                        background = background.convert('RGBA')
                    
                    background.paste(picto, (x_pos, y_pos), picto)
        
        return background
    
    def process_product(self, product_image_path, vertical_selections, horizontal_selections):
        """Process the product image with vertical and horizontal pictos"""
        try:
            # Load product image
            product_image = Image.open(product_image_path)
            
            # Convert to RGBA to preserve transparency (no white background frame)
            if product_image.mode == 'P':
                product_image = product_image.convert('RGBA')
            elif product_image.mode not in ('RGBA', 'RGB'):
                product_image = product_image.convert('RGBA')
            elif product_image.mode == 'RGB':
                # Keep RGB but we'll convert to RGBA in center_product
                pass
            
            # Create background
            background = self.create_background()
            
            # Center product on background
            background = self.center_product(product_image, background)
            
            # Add vertical pictos (left side)
            background = self.add_vertical_pictos(background, vertical_selections)
            
            # Add horizontal pictos (right side, vertical)
            background = self.add_horizontal_pictos(background, horizontal_selections)
            
            # Convert back to RGB for saving (WebP supports RGB)
            if background.mode == 'RGBA':
                rgb_background = Image.new('RGB', background.size, (255, 255, 255))
                rgb_background.paste(background, (0, 0), background)
                background = rgb_background
            
            # Save the final image as WebP
            base_name = os.path.splitext(os.path.basename(product_image_path))[0]
            output_path = f'media/results/result_{base_name}.webp'
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            background.save(output_path, 'WEBP', quality=95)
            
            return output_path
            
        except Exception as e:
            print(f"Error processing image: {e}")
            import traceback
            traceback.print_exc()
            return None


def home(request):
    """Home page with the product submission form - supports multiple images"""
    if request.method == 'POST':
        form = ProductSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            # Get uploaded files (multiple)
            files = request.FILES.getlist('product_images')
            
            if not files:
                messages.error(request, 'Please select at least one image.')
                return render(request, 'generator/home.html', {'form': form})
            
            # Create a batch submission to store the shared picto selections
            batch = BatchSubmission.objects.create(
                vertical_pos_1=form.cleaned_data.get('vertical_pos_1') or '',
                vertical_pos_2=form.cleaned_data.get('vertical_pos_2') or '',
                vertical_pos_3=form.cleaned_data.get('vertical_pos_3') or '',
                vertical_pos_4=form.cleaned_data.get('vertical_pos_4') or '',
                vertical_pos_5=form.cleaned_data.get('vertical_pos_5') or '',
                horizontal_cat_1=form.cleaned_data.get('horizontal_cat_1') or '',
                horizontal_file_1=form.cleaned_data.get('horizontal_file_1') or '',
                horizontal_cat_2=form.cleaned_data.get('horizontal_cat_2') or '',
                horizontal_file_2=form.cleaned_data.get('horizontal_file_2') or '',
                horizontal_cat_3=form.cleaned_data.get('horizontal_cat_3') or '',
                horizontal_file_3=form.cleaned_data.get('horizontal_file_3') or '',
                horizontal_cat_4=form.cleaned_data.get('horizontal_cat_4') or '',
                horizontal_file_4=form.cleaned_data.get('horizontal_file_4') or '',
                horizontal_cat_5=form.cleaned_data.get('horizontal_cat_5') or '',
                horizontal_file_5=form.cleaned_data.get('horizontal_file_5') or '',
            )
            
            # Gather selections from batch
            vertical_selections = [
                batch.vertical_pos_1, batch.vertical_pos_2, batch.vertical_pos_3,
                batch.vertical_pos_4, batch.vertical_pos_5
            ]
            horizontal_selections = [
                (batch.horizontal_cat_1, batch.horizontal_file_1),
                (batch.horizontal_cat_2, batch.horizontal_file_2),
                (batch.horizontal_cat_3, batch.horizontal_file_3),
                (batch.horizontal_cat_4, batch.horizontal_file_4),
                (batch.horizontal_cat_5, batch.horizontal_file_5),
            ]
            
            # Process each uploaded image
            generator = ProductIconGenerator()
            success_count = 0
            
            for uploaded_file in files:
                # Save the uploaded file
                file_path = default_storage.save(f'products/{uploaded_file.name}', ContentFile(uploaded_file.read()))
                full_path = default_storage.path(file_path)
                
                # Create product submission
                submission = ProductSubmission.objects.create(
                    batch=batch,
                    product_image=file_path
                )
                
                # Process the image
                result_path = generator.process_product(
                    full_path,
                    vertical_selections,
                    horizontal_selections
                )
                
                if result_path:
                    submission.result_image = result_path.replace('media/', '')
                    submission.save()
                    success_count += 1
            
            if success_count > 0:
                messages.success(request, f'Successfully generated {success_count} product image(s)!')
                return redirect('batch_result', batch_id=batch.id)
            else:
                messages.error(request, 'Error generating product images.')
    else:
        form = ProductSubmissionForm()
    
    return render(request, 'generator/home.html', {'form': form})


def get_picto_data_from_batch(batch):
    """Extract picto data from a batch submission for preview editor"""
    vertical_pictos = []
    vertical_positions = [575, 430, 285, 140, 5]  # Y positions for vertical pictos (maintaining spacing)
    
    for i in range(1, 6):
        filename = getattr(batch, f'vertical_pos_{i}', '') or ''
        if filename:
            vertical_pictos.append({
                'url': f'/data/Vertical_pictos/{filename}',
                'x': 20,
                'y': vertical_positions[i-1]
            })
    
    horizontal_pictos = []
    x_pos = 800 - 120  # Right side, 120px from right edge
    vertical_positions = [575, 430, 285, 140, 5]  # Same Y positions as left vertical pictos (maintaining spacing)
    
    for i in range(1, 6):
        category = getattr(batch, f'horizontal_cat_{i}', '') or ''
        filename = getattr(batch, f'horizontal_file_{i}', '') or ''
        if category and filename:
            horizontal_pictos.append({
                'url': f'/data/horizantal_Pictos/{category}/{filename}',
                'x': x_pos,
                'y': vertical_positions[i-1]
            })
    
    return {
        'vertical': vertical_pictos,
        'horizontal': horizontal_pictos,
        'background_url': '/backgrounds/background.jpg'
    }


def result(request, submission_id):
    """Display the result page with a single generated image"""
    try:
        submission = ProductSubmission.objects.get(id=submission_id)
        
        # Get picto data for preview editor
        picto_data = {}
        if submission.batch:
            picto_data = get_picto_data_from_batch(submission.batch)
        
        return render(request, 'generator/result.html', {
            'submission': submission,
            'picto_data': json.dumps(picto_data)
        })
    except ProductSubmission.DoesNotExist:
        messages.error(request, 'Submission not found.')
        return redirect('home')


def batch_result(request, batch_id):
    """Display results for a batch of processed images"""
    try:
        batch = BatchSubmission.objects.get(id=batch_id)
        products = batch.products.all()
        
        # Get picto data for preview editor
        picto_data = get_picto_data_from_batch(batch)
        
        return render(request, 'generator/batch_result.html', {
            'batch': batch,
            'products': products,
            'picto_data': json.dumps(picto_data)
        })
    except BatchSubmission.DoesNotExist:
        messages.error(request, 'Batch not found.')
        return redirect('home')


def get_horizontal_files(request):
    """API endpoint to get files for a horizontal category"""
    category = request.GET.get('category', '')
    
    if not category:
        return JsonResponse({'files': []})
    
    files = get_horizontal_files_for_category(category)
    
    # Return list of dicts with value and display name
    file_choices = []
    for f in files:
        display_name = os.path.splitext(f)[0].replace('_', ' ').replace('-', ' ')
        file_choices.append({'value': f, 'label': display_name})
    
    return JsonResponse({'files': file_choices})
