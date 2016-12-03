Remote-first
============

Remote-first is a job site written with Flask and backed by sqlite. This is the
'live' version of that site, that means that you'll need to modify the `pay_ad`
function to bypass the Stripe integration. This project is primarily just an
example that you can use to learn from. It consists of 4 pages, an index page,
an ad page that is unique based on the ad (which is identical to the preview
page minus the checkout button), and a job submission page. You can read more
about the design of this project here:
https://hungryadmin.com/starting-and-finishing-a-project.html and more about
shutting down this project here: INSERT LINK WHEN PUBLISHED

Screenshots
-----------

#### Front Page

![alt text](https://github.com/gravyboat/remote-first/raw/master/preview_images/remote_first_frontpage.png "Front Page")

#### Example Ad

![alt text](https://github.com/gravyboat/remote-first/raw/master/preview_images/remote_first_example_ad.png "Example Ad")

#### Submission Page

![alt text](https://github.com/gravyboat/remote-first/raw/master/preview_images/remote_first_submission_page.png "Submission Page")

How to set up the project
-------------------------

Setting up the project is just a matter of instaling the appropriate
requirements via the requirements file (preferably inside a virtualenv), 
`pip install -r requirements.txt`, importing the schema to the
appropriately named database
(based on the conf), `sqlite3 db_remotefirst.db < schema.sql` by default while
in the remote-first directory, and then running the main remotefirst.py file.
As noted above keep in mind that specific functionality is expected in terms
of connectivity to Twitter and Stripe, you can easily modify these sections
to exclude those requirements like I did during development.
