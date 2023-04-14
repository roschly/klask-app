# klask-app
A streamlit app for keeping track of matches and ranking players of private Klask tournaments, e.g. in the office.

Online demo version:
https://roschly-klask-app-app-gc20lp.streamlit.app/

## How to use
Clone this repo, pip install dependencies and type the following in a commandline:
`streamlit run app.py`

### important configs
A `config.yaml` contains:
- `match_folder`: path to folder containing matches
- `players`: path to yaml file containing a list of available players

If neither of these exists, the app will bootstrap on start.

### bootstrapping
If neither `players` nor `match_folder` exist, the app will bootstrap with predefined names and random matches.
If your app has bootstrapped, just stop it, delete the matches folder and replace the players with your own and reboot.

### less important configs
`hall_of_fame`: a path to a .csv file containing past champions and the top 3 seeding.
This is specific for the way we run tournaments, and not necessary:
A longer period (approx 3 weeks) of qualifying play. Anyone can challenge anyone else.
Tournament (approx 1 week) bracket, with people being matched according to their score.

Tournament score it kept separate from this app.
