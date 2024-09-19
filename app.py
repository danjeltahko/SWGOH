from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

from GAC import calculate_attack_teams


app = FastAPI()

# Mount static files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/submit", response_class=HTMLResponse)
async def submit_form(request: Request):
    form_data = await request.form()
    return templates.TemplateResponse(
        "result.html", {"request": request, "data": form_data}
    )


@app.post("/calculate")
async def calculate(request: Request):

    data = await request.json()

    # Extract data from the request
    ally_code = data.get("allyCode")  # str
    min_gear = int(data.get("minGear"))  # str
    mode = data.get("mode")
    rank = data.get("rank")
    user_defense = data.get("userDefense")
    user_attack = data.get("userAttack")
    opponent_defense = data.get("opponentDefense")

    gac_round = {
        "opponent": opponent_defense,
        "player": user_defense,
        "used_attack": user_attack,
    }
    """
    Used attack is none
    """
    focus_zone = ["T1", "B1", "B2"]

    print(gac_round)

    attack_recommendations = calculate_attack_teams(
        ally_code=ally_code,
        gac_season="Season_55",
        gac_round=gac_round,
        min_gear_level=int(min_gear),
        focus_zone=focus_zone,
    )

    # Return the recommendations as JSON
    return JSONResponse(content={"attackRecommendations": attack_recommendations})


"""
Ally code: 454-998-525

My Defense:

    TEAM 1: Jabba | Krrsantan | Boussh
    TEAM 2: Qui-Gon | Anakin | Ki-Adi-Mundi
    TEAM 3: Shaak Ti | Echo | ARC
    TEAM 4: Hera | Kanan | Rex
    TEAM 5: Finn | Finn | Poe
"""
