import trueskill as ts

# Set parameters for trueskill calculations
SIGMA = ts.SIGMA  # Default sigma value
BETA = SIGMA  # Increase beta to make initial ratings less volatile
TAU = (
    ts.SIGMA / 20
)  # Increase tau to prevent ratings getting "stuck" after a number of matches
DRAW_PROBABILITY = 0.0  # Not possible to draw
MU = 25.0  # Default TrueSkill rating


def ts_setup():
    ts.setup(
        beta=BETA,
        sigma=SIGMA,
        tau=TAU,
        draw_probability=DRAW_PROBABILITY,
    )
