# Star Wars Galaxy of Hereoes

This project is a Grand Arena Championship planner to calculate the best teams to use against your opponents defense. It uses the same algorithm to solve sudoku, which can make it a bit slow somethimes, considering the algortihm is used for exact one possible solution. And in this case it depends on your available characters, so sometime it isn't even possible to use an attack team against every opponents defense team.


## Usage
Start with cloning this repository and then install all the required python libraries.
```bash
pip install -r requirements.txt
```

When everything is installed, start the fastapi server and open up local host in a browser.
```bash
fastapi dev app.py
```

## Upcoming TODOS:

### Front End
- [ ] Add button for collapse zones in opponent defense
- [ ] Create checkbox for un/focus opponent zones
- [ ] Better way to have all available characters stored. Api would be nice
- [ ] Add (no gl) button for defense teams, so GLS wont be recommended for that team
- [ ] Maybe even add a threshold for some teams, so it will pick other teams.

### Main Program
- [ ] Add so depending on MODE, will get the corresponding data with counters.

### Scraping
- [ ] Scrape all the pages for counters.
- [ ] Calculate the the most seen counters, and base the win rate based on that.

### Automation
- [ ] Checking new characters every day, deploy webapp with ned characters if found
- [ ] Check for new counters data, deploy webapp with new counters if found

