

# SWGOH GAC PROJECT

This project is split up in three steps.

1. Scrape the latest available GAC Seasons
2. FastAPI Web App, for choosing def & attack
3. See best possible fights with what ´´´user´´´ has left to use.

## Scrape GAC Seasons

1. Get latest GAC Season urls.
2. Get all available characters from the API.
3. Get all counters for each team(leader).
4. Save that seasons data to json file.

## FastAPI Web App

* Get users characters from ALLY_ID from API.
* Remove the characters from that list with those in def.

## Get Recommenden teams to use for each team

1. Go through each opponents def and find all the counters.
2. Calculate the best teams to use for each def setup.
3. Return the best team to use for each def setup.

4. BONUS: Add opponents ally_code, to see what he possible has behind wall.
or maybe scrape the website to see what he/she usually puts in defense.

