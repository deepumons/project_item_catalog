# Item Catalog

# About

A light weight RESTful web application that maintains a list of items, and their categories as a product catalog. This project is my submission for the Udacity Full Stack Nanodegree program.

# Contents

The project is organized in the following way:
/ - Root folder
  /static - Contains the CSS StyleSheet and images used in this project.
  /templates  - Contains the html template files referenced by the project.
project.py  - The main python file.
database_setup.py - Setup up the ORM layer, classes, etc.
database_init.py - Contains python code to initialize the database with sample data.

# Acknowledgements

The theme/skin of the project is adapted from the Personified theme from <a href="http://www.freecsstemplates.org/">Free CSS Templates</a>. Used under Creative Commons Attribution 2.5 License.

# Dependencies

The project has the following Dependencies:
1. FLASK framework
2. SqlAlchemy as the data base access / ORM layer
3. Google OAuth as the authentication provider
4. Virtualbox + Vagrant for providing the run time for the application

# Installation and running the project

1. Install Vagrant and VirtualBox
2. Clone the fullstack-nanodegree-vm from https://github.com/udacity/fullstack-nanodegree-vm
3. Launch the Vagrant VM (using vagrant up command)
4. Login to the VM (using vagrant ssh command)
5. Clone this project from  https://github.com/urdeepak/project_item_catalog
6. Navigate to /vagrant/project_item_catalog folder
7. Setup the database by running python database_setup.py
8. Fill the database with sample data by running python database_init.py
9. Start the application by running python project.py
10. Access the application by visiting http://localhost:5000 from the browser
