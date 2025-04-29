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