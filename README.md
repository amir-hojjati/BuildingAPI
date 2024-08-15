# Project API

## Overview

This is a FastAPI-based backend service that manages building limits and height plateaus for different projects. It can create, update, delete, and retrieve data for building limits, height plateaus, and their associated splits.

## Features

- Create a new project with building limits and height plateaus.
- Update existing projects.
- Delete a project and all associated data.
- Retrieve building limits, height plateaus, and splits for a project.

## Setup

### Requirements

- Python 3.9
- Docker (for containerized deployment)

### Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/project-api.git
   cd project-api

### Create a virtual environment:
    python3 -m venv venv
    source venv/bin/activate

### Install dependencies:
    pip install -r requirements.txt

### Set up environment variables:
Set the conn_str environment variable, or create a .env file in the root of the project with the following content: 
```bash    
conn_str=postgresql://user:password@localhost/dbname
```

### Run the application:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

### Running test:
```bash
pytest ./tests/
```

### Running with Docker
You can use Docker to build and start the containers:
```bash
docker build .
```

### Access the application:

The API will be available at http://localhost:8000.

### API Endpoints

POST /create-project: Create a new project with building limits and height plateus.

PUT /update-project: Update an existing project with a new building limit or height plateaus, or both.

DELETE /delete-project: Delete a project and all its data.

GET /building-limits/{project_id}: Retrieve building limits for a project.

GET /height-plateaus/{project_id}: Retrieve height plateaus for a project.

GET /split-building-limits/{project_id}: Retrieve split building limits for a project.


### Assumptions
- The height plateaus should at least cover the building limit area. They can be bigger in which case: area(building_limit) < sum(area(heigh_plateaus)) , but they shouldn’t be smaller.


- There can be multiple building limits and multiple height plateaus.


- There shouldn’t be an overlap and/or gaps between height plateaus. If there are, respond with error.


- Concurrency will be handled using optimistic locking. Read is always permissible, update is permissible if there was no change since last read.


- Users are part of a shared workspace where they can collaborate on different projects, by creating new projects or updating existing ones. Conflicts may arise during collaborative work on existing projects. User authentication is assumed to be out of scope for this assignment.
