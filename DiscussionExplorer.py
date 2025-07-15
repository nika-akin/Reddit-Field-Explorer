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
# Custom CSS for Responsive and Desktop + Mobile Optimization
st.markdown("""
<style>
/* 🌐 Global layout constraints */
.block-container {
    padding: 2rem 3rem !important;
    max-width: 1200px;
    margin: auto;
}

/* 🧱 Container cleanup */
[data-testid="stVerticalBlock"], .element-container {
    background: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* 📊 Plot and chart containers */
.element-container:has(canvas), .element-container:has(svg),
iframe, .stHtml {
    background-color: transparent !important;
}

/* 🎛️ Expander body */
.stExpanderContent {
    background-color: transparent !important;
    padding: 0.5rem 1rem;
}

/* 📑 Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    justify-content: start;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}

.stTabs [data-baseweb="tab-list"] button {
    font-size: 18px !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
    margin: 4px 8px 0 0 !important;
    border-radius: 10px !important;
    background-color: #f0f2f6 !important;
    color: #333 !important;
    border: none;
    transition: all 0.2s ease;
}

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background-color: #0072bb !important;
    color: #fff !important;
}

/* 📐 Improve spacing between columns */
.css-1r6slb0 > div {
    gap: 2rem !important;
}

/* 📱 Responsive spacing for mobile */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem !important;
    }

    .stTabs [data-baseweb="tab-list"] button {
        width: 100% !important;
        font-size: 16px !important;
    }

    .css-1r6slb0 > div {
        gap: 1rem !important;
    }
}
</style>
""", unsafe_allow_html=True)


st.markdown(
    """
    <style>
    .sponsor-banner {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }

    .sponsor-banner img {
        height: 50px;
        margin-right: 15px;
    }

    .sponsor-banner .sponsor-text {
        font-size: 1.1rem;
        color: #444;
    }

    @media (max-width: 768px) {
        .sponsor-banner {
            flex-direction: column;
            align-items: flex-start;
        }

        .sponsor-banner img {
            margin-bottom: 10px;
        }
    }
    </style>

    <div class="sponsor-banner">
        <img src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48c3ZnIGlkPSJFYmVuZV8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB2aWV3Qm94PSIwIDAgODcuNDggNDYiPjxkZWZzPjxzdHlsZT4uY2xzLTF7ZmlsbDp1cmwoI1VuYmVuYW5udGVyX1ZlcmxhdWZfNi0yKTt9LmNscy0ye2ZpbGw6dXJsKCNVbmJlbmFubnRlcl9WZXJsYXVmXzYtMTApO30uY2xzLTN7ZmlsbDp1cmwoI1VuYmVuYW5udGVyX1ZlcmxhdWZfNi03KTt9LmNscy00e2ZpbGw6dXJsKCNVbmJlbmFubnRlcl9WZXJsYXVmXzYtOCk7fS5jbHMtNXtmaWxsOnVybCgjVW5iZW5hbm50ZXJfVmVybGF1Zl82LTQpO30uY2xzLTZ7ZmlsbDp1cmwoI1VuYmVuYW5udGVyX1ZlcmxhdWZfNi01KTt9LmNscy03e2ZpbGw6dXJsKCNVbmJlbmFubnRlcl9WZXJsYXVmXzYtNik7fS5jbHMtOHtmaWxsOnVybCgjVW5iZW5hbm50ZXJfVmVybGF1Zl82LTkpO30uY2xzLTl7ZmlsbDp1cmwoI1VuYmVuYW5udGVyX1ZlcmxhdWZfNik7fS5jbHMtMTB7ZmlsbDp1cmwoI1VuYmVuYW5udGVyX1ZlcmxhdWZfNi0zKTt9PC9zdHlsZT48bGluZWFyR3JhZGllbnQgaWQ9IlVuYmVuYW5udGVyX1ZlcmxhdWZfNiIgeDE9IjI1LjI3IiB5MT0iMTIuNSIgeDI9IjU3Ljg3IiB5Mj0iNDkuNjQiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj48c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiMxNTQyOTAiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiM0MDZjYjIiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iVW5iZW5hbm50ZXJfVmVybGF1Zl82LTIiIHgxPSI0MS4yMSIgeTE9Ii0xLjUiIHgyPSI3My44MiIgeTI9IjM1LjY0IiB4bGluazpocmVmPSIjVW5iZW5hbm50ZXJfVmVybGF1Zl82Ii8+PGxpbmVhckdyYWRpZW50IGlkPSJVbmJlbmFubnRlcl9WZXJsYXVmXzYtMyIgeDE9IjcuMDgiIHkxPSIyOC40NyIgeDI9IjM5LjY4IiB5Mj0iNjUuNjEiIHhsaW5rOmhyZWY9IiNVbmJlbmFubnRlcl9WZXJsYXVmXzYiLz48bGluZWFyR3JhZGllbnQgaWQ9IlVuYmVuYW5udGVyX1ZlcmxhdWZfNi00IiB4MT0iMTIuMDYiIHkxPSIyNC4wOSIgeDI9IjQ0LjY3IiB5Mj0iNjEuMjMiIHhsaW5rOmhyZWY9IiNVbmJlbmFubnRlcl9WZXJsYXVmXzYiLz48bGluZWFyR3JhZGllbnQgaWQ9IlVuYmVuYW5udGVyX1ZlcmxhdWZfNi01IiB4MT0iMTkuMjYiIHkxPSIxNy43NyIgeDI9IjUxLjg3IiB5Mj0iNTQuOTEiIHhsaW5rOmhyZWY9IiNVbmJlbmFubnRlcl9WZXJsYXVmXzYiLz48bGluZWFyR3JhZGllbnQgaWQ9IlVuYmVuYW5udGVyX1ZlcmxhdWZfNi02IiB4MT0iNDIuOTYiIHkxPSItMy4wNCIgeDI9Ijc1LjU3IiB5Mj0iMzQuMTEiIHhsaW5rOmhyZWY9IiNVbmJlbmFubnRlcl9WZXJsYXVmXzYiLz48bGluZWFyR3JhZGllbnQgaWQ9IlVuYmVuYW5udGVyX1ZlcmxhdWZfNi03IiB4MT0iNDkuNzMiIHkxPSItOC45OCIgeDI9IjgyLjM0IiB5Mj0iMjguMTYiIHhsaW5rOmhyZWY9IiNVbmJlbmFubnRlcl9WZXJsYXVmXzYiLz48bGluZWFyR3JhZGllbnQgaWQ9IlVuYmVuYW5udGVyX1ZlcmxhdWZfNi04IiB4MT0iMzEuNjYiIHkxPSI2Ljg4IiB4Mj0iNjQuMjciIHkyPSI0NC4wMiIgeGxpbms6aHJlZj0iI1VuYmVuYW5udGVyX1ZlcmxhdWZfNiIvPjxsaW5lYXJHcmFkaWVudCBpZD0iVW5iZW5hbm50ZXJfVmVybGF1Zl82LTkiIHgxPSIyNS4zMyIgeTE9IjEyLjQ0IiB4Mj0iNTcuOTMiIHkyPSI0OS41OSIgeGxpbms6aHJlZj0iI1VuYmVuYW5udGVyX1ZlcmxhdWZfNiIvPjxsaW5lYXJHcmFkaWVudCBpZD0iVW5iZW5hbm50ZXJfVmVybGF1Zl82LTEwIiB4MT0iMzcuMDEiIHkxPSIyLjE5IiB4Mj0iNjkuNjIiIHkyPSIzOS4zMyIgeGxpbms6aHJlZj0iI1VuYmVuYW5udGVyX1ZlcmxhdWZfNiIvPjwvZGVmcz48cGF0aCBjbGFzcz0iY2xzLTkiIGQ9Im02MS41MywzNS4xN2MtLjkzLjA5LTEuNzkuNC0yLjUxLjg5bC0zLjMyLTMuNjVjLjQ2LS40OC44OS0xLDEuMjYtMS41NS0uMDMsMC0uMDYsMC0uMSwwaC0xLjc3Yy0xLjc0LDIuMDctNC4zNCwzLjM4LTcuMjUsMy4zOC0zLjI2LDAtNi4xNS0xLjY2LTcuODUtNC4xOC0uNC4zLS44NS41Mi0xLjMzLjY4LjM2LjU1Ljc3LDEuMDcsMS4yMiwxLjU0bC0yLjc0LDIuOTljLS41Ny0uMzktMS4yNS0uNjQtMS45OS0uNy0yLjM1LS4yMi00LjQ0LDEuNTItNC42NSwzLjg3aDBjLS4yMiwyLjM1LDEuNTIsNC40NCwzLjg3LDQuNjUuMTMuMDEuMjYuMDIuNC4wMiwyLjE4LDAsNC4wNS0xLjY3LDQuMjYtMy44OS4xLTEuMDgtLjIyLTIuMS0uODEtMi45MmwyLjc2LTMuMDFjMS44OCwxLjUyLDQuMjcsMi40Myw2Ljg3LDIuNDNzNC44OC0uODcsNi43NC0yLjMzbDMuMzIsMy42NGMtLjkyLDEuMDctMS40MiwyLjUtMS4yOCw0LjAyLjEzLDEuNDQuODIsMi43NSwxLjkzLDMuNjguOTguODIsMi4yLDEuMjYsMy40NiwxLjI2LjE3LDAsLjM0LDAsLjUtLjAyLDEuNDQtLjEzLDIuNzUtLjgyLDMuNjgtMS45My45My0xLjExLDEuMzYtMi41MiwxLjIzLTMuOTctLjI3LTIuOTgtMi45Mi01LjE4LTUuOS00LjkxWm0tMjMuOTksMy45MmMtLjE0LDEuNTMtMS41LDIuNjctMy4wNCwyLjUyLTEuNTMtLjE0LTIuNjctMS41LTIuNTItMy4wNGgwYy4xNC0xLjUzLDEuNTEtMi42NywzLjA0LTIuNTIsMS41My4xNCwyLjY3LDEuNSwyLjUyLDMuMDRabTI3LjUxLDRjLS42Ny44MS0xLjYyLDEuMzEtMi42NywxLjQtMS4wNS4xLTIuMDctLjIyLTIuODgtLjg5LS44MS0uNjctMS4zMS0xLjYyLTEuNC0yLjY3LS4yLTIuMTYsMS40LTQuMDgsMy41Ni00LjI4LDIuMTYtLjIsNC4wOCwxLjQsNC4yOCwzLjU2LjEsMS4wNS0uMjIsMi4wNy0uODksMi44OFoiLz48cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Im02NC4xNC4wM2MtNC4yNC0uMzktNy45OSwyLjc0LTguMzgsNi45Ny0uMTksMi4wNS40Myw0LjA1LDEuNzUsNS42NC4wNi4wNy4xMi4xNC4xOC4ybC0zLjA1LDMuMzNjLTEuODctMS40OC00LjIzLTIuMzctNi44LTIuMzdzLTUsLjkxLTYuODgsMi40NGwtMS45OS0yLjE5Yy44NC0xLjA2LDEuMy0yLjQzLDEuMTctMy44OC0uMjctMi45OC0yLjkyLTUuMTgtNS45LTQuOTEtMS40NC4xMy0yLjc1LjgyLTMuNjgsMS45My0uOTMsMS4xMS0xLjM2LDIuNTItMS4yMywzLjk3LjI2LDIuODEsMi42Myw0LjkzLDUuNCw0LjkzLjE2LDAsLjMzLDAsLjUtLjAyLDEtLjA5LDEuOTEtLjQ1LDIuNjctMWwxLjk4LDIuMTdjLS44MS44Ni0xLjQ4LDEuODQtMS45OCwyLjkzLjUuMDkuOTguMjUsMS40Mi40NywxLjU0LTMuMTcsNC43OC01LjM1LDguNTMtNS4zNSwyLjYsMCw0Ljk3LDEuMDYsNi42OCwyLjc2aDEuOThjLS4yNC0uMzEtLjQ5LS42LS43Ni0uODhsMy4wNC0zLjMyYzEuMTQuODcsMi41LDEuNCwzLjk1LDEuNTMuMjQuMDIuNDguMDMuNzEuMDMsMy45NCwwLDcuMy0zLjAxLDcuNjctNywuMzktNC4yMy0yLjc0LTcuOTktNi45Ny04LjM4Wm0tMjkuMDYsMTQuNTZjLTEuMDUuMDktMi4wNy0uMjItMi44OC0uODktLjgxLS42Ny0xLjMxLTEuNjItMS40LTIuNjdzLjIyLTIuMDcuODktMi44OGMuNjctLjgxLDEuNjItMS4zMSwyLjY3LTEuNCwyLjE2LS4yLDQuMDgsMS40LDQuMjgsMy41Ni4yLDIuMTYtMS40LDQuMDgtMy41Niw0LjI4Wm0zNC41NS02LjMxYy0uMTUsMS42Ni0uOTQsMy4xNS0yLjIyLDQuMjEtMS4yOCwxLjA2LTIuODksMS41Ni00LjU1LDEuNDEtMS42Ni0uMTUtMy4xNS0uOTQtNC4yMS0yLjIyLTEuMDYtMS4yOC0xLjU2LTIuODktMS40MS00LjU1LjE1LTEuNjYuOTQtMy4xNSwyLjIyLTQuMjEsMS4yOC0xLjA2LDIuODktMS41Niw0LjU1LTEuNDEsMy40Mi4zMSw1Ljk0LDMuMzUsNS42Myw2Ljc3WiIvPjxwYXRoIGNsYXNzPSJjbHMtMTAiIGQ9Im01LjY3LDI0LjI5Yy0uNDMtLjE5LS45OS0uMzgtMS42Ny0uNTYtLjUyLS4xNC0uOTItLjI3LTEuMjItLjM5LS4zLS4xMi0uNTQtLjI4LS43NC0uNDgtLjE5LS4yLS4yOS0uNDYtLjI5LS43OCwwLS40Ny4xNS0uODIuNDYtMS4wNy4zMS0uMjUuNy0uMzcsMS4xOS0uMzcuNTQsMCwuOTcuMTMsMS4yOS40LjMzLjI3LjUxLjU5LjU0Ljk3aDEuODdjLS4wNy0uODctLjQyLTEuNTYtMS4wNi0yLjA2LS42NC0uNS0xLjQ2LS43NS0yLjQ2LS43NS0uNywwLTEuMzIuMTItMS44Ni4zNnMtLjk1LjU4LTEuMjUsMS4wM2MtLjMuNDUtLjQ1Ljk3LS40NSwxLjU2LDAsLjY0LjE1LDEuMTYuNDUsMS41NS4zLjM5LjY2LjY3LDEuMDguODYuNDIuMTguOTcuMzYsMS42NC41NC41NC4xNC45NS4yNywxLjI2LjM5LjMuMTIuNTUuMjkuNzYuNTEuMi4yMi4zLjUuMy44NSwwLC40NS0uMTYuODEtLjQ5LDEuMDktLjMzLjI4LS43OC40Mi0xLjM3LjQycy0xLS4xNC0xLjMyLS40M2MtLjMxLS4yOS0uNDktLjY1LS41My0xLjFIMGMwLC41OS4xNiwxLjEyLjQ4LDEuNTYuMzIuNDUuNzUuNzksMS4zMSwxLjAzLjU2LjI0LDEuMTguMzYsMS44Ny4zNi43MywwLDEuMzctLjE0LDEuOTEtLjQyLjU0LS4yOC45NS0uNjYsMS4yMy0xLjEyLjI4LS40Ny40Mi0uOTYuNDItMS40OSwwLS42NS0uMTUtMS4xOC0uNDUtMS41Ny0uMy0uMzktLjY3LS42OC0xLjEtLjg3WiIvPjxwYXRoIGNsYXNzPSJjbHMtNSIgZD0ibTE1LjQ4LDIxLjg1Yy0uNjMtLjM1LTEuMzQtLjUyLTIuMTMtLjUycy0xLjQ5LjE3LTIuMTMuNTJjLS42My4zNS0xLjE0Ljg0LTEuNSwxLjQ5LS4zNy42NC0uNTUsMS4zOC0uNTUsMi4yMnMuMTgsMS41OC41NCwyLjIyLjg1LDEuMTQsMS40NywxLjQ5Yy42Mi4zNSwxLjMyLjUzLDIuMS41M3MxLjUtLjE4LDIuMTUtLjUzYy42NS0uMzUsMS4xNi0uODUsMS41NC0xLjQ5LjM4LS42NC41Ni0xLjM4LjU2LTIuMjJzLS4xOC0xLjU3LS41NS0yLjIyYy0uMzctLjY0LS44Ny0xLjE0LTEuNS0xLjQ5Wm0tLjA0LDUuMjJjLS4yNC40Mi0uNTUuNzMtLjkzLjk0LS4zOC4yMS0uNzkuMzEtMS4yMy4zMS0uNjgsMC0xLjI1LS4yNC0xLjctLjcyLS40NS0uNDgtLjY4LTEuMTYtLjY4LTIuMDQsMC0uNTkuMTEtMS4xLjMzLTEuNTEuMjItLjQxLjUxLS43Mi44OC0uOTMuMzctLjIxLjc4LS4zMSwxLjIxLS4zMXMuODQuMSwxLjIyLjMxYy4zOC4yMS42OC41Mi45MS45My4yMy40MS4zNC45MS4zNCwxLjUxcy0uMTIsMS4xLS4zNiwxLjUyWiIvPjxwb2x5Z29uIGNsYXNzPSJjbHMtNiIgcG9pbnRzPSIyNS4xNyAyNy40MiAyMS41NCAxOS4zMiAxOS43MSAxOS4zMiAxOS43MSAyOS42NSAyMS40MSAyOS42NSAyMS40MSAyMi41OCAyNC41NyAyOS42NSAyNS43NSAyOS42NSAyOC45IDIyLjU4IDI4LjkgMjkuNjUgMzAuNiAyOS42NSAzMC42IDE5LjMyIDI4Ljc4IDE5LjMyIDI1LjE3IDI3LjQyIi8+PHBhdGggY2xhc3M9ImNscy03IiBkPSJtNzAuMTEsMjEuOGMtLjYtLjM0LTEuMjktLjUxLTIuMDctLjUxcy0xLjUxLjE3LTIuMTMuNTJjLS42Mi4zNS0xLjEuODQtMS40NCwxLjQ4LS4zNC42NC0uNTEsMS4zOC0uNTEsMi4yMnMuMTgsMS41OC41MywyLjIyLjg0LDEuMTQsMS40NiwxLjQ5Yy42Mi4zNSwxLjMyLjUzLDIuMS41My45NiwwLDEuNzctLjI0LDIuNDItLjcyLjY1LS40OCwxLjEtMS4xLDEuMzUtMS44NWgtMS44M2MtLjM4Ljc2LTEuMDIsMS4xNC0xLjkzLDEuMTQtLjYzLDAtMS4xNy0uMi0xLjYxLS41OS0uNDQtLjQtLjY4LS45Mi0uNzMtMS41OGg2LjI2Yy4wNC0uMjUuMDYtLjUzLjA2LS44MywwLS43OS0uMTctMS40OS0uNTEtMi4xLS4zNC0uNjEtLjgxLTEuMDgtMS40MS0xLjQyWm0tNC4zOSwyLjk5Yy4wOC0uNjMuMzMtMS4xNC43NC0xLjUxLjQyLS4zNy45Mi0uNTYsMS41LS41Ni42NCwwLDEuMTguMTksMS42Mi41Ni40NC4zOC42Ni44OC42NywxLjVoLTQuNTRaIi8+PHBhdGggY2xhc3M9ImNscy0zIiBkPSJtODcuMDQsMjIuODljLS4yOS0uNTMtLjY5LS45Mi0xLjItMS4xOXMtMS4wOS0uNC0xLjczLS40Yy0uNiwwLTEuMTcuMTUtMS43LjQ0LS41My4yOS0uOTEuNjktMS4xNiwxLjE4LS4yOC0uNTMtLjY3LS45My0xLjE5LTEuMi0uNTItLjI4LTEuMS0uNDItMS43NS0uNDItLjQ5LDAtLjk0LjA5LTEuMzcuMjgtLjQzLjE5LS43OC40NS0xLjA2Ljc5di0uOTRoLTEuN3Y4LjE5aDEuN3YtNC41OGMwLS43My4xOS0xLjMuNTYtMS42OS4zNy0uMzkuODctLjU5LDEuNTEtLjU5czEuMTMuMiwxLjUuNTljLjM3LjM5LjU1Ljk1LjU1LDEuNjl2NC41OGgxLjY4di00LjU4YzAtLjczLjE5LTEuMy41Ni0xLjY5LjM3LS4zOS44Ny0uNTksMS41MS0uNTlzMS4xNC4yLDEuNS41OWMuMzcuMzkuNTUuOTUuNTUsMS42OXY0LjU4aDEuNjh2LTQuODNjMC0uNzQtLjE1LTEuMzgtLjQ0LTEuOVoiLz48cGF0aCBjbGFzcz0iY2xzLTQiIGQ9Im00OS42OCwyMC43N3YtMS42aC0yLjA1bC0xLjEyLDEuNi0zLjg4LDUuNTd2MS4yOGg1LjM4djIuMjZoMS42N3YtMi4yNmgxLjM4di0xLjQ3aC0xLjM4di01LjM3Wm0tMS41OSw1LjM3aC0zLjUxbDMuNTEtNS4yNXY1LjI1WiIvPjxwYXRoIGNsYXNzPSJjbHMtOCIgZD0ibTM4LjkxLDIxLjgzYy0uNi0uMzQtMS4yOS0uNTEtMi4wNy0uNTFzLTEuNTEuMTctMi4xMy41MmMtLjYyLjM1LTEuMS44NC0xLjQ0LDEuNDgtLjM0LjY0LS41MSwxLjM4LS41MSwyLjIycy4xOCwxLjU4LjUzLDIuMjJjLjM1LjY0Ljg0LDEuMTQsMS40NiwxLjQ5LjYyLjM1LDEuMzIuNTMsMi4xLjUzLjk2LDAsMS43Ny0uMjQsMi40Mi0uNzIuMzItLjI0LjYtLjUxLjgyLS44MnMuNC0uNjUuNTItMS4wM2gtMS44M2MtLjM4Ljc2LTEuMDIsMS4xNC0xLjkzLDEuMTQtLjYzLDAtMS4xNy0uMi0xLjYxLS41OS0uNDQtLjQtLjY4LS45Mi0uNzMtMS41OGg2LjI2Yy4wNC0uMjUuMDYtLjUzLjA2LS44MywwLS43OS0uMTctMS40OS0uNTEtMi4xLS4zNC0uNjEtLjgxLTEuMDgtMS40MS0xLjQyWm0tNC4zOSwyLjk5Yy4wOC0uNjMuMzMtMS4xNC43NC0xLjUxLjQyLS4zNy45Mi0uNTYsMS41LS41Ni42NCwwLDEuMTguMTksMS42Mi41Ni40NC4zOC42Ni44OC42NywxLjVoLTQuNTRaIi8+PHBhdGggY2xhc3M9ImNscy0yIiBkPSJtNTkuNzUsMTkuOTJjLS44My0uNDItMS43OS0uNjMtMi44OS0uNjNoLTMuMzh2MTAuMzNoMy4zOGMuODMsMCwxLjU3LS4xMiwyLjI1LS4zNS4yMi0uMDguNDQtLjE3LjY1LS4yNy4xLS4wNS4yLS4xMS4zLS4xNi42OC0uNCwxLjIyLS45NCwxLjYyLTEuNjEuNDUtLjc3LjY4LTEuNjkuNjgtMi43NHMtLjIzLTEuOTctLjY4LTIuNzZjLS40NS0uNzktMS4wOS0xLjM5LTEuOTItMS44MVptLS4xMSw3LjM0Yy0uNjQuNjUtMS41Ny45OC0yLjc4Ljk4aC0xLjY4di03LjU3aDEuNjhjMS4yMSwwLDIuMTQuMzQsMi43OCwxLjAxLjY0LjY3Ljk3LDEuNjEuOTcsMi44MXMtLjMyLDIuMTEtLjk3LDIuNzdaIi8+PC9zdmc+" alt="KIT Logo">
        <div class="sponsor-text">
            <strong>Funded by the European Union</strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <style>
    .contact-card {
        background-color: #f9fafc;
        padding: 24px;
        border-radius: 12px;
        margin-top: 40px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: box-shadow 0.3s ease-in-out;
    }

    .contact-card:hover {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    }

    .contact-card h3 {
        margin-bottom: 12px;
        color: #1a1a1a;
        font-size: 24px;
    }

    .contact-card p {
        font-size: 1.05rem;
        margin-bottom: 15px;
        color: #333;
    }

    .contact-card ul {
        list-style: none;
        padding-left: 0;
    }

    .contact-card li {
        margin-bottom: 10px;
        font-size: 1rem;
    }

    .contact-card a {
        color: #0072bb;
        text-decoration: none;
        font-weight: 500;
    }

    .contact-card a:hover {
        text-decoration: underline;
    }
    </style>

    <div class="contact-card">
        <h3> Welcome to the Reddit Explorer </h3>
        <p>We’d love to hear your feedback, suggestions, or questions. Reach out to us directly:</p>
        <ul>
            <li>📧 <a href="mailto:veronika.batzdorfer@kit.edu">veronika.batzdorfer@kit.edu</a></li>
            <li>📧 <a href="mailto:sven.banisch@kit.edu">sven.banisch@kit.edu</a></li>
            <li>📧 <a href="mailto:oswald@mpib-berlin.mpg.de">oswald@mpib-berlin.mpg.de</a></li>
            <li>
               <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" 
                    alt="GitHub" style="height: 18px; vertical-align: middle; margin-right: 6px;">
               <a href="https://github.com/lfoswald/reddit-discussion-field-experiment" target="_blank">
                   GitHub: Reddit Field Experiment
               </a>
           </li>
       </ul>
    </div>
    """,
    unsafe_allow_html=True
)





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



st.markdown("---")

st.title("Reddit Opinion Dynamics Explorer")
st.markdown("---")


# Sidebar: Global Controls
#st.sidebar.header("🎚️ Experiment Controls")
#selected_subreddits = st.sidebar.multiselect("Select Subreddit", subreddits,default=subreddits[0])
#selected_topic = st.sidebar.radio("Select Topic", topics)

# --- Layout: Sidebar-style controls + Tabs ---
col1, col2 = st.columns([1, 3])  # Left column (smaller) for controls, right column (larger) for content

# Left column (controls)
with col1:
    st.markdown("### Experiment Controls 🎚️")
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
    
    🎚️ **Advanced options** let you:
    - Scale node sizes by **comment length** or **toxicity**
    - Include **vote scores** to assess comment reception
    """)

    st.markdown("---")
    st.markdown("## Comment Settings 🔧")
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
    
    🎚️ Use the controls to simulate how opinions might evolve if these dynamics continue over time.
    
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
        st.markdown("### Evolution Controls 🎚️")
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




