# Product Icon Generator - Docker Setup

A Django web application for generating branded product images with icons, containerized with Docker.

## 🚀 Quick Start with Docker

### Prerequisites

- **Docker Desktop** installed and running ([Download here](https://www.docker.com/products/docker-desktop/))
- **Git** (to clone the repository)

### Step 1: Clone the Repository

```bash
git clone <your-github-repo-url>
cd micro
```

### Step 2: Build and Run with Docker Compose

```bash
# Build and start all containers
docker compose up --build

# Or run in detached mode (background)
docker compose up -d --build
```

This will:
- Build the Django web application container
- Run database migrations automatically (using SQLite)
- Start the Django server on `http://localhost:8000`

### Step 4: Access the Application

Open your browser and navigate to:
- **Web Application**: http://localhost:8000

### Step 5: View in Docker Desktop

1. Open **Docker Desktop**
2. Go to the **Containers** tab
3. You should see the container running:
   - `product-web` (Django application with SQLite database)

## 📋 Common Docker Commands

```bash
# Start containers
docker compose up

# Start in background
docker compose up -d

# Stop containers
docker compose down

# Stop and remove volumes (clean database)
docker compose down -v

# View logs
docker compose logs

# View logs for the web service
docker compose logs web

# Rebuild containers
docker compose up --build

# Execute commands in container
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## 🗄️ Database Setup

The application uses **SQLite** by default (no separate database container needed):
- Database file: `django_app/db.sqlite3`
- The database is automatically created on first startup
- Migrations run automatically when the container starts

To manually run migrations:
```bash
docker compose exec web python manage.py migrate
```

To create a superuser (admin):
```bash
docker compose exec web python manage.py createsuperuser
```

## 📁 Project Structure

```
micro/
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── .env.docker.example     # Environment variables template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Root-level dependencies
└── django_app/             # Django application
    ├── manage.py
    ├── requirements.txt
    ├── product_generator/  # Django project settings
    ├── generator/          # Main app
    ├── templates/          # HTML templates
    ├── media/              # Uploaded files
    └── static/             # Static files
```

## 🔧 Configuration

### Environment Variables

The application uses **SQLite** by default (no configuration needed).

If you want to use MySQL instead, you can:
1. Add a MySQL service to `docker-compose.yml`
2. Set `DB_ENGINE=mysql` in the environment variables
3. Configure MySQL connection settings

## 🐛 Troubleshooting

### Containers not showing in Docker Desktop

1. **Check if Docker Desktop is running**
   - Look for Docker icon in system tray
   - Open Docker Desktop and ensure it's running

2. **Check if containers are actually running**
   ```bash
   docker compose ps
   ```

3. **Check logs for errors**
   ```bash
   docker compose logs
   ```

### Port already in use

If port 8000 is already in use:

1. Edit `docker-compose.yml`
2. Change the port mapping (e.g., `"8001:8000"` for web)

### Database connection errors

1. Ensure the container is running: `docker compose ps`
2. Check the logs: `docker compose logs web`
3. SQLite database file is stored at `django_app/db.sqlite3` (persisted via volume mount)

### Permission errors (Linux/Mac)

If you get permission errors:
```bash
sudo docker compose up --build
```

## 📤 Sharing with Your Team

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Docker setup"
   git push origin main
   ```

2. **Share the repository URL** with your team lead

3. **Team lead can then**:
   - Clone the repository
   - Follow the "Quick Start with Docker" steps above
   - No need to install Python, SQLite, or any dependencies locally!

## 🔒 Security Notes

- **Never commit** `.env.docker` to Git (it's in `.gitignore`)
- Change default passwords in production
- Use strong `SECRET_KEY` in production
- Set `DEBUG=False` in production

## 📚 Additional Documentation

For more details about the Django application itself, see [django_app/README.md](django_app/README.md)

## 🆘 Need Help?

If you encounter issues:
1. Check the logs: `docker compose logs`
2. Ensure Docker Desktop is running
3. Try rebuilding: `docker compose up --build`
4. Check that port 8000 is not in use by other applications

