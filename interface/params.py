import altair as alt


url = "https://raw.githubusercontent.com/odileeds/hexmaps/gh-pages/maps/uk-constituencies-2019-BBC.hexjson"
api_url = "https://ukelection-image-ne4yelgixa-no.a.run.app/predict"
extra_cols = "https://raw.githubusercontent.com/nnoble13/UK_election/master/interface/Scotland_NI_results.csv"

parties = ["con", "lab", "lib", "oth", "snp", "dup", "sf", "sdlp", "alliance"]
party_colours = [
    "#0087DC",
    "#dc143c",
    "#FAA61A",
    "#005B54",
    "#FDF38E",
    "#D46A4C",
    "#326760",
    "#2AA82C",
    "#F6CB2F",
]
colours_obj = alt.Color(
    "winning_party:N", scale=alt.Scale(domain=parties, range=party_colours)
)
parties_full = [
    "Conservative Party",
    "Labour Party",
    "Liberal Democratic Party",
    "Other Parties",
    "Other Parties",
    "Other Parties",
    "Other Parties",
    "Other Parties",
    "Other Parties",
]

sidebar_title = """Predictions for England and Wales"""
app_sidebar_description = """See how changes in polling \npercentages can affect \nthe outcome of the next election."""
disclaimer = """_Scotland and Northern Ireland are not included in this prediction, and are displayed with 2019 results._
"""
