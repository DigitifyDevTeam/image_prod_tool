import os
from django import forms
from .models import BatchSubmission

def get_vertical_picto_choices():
    """Dynamically scan Vertical_pictos folder and return choices"""
    choices = [('', '-- None --')]
    base_dir = os.path.dirname(os.path.dirname(__file__))
    vertical_dir = os.path.join(base_dir, 'Data', 'Vertical_pictos')
    
    if os.path.exists(vertical_dir):
        # Get files from main directory only (exclude custom_uploads subfolder and .old files)
        files = sorted([f for f in os.listdir(vertical_dir) 
                       if f.endswith(('.webp', '.png', '.jpg', '.jpeg')) 
                       and os.path.isfile(os.path.join(vertical_dir, f))
                       and not f.endswith('.old')])
        for f in files:
            # Use filename without extension as display name
            display_name = os.path.splitext(f)[0].replace('_', ' ').replace('-', ' ').title()
            choices.append((f, display_name))
        
        # DO NOT include custom_uploads - those are temporary files only
        # They will be added to dropdown dynamically via JavaScript after upload
    
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


class FlexibleSelect(forms.Select):
    """Select widget that includes the current value in choices even if not in initial choices"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None, renderer=None):
        # If value exists and is not in choices, add it
        if value and value not in [choice[0] for choice in self.choices]:
            display_name = os.path.splitext(str(value))[0].replace('_', ' ').replace('-', ' ').title()
            self.choices = list(self.choices) + [(value, display_name)]
        return super().render(name, value, attrs, renderer)


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
        # Use CharField with Select widget to allow custom uploads not in initial choices
        for i in range(1, 6):
            field_name = f'vertical_pos_{i}'
            # Get current value if form is being re-rendered
            current_value = None
            if self.data:
                current_value = self.data.get(field_name, '').strip()
            elif self.initial:
                current_value = self.initial.get(field_name, '').strip()
            
            # If there's a value not in choices, add it
            choices = list(vertical_choices)
            if current_value and current_value not in [choice[0] for choice in choices]:
                display_name = os.path.splitext(current_value)[0].replace('_', ' ').replace('-', ' ').title()
                choices.append((current_value, display_name))
            
            self.fields[field_name] = forms.CharField(
                required=False,
                widget=forms.Select(choices=choices, attrs={'class': 'form-select'})
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
        
        base_dir = os.path.dirname(os.path.dirname(__file__))
        vertical_dir = os.path.join(base_dir, 'Data', 'Vertical_pictos')
        custom_uploads_dir = os.path.join(vertical_dir, 'custom_uploads')
        
        # Validate vertical picto selections - check if file exists
        for i in range(1, 6):
            filename = cleaned_data.get(f'vertical_pos_{i}', '').strip()
            if filename:
                # Check if file exists in main directory or custom_uploads
                main_path = os.path.join(vertical_dir, filename)
                custom_path = os.path.join(custom_uploads_dir, filename) if os.path.exists(custom_uploads_dir) else None
                
                if not os.path.exists(main_path) and (not custom_path or not os.path.exists(custom_path)):
                    self.add_error(f'vertical_pos_{i}', f'Selected picto file does not exist: {filename}')
        
        # For each horizontal position, if a category is selected, validate file is from that category
        for i in range(1, 6):
            cat = cleaned_data.get(f'horizontal_cat_{i}')
            file = cleaned_data.get(f'horizontal_file_{i}')
            
            if cat and file:
                valid_files = get_horizontal_files_for_category(cat)
                if file not in valid_files:
                    self.add_error(f'horizontal_file_{i}', f'Invalid file for category {cat}')
        
        return cleaned_data
