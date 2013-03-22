Who Have I Been Talking To
=====================

"Who Have I Been Talking To" (aka WHIBTT) is a visualization of the users' email account that can provide insights about his/her relationships with others and how those relations have evolved over time.

![Overview](/docs/overview.png)


About the project
=====================

Our project's visualization is divided into three distinct areas:
- Main Timeline - This area occupies the top of the visualization. This is the main visualization partition of
the tool and it provides information about e-mail relationships on a monthly basis.
- Secondary Timeline - Located on the left lower part of the visualization, the Secondary Timeline shows the same information as the main but on a daily basis.
- Topic Cloud - Like a typical tagcloud, this visualization has the purpose of showing the most discussed/distinctive topics present in e-mail subjects.

The project is considered closed (this means that we don't plan to work on it any longe) but with (already identified) improvement opportunities :)

For more information, I strongly recommend you to read the [full paper](docs/Final Papel.pdf)

About the project Part II - A little history
=====================

This project was developed by me and Tiago Garcia while we were taking the "Personal Information Management and Visualization" course at Instituto Superior Técnico.
As part of the course, we have written a small paper describing and praising our work. Later on, that paper was presented in the AVI'12 conference. You can check the final paper [here](http://dl.acm.org/citation.cfm?id=2254647&preflayout=tabs).

About the technology
=====================

For this project we used:
- Python (2.7) - The backbone of the application, where it all happens. Literally.
- Cherrypy - A Minimalist Python Web Framework that allows developers to build web applications in much the same way they would build any other object-oriented Python program. 
- jQuery / jQuery UI- For dealing with the client side scripts and UI.
- Protovis - A nice visualization toolkit that uses JavaScript and SVG for web-native visualizations.

About using it
=====================

This project is just a proof of concept, a prototype. Issues such as performance, security, etc, were not taken into account. 
The objective was to show our idea through a simple and fast implementation with just a few weeks of analysis, development and tests.

Having said that, here are the steps you should follow to see it live:
1) Download and install Python 2.7. It may just work on other versions, but this "official" python version for this project

- Download and unzip this project to your computer (duh!)
- Run (double click) server.py at the root of the project. This will start a local websserver and automatically open a browser's window.
- Enter your email (gmail accounts only) and password and login.
- WHIBTT will now start indexing your email. Indexing all of your emails will take it's time but the application lets you see results with just a few emails indexed.
