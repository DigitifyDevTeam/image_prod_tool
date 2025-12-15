import os
from django import forms
from .models import BatchSubmission

def get_vertical_picto_choices():
    """Dynamically scan Vertical_pictos folder and return choices"""
    choices = [('', '-- None --')]
    base_dir = os.path.dirname(os.path.dirname(__file__))
    vertical_dir = os.path.join(base_dir, 'Data', 'Vertical_pictos')
    
    if os.path.exists(vertical_dir):
        files = sorted([f for f in os.listdir(vertical_dir) if f.endswith(('.webp', '.png', '.jpg', '.jpeg'))])
        for f in files:
            # Use filename without extension as display name
            display_name = os.path.splitext(f)[0].replace('_', ' ').replace('-', ' ').title()
            choices.append((f, display_name))
    
    return choices

def get_horizontal_category_choices():
    """Dynamically scan horizantal_Pictos folder for category subfolders"""
    choices = [('', '-- None --')]
    base_dir = os.path.dirname(os.path.dirname(__file__))
    horizontal_dir = os.path.join(base_dir, 'Data', 'horizantal_Pictos')
    
    if os.path.exists(horizontal_dir):
        categories = sorted([d for d in os.listdir(horizontal_dir) if os.path.isdir(os.path.join(horizontal_dir, d))])
        for cat in categories:
            choices.append((cat, cat))
    
    return choices

def get_horizontal_files_for_category(category):
    """Get files for a specific horizontal category"""
    files = []
    base_dir = os.path.dirname(os.path.dirname(__file__))
    cat_dir = os.path.join(base_dir, 'Data', 'horizantal_Pictos', category)
    
    if os.path.exists(cat_dir):
        files = sorted([f for f in os.listdir(cat_dir) if f.endswith(('.webp', '.png', '.jpg', '.jpeg'))])
    
    return files


class MultipleFileInput(forms.ClearableFileInput):
    """Custom widget for multiple file upload"""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Custom field for multiple file upload"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class ProductSubmissionForm(forms.Form):
    """Form for product submission with multiple image support and picto position selectors"""
    
    # Multiple file upload field
    product_images = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'multiple': True
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        vertical_choices = get_vertical_picto_choices()
        horizontal_cat_choices = get_horizontal_category_choices()
        
        # Set up vertical position dropdowns
        for i in range(1, 6):
            field_name = f'vertical_pos_{i}'
            self.fields[field_name] = forms.ChoiceField(
                choices=vertical_choices,
                required=False,
                widget=forms.Select(attrs={'class': 'form-select'})
            )
        
        # Set up horizontal category and file dropdowns
        for i in range(1, 6):
            cat_field = f'horizontal_cat_{i}'
            file_field = f'horizontal_file_{i}'
            
            self.fields[cat_field] = forms.ChoiceField(
                choices=horizontal_cat_choices,
                required=False,
                widget=forms.Select(attrs={
                    'class': 'form-select horizontal-category',
                    'data-position': str(i)
                })
            )
            
            # File field - use CharField to accept any value from JavaScript
            self.fields[file_field] = forms.CharField(required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # For each horizontal position, if a category is selected, validate file is from that category
        for i in range(1, 6):
            cat = cleaned_data.get(f'horizontal_cat_{i}')
            file = cleaned_data.get(f'horizontal_file_{i}')
            
            if cat and file:
                valid_files = get_horizontal_files_for_category(cat)
                if file not in valid_files:
                    self.add_error(f'horizontal_file_{i}', f'Invalid file for category {cat}')
        
        return cleaned_data
