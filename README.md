# Flask Backend API Template

This project is a template application designed for backend API development using Flask.

## Installation

1. Clone this project:
    ```bash
    git clone https://github.com/username/project-name.git
    cd project-name
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    source venv/bin/activate  # MacOS/Linux
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Start the application:
    ```bash
    flask run
    ```

2. Test the API using your browser or a tool like Postman:
    - `GET /api/v1/resource`: Example of a GET request.
    - `POST /api/v1/resource`: Example of a POST request.

## CLI Commands

This project includes several CLI commands to manage database migrations.

1. Initialize the database:
    ```bash
    python db_cli.py init
    ```
    This command initializes the database for migrations.

2. Create a new migration:
    ```bash
    python db_cli.py migrate --message "your migration message"
    ```
    This command creates a new migration with the specified message. The default message is "migration".

3. Apply the latest migrations:
    ```bash
    python db_cli.py upgrade
    ```
    This command applies all the latest migrations to the database.

4. Downgrade the database:
    ```bash
    python db_cli.py downgrade --revision "revision_id"
    ```
    This command downgrades the database to the specified revision. The default is one step back.


## Contribution

If you would like to contribute, please open an issue first. Submit your changes via a pull request.

1. Fork the project (click the Fork button at the top right)
2. Create a new branch (`git checkout -b new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push the branch (`git push origin new-feature`)
5. Open a pull request

## License

This project is licensed under the MIT License. For more information, see the `LICENSE` file.
