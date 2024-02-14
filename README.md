## Letterboxd List Downloader

This project provides a [web-based](https://lizard.streamlit.app/) tool for downloading user lists from Letterboxd[*](https://letterboxd.com/about).

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Python](https://img.shields.io/badge/Python-3.11.4-blue)](https://www.python.org) [![Streamlit](https://img.shields.io/badge/Streamlit-1.30.0-green)](https://streamlit.io)

### Table of Contents

- [Usage](#usage)
- [Local Installation](#local-installation)

### Usage

1. Enter the `username/list-name` or the direct `list URL` into the textbox on the main page or use the `'q'` argument as a URL parameter.
   - Examples for user and list:
     - `fastfingertips/list_name` ([with q arg](https://lizard.streamlit.app/?q=fastfingertips/list_name))
     - `fastfingertips/list/list_name` ([with q arg](https://lizard.streamlit.app/?q=fastfingertips/list/list_name))
     - _with filter_:
       - `fastfingertips/list_name/genre/crime` ([with q arg](https://lizard.streamlit.app/?q=fastfingertips/list_name/genre/crime))
       - `fastfingertips/list/list_name/genre/crime` ([with q arg](https://lizard.streamlit.app/?q=fastfingertips/list/list_name/genre/crime))
   - Examples for user list URLs (http or https):
     - `https://letterboxd.com/fastfingertips/list/list_name` ([with q arg](https://lizard.streamlit.app/?q=https://letterboxd.com/fastfingertips/list/list_name))
     - `https://boxd.it/rSrSc` ([with q arg](https://lizard.streamlit.app/?q=https://boxd.it/rSrSc))
     - _with filter_:
       - `https://letterboxd.com/fastfingertips/list/list_name/genre/crime` ([with q arg](https://lizard.streamlit.app/?q=https://letterboxd.com/fastfingertips/list/list_name/genre/crime))
       - `https://letterboxd.com/fastfingertips/list/list_name/decade/1990s/genre/crime` ([with q arg](https://lizard.streamlit.app/?q=https://letterboxd.com/fastfingertips/list/list_name/decade/1990s/genre/crime))
       - letterboxd short links do not support filters, so we did not implement this. it seems these are used only for sharing the list.
0. Press Enter.
0. If the list is verified, detailed information about the list will be presented.

### Local Installation
You can use the Letterboxd List Downloader without installing anything on your local machine by visiting the [web application](https://lizard.streamlit.app/).

If you prefer to run the Letterboxd List Downloader locally, follow these steps:

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/FastFingertips/lizard-web.git
    ```

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Application:**
    ```bash
    streamlit run main.py --server.port 8080
    ```

Now, you can access the Letterboxd List Downloader locally by opening your web browser and navigating to [http://localhost:8080](http://localhost:8080).
