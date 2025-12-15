# Product Icon Generator - Django Web App

A beautiful Django web application that allows users to upload product images, answer questions, and generate branded product images with icons.

## Features

- 🌐 **Web Interface**: Beautiful, responsive web interface built with Django and Bootstrap
- 📤 **Image Upload**: Easy drag-and-drop or click-to-upload functionality
- ❓ **Interactive Questions**: Checkbox-based questions for product attributes
- 🎨 **Beautiful Design**: Modern UI with gradient backgrounds and card layouts
- 📱 **Responsive**: Works perfectly on desktop, tablet, and mobile devices
- 💾 **Database Storage**: Stores all submissions and results in SQLite database
- 📥 **Download Results**: Direct download of generated images

## Installation

1. **Navigate to the Django app directory**:
```bash
cd django_app
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run database migrations**:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Create media directories**:
```bash
mkdir media
mkdir media/products
mkdir media/results
```

5. **Run the development server**:
```bash
python manage.py runserver
```

6. **Open your browser** and go to: `http://127.0.0.1:8000/`

## Usage

1. **Upload Product Image**: Click "Choose File" and select your product image
2. **Answer Questions**: Check the boxes that apply to your product:
   - ExtraFort?
   - 0% THC?
   - Nouvelle Formule?
   - Made in France?
   - CaliWeed?
   - Bio?
   - Sativa (10-20%)?
   - Indica (10-20%)?
   - CBD 10-20%?
3. **Generate**: Click "Generate Product Image"
4. **Download**: View your result and download the generated image

## Project Structure

```
django_app/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── product_generator/        # Django project settings
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── generator/               # Main app
│   ├── __init__.py
│   ├── apps.py              # App configuration
│   ├── models.py            # Database models
│   ├── forms.py             # Django forms
│   ├── views.py             # View functions
│   └── urls.py              # App URL patterns
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   └── generator/           # App templates
│       ├── home.html        # Home page
│       └── result.html      # Result page
├── media/                   # Uploaded files
│   ├── products/            # Original product images
│   └── results/             # Generated result images
└── icons/                   # Generated icon files
```

## Questions & Icons

The application includes 9 different questions, each with its own icon:

- **ExtraFort**: Black text icon
- **0% THC**: Red text icon
- **Nouvelle Formule**: Blue text icon
- **Made in France**: French flag colored icon
- **CaliWeed**: Green text icon
- **Bio**: Black text with leaf design
- **Sativa (10-20%)**: Circular icon with percentage
- **Indica (10-20%)**: Circular icon with percentage
- **CBD 10-20%**: Circular icon with percentage

## Background Design

The generated images feature:
- 🌿 Beautiful nature-themed background
- 🎨 Light green curved overlays
- 🌳 Tree root and branch outlines
- 🏆 Golden circular stand for the product
- 📍 Strategic icon placement

## Technologies Used

- **Backend**: Django 4.2+
- **Frontend**: Bootstrap 5, Font Awesome
- **Image Processing**: Pillow (PIL)
- **Database**: SQLite
- **Styling**: CSS3 with gradients and animations

## Customization

You can easily customize:
- **Questions**: Edit the form fields in `forms.py`
- **Icons**: Modify the icon creation in `views.py`
- **Background**: Change the background design in the `create_background()` method
- **Styling**: Update the CSS in `base.html`

## Production Deployment

For production deployment:
1. Set `DEBUG = False` in `settings.py`
2. Configure a production database (MySQL is supported out of the box)
3. Set up static file serving
4. Configure media file storage
5. Use a production WSGI server (Gunicorn + Nginx)

## Running with Docker

From the project root (where `docker-compose.yml` is located):

```bash
docker compose build
docker compose up
```

This will start:
- a **MySQL** database container
- the **Django** web container on `http://localhost:8000/`

The Django app is configured to use:
- SQLite by default (when `DB_ENGINE` is not set)
- **MySQL** when `DB_ENGINE=mysql` and the related DB env vars are provided

You can override the database configuration using environment variables:

- `DB_ENGINE` (`sqlite` or `mysql`)
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`


## License

This project is open source and available under the MIT License. 