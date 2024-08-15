# Building Limit API

## Overview

This is a FastAPI-based backend service that manages building limits and height plateaus for different projects. It can create, update, delete, and retrieve data for building limits, height plateaus, and their associated splits.

## Features

- Create a new project with building limits and height plateaus.
- Update existing projects.
- Delete a project and all associated data.
- Retrieve building limits, height plateaus, and splits for a project.

## Setup

### Requirements

- Python (built with 3.12)
- Packages in requirements.txt
- Docker (for containerized deployment)

### Running Locally

### Clone the repository
   ```bash
   git clone https://github.com/amir-hojjati/BuildingAPI.git
   cd BuildingAPI

### Create a virtual environment:
    python3 -m venv venv
    source venv/bin/activate

### Install dependencies:
    pip install -r requirements.txt

### Set up environment variables:
Set the conn_str as environment variable to access production postgres database. sqlite can be used for local tests, but a postgres instance on [Render](https://render.com/) is deployed for production.
```bash    
conn_str=postgresql://user:password@localhost/dbname
```

### Run the application:
You can run the app/main.py directly for test purposes. Alternatively:
```bash    
uvicorn app.main:app --host 'localhost' --port 8000 --reload
```
### Running tests:
The test cases do not cover all possible cases, but demonstrate several examples of the type of cases that should be tested. It could benefit from additional tests.
```bash
pytest ./tests/
```

### Running with Docker
You can use Docker to build and start the containers:
```bash
docker build .
```

### Access the application:

The API (deployed on [Render](https://render.com/)) is publicly available at: [https://buildingapi-0jnu.onrender.com/](https://buildingapi-0jnu.onrender.com/) (use as base url, no api key required for now)

Swagger UI is also available at [https://buildingapi-0jnu.onrender.com/docs](https://buildingapi-0jnu.onrender.com/docs), which is useful for testing the API through a UI.

This is a free instance, and will spin down after a period of inactivity, which can delay initial requests by 50 seconds or more. The database instance will also be suspended after 3 days of inactivity (and will be deleted after 30 days) and may need reactivation (but it's free! Contact me it it's been suspended.).

### API Endpoints

POST /create-project: Creates a new project with the provided building limits (Geojson, required) and height plateus (Geojson, required), calculates the splits, and stores everything. Every project automatically starts with version 1. Use the contents of "sample.json" as input to quickly test it. After that, the result of "GET /building-limits/" or "GET /height-plateaus" or their combination can be directly used as input to "PUT /update-project".

PUT /update-project: Update an existing project with a new building limit or new height plateaus, or both. Normally, the user needs to choose a project, and fetch the existing version of height_plateaus and building_limits for that project using GET /building-limits or GET /height-plateaus (that include a version number), make modification to either of them or to both, and send back the modified entity to the endpoint (version will be incremented automatically, so no need to change it).

DELETE /delete-project: Delete a project and all its data.

GET /building-limits/{project_id}: Retrieve versioned building limits for a project.

GET /height-plateaus/{project_id}: Retrieve versioned height plateaus for a project.

GET /split-building-limits/{project_id}: Retrieve split building limits for a project.


### Assumptions
- The height plateaus should at least cover the building limit area, with no gaps. They can be bigger, in which case: area(building_limit) < sum(area(heigh_plateaus)) , but they shouldn’t be smaller.


- There can be multiple building limits and multiple height plateaus.


- There shouldn’t be an overlap between height plateaus. If there are, respond with error.


- Concurrency will be handled using optimistic locking. Read is always permissible, update is permissible if there was no change since last read.


- Users are part of a shared workspace where they can collaborate on different projects, by creating new projects or updating existing ones. Conflicts may arise during collaborative work on existing projects. User authentication is assumed to be out of scope for this assignment.
