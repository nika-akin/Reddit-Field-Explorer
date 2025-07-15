
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
import numpy as np
from pyvis.network import Network
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile
import os


st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            width: 550px !important;  /* Change to desired width */
        }
        [data-testid="stSidebarContent"] {
            width: 500px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Load the CSVs
# Comment Data:
@st.cache_data
def load_data():
    discussions_path = "../data/discussions_anon.csv"
    pre_survey_path = "../data/pre_survey_anon.csv"
    post_survey_path = "../data/post_surveys_anon.csv"
    df_discussions = pd.read_csv(discussions_path)
    df_pre = pd.read_csv(pre_survey_path)
    df_post = pd.read_csv(post_survey_path)
    return df_discussions, df_pre, df_post

df_comments, df_pre_survey, df_post_survey = load_data()


# Extract users, topics and subreddits
users_comments = df_comments['ParticipantID'].unique().astype(str)
users_pre = df_pre_survey['ParticipantID'].unique().astype(str)

users = np.intersect1d(users_pre,users_comments)
df_pre_all = df_pre_survey[df_pre_survey['ParticipantID'].isin(users)]

subreddits = df_comments['subreddit'].unique()
topics = df_comments['post_title'].unique()
# Get associated survey topics in right order
topics_survey = ['issue_attitudes_ukraine','issue_attitudes_renewable','issue_attitudes_immigration','issue_attitudes_fur','issue_attitudes_ubi','issue_attitudes_vaccine','issue_attitudes_airbnb','issue_attitudes_gaza','issue_attitudes_sexwork','issue_attitudes_socialmedia','issue_attitudes_healthcare','issue_attitudes_bodycams','issue_attitudes_minwage','issue_attitudes_guns','issue_attitudes_loan','issue_attitudes_deathpenalty','issue_attitudes_climate','issue_attitudes_vegetarian','issue_attitudes_ai','issue_attitudes_gender']


st.title("Discussion Explorer ...")
st.subheader("... for the Reddit Field Experiment")

# Select topic and subreddit via streamlit interface
# Sidebar filters
st.header("Please select a topic and a subreddit in the side bar")
st.sidebar.header("Select a topic and a subreddit")
selected_topic = st.sidebar.selectbox("Select a Topic", topics)
#tx = np.where(topics_survey == selected_topic)
#selected_topic = topics[tx]
selected_subreddit = st.sidebar.selectbox("Select a Subreddit", subreddits)
filtered_df = df_comments[
    (df_comments['post_title'] == selected_topic) &
    (df_comments['subreddit'] == selected_subreddit)
    ]



##################################################################
##  COMMENT TREE PART
##################################################################

with_users = False

st.header("Comment Trees")

st.sidebar.header("Visualization options for comment trees")
map_to_size = ['comment length', 'comment toxicity']
size_map = st.sidebar.selectbox("What should be mapped to node size?", map_to_size)

with_score = st.sidebar.checkbox("Include Vote Score", value=False)



# Create an empty graph
graph = nx.DiGraph()  # DiGraph for directed graphs
userset = filtered_df['ParticipantID'].unique()
if with_users:
    for user in userset:
        graph.add_node(user, color="grey", label=user)

# Iterate through rows and add nodes
for ix, row in filtered_df.iterrows():
    # Get user data from survey for mapping opinions and comment length
    user = row['ParticipantID']
    tx = np.where( topics == row['post_title'] )[0][0]
    topic = topics_survey[tx]
    if size_map == 'comment toxicity':
        size = row['comment_toxicity'] * 50
    else:
        #text = row['text_comment']
        text_len = row['length_comment_char']
        size = 8.0 + text_len/100

    # check if we have the user in the survey and map its opinion
    if user in users_pre:
        opinion = df_pre_all.loc[df_pre_all['ParticipantID'] == user, topic].iloc[0]
        #print(opinion)
        if opinion <= 3:
            rgb_tuple = (1-(opinion-1)/2, 0.2, 0.2)
        else:
            rgb_tuple = (0.2, 0.2, (opinion-4)/2)
        color = f"rgb({int(rgb_tuple[0] * 255)},{int(rgb_tuple[1] * 255)},{int(rgb_tuple[2] * 255)})"
    else:
        rgb_tuple = (0.1, 0.9, 0.1)
        color = f"rgb({int(rgb_tuple[0] * 255)},{int(rgb_tuple[1] * 255)},{int(rgb_tuple[2] * 255)})"

    graph.add_node(row['comment_id'], color=color, size=size, label=user)
    graph.add_edge(row['comment_id'], row['parent_id'])
    if with_users:
        graph.add_edge(row['ParticipantID'], row['comment_id'])
    if with_score:
        score = row['score_comment']
        if score < 0:
            rgb_tuple = (1.0, 0.0, 0.0)
        elif score > 0:
            rgb_tuple = (0.0, 0.0, 1.0)
        else:
            rgb_tuple = (0.0, 0.0, 0.0)
        color = f"rgb({int(rgb_tuple[0] * 255)},{int(rgb_tuple[1] * 255)},{int(rgb_tuple[2] * 255)})"
        size = 1.0#np.abs(score)
        print(row['comment_id'])
        graph.add_node(str(ix), color=color, size=size, label=score)
        graph.add_edge(str(ix), row['comment_id'], weight=score)

net = Network(
    notebook=True,
    height="750px",
    width="100%",
    directed=True,
    bgcolor="#ffffff",
    font_color="black"
    #cdn_resources="in_line"  # Fix for Jupyter display issues
)
# Convert NetworkX graph to Pyvis graph
net.from_nx(graph)

# Show the interactive graph
net.show("interactive_graph.html")

HtmlFile = open("interactive_graph.html", 'r', encoding='utf-8')
source_code = HtmlFile.read()
components.html(source_code, height=800, width=None, scrolling=True)


##################################################################
##  PARTICIPATION PART
##################################################################

st.header("Participation")

st.sidebar.header("Options for participation")
show_hist = ['Comment activity', 'User dropout']
hist_show = st.sidebar.selectbox("What do you want to see?", show_hist)

tx = np.where(topics == selected_topic)[0][0]
#topic = topics_survey[tx]

filtered_df_pre = df_pre_all[df_pre_all['subreddit'] == selected_subreddit]
all_group_users = filtered_df_pre['ParticipantID'].unique().astype(str)
#st.subheader(len(all_group_users))

filtered_df_comments = df_comments[df_comments['post_title'].isin([topics[tx]])]
filtered_df_comments = filtered_df_comments[filtered_df_comments['subreddit'].isin([selected_subreddit])]

active_group_users = filtered_df_comments['ParticipantID'].unique().astype(str)

attsAll = filtered_df_pre[ topics_survey[tx] ]
attsAll = 2 * (attsAll - 1) / 5 - 1

filtered_df_pre_current = filtered_df_pre[filtered_df_pre['ParticipantID'].isin(active_group_users)]
attsAct = filtered_df_pre_current[ topics_survey[tx] ]
attsAct = 2 * (attsAct - 1) / 5 - 1


# user dropout
filtered_df_pre = df_pre_survey[df_pre_survey['subreddit'] == selected_subreddit]
all_group_users_pre = filtered_df_pre['ParticipantID'].unique().astype(str)
#st.subheader(len(all_group_users_pre))


filtered_df_pre_current = filtered_df_pre[filtered_df_pre['ParticipantID'].isin(all_group_users_pre)]
attsAllPre = filtered_df_pre_current[ topics_survey[tx] ]
attsAllPre = 2 * (attsAllPre - 1) / 5 - 1

# engaged_df = filtered_df_comments[filtered_df_comments['root_comment']==0]
# engaged_users = engaged_df['ParticipantID']
# filtered_df_pre = df_pre_all[df_pre_all['ParticipantID'].isin(engaged_users)]
#
# attsEngaged = pd.concat([
#     filtered_df_pre.loc[filtered_df_pre['ParticipantID'] == user, topics_survey[tx]]
#     for user in engaged_users
# ], ignore_index=True)
#
# print(attsEngaged)
#
# attsEngaged = 2 * (attsEngaged - 1) / 5 - 1


data = {
    "Column1": attsAll,
    "Column2": attsAct,
    "Column3": attsAllPre,
}
df = pd.DataFrame(data)

# Compute histogram values for both columns
#bins = np.linspace(-1, 1, 7)
bins = np.array([-1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2])
hist1, bin_edges = np.histogram(df["Column1"], bins=bins)
hist2, _ = np.histogram(df["Column2"], bins=bins)
hist3, _ = np.histogram(df["Column3"], bins=bins)
#hist1 = hist1#/hist1.sum()
#hist2 = hist2#/hist2.sum()

# Define bar width and positions
bar_width = 0.8 * (bin_edges[1] - bin_edges[0])  # Set bar width as a fraction of bin width
bar_positions = bin_edges[:-1] + (bar_width / 2)  # Adjust bar positions

fig, axes = plt.subplots(1, 3, figsize=(18, 4), sharey=False, facecolor="white")
plt.subplots_adjust(wspace=0.3, hspace=0.4)
for ax in axes:
    ax.set_facecolor("white")  # White background for each subplot
    #ax.grid(axis="both", linestyle="-", alpha=0.7, color="gray")
    ax.set_xlabel("Attitude", fontsize=14)
    ax.set_xticks(bins-0.2)
    for spine in ax.spines.values():
        spine.set_visible(True)  # Ensure all spines are visible
        spine.set_edgecolor([0.2,0.2,0.2])  # Set the frame color
        spine.set_linewidth(1.5)  # Adjust the frame thickness

edge_width = 0.0
bar_alpha = 0.8

if hist_show == 'Comment activity':
    st.subheader("Active users and participation rate in")
    st.subheader(f"{selected_subreddit} on {topics_survey[tx]}")
    st.subheader("\n")

    axes[0].bar(bar_positions, hist1, width=bar_width, label="All", color="blue",alpha = bar_alpha, edgecolor="white",linewidth=edge_width)
    # Add titles and labels
    axes[0].set_title("All users", fontsize=24)
    axes[0].set_ylabel("Number of Users", fontsize=18)

    axes[1].set_title("Active users", fontsize=24)
    axes[1].bar(bar_positions, hist2, width=bar_width, label="All", color="red",alpha = bar_alpha, edgecolor="white",linewidth=edge_width)
    axes[1].set_ylabel("Number of Users", fontsize=18)

    axes[2].set_title("Participation ratio", fontsize=24)
    axes[2].bar(bar_positions, hist2/hist1, width=bar_width, label="All", color="green",alpha = bar_alpha, edgecolor="white",linewidth=edge_width)
    axes[2].set_ylabel("Ratio of Active Users", fontsize=18)

elif hist_show == 'User dropout':
    st.subheader(f"Dropout in {selected_subreddit}")
    st.subheader(f"Attitude distributions for {topics_survey[tx]}")
    st.subheader("\n")

    axes[0].set_title("Survey participants", fontsize=24)
    axes[0].bar(bar_positions, hist3-hist1, width=bar_width, label="All", color="blue",alpha = bar_alpha, edgecolor="white",linewidth=edge_width)
    axes[0].set_ylabel("User Number", fontsize=18)

    axes[1].set_title("Discussion participants", fontsize=24)
    axes[1].bar(bar_positions, hist1, width=bar_width, label="All", color="red",alpha = bar_alpha, edgecolor="white",linewidth=edge_width)
    axes[1].set_ylabel("User Number", fontsize=18)

    axes[2].set_title("Dropout rate", fontsize=24)
    axes[2].bar(bar_positions, (hist3-hist1)/hist3, width=bar_width, label="All", color="green",alpha = bar_alpha, edgecolor="white",linewidth=edge_width)
    axes[2].set_ylabel("Dropout rate", fontsize=18)


st.pyplot(fig)


##################################################################
##  OPINION EVOLUTION PART
##
## code developed in "regression and opinion change.ipynb"
##################################################################

st.header("Projected attitude change")

tx = np.where(topics == selected_topic)[0][0]
topic = topics_survey[tx]

filtered_df_pre = df_pre_all[df_pre_all['subreddit'] == selected_subreddit]
filtered_df_post = df_post_survey[df_post_survey['subreddit'] == selected_subreddit]
filtered_df_post_valid = filtered_df_post.copy()
filtered_df_post_valid = filtered_df_post_valid.dropna(subset=[topic])

valid_users = filtered_df_post_valid['ParticipantID'].unique().astype(str)
valid_users = np.intersect1d(users, valid_users)

filtered_df_pre_valid = filtered_df_pre[filtered_df_pre['ParticipantID'].isin(valid_users)]

# Merge pre and post DataFrames on 'ParticipantID'
merged_df = filtered_df_pre_valid[['ParticipantID', topic]].merge(
    filtered_df_post_valid[['ParticipantID', topic]],
    on='ParticipantID',
    how='inner',  # Ensures only matching participants are considered
    suffixes=('_pre', '_post')  # Differentiate columns
)

# Extract aligned pre and post values
attsPre = merged_df[f"{topic}_pre"].values
attsPost = merged_df[f"{topic}_post"].values

transition_matrix = np.zeros((6, 6))
for ax,a in enumerate(attsPre):
    b = attsPost[ax]
    transition_matrix[int(a)-1, int(b)-1] += 1

row_sums = transition_matrix.sum(axis=1, keepdims=True)
transition_matrix = np.divide(transition_matrix, row_sums, where=row_sums != 0)

bins = np.array([-1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2])
attsPreN = 2*(attsPre-1)/5-1
attsPostN = 2*(attsPost-1)/5-1
histPre, bin_edges = np.histogram(attsPreN, bins=bins)
histPost, _ = np.histogram(attsPostN, bins=bins)


import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time

# UI components
st.title("Opinion Dynamics Visualization")

step = st.slider("Number of steps", 1, 50, 50)
animate = st.checkbox("Animate step-by-step")

bins_labels = ['1', '2', '3', '4', '5', '6']

# Normalize distributions
initial_distribution = histPre / histPre.sum()
empirical_post_distribution = histPost / histPost.sum()

# Animate if checked
if animate:
    progress_text = st.empty()
    chart_placeholder = st.empty()
    for s in range(1, step + 1):
        progress_text.write(f"Step {s}")
        projected_dist = initial_distribution @ np.linalg.matrix_power(transition_matrix, s)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(bins_labels, projected_dist, color='orange')
        ax.set_ylim(0, max(initial_distribution.max(), empirical_post_distribution.max()) * 1.1)
        ax.set_title(f'Projected Distribution (Step {s})')
        ax.set_ylabel('Probability')
        chart_placeholder.pyplot(fig)
        time.sleep(0.3)
else:
    # Compute single-step projection
    projected_dist = initial_distribution @ np.linalg.matrix_power(transition_matrix, step)

    # Static bar charts
    fig, axs = plt.subplots(1, 3, figsize=(18, 4), sharey=True)
    axs[0].bar(bins_labels, initial_distribution, color='skyblue')
    axs[0].set_title('Initial (Pre) Distribution')
    axs[0].set_ylabel('Probability')

    axs[2].bar(bins_labels, projected_dist, color='orange')
    axs[2].set_title(f'Projected Distribution ({step} steps)')

    axs[1].bar(bins_labels, empirical_post_distribution, color='green')
    axs[1].set_title('Empirical Post Distribution')

    st.pyplot(fig)

# Plot transition matrix
fig2, ax2 = plt.subplots(figsize=(4, 4),constrained_layout=True)
sns.heatmap(transition_matrix, annot=True, fmt=".2f", cmap="viridis", ax=ax2,
            xticklabels=bins_labels, yticklabels=bins_labels)
ax2.set_title("Transition Matrix")
ax2.set_xlabel("To")
ax2.set_ylabel("From")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.pyplot(fig2)

#st.pyplot(fig2)












# # Normalize histPre to make it a probability distribution
# pre_distribution = histPre / histPre.sum()
# post_distribution = histPost / histPost.sum()
# # Raise the transition matrix to the 50th power
# transition_matrix_50 = np.linalg.matrix_power(transition_matrix, 50)
# # Apply the matrix to the initial distribution
# future_distribution = pre_distribution @ transition_matrix_50

#
# st.write(histPre)
#
# # Define bar width and positions
# bar_width = 0.8 * (bin_edges[1] - bin_edges[0])  # Set bar width as a fraction of bin width
# bar_positions = bin_edges[:-1] + (bar_width / 2)  # Adjust bar positions
# edge_width = 0.0
# bar_alpha = 0.8
#
# fig, axes = plt.subplots(1, 3, figsize=(18, 4), sharey=False, facecolor="white")
# plt.subplots_adjust(wspace=0.3, hspace=0.4)
# for ax in axes:
#     ax.set_facecolor("white")  # White background for each subplot
#     #ax.grid(axis="both", linestyle="-", alpha=0.7, color="gray")
#     ax.set_xlabel("Attitude", fontsize=14)
#     ax.set_xticks(bins-0.2)
#     for spine in ax.spines.values():
#         spine.set_visible(True)  # Ensure all spines are visible
#         spine.set_edgecolor([0.2,0.2,0.2])  # Set the frame color
#         spine.set_linewidth(1.5)  # Adjust the frame thickness
#
# axes[0].bar(bar_positions, pre_distribution, width=bar_width, label="All", color="blue",alpha = bar_alpha, edgecolor="white",linewidth=edge_width)
# # Add titles and labels
# axes[0].set_title("All users", fontsize=24)
# axes[0].set_ylabel("Number of Users", fontsize=18)
#
# axes[1].bar(bar_positions, post_distribution, width=bar_width, label="All", color="blue",alpha = bar_alpha, edgecolor="white",linewidth=edge_width)
# # Add titles and labels
# axes[1].set_title("All users", fontsize=24)
# axes[1].set_ylabel("Number of Users", fontsize=18)
#
# axes[2].bar(bar_positions, future_distribution, width=bar_width, label="All", color="blue",alpha = bar_alpha, edgecolor="white",linewidth=edge_width)
# # Add titles and labels
# axes[2].set_title("All users", fontsize=24)
# axes[2].set_ylabel("Number of Users", fontsize=18)
#
# st.pyplot(fig)
# #st.text(transition_matrix)
#
# fig, ax = plt.subplots(figsize=(8, 6))
# sns.heatmap(transition_matrix, annot=True, cmap="Blues", fmt=".2f",
#             xticklabels=[1, 2, 3, 4, 5, 6], yticklabels=[1, 2, 3, 4, 5, 6])
# ax.set_xlabel("Post-Attitude")
# ax.set_ylabel("Pre-Attitude")
# ax.set_title("Transition Matrix Heatmap")
# #plt.tight_layout()
# st.pyplot(fig)
