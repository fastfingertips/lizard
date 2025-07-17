import streamlit as st
from letterboxdpy.user import User
from letterboxdpy.movie import Movie


def display_movie_poster(slug, poster_url, name, width=150):
    """Display a movie poster with a link to its Letterboxd page."""
    st.markdown(
        f'<a href="https://letterboxd.com/film/{slug}/" target="_blank">'
        f'<img src="{poster_url}" alt="{name}" width="{width}" style="cursor: pointer;" />'
        f'</a>',
        unsafe_allow_html=True
    )

def profile_page():
    st.title("Profile")
    
    username = st.text_input("Enter Username")
    if not username:
        st.info("Please enter a username")
        return
    
    try:
        user_instance = User(username)
    except Exception as e:
        st.error(f"Error fetching user: {str(e)}")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        avatar = user_instance.get_avatar()
        if avatar and avatar['exists']:
            st.image(avatar['url'], caption="Profile Picture", width=200)
        else:
            st.image("https://via.placeholder.com/200", caption="Profile Picture")
    
    with col2:
        st.markdown(f"**{user_instance.display_name}**")
        st.markdown(f"Username: @{user_instance.username}")
        
        if user_instance.bio:
            st.markdown(user_instance.bio)
        
        if user_instance.location:
            st.markdown(f":round_pushpin: {user_instance.location}")
        if user_instance.website:
            st.markdown(f":globe_with_meridians: [{user_instance.website}]({user_instance.website})")
        
        stats = user_instance.stats
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1: st.metric("Films", stats['films'])
        with col2: st.metric("This Year", stats['this_year'])
        with col3: st.metric("Lists", stats['lists'])
        with col4: st.metric("Following", stats['following'])
        with col5: st.metric("Followers", stats['followers'])
    
    if user_instance.favorites:
        st.subheader("Favorite Films")
        
        cols = st.columns(4, gap="medium")
        
        for i, (movie_id, movie) in enumerate(user_instance.favorites.items()):
            with cols[i % 4]:
                try:
                    film = Movie(movie['slug'])
                    display_movie_poster(movie['slug'], film.poster, movie['name'])
                except Exception as e:
                    st.error(f"Error loading poster for {movie['name']}: {str(e)}")
                    st.image("https://via.placeholder.com/150", caption=movie['name'])
    
    if user_instance.recent and user_instance.recent['diary']:
        st.subheader("Recent Activity")
        
        recent_films = []
        for month, days in user_instance.recent['diary']['months'].items():
            for day, films in days.items():
                recent_films.extend(films)
                if len(recent_films) >= 4:
                    break
            if len(recent_films) >= 4:
                break
        
        cols = st.columns(4, gap="medium")
        
        for i, film in enumerate(recent_films[:4]):
            with cols[i]:
                try:
                    recent_movie = Movie(film['slug'])
                    display_movie_poster(film['slug'], recent_movie.poster, film['name'])
                except Exception as e:
                    st.error(f"Error loading poster for {film['name']}: {str(e)}")
                    st.image("https://via.placeholder.com/150", caption=film['name'])

if __name__ == "__main__":
    st.warning('This page is under construction.', icon='🚧')
    profile_page()