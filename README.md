# SIT (Simple Issue Tracker)
===============


## Setting up development environment

The development environment can be setup either like a pythonista
with the usual python module setup, or like a docker user.

## REDIS SERVER & POSTGRESSQL is required

### The pythonista way

Ensure that you have an updated version of pip

```
pip --version
```
Should atleast be 1.5.4

If pip version is less than 1.5.4 upgrade it
```
pip install -U pip
```

This will install latest pip

Ensure that you are in virtualenv
if not install virtual env
```
sudo pip install virtualenv
```
This will make install all dependencies to the virtualenv
not on your root

From the module folder install the dependencies. This also installs
the module itself in a very pythonic way.

```
pip install -r requirements.txt
```
## NOTE
Postgresql must be installed.
if not, install postgres and its server-side extensions

Run app by 
```
python manage.py runserver
```
### 

## ADD USER (POST)
All fields are compulsory
```
FIELDS MANDATORY
	username
	password
	first_name
	last_name
	email
```
In response 
```{
    "username": "hriks",
    "first_name": "Amit",
    "last_name": "Gupta",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNhYXJhIiwicGFzc3dvcmQiOiJocmlrczkyMzIifQ.sR4hapJk1jMarAL88hZMqfOhxFmpU8eWoiH-yFnE_Kw",
    "email": "hriks@outlook.com",
    "status_code": 201,
    "success_message": "Request processed successfully!"
}
```
Note access_token for futher authentication use

## UPDATE USER (POST)
```
FIELDS MANDATORY
	accesstoken

UPDATEABLE FIELDS(OPTIONAL)
	email
	password
```
In response 
```{
    "username": "hrik",
    "first_name": "Amit",
    "last_name": "Gupta",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImhyaWsiLCJwYXNzd29yZCI6ImhyaWtzOTIzMiJ9.f_964XOleYoiDAU7QaIa9rmd0fSYx1B2okai9woJgSg",
    "email": "hriks@outlook.com",
    "status_code": 200,
    "success_message": "Request processed successfully!"
}
```
In Case password change
You will get new access_token

## ADD ISSUE (POST)
```
FIELDS MANDATORY
	accesstoken
	title
	description
	assignee

```
In response 
```
{
    "title": "test issue",
    "description": "Some description here",
    "assignee": "saara",
    "created_by": "hrik",
    "status": "open",
    "reference_no": "SIT8353",
    "status_code": 201,
    "success_message": "Request processed successfully!"
}
```
Note reference_no for further crud operations

## UPDATE ISSUE (POST)
```
FIELDS MANDATORY
	accesstoken

UPDATEABLE FIELDS
	status
	assignee

```
In response
```
{
    "title": "test issue",
    "description": "Some description here",
    "assignee": "hrikss",
    "created_by": "hrik",
    "status": "closed",
    "reference_no": "SIT8353",
    "status_code": 200,
    "success_message": "Request processed successfully!"
}
```
## DELETE ISSUE (DELETE)
```
FIELDS MANDATORY
	accesstoken
	reference_no
```
In response
```
{
    "status_code": 200,
    "success_message": "Request processed successfully!",
    "issues": "SIT8844 deleted successfully"
}
```

## GET ALL ISSUE (GET)
```
FIELDS MANDATORY
	accesstoken

FILTERS FIELDS(OPTIONAL)
	assignee
	status

ALL data in query params
```
In response
```
{
    "status_code": 200,
    "success_message": "Request processed successfully!",
    "issues": [
        {
            "title": "test issue",
            "description": "Some Descriptions here",
            "assignee": "hrikss",
            "created_by": "hrik",
            "status": "closed",
            "reference_no": "SIT8353"
        },
        {
            "title": "test issue",
            "description": "Some Descriptions here",
            "assignee": "hrikss",
            "created_by": "hrik",
            "status": "open",
            "reference_no": "SIT0037"
        },
        {
            "title": "First issues",
            "description": "Some Descriptions here",
            "assignee": "hrikss",
            "created_by": "hrik",
            "status": "open",
            "reference_no": "SIT6605"
        }
    ]
}
```

## ERROR CODES
```
    INVN000 => Internal Server Error.
    INVN001 => Access token not provided.
    INVN002 => Invalid accesstoken provided.
    INVN003 => User doesnot exists.
    INVN004 => Incorrect fields provided.
    INVN005 => Mandatory fields are missing.
    INVN006 => User already exists with this username.
    INVN007 => Assignee not found with the username provided. Please verify username
    INVN008 => Requestor is not the owner for this issue.
    INVN009 => Issue could not be raised as similar issue was found.
    INVN010 => Issue DoesNotExist.
```