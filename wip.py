import streamlit as st
import pandas as pd
import networkx as nx
import numpy as np
from pyvis.network import Network
import tempfile
import os

# Load the CSV files
@st.cache_data
def load_data():
    discussions_path = "../data/discussions_collab.csv"
    pre_survey_path = "../data/pre_survey_anon.csv"
    df_discussions = pd.read_csv(discussions_path)
    df_pre_survey = pd.read_csv(pre_survey_path)
    return df_discussions, df_pre_survey

df, df_pre_all = load_data()

# Extract unique values for dropdowns
users = df['ParticipantID'].unique()
subreddits = df['subreddit'].unique()
topics = df['post_title'].unique().astype(str)
topics_survey = [
    'issue_attitudes_ukraine', 'issue_attitudes_renewable', 'issue_attitudes_immigration',
    'issue_attitudes_fur', 'issue_attitudes_ubi', 'issue_attitudes_vaccine', 'issue_attitudes_airbnb',
    'issue_attitudes_gaza', 'issue_attitudes_sexwork', 'issue_attitudes_socialmedia',
    'issue_attitudes_healthcare', 'issue_attitudes_bodycams', 'issue_attitudes_minwage',
    'issue_attitudes_guns', 'issue_attitudes_loan', 'issue_attitudes_deathpenalty',
    'issue_attitudes_climate', 'issue_attitudes_vegetarian', 'issue_attitudes_ai',
    'issue_attitudes_gender'
]

# Sidebar filters
st.sidebar.header("Filters")
selected_topic = st.sidebar.selectbox("Select a Topic", topics)
selected_subreddit = st.sidebar.selectbox("Select a Subreddit", subreddits)

# Filter the dataframe based on user input
filtered_df = df[
    (df['post_title'] == selected_topic) &
    (df['subreddit'] == selected_subreddit)
    ]

# Build the network graph
with_users = st.sidebar.checkbox("Include Users in Graph", value=False)

def create_graph(filtered_df, with_users):
    graph = nx.DiGraph()
    users_pre = df_pre_all['ParticipantID'].unique().astype(str)
    for ix, row in filtered_df.iterrows():
        user = row['ParticipantID']
        tx = np.where(topics == row['post_title'])[0][0]
        text = row['text_comment']
        size = 5.0 + len(text) / 100
        topic = topics_survey[tx]
        if user in users_pre:
            opinion = df_pre_all.loc[df_pre_all['ParticipantID'] == user, topic].iloc[0]
            if opinion <= 3:
                rgb_tuple = ((opinion - 1) / 2, 0.2, 0.2)
            else:
                rgb_tuple = (0.2, 0.2, (opinion - 4) / 2)
            color = f"rgb({int(rgb_tuple[0] * 255)}, {int(rgb_tuple[1] * 255)}, {int(rgb_tuple[2] * 255)})"
        else:
            color = "rgb(25, 225, 25)"
        graph.add_node(row['comment_id'], color=color, size=size, label=user)
        if with_users:
            graph.add_node(user, color="grey", label=user)
            graph.add_edge(user, row['comment_id'])
        graph.add_edge(row['comment_id'], row['parent_id'])
    return graph

graph = create_graph(filtered_df, with_users)

# Render the graph using PyVis
net = Network(
    height="750px",
    width="100%",
    directed=True,
    bgcolor="#ffffff",
    font_color="black"
)
net.from_nx(graph)

# Generate temporary file to display the graph
with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
    net.show(temp_file.name)
    temp_file_path = temp_file.name

# Embed the graph in Streamlit
st.subheader("Interactive Network Graph")
with open(temp_file_path, "r", encoding="utf-8") as f:
    graph_html = f.read()

st.components.v1.html(graph_html, height=750, scrolling=True)

# Clean up the temporary file
os.unlink(temp_file_path)
