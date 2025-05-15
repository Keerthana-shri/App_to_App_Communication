# App_to_App_Communication
## Installation
1. Clone the repository

    `git clone https://github.com/Keerthana-shri/App_to_App_Communication`

    `cd App_to_App_Communication`

2. From the root directory of the project, activate the shell after installing pipenv.

   `pip install pipenv`

   `pipenv install`

   `pipenv shell`


## Run the application

Change directory to src

`cd src`

Run the application with:

`uvicorn server:app --reload`

## Set up pre-commit hooks for linting

`pre-commit install`


# Successful API responses on API Key CRUD operations

## Creating API Key:
![alt text](example_images/image.png)

## Duplication of API Key creation is restricted when status is active/revoked
![alt text](example_images/image-1.png)

## Revoking API Key in the POST method, if the status is inactive
![alt text](example_images/image-6.png)

## Invalid messages
![alt text](example_images/image-2.png)

![alt text](example_images/image-3.png)

![alt text](example_images/image-8.png)

## Updating API Key details
![alt text](example_images/image-4.png)

## If status of any API key is "revoked" then updating it is not allowed
![alt text](example_images/image-9.png)

## Get API Key (Because the updated expire date is past the current date, the status has automatically changed to inactive)
![alt text](example_images/image-5.png)

## Deleting API Key
![alt text](example_images/image-7.png)
