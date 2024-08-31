# Music Streaming Application

## Overview

The Music Streaming Application is a modern, scalable, and user-centric platform designed to meet various user needs. It utilizes a Model-View-Controller (MVC) architecture, ensuring a clear separation of concerns and a structured approach to development.

## 1. App Design Architecture

### 1.1 Models

- **User Model:** Represents user data including username, password, and registration date.
- **Creator Model:** Represents creator data such as username, songs, albums, and registration date.
- **Song Model:** Stores information about songs like song name, artist, genre, lyrics, file, songwriter ID, play count, and album.
- **Album Model:** Contains details about albums including album name, album creator, and number of views.
- **Playlist Model:** Manages user-created playlists and their associated songs.
- **Genre Model:** Represents different music genres.
- **Notification Model:** Manages notifications sent by users to the admin.

### 1.2 Controllers

- **User Controller:**
  - Manages user-related operations such as registration, login, and authentication.
  - Handles user sessions and maintains session data.
  - Displays songs available for listening.

- **Song Controller:**
  - **Retrieve Songs:** Fetches song information, genres, and artists for display and streaming.
  - **Search Functionality:** Provides search capabilities for songs or albums based on user input.
  - **Song Streaming:** Manages the rating and play counts of songs.

- **Album Controller:**
  - **Album Information:** Retrieves album details including tracks and artists.
  - **Create and Manage Album:** Enables creators to create, update, and delete albums.

- **Playlist Controller:**
  - **Create and Manage Playlists:** Allows users to create, update, and delete playlists.
  - **Playlist Information:** Fetches details about specific playlists, including their songs.

- **Genre Controller:**
  - **Genre-Based Content:** Retrieves songs based on selected genres.
  - **Genre Information:** Provides details about different music genres available on the platform.

- **Admin Controller:**
  - Manages administrative tasks and privileges within the application.
  - Controls access to administrative functionalities such as app statistics.
  - Handles actions related to content management, including blacklisting and whitelisting songs, albums, and creators.

## 2. Conclusion

The app architecture emphasizes modularity, allowing for easy scalability and maintenance. It ensures that the business logic (controllers), data (models), and user interface (views) remain decoupled, facilitating efficient development and future enhancements. The MVC design pattern provides a structured approach to manage and manipulate data, handle user interactions, and present information effectively. The app's controllers facilitate seamless interaction between the user interface and the data model, enabling a rich and intuitive user experience in accessing, exploring, and enjoying music content.

## Technologies Used

- **Backend Framework:** Python - FLASK
- **Frontend Framework:** HTML, CSS, JAVASCRIPT, JINJA2
- **Database:** MY SQL
- **Libraries Used:** Pandas, Matplotlib (for generation of charts and tables)
