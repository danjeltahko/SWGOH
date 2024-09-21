from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from GAC import calculate_attack_teams

app = FastAPI()

# Mount static files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/calculate")
async def calculate(request: Request):

    # Get the JSON data from the request
    data = await request.json()

    # Extract data from the request
    ally_code = data.get("allyCode")  # str
    min_gear = int(data.get("minGear"))  # int
    mode = data.get("mode")  # str
    user_defense = data.get("userDefense")  # dict
    user_attack = data.get("userAttack")  # dict
    opponent_defense = data.get("opponentDefense")  # dict

    # Create the GAC round object
    gac_round = {
        "opponent": opponent_defense,
        "player": user_defense,
        "used_attack": user_attack,
    }

    # At the moment dummy data
    focus_zone = ["T1", "B1", "B2"]

    # Calculate the attack recommendations
    attack_recommendations = calculate_attack_teams(
        ally_code=ally_code,
        mode=mode,
        gac_round=gac_round,
        min_gear_level=int(min_gear),
        focus_zone=focus_zone,
        debug=False,
    )

    # Return the recommendations as JSON
    return JSONResponse(content={"attackRecommendations": attack_recommendations})
