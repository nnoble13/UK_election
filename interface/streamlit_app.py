import altair as alt
import streamlit as st
import pandas as pd
import numpy as np
from data_to_chart_prep import (
    get_basemap,
    get_election_data,
    merge_dataframes,
    fetch_data_from_api,
    add_scotland_ni_data,
    color_party,
    df_selection_dropbox,
)
from params import *
from io import BytesIO

############################################################################
############_________Sliders sidebar goes here________##############
st.set_page_config(layout="wide")
st.title("2024 UK Election Predictor")
col1, col2 = st.columns([0.5, 0.5], gap="small")

# Title for left sidebar
st.sidebar.subheader(sidebar_title)


# Title for the sliders
st.sidebar.markdown(app_sidebar_description)

conservative_rating = st.sidebar.slider(
    "Conservative Rating", min_value=0, max_value=100, value=25, format="%d%%"
)
labor_party_rating = st.sidebar.slider(
    "Labour Party Rating", min_value=0, max_value=100, value=44, format="%d%%"
)
libdem_party_rating = st.sidebar.slider(
    "Lib Dem Rating", min_value=0, max_value=100, value=10, format="%d%%"
)
other_party_rating = st.sidebar.slider(
    "Other Parties", min_value=0, max_value=100, value=21, format="%d%%"
)

params = {
    "con_poll": conservative_rating / 100,
    "lab_poll": labor_party_rating / 100,
    "lib_poll": libdem_party_rating / 100,
    "oth_poll": other_party_rating / 100,
}

total_params = sum(params.values())
if total_params > 1:
    st.sidebar.error("The sum of all values must be lower than 100%. Please try again.")
    st.stop()

st.sidebar.markdown(disclaimer)
#############################################################################
###########################__Data goes here___###############################
######################____BASE___MAP___DATA____##############################


map_df = get_basemap(url)
scotni_df = add_scotland_ni_data(extra_cols)
data_source = fetch_data_from_api(api_url, params=params, headers=None)
pred_df = get_election_data(data_source)
df = merge_dataframes(scotni_df, pred_df, map_df)

#############################################################################
#######################__shortcut to full text___############################
party_counts = df["winning_party"].value_counts()
max_winning_party = party_counts.idxmax()
max_winning_party_index = parties.index(max_winning_party)
party_full_name = parties_full[max_winning_party_index]

second_winning_party_count = party_counts.iloc[1] if len(party_counts) > 1 else 0
second_winning_party = party_counts.drop(max_winning_party).idxmax()
second_winning_party_index = parties.index(second_winning_party)
second_party_full_name = parties_full[second_winning_party_index]

#############################################################################
###########################__OPTIONAL___##########################
# Display the current values of the sliders
# party_text = f"""
# Conservative Party Rating: {conservative_rating}%

# Labour Party Rating: {labor_party_rating}%

# Lib Dem Party Rating: {libdem_party_rating}%

# Other Parties Rating: {other_party_rating}%
# """

# st.sidebar.markdown(party_text)

####################################################################
#############_________Map gets displayed here________###############
# brush = alt.selection(type="interval")

map = (
    alt.Chart(df)
    .mark_square()
    .encode(
        x=alt.X("q").scale(zero=False).axis(None),
        y=alt.Y("r").scale(zero=False).axis(None),
        color=colours_obj.legend(None),
        size=alt.value(65),
        tooltip=["n:N"],
    )
    .properties(width=440, height=540)
    .configure_axis(grid=False)
    .configure_view(strokeWidth=0)
)

bar_ch = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X("count():Q", title="Total Count"),
        y=alt.Y("winning_party:N", title="Winning Party", axis=None, sort="-x"),
        tooltip=[
            alt.Tooltip("winning_party:N"),
        ],
        color=colours_obj.legend(
            title="Legend",
            orient="bottom",
            columns=5,
            fillColor="white",
            direction="vertical",
        ),
    )
    .properties(
        title="Constituencies Won",
        width=400,
    )
)

###############################################################################
##########_________Displaying info into two columns and below________###########

with col1:
    st.altair_chart(map)


with col2:
    st.header(" ")
    st.altair_chart(bar_ch)

st.markdown(
    f"""
    Based on the polling percentages you've chosen, we predict that
    the **{party_full_name}** will win in **{party_counts.max()}** constituencies, with **{party_counts.max()/party_counts.sum()*100:.2f}%** of the vote,
    followed by the **{second_party_full_name}** with **{party_counts[second_winning_party]}** constituencies with **{second_winning_party_count/party_counts.sum()*100:.2f}%** of the vote."""
)


# Create a download button
download_button = st.download_button(
    label="Download Predictions",
    data=df.to_csv(index=False),
    file_name="prediction.csv",
    key="download_button",
)


st.divider()


###############################################################################
#####################_________CONSTITUENCY SELECTOR________####################

st.subheader("Constituency Selector")
st.markdown(
    """
    Use the dropdown menu below to select a constituency and see the predicted breakdown of votes.
    """
)
# Select the constituency
option = st.selectbox(
    label="Select a constituency",
    options=df["n"],
)

col3, col4 = st.columns([0.5, 0.5], gap="small")


# Pick the value we need
selection_df = df_selection_dropbox(df, option)

# Rename columns, transpose, set column names to votes, and add percentage column
selection_df.columns = ["Conservative", "Labour", "Lib Dem", "Other"]
selection_df = selection_df.T.reset_index()
selection_df.columns = ["Party", "Predicted Votes"]
selection_df["Predicted Percentage"] = (
    selection_df["Predicted Votes"] / selection_df["Predicted Votes"].sum()
) * 100
# Format votes with commas (1,000) and then format % as percentages
formatted_df = selection_df.copy()
formatted_df["Predicted Votes"] = selection_df["Predicted Votes"].apply(
    "{:,.0f}".format
)
formatted_df["Predicted Percentage"] = formatted_df["Predicted Percentage"].apply(
    "{:.1f}%".format
)
# Apply colors to the DF
colored_df = formatted_df.style.apply(color_party, axis=1)
colored_contrast_df = colored_df.applymap(
    lambda x: "color:black" if x else "color:black;"
)


con_winning_party_row = selection_df.loc[selection_df["Predicted Votes"].idxmax()]

with col3:
    st.dataframe(colored_contrast_df, hide_index=True)

dropbox_selection_summary = f"""
    You have chosen **{option}**, which is predicted to be won by the **{con_winning_party_row['Party']}**
    with **{con_winning_party_row['Predicted Votes']:,}** votes or ({con_winning_party_row['Predicted Percentage']:.2f}%).
    """

with col4:
    st.markdown(dropbox_selection_summary)
