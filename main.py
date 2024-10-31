from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import http.server
from msal import ConfidentialClientApplication


# Initialize FastAPI app
app = FastAPI()

# Define a request body model
class Request(BaseModel):
    email: str
    key_1: str
    key_2: str
    key_3: str


@app.post("/check")
async def chat(request: Request):
    try:
        app = ConfidentialClientApplication(request.key_1, authority=f"https://login.microsoftonline.com/{request.key_2}", client_credential=request.key_3)
        # Get the access token
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        access_token = result["access_token"]
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json",}

        if "access_token" in result:
           # Access token retrieved successfully
           headers = {"Authorization": "Bearer " + result["access_token"]}
           # Fetch all users
           response = requests.get(f"https://graph.microsoft.com/v1.0/users?$filter=mail eq '{request.email}'", headers=headers,)

        if response.status_code == 200:
           from_container = []
           body_container = []
           users = response.json().get("value", [])
           for user in users:
               user_id = user["id"]
               response = requests.get(f"https://graph.microsoft.com/v1.0/users/{user_id}/messages",headers=headers,)

               if response.status_code == 200:
                  emails = response.json().get("value", [])
                  for email in emails:
                      from_container.append(email["from"])
                      body_container.append(email["body"])
           return {"from" : from_container, "body" : body_container}  
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))


# Root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Check Emails!"}