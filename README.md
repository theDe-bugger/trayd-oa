# Job Management API

A RESTful API built with Flask for managing construction jobs and workers. This API provides comprehensive job and worker management capabilities with advanced querying, relationships, and performance features. This was made by Jaimil for Trayd. It is also deployed on PythonAnywhere as a production server on the following URL: `https://thedebugger46.pythonanywhere.com`.

## Setup Instructions

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python app.py
```

The server will start on `http://localhost:5000`

## Running Tests

I set up some test cases to track a few features of the API. You can run them with the following instructions:

1. Make sure the API server is running in a separate terminal
2. You can also run the tests on the deployed server by changing the BASE_URL in test_api.py to PROD_URL instead of LOCAL_URL
3. Run the tests with:

```bash
pytest test_api.py
```

## API Documentation

### Jobs

#### Create a Job

- **Endpoint:** `POST /jobs`
- **Content-Type:** `application/json`
- **Request Body:**

```json
{
  "name": "Downtown Office Renovation",
  "customer": "ABC Corp",
  "startDate": "2024-03-15",
  "endDate": "2024-06-15",
  "status": "In Progress"
}
```

- **Response (201 Created):**

```json
{
  "id": 1,
  "name": "Downtown Office Renovation",
  "customer": "ABC Corp",
  "startDate": "2024-03-15",
  "endDate": "2024-06-15",
  "status": "In Progress",
  "workerCount": 0
}
```

#### Get All Jobs

- **Endpoint:** `GET /jobs`
- **Query Parameters:**
  - `name`: Filter jobs by name (partial match)
  - `customer`: Filter jobs by customer (partial match)
  - `status`: Filter by job status
  - `startAfter`: Filter jobs starting after date (YYYY-MM-DD)
  - `endBefore`: Filter jobs ending before date (YYYY-MM-DD)
  - `sortBy`: Sort by field (name, customer, start_date, end_date, status)
  - `order`: Sort order (asc, desc)
  - `page`: Page number for pagination
  - `limit`: Number of items per page
- **Response (200 OK):**

```json
{
  "jobs": [
    {
      "id": 1,
      "name": "Downtown Office Renovation",
      "customer": "ABC Corp",
      "startDate": "2024-03-15",
      "endDate": "2024-06-15",
      "status": "In Progress",
      "workerCount": 2
    }
  ],
  "pagination": {
    "page": 1,
    "perPage": 10,
    "total": 1,
    "pages": 1
  }
}
```

#### Delete a Job

- **Endpoint:** `DELETE /jobs/<job_id>`
- **Response:** 204 No Content

### Workers

#### Create a Worker

- **Endpoint:** `POST /workers`
- **Request Body:**

```json
{
  "name": "John Doe",
  "role": "Electrician",
  "jobId": 1
}
```

#### Bulk Create Workers

- **Endpoint:** `POST /workers/bulk`
- **Request Body:**

```json
[
  {
    "name": "John Doe",
    "role": "Electrician",
    "jobId": 1
  },
  {
    "name": "Jane Smith",
    "role": "Carpenter",
    "jobId": 1
  }
]
```

#### Get Workers

- **Endpoint:** `GET /workers`
- **Query Parameters:**
  - `name`: Filter by worker name
  - `role`: Filter by worker role
  - `jobId`: Filter by assigned job
  - `page`: Page number
  - `limit`: Items per page
- **Response:**

```json
{
  "workers": [
    {
      "id": 1,
      "name": "John Doe",
      "role": "Electrician",
      "jobId": 1
    }
  ],
  "pagination": {
    "page": 1,
    "perPage": 10,
    "total": 1,
    "pages": 1
  }
}
```

#### Get Workers for a Job

- **Endpoint:** `GET /jobs/<job_id>/workers`
- **Response:**

```json
[
  {
    "id": 1,
    "name": "John Doe",
    "role": "Electrician",
    "jobId": 1
  }
]
```

### Statistics

#### Get System Statistics

- **Endpoint:** `GET /stats`
- **Response:**

```json
{
  "jobs": {
    "total": 10,
    "byStatus": {
      "In Progress": 6,
      "Completed": 4
    }
  },
  "workers": {
    "total": 15,
    "byRole": {
      "Electrician": 5,
      "Carpenter": 4,
      "Plumber": 6
    }
  }
}
```

## Technical Approach

This project implements a RESTful API using Flask and SQLAlchemy with the following features:

1. **Advanced Querying:**

   - Date range filtering
   - Status filtering
   - Flexible sorting options
   - Case-insensitive search

2. **Data Relationships:**

   - Job-Worker one-to-many relationship
   - Worker assignment management
   - Role-based worker categorization

3. **Performance Features:**

   - Pagination for all list endpoints
   - Bulk creation support
   - Efficient database queries
   - Statistical aggregations

4. **Error Handling:**

   - Input validation
   - Proper HTTP status codes
   - Consistent error responses
   - Transaction management

5. **Database Design:**
   - SQLite for development (easily adaptable to PostgreSQL/MySQL)
   - Proper foreign key constraints
   - Indexed fields for performance

## Example API Usage

### Using cURL

1. Create a job:

```bash
curl -X POST http://localhost:5000/jobs \
-H "Content-Type: application/json" \
-d '{
    "name": "Downtown Office Renovation",
    "customer": "ABC Corp",
    "startDate": "2024-03-15",
    "endDate": "2024-06-15",
    "status": "In Progress"
}'
```

2. Advanced job search:

```bash
curl "http://localhost:5000/jobs?startAfter=2024-01-01&endBefore=2024-12-31&status=In%20Progress&sortBy=name&order=desc"
```

3. Create a worker:

```bash
curl -X POST http://localhost:5000/workers \
-H "Content-Type: application/json" \
-d '{
    "name": "John Doe",
    "role": "Electrician",
    "jobId": 1
}'
```

4. Get system statistics:

```bash
curl http://localhost:5000/stats
```
