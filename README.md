# EpicCollaborate

EpicCollaborate is a platform designed to connect Sponsors and Influencers, enabling sponsors to get their products or services advertised and allowing influencers to receive monetary benefits. This platform provides functionalities for influencers, sponsors, and admins, facilitating smooth coordination and management of campaigns and engagements.

## Project Details

- **Project Name**: EpicCollaborate
- **Project Statement**: To build a platform that connects sponsors and influencers for advertising and monetary benefits.
- **Course**: MAD 1 Project
- **Author**: Abhinav Sonone
- **Roll Number**: 22f1001278 (IITM BS Data Science)

## Features

- **User Roles**:
  - **Influencers**: Can manage their profiles and engage in campaigns.
  - **Sponsors**: Can create campaigns and manage sponsorship requests.
  - **Admin**: Has additional rights to blacklist or delete users and remove inappropriate campaigns.
- **Database**: The project started with defining the database schema, identifying entities, attributes, and relationships.
- **Frontend**: Developed using Flask, Bootstrap, and Jinja2 with templates for signup, navigation, and dashboard.
- **Backend**: Developed iteratively alongside frontend, with separate functionalities for influencers, sponsors, and admin.
- **ER Diagram**: The database schema includes entities such as users, campaigns, and requests.

## Tech Stack

- **Frameworks and Libraries**:
  - Flask
  - SQLAlchemy
  - Bootstrap
  - Jinja2
  - SQLite
  - Plotly Express

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/epiccollaborate.git
   ```

2. Navigate to the project directory:

   ```bash
   cd epiccollaborate
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:

   ```bash
   python setup_db.py
   ```

5. Run the application:

   ```bash
   python app.py
   ```

## Usage

- Access the application at `http://localhost:5000`.
- Sign up as an influencer, sponsor, or log in as an admin to manage the platform.

## ER Diagram

![ER Diagram](path/to/er_diagram.png)

## Debugging and Styling

- Custom CSS styling was implemented to enhance aesthetics and ensure smooth navigation.
- Debugging was performed to refine platform functionality and resolve issues.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
