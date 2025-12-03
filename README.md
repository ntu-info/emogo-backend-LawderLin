# EmoGo Backend

EmoGo is course project for practicing building a product.

In this section, we need to build the backend for the product.

The frontend allows user to:

- Record their mood and activity, which contains:
    - Current mood in scale from 1 to 5.
    - A video log.
    - Geographical location, longitude and latitude
- Export their record in csv format.

## Features

✅ **FastAPI Backend** - High-performance async API
✅ **MongoDB Integration** - NoSQL database for data storage
✅ **CSV Export** - Export mood records in CSV format
✅ **Video Upload** - Support for video file uploads
✅ **Statistics** - Get mood analytics and distribution
✅ **Interactive API Docs** - Swagger UI & ReDoc

## Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Git

### Installation & Running

#### Option 1: Using the Quick Start Script (Recommended)

```bash
chmod +x start.sh
./start.sh
```

This will automatically:
- Start MongoDB in Docker
- Handle port conflicts
- Start the FastAPI backend

#### Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start MongoDB with Docker:**
   ```bash
   # If port 27017 is available:
   docker-compose up -d
   
   # If port 27017 is in use (use alternative port):
   MONGO_PORT=27018 docker-compose up -d
   ```

3. **Set environment variables:**
   ```bash
   # For default port (27017)
   export MONGODB_URL="mongodb://admin:password@localhost:27017/emogo_db"
   
   # For custom port (27018)
   export MONGODB_URL="mongodb://admin:password@localhost:27018/emogo_db"
   ```

4. **Run the backend:**
   ```bash
   python main.py
   ```

### Access the Application

- **API Server:** http://localhost:8000
- **Swagger Documentation:** http://localhost:8000/docs
- **ReDoc Documentation:** http://localhost:8000/redoc
- **Mongo Express (DB GUI):** http://localhost:8081

**Default Mongo Express Credentials:**
- Username: `admin`
- Password: `password`

## Troubleshooting

### Port Already in Use

If you get an error like:
```
ports are not available: exposing port TCP 0.0.0.0:27017 -> bind: address already in use
```

**Solutions:**
1. Use a different port: `MONGO_PORT=27018 docker-compose up -d`
2. Kill the process using the port: `lsof -i :27017` then `kill -9 <PID>`
3. Clean up old containers: `docker-compose down -v`

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for more details.

## API Documentation

See [API_DOCS.md](./API_DOCS.md) for complete API reference including:
- Create mood record
- Get records
- Export CSV
- Upload videos
- View statistics

## Project Structure

```
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # MongoDB & Mongo Express setup
├── start.sh             # Quick start script
├── .env.example         # Environment variables template
├── API_DOCS.md          # Complete API documentation
├── TROUBLESHOOTING.md   # Troubleshooting guide
└── README.md            # This file
```

## Development Todo

- [x] Setup MongoDB for data storage
- [x] Complete FastAPI for storing/exporting data
- [ ] Add authentication/authorization
- [ ] Add data validation and error handling
- [ ] Add unit tests
- [ ] Deploy to production server
- [ ] Add frontend integration

## Environment Variables

Create a `.env` file (or use `.env.example` as template):

```bash
# MongoDB
MONGO_PORT=27017
MONGODB_URL=mongodb://admin:password@localhost:27017/emogo_db
MONGODB_DB=emogo_db

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

## Example Usage

### Create a mood record:
```bash
curl -X POST "http://localhost:8000/api/records" \
  -H "Content-Type: application/json" \
  -d '{
    "mood": 4,
    "activity": "studying",
    "longitude": 121.5654,
    "latitude": 25.0330,
    "video_url": "https://example.com/video.mp4"
  }'
```

### Get all records:
```bash
curl "http://localhost:8000/api/records"
```

### Export as CSV:
```bash
curl "http://localhost:8000/api/export/csv" -o mood_records.csv
```

### Get statistics:
```bash
curl "http://localhost:8000/api/stats"
```

## Stopping Services

```bash
# Stop MongoDB and Mongo Express
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## License

Course project for NTU