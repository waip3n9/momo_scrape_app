# Introduction to this app
This app is written in Python as the backend code and some css,html,jinja2, and javascript for the frontend of the website.
This app uses Flask to create an API that enables users to key in the product that they wish to search in an online shopping website, "momo".
This app particularly focuses on showing the items that matters most to a user without all the other advertisements which sometimes can be confusing.
It shows the most popular products from top to bottom and a link that will redirect users to the details of the product.
I have some ideas on how to improve the app further and it will be updated over time. For now this should be sufficient for use.

# Main Modules used
- MySQL database
- Selenium
- BeautifulSoup
- Flask
- Pandas

# Note
- The number of products can go up to thousands and will take quite some time for it to scrape all the details.
- So for trial purpose, the default number of products is set to 150, which is 5 pages of products.
- If one wishes to scrape all the products, a simple modification in the code can be done in line 134 of the code.

