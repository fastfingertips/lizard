## Lizard - Letterboxd Data Processor

This project provides a [web-based](https://lizard.streamlit.app/) tool for downloading and processing Letterboxd data including user lists and watchlists from Letterboxd[*](https://letterboxd.com/about).

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Python](https://img.shields.io/badge/Python-3.12.10-blue)](https://www.python.org) [![Streamlit](https://img.shields.io/badge/Streamlit-1.30.0-green)](https://streamlit.io)

https://github.com/FastFingertips/lizard/assets/46646991/fddd4d83-06b2-4975-9907-8de5abc170b8

### Table of Contents

- [Usage](#usage)
- [Local Installation](#local-installation)
- [Documentation](#documentation)

### Usage

**For User Lists:**
1. Enter the `username/list-name` or the direct `list URL` into the textbox on the main page or use the `'q'` argument as a URL parameter.
   - Examples for user lists:
     - [`fastfingertips/list_name`](https://lizard.streamlit.app/?q=fastfingertips/list_name)
     - [`fastfingertips/list/list_name`](https://lizard.streamlit.app/?q=fastfingertips/list/list_name)
     - _with filter_:
       - [`fastfingertips/list_name/genre/crime`](https://lizard.streamlit.app/?q=fastfingertips/list_name/genre/crime)
       - [`fastfingertips/list/list_name/genre/crime`](https://lizard.streamlit.app/?q=fastfingertips/list/list_name/genre/crime)

**For Watchlists:**
1. Enter just the `username` to access their watchlist data.
   - Example for watchlists:
     - [`fastfingertips`](https://lizard.streamlit.app/?q=fastfingertips) (username only)

**For User List URLs (http or https):**
   - Examples:
     - [`https://letterboxd.com/fastfingertips/list/list_name`](https://lizard.streamlit.app/?q=https://letterboxd.com/fastfingertips/list/list_name)
     - [`https://boxd.it/rSrSc`](https://lizard.streamlit.app/?q=https://boxd.it/rSrSc)
     - _with filter_:
       - [`https://letterboxd.com/fastfingertips/list/list_name/genre/crime`](https://lizard.streamlit.app/?q=https://letterboxd.com/fastfingertips/list/list_name/genre/crime)
       - [`https://letterboxd.com/fastfingertips/list/list_name/decade/1990s/genre/crime`](https://lizard.streamlit.app/?q=https://letterboxd.com/fastfingertips/list/list_name/decade/1990s/genre/crime)
       - letterboxd short links do not support filters, so we did not implement this. it seems these are used only for sharing the list.
0. Press Enter.
0. If the list is verified, detailed information about the list will be presented.

### Local Installation
You can use Lizard without installing anything on your local machine by visiting the [web application](https://lizard.streamlit.app/).

If you prefer to run Lizard locally, follow these steps:

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/FastFingertips/lizard.git
    cd lizard
    ```

2. **Install Dependencies:**
    ```bash
    # Option 1: Using pip with requirements.txt
    pip install -r requirements.txt

    # Option 2: Using modern pyproject.toml (recommended)
    pip install -e .
    ```

3. **Run the Application:**
    ```bash
    streamlit run main.py --server.port 8080
    ```

Now, you can access the Letterboxd List Downloader locally by opening your web browser and navigating to [http://localhost:8080](http://localhost:8080).

### Documentation

For comprehensive API references and documentation links used throughout the project, see [docs/references.md](docs/references.md). This includes:

- Streamlit API references
- Python standard library documentation
- Third-party library documentation
- Development tools and external services
