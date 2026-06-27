# Cinematch

Cinematch is a premium movie recommendation web application built with Python Flask and powered by ShaktiDB (a PostgreSQL-compatible database). It features a modern, glassmorphism UI, interactive movie rating, and an intelligent recommendation algorithm.

## Features
*   **Sleek UI:** Dark mode, glassmorphism aesthetic, and dynamic responsive grid.
*   **Smart Recommendations:** Recommends top-rated movies based on your favorite genres.
*   **Dockerized:** Easily deployable using Docker and Docker Compose.

## Prerequisites
*   Docker and Docker Compose
*   (Optional) A running instance of ShaktiDB or standard PostgreSQL.

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/cinematch.git
    cd cinematch
    ```

2.  **Configure the Database:**
    Ensure your database configuration matches the environment variables in `docker-compose.yml`. By default, it is configured to connect to a database on `172.17.0.2:8080`.

3.  **Start the Application:**
    ```bash
    docker-compose up -d --build
    ```

4.  **Initialize Mock Data:**
    Run the initialization script inside the web container to create tables and seed data:
    ```bash
    docker-compose exec web python init_db.py
    ```

5.  **Access the Website:**
    Navigate to `http://localhost:5000` in your web browser.
