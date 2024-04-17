# Warbler

Warbler is a social media platform where users can post short messages, follow other users, like messages, and more.

## Getting Started

To get started with Warbler, follow these steps:

1. Clone this repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using `pip install -r requirements.txt`.
4. Set up the environment variables for `SECRET_KEY` and `DATABASE_URL`.
5. Run the Flask application using `python app.py`.
6. Access the application in your web browser at `http://localhost:5000`.

## Features

- **User Authentication**: Users can sign up, log in, and log out.
- **User Profiles**: Users have profiles where they can update their information and view their messages.
- **Messages**: Users can post short messages (warbles) for others to see.
- **Likes**: Users can like messages posted by other users.
- **Follows**: Users can follow other users to see their messages in their timeline.

## File Structure

- `app.py`: Contains the main Flask application and routes.
- `models.py`: Defines the database models using SQLAlchemy.
- `forms.py`: Defines the forms for user input using Flask-WTF.
- `templates/`: Contains HTML templates for rendering pages.
- `static/`: Contains static files such as images and CSS stylesheets.

## Dependencies

Warbler uses the following dependencies:

- Flask: A micro web framework for Python.
- Flask-WTF: Integration of WTForms with Flask for handling forms.
- Flask-DebugToolbar: Debug toolbar for Flask applications.
- SQLAlchemy: SQL toolkit and Object-Relational Mapping (ORM) for Python.
- Flask-Bcrypt: Flask extension for hashing passwords.

## Contributing

If you would like to contribute to Warbler, feel free to fork the repository and submit a pull request. Your contributions are always welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

