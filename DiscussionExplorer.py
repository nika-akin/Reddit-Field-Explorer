import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
import numpy as np
from pyvis.network import Network
import matplotlib.pyplot as plt
import seaborn as sns
import time
import tempfile
import os

##################################################################
##  Visual Settings

st.set_page_config(layout="wide", page_title="Reddit Opinion Dynamics")

# Custom CSS for Responsive and Desktop + Mobile Optimization
st.markdown("""
    <style>
    /* Title and subtitle spacing */
    h1 {
        margin-bottom: 0.75rem !important;
    }
    h2, h3 {
        margin-top: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* General spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Expander-style sidebar panel */
    .custom-control-panel {
        background-color: #f7f7f9;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 2rem;
    }

    /* Tabs visual polish */
    .stTabs [data-baseweb="tab-list"] {
        flex-wrap: wrap;
        gap: 8px;
        justify-content: start;
    }

    .stTabs [data-baseweb="tab"] {
        border: 2px solid transparent;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 1.1rem;
        font-weight: 500;
        background-color: #f0f2f6;
        color: #333;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        border-color: #66a3ff;
        background-color: #e6f0ff;
    }

    .stTabs [aria-selected="true"] {
        border-color: #1a73e8;
        background-color: #e6f0ff;
        font-weight: 700;
        color: #1a73e8;
    }

    /* Markdown content spacing */
    div[data-testid="stMarkdownContainer"] p {
        font-size: 1.05rem;
        line-height: 1.6;
        margin-bottom: 0.75rem;
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 6px 12px;
            font-size: 1rem;
        }

        .custom-control-panel {
            padding: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)







##################################################################
##  Load the data

@st.cache_data
def load_data():
    discussions_path = "data/discussions_anon.csv"
    pre_survey_path = "data/pre_survey_anon.csv"
    post_survey_path = "data/post_surveys_anon.csv"
    df_discussions = pd.read_csv(discussions_path)
    df_pre = pd.read_csv(pre_survey_path)
    df_post = pd.read_csv(post_survey_path)
    return df_discussions, df_pre, df_post

df_comments, df_pre_survey, df_post_survey = load_data()

subreddits = df_comments['subreddit'].unique()
topics = df_comments['post_title'].unique()
# Get associated survey topics in right order
topics_survey = ['issue_attitudes_ukraine','issue_attitudes_renewable','issue_attitudes_immigration','issue_attitudes_fur','issue_attitudes_ubi','issue_attitudes_vaccine','issue_attitudes_airbnb','issue_attitudes_gaza','issue_attitudes_sexwork','issue_attitudes_socialmedia','issue_attitudes_healthcare','issue_attitudes_bodycams','issue_attitudes_minwage','issue_attitudes_guns','issue_attitudes_loan','issue_attitudes_deathpenalty','issue_attitudes_climate','issue_attitudes_vegetarian','issue_attitudes_ai','issue_attitudes_gender']





st.title("🧠 Reddit Opinion Dynamics Explorer")

# Sidebar: Global Controls
#st.sidebar.header("🔧 Experiment Controls")
#selected_subreddits = st.sidebar.multiselect("Select Subreddit", subreddits,default=subreddits[0])
#selected_topic = st.sidebar.radio("Select Topic", topics)

# --- Layout: Sidebar-style controls + Tabs ---
col1, col2 = st.columns([1, 3])  # Left column (smaller) for controls, right column (larger) for content

# Left column (controls)
with col1:
    st.markdown("### 🔧 Experiment Controls")
    selected_subreddits = st.multiselect("Choose Subreddit(s)", subreddits, default=subreddits[0])
    selected_topic = st.radio("Choose Topic", topics)

# Right column (main content)
with col2:


# Main Tabs
     tab1, tab2, tab3 = st.tabs(["🌳 Comment Trees", "📊 Participation", "📈 Opinion Dynamics"])


##################################################################
##  Comment trees

with tab1:
    st.markdown("""
    Explore full Reddit conversation trees for the selected topic and subreddit(s).  
    Each tree reveals how a discussion unfolded: who replied to whom, and how active each branch became.  
    
    **Node colors represent users' attitudes** (measured in the pre-survey):  
    - 🔴 Red = more negative opinions  
    - 🔵 Blue = more positive opinions
    
    You can compare multiple subreddits side by side.
    
    🔧 **Advanced options** let you:
    - Scale node sizes by **comment length** or **toxicity**
    - Include **vote scores** to assess comment reception
    """)

    st.markdown("---")
    st.markdown("## 🔧 Comment Settings")
    map_to_size = ['comment length', 'comment toxicity']
    size_map = st.selectbox("What should be mapped to node size?", map_to_size)
    with_score = st.checkbox("Include Vote Score", value=False)
    st.markdown("---")
    st.subheader(f"Comment Tree for Post: {selected_topic}")
    # This is to avoid an error message if no subreddit is selected
    if len(selected_subreddits) == 0:
        selected_subreddits = [subreddits[0]]
    cols = st.columns(len(selected_subreddits))

    # Loop through selected topics
    for i, subreddit in enumerate(selected_subreddits):
        # Call your function to render comment tree plot/data
        with cols[i]:
            #subreddit = selected_subreddits[i]
            st.subheader(f"{subreddit}")
            # Filter data for this topic and subreddit
            filtered_df_comments = df_comments[
                (df_comments['post_title'] == selected_topic) &
                (df_comments['subreddit'] == subreddit)
                ]
            if filtered_df_comments.empty:
                st.write(f"No comments found for {subreddit} on topic {selected_topic}.")
                continue

            # Create graph
            graph = nx.DiGraph()
            users_comments = filtered_df_comments['ParticipantID'].unique().astype(str)
            users_pre = df_pre_survey['ParticipantID'].unique().astype(str)
            users = np.intersect1d(users_pre,users_comments)
            filtered_df_pre = df_pre_survey[df_pre_survey['ParticipantID'].isin(users)]

            for ix, row in filtered_df_comments.iterrows():
                user = row['ParticipantID']
                # Map topic to survey name (if needed)
                tx = np.where(topics == row['post_title'])[0][0]
                topic_survey = topics_survey[tx]
                # Size mapping
                size = row['comment_toxicity'] * 50 if size_map == 'comment toxicity' else 8.0 + row['length_comment_char'] / 100

                # Color mapping by opinion
                if user in users:
                    opinion = filtered_df_pre.loc[filtered_df_pre['ParticipantID'] == user, topic_survey].iloc[0]
                    if opinion <= 3:
                        rgb = (1 - (opinion - 1) / 2, 0.2, 0.2)
                    else:
                        rgb = (0.2, 0.2, (opinion - 4) / 2)
                else:
                    rgb = (0.1, 0.9, 0.1)
                color = f"rgb({int(rgb[0]*255)},{int(rgb[1]*255)},{int(rgb[2]*255)})"

                # Add comment node and edges
                graph.add_node(row['comment_id'], color=color, size=size, label=user)
                graph.add_edge(row['comment_id'], row['parent_id'])

                # Include vote scores if requested
                if with_score:
                    score = row['score_comment']
                    score_rgb = (1.0, 0.0, 0.0) if score < 0 else (0.0, 0.0, 1.0) if score > 0 else (0.0, 0.0, 0.0)
                    score_color = f"rgb({int(score_rgb[0]*255)},{int(score_rgb[1]*255)},{int(score_rgb[2]*255)})"
                    graph.add_node(f"score_{ix}", color=score_color, size=1.0, label=str(score))
                    graph.add_edge(f"score_{ix}", row['comment_id'])

            if len(graph.nodes) == 0:
                st.write(f"No nodes were added to the graph for {selected_topic}.")
                continue

            # Generate and show Pyvis graph
            net = Network(height="600px", width="100%", directed=True, bgcolor="#ffffff", font_color="black")

            # Check if graph has nodes and edges
            if graph.nodes:
                net.from_nx(graph)
                
                with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.html') as tmp_file:
                  net.save_graph(tmp_file.name)
                  tmp_file.seek(0)
                  html_content = tmp_file.read()

                # Display graph
                components.html(html_content, height=650, scrolling=True)
                os.remove(tmp_file.name)

                    
            else:
                st.write(f"No graph generated for {selected_topic}.")



##################################################################
##  Participation

with tab2:
    #st.markdown("---")
    st.markdown(f"## Participation and Experiment Dropout")

    st.markdown("""
    This section shows how participation in the Reddit discussion varies by users' initial attitudes.  
    We compare three groups:
    
    - **All Registered Users**  
    - **Experiment Participants**  
    - **Active Commenters**  
    
    You’ll see how attitudes are distributed in each group, and how likely users in each bin were to participate.  
    This helps identify whether certain opinion profiles are more engaged or more likely to speak up.
    """)
    st.markdown("---")
    st.markdown(f"### Topic: {selected_topic}")
    st.markdown("### Subreddits:")
    for sub in selected_subreddits:
        st.markdown(f"- {sub}")

    st.markdown("---")

    filtered_df_comments = df_comments[
        (df_comments['post_title'] == selected_topic) &
        (df_comments['subreddit'].isin(selected_subreddits))
        ]
    filtered_df_pre = df_pre_survey[df_pre_survey['subreddit'].isin(selected_subreddits)]

    # All users registered for the experiment
    all_users = filtered_df_pre['ParticipantID'].unique().astype(str)
    filtered_df_pre_all = filtered_df_pre[filtered_df_pre['ParticipantID'].isin(all_users)]
    attsAll = filtered_df_pre_all[ topics_survey[tx] ]
    attsAll = 2 * (attsAll - 1) / 5 - 1

    # Users active in the comments
    act_users = filtered_df_comments['ParticipantID'].unique().astype(str)
    filtered_df_pre_act = filtered_df_pre[filtered_df_pre['ParticipantID'].isin(act_users)]
    attsAct = filtered_df_pre_act[ topics_survey[tx] ]
    attsAct = 2 * (attsAct - 1) / 5 - 1

    # All users the participated at some point
    users_comments = df_comments['ParticipantID'].unique().astype(str)
    exp_users = np.intersect1d(all_users,users_comments)
    filtered_df_pre_exp = filtered_df_pre[filtered_df_pre['ParticipantID'].isin(exp_users)]
    attsExp = filtered_df_pre_exp[ topics_survey[tx] ]
    attsExp = 2 * (attsExp - 1) / 5 - 1

    st.text(f"Number of registered users: {len(all_users)}")
    st.text(f"Number of participating users: {len(exp_users)}")
    st.text(f"Number of active users: {len(act_users)}")


    st.markdown(f"### Attitude Distributions ({selected_topic})")

    bins = np.linspace(-1.2, 1.2, 7)  # 6 bins centered on categories
    titles = ["All Registered Users", "Experiment Population", "Active Commenters"]
    data = [attsAll, attsExp, attsAct]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)

    for ax, d, title in zip(axes, data, titles):
        counts, _, bars = ax.hist(d, bins=bins, density=False, color='skyblue', edgecolor='black')
        ax.set_title(title)
        ax.set_xlabel("Attitude")
        ax.set_xticks(bins[0:6]+0.2)
        ax.set_xticklabels([f"{round(b+0.2, 1)}" for b in bins[0:6]])
        #ax.grid(axis='y')
        ax.grid(axis='y', linestyle='--', linewidth=0.6, alpha=0.7)

        # Add count labels above bars
        for rect, count in zip(bars, counts):
            height = rect.get_height()
            if height > 0:
                ax.text(rect.get_x() + rect.get_width()/2., height + 1,
                        f"{int(count)}", ha='center', va='bottom', fontsize=8)

    axes[0].set_ylabel("Number of Users")
    #fig.suptitle("Attitude Distributions by Group (Absolute Counts)")
    st.pyplot(fig)

    data = {
        "Experiment Population": attsExp,
        "Active Commenters": attsAct,
        "All Registered Users": attsAll,
    }
    df = pd.DataFrame(data)

    figKDE, ax = plt.subplots(figsize=(8, 4))
    for col in df.columns:
        sns.kdeplot(df[col], label=col, ax=ax, fill=True, alpha=0.3)

    ax.set_title("Attitude Distributions")
    ax.set_xlabel("Attitude")
    ax.set_ylabel("Density")
    ax.legend()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.pyplot(figKDE)

    st.markdown("---")
    st.markdown(f"### Dropout and Participation Rates by Attitude ({selected_topic})")

    # Histogram counts
    hist_all, _ = np.histogram(attsAll, bins=bins)
    hist_exp, _ = np.histogram(attsExp, bins=bins)
    hist_act, _ = np.histogram(attsAct, bins=bins)

    # Avoid divide-by-zero
    rate_exp_vs_all = np.divide(hist_exp, hist_all, where=hist_all != 0)
    rate_act_vs_exp = np.divide(hist_act, hist_exp, where=hist_exp != 0)

    bin_labels = [f"{round(b+0.2, 1)}" for b in bins[:-1]]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)

    # Plot 1
    axes[0].bar(bin_labels, rate_exp_vs_all * 100, color='mediumseagreen')
    axes[0].set_title("Experiment dropout rates")
    axes[0].set_ylabel("Percentage (%)")
    axes[0].set_xlabel("Attitude")
    axes[0].grid(axis='y', linestyle='--', linewidth=0.6, alpha=0.7)

    # Plot 2
    axes[1].bar(bin_labels, rate_act_vs_exp * 100, color='tomato')
    axes[1].set_title("Discussion participation rates")
    axes[1].set_xlabel("Attitude")
    axes[1].grid(axis='y', linestyle='--', linewidth=0.6, alpha=0.7)

    #fig.suptitle("Dropout and Participation Rates by Attitude")
    st.pyplot(fig)


##################################################################
##  Opinion Dynamics

with tab3:
    st.markdown("## Opinion Change and Attitude Transition Matrix")
    st.markdown("""
    This section models how opinions shift over time based on the experimental data.  
    You’ll see:
    
    - 🟦 **Pre-discussion attitudes**  
    - 🔁 **Transition matrix** based on actual changes between pre and post  
    - 🟥 **Post-discussion attitudes**
    
    🔧 Use the controls to simulate how opinions might evolve if these dynamics continue over time.
    
    You can:
    - Step forward one time unit at a time
    - Or run a full animation across multiple steps
    
    The bars represent the projected attitude distribution at each step.  
    A vertical dashed line shows the current mean attitude.
    """)

    st.markdown("---")
    st.subheader(f"Topic: {selected_topic}")
    st.subheader("Subreddits:")
    for sub in selected_subreddits:
        st.markdown(f"- {sub}")

    st.markdown("---")
    tx = np.where(topics == selected_topic)[0][0]
    topic = topics_survey[tx]
    filtered_df_pre = df_pre_survey[df_pre_survey['subreddit'].isin(selected_subreddits)]
    filtered_df_post = df_post_survey[df_post_survey['subreddit'].isin(selected_subreddits)]
    filtered_df_post_valid = filtered_df_post.copy()
    filtered_df_post_valid = filtered_df_post_valid.dropna(subset=[topic])

    users_pre = filtered_df_pre['ParticipantID'].unique().astype(str)
    valid_users = filtered_df_post_valid['ParticipantID'].unique().astype(str)
    valid_users = np.intersect1d(users_pre, valid_users)

    filtered_df_pre_valid = filtered_df_pre[filtered_df_pre['ParticipantID'].isin(valid_users)]

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

    bins = np.linspace(-1.2, 1.2, 7)  # 6 bins centered on categories

    # Normalize for histogram binning
    attsPreN = 2 * (attsPre - 1) / 5 - 1
    attsPostN = 2 * (attsPost - 1) / 5 - 1
    bins = np.linspace(-1.2, 1.2, 7)
    bin_labels = [f"{round(b+0.2, 1)}" for b in bins[:-1]]

    # Pre/Post Histograms
    histPre, _ = np.histogram(attsPreN, bins=bins)
    histPost, _ = np.histogram(attsPostN, bins=bins)

    # Plot layout
    fig, axs = plt.subplots(1, 3, figsize=(18, 4), gridspec_kw={'width_ratios': [1, 1.2, 1]})

    # Plot 1: Pre
    axs[0].bar(bin_labels, histPre, color='skyblue', edgecolor='black')
    axs[0].set_title("Pre Attitudes")
    axs[0].set_ylabel("User Count")
    axs[0].set_xlabel("Attitude")

    # Plot 2: Transition Matrix
    sns.heatmap(transition_matrix, annot=True, fmt=".2f", cmap="Blues", ax=axs[1],
                xticklabels=["-1","-0.6","-0.2","0.2","0.6","1"], yticklabels=["-1","-0.6","-0.2","0.2","0.6","1"])
    axs[1].set_title("Transition Matrix")
    axs[1].set_xlabel("Post")
    axs[1].set_ylabel("Pre")

    # Plot 3: Post
    axs[2].bar(bin_labels, histPost, color='salmon', edgecolor='black')
    axs[2].set_title("Post Attitudes")
    axs[2].set_xlabel("Attitude")

    #fig.suptitle("Attitude Shift Overview")
    st.pyplot(fig)

    st.markdown("---")
    st.markdown("## Projected Opinion Dynamics")

        # Track topic/subreddit changes
    if "last_topic" not in st.session_state or "last_subs" not in st.session_state:
        st.session_state.last_topic = selected_topic
        st.session_state.last_subs = selected_subreddits

    # Check if selection changed
    if (st.session_state.last_topic != selected_topic or
            st.session_state.last_subs != selected_subreddits):
        st.session_state.step_count = 0
        st.session_state.current_distribution = histPre / histPre.sum()
        st.session_state.last_topic = selected_topic
        st.session_state.last_subs = selected_subreddits

    # Interactive Controls
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 🔧 Evolution Controls")
        st.markdown('#### Step-by-Step')
        # Initialize session state on first load
        if "step_count" not in st.session_state:
            st.session_state.step_count = 0
            st.session_state.current_distribution = histPre / histPre.sum()
        # Button to advance one step
        if st.button("Advance One Step"):
            st.session_state.step_count += 1
            st.session_state.current_distribution = (
                    st.session_state.current_distribution @ transition_matrix
            )
        if st.button("🔄 Reset to Step 0"):
            st.session_state.step_count = 0
            st.session_state.current_distribution = histPre / histPre.sum()
        # Show current step
        st.markdown(f"**Current step: {st.session_state.step_count}**")
        st.markdown("---")
        st.markdown('#### Animation')
        step = st.slider("Number of steps to simulate", min_value=1, max_value=100, value=20)
        animate = st.checkbox("Animate step-by-step")
    with col2:
        #opinion_values = np.array([1, 2, 3, 4, 5, 6])
        opinion_values = np.array([-1, -0.6, -0.2, 0.2, 0.6, 1])
        #st.text(np.sum(st.session_state.current_distribution * opinion_values))

        # Animate if checked
        if animate:
            st.session_state.step_count = 0
            st.session_state.current_distribution = histPre / histPre.sum()

            progress_text = st.empty()
            chart_placeholder = st.empty()
            for s in range(1, step + 1):
                st.session_state.step_count = s
                st.session_state.current_distribution = (
                        st.session_state.current_distribution @ transition_matrix
                )

                fig, ax = plt.subplots(figsize=(6, 3))
                ax.bar(bin_labels, st.session_state.current_distribution, color='orange', edgecolor='black')
                ax.set_ylim(0, 1)
                ax.set_xlabel("Attitude")
                mean_opinion = np.sum(st.session_state.current_distribution * opinion_values)
                mo = (mean_opinion + 1)*2.5
                ax.axvline(x=mo, color='black', linestyle='--', linewidth=2, label='Mean')
                ax.set_title(f"Projected Distribution – Step {s}")
                ax.set_ylabel("Probability")
                progress_text.markdown(f"**Step {s}**")
                chart_placeholder.pyplot(fig)
                plt.close(fig)
                time.sleep(0.5)  # Adjust delay here
        else:
            # Plot current distribution (manual step mode)
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.bar(bin_labels, st.session_state.current_distribution, color='orange', edgecolor='black')
            ax.set_ylim(0, 1)
            ax.set_xlabel("Attitude")
            mean_opinion = np.sum(st.session_state.current_distribution * opinion_values)
            mo = (mean_opinion + 1)*2.5
            ax.axvline(x=mo, color='black', linestyle='--', linewidth=2, label='Mean')
            ax.set_title(f"Projected Distribution – Step {st.session_state.step_count}")
            ax.set_ylabel("Probability")
            st.pyplot(fig)
            plt.close(fig)



