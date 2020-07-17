# Dream Homes :house: :house_with_garden:
AA web application named **Dream Homes (dreamhomes.com.au)** was created  for advertising **real estate properties** in Australia in order to find the latest **homes for sale or rent**. using **Python (Django), jQuery, SQLite3, HTML5, CSS3 &amp; Bootstrap**

View Screencast on https://youtu.be/ys027FniCmQ


There are two types of Ad packages named **Standard package** and **Premium package**. In order to advertise a property for sale,  Standard package costs AUD 750 and Premium package AUD 1000. For rental property advertisement, Standard package costs AUD 250 and Premium package AUD 400

If you choose Premium package, your property will appear higher in search results.
You can create an advertisement now and save it and pay later. But, if you saved an ad, it will not be displayed on results until you have paid.

---

### **Features:**

1. **_Registration, Login, Logout, forgot password_**

Site users are able to register for the web application with a username, password, first name, last name and email address. Users are able to log in and log out of the website. If users forget their passwords, they can reset the password via an email reset password link.

---

2. **_Viewing Ads_**

Once logged in, users are taken to the home page where they are able to search properties for sale or rent in a given location.

Users are able to **filter the search criteria** by the following fields:
```
    Property type - (select from a dropdown list)
    Location - (select suburb, state and postcode from autocomplete dropdown)
    Include surrounding area checkbox - if this is checked, all sale or rent properties within 25 kms from the above location will be included in search results 
    No of bedrooms -  (select from a dropdown list)
    No of bathrooms -  (select from a dropdown list)
    No of parking -  (select from a dropdown list)
    Price range - slider to select a price range
```
Users are able to **sort the results** by “Most Recent listing” or  by “Location (A-Z)” or by “Location (Z-A)”  or by “Price (High - Low)” or by “Price (Low - High)”  

Each list item displays a summary of Ad details including an image slider, no of bedrooms, no of bathrooms , no of parking, address  and price (for rental properties price will be a weekly amount, for sale properties it will be a price range or if the price is not entered whether it is sale, auction or contact agent). There is a link to see more details of a selected Ad

**Pagination is available** on this page. Currently displays nine Ads per page & it is a configurable parameter.

---

3. **_More Details page_**

Once users click on “Details” link from a selected Ad, they are able to see **additional details** about the Ad. Especially they are able to send messages to the seller from this page.

Following details are displayed on this page:
```
    Image slider to see all uploaded Images
    Property address on a Google map view
    No of bedrooms, bathrooms and Parking
    Floor plan if uploaded
    Auction date & time if available 
    Inspection dates and times if available
    Additional description about the property
```
---

4. **_Post an Ad_**

Once logged in, users are able to post an Ad about rental or sale of property. They can pay now and make ad live or save now & pay later in order to make it live

Following details need to be provided in order to publish a sale Ad:
```
    Select preferred AD package - Standard or Premium
    From Price
    To price
    Ad type - for sale or for auction or contact agent or under contract
    Title
    Description
    Property Type - (i.e. whether it is a Apartment or House or Townhouse etc..)
    Auction Date - if available 
    Address Line
    Location -  (select suburb, state and postcode from autocomplete dropdown)
    No of bedrooms (select from a dropdown list)
    No of bathrooms (select from a dropdown list)
    No of Parking (select from a dropdown list)
    Garages (select from a dropdown list)
    Land Area - if available
    Contact name
    Email
    Mobile
    Floor plan - upload if available 
    Upload up to 6 images. At leases one image required
    Upcoming inspection dates if available 
    Finally user need to accept terms and condition of posting an Ad.
```

Following details need to be provided in order to publish a rental Ad:
```
    Select preferred AD package - Standard or Premium
    Weekly price
    Title
    Description
    Property Type - (i.e. whether it is a Apartment or House or Townhouse etc..)
    Address Line
    Location -  (select suburb, state and postcode from autocomplete dropdown)
    No of bedrooms (select from a dropdown list)
    No of bathrooms (select from a dropdown list)
    No of Parking (select from a dropdown list)
    Garages (select from a dropdown list)
    Contact name
    Email
    Mobile
    Floor plan - upload if available 
    Upload up to 6 images. At leases one image required
    Upcoming inspection dates if available 
    Finally user need to accept terms and condition of posting an Ad
```   
---

5. **_Payment_**

If users select  “Go to Payment” link on above, then they will be redirected to **Stripe payment** page where user will be able to enter their credit card details and make a payment. If a user decided to click “cancel payment” the item will be saved without a payment and redirected to details page where they can edit or make payments. But if payment is successful, ad will be Live and user can edit it if needed

---

6. **_View & Edit Ads posted by me (My Ads)_**

There is a link at the top of navigation bar named “My Ads”. Once they click on this link, users are able to see list of all Live or Saved Ads which are posted by them (for sale and for rent items are listed in two separate tabs)
Under each Ad there is a **“Edit” link** where users are able to edit the details of Ads which are already published.
Under each ad on Saved Ads section there are links for ‘Edit” or “pay Now”. If users click on “Pay Now” then they can select the ad package and go to Stripe payment page.

---

### **Technical Details:**

Developed using **JavaScript**, **Python**, and **SQL**. Used **Django**, **sqlite3 DB**, **jQuery** and **Bootstrap**.

**Below is a brief description about the project structure:**

Used Django’s **in built Authentication and Authorisation system** for user registration, login, logout and forgot password sections.

---

**12 tables were used** in the sqlite3 DB apart from the Django’s inbuilt user tables.
```
    1.  Locations table (Location Model) - maintain a list of all suburbs in Australia including their postcode, state, longitude and latitude. I was able to find a free csv file online with above details. I wrote a python function to insert data into the table by reading the csv file
    2.  Buy_ad_items  table (Buy_Ad_Item Model)  - maintain a list of all sale properties posted by sellers
    3.  Buy_item_inspections table (Buy_Item_Inspection Model)  - maintain inspection details of sale properties - date & time of each inspection, seller can enter up to 4 inspections
    4.  Buy_item_pictures table (Buy_Item_Picture Model)  - maintain pictures of sale properties, up to 6 Images
    5.  Buy_item_ad_types table (Buy_Item_Ad_Type Model)  - maintain list of sale item types
    6.  Rent_ad_items table (Rent_Ad_Item Model)  - maintain a list of all rent properties posted by sellers
    7.  Rent_item_inspections table (Rent_Item_Inspection Model)  - maintain inspection details of rent properties - date & time of each inspection, seller can enter up to 4 inspections
    8.  Rent_item_pictures table (Rent_Item_Picture Model)  - Keep pictures of rent properties, up to 6 Images
    9.  Property_types table (Property_Type Model)  - maintain a list of all property types
    10.  Bedroom table (Bedroom Model)  - maintain a list of numbers of bedroom categories 
    11.  Bathroom table (Bathroom Model)  - maintain a list of number of bathroom categories
    12.  Parkings table (Parking Model)  - maintain a list of numbers of parking categories
```

----

**21 views were used** on views.py

```
    1. login_view  - user login 
    2. register_view - user registration
    3. logout_view - user logout
    4. forgot_password - resetting password if you forgot it. Email link will be sent to user’s email
    5. index - home page. there are two tabs named ‘Buy’ and ‘Rent’, users are able to see all live property listings
    6. autocomplete_location - ajax based autocomplete for location
    7. ad_more_details - view more details of a selected Ad
    8. post_ad - post an ad either sale or rental property
    9. edit_ad - edit Live ad (paid ads)
    10. edit_saved_ad - edit non Live ads which are saved. (not paid ads)
    11. delete_pic - delete Images uploaded for an ad
    12. delete_floorplan - delete floor plan image uploaded for an ad
    13. payment - process payment redirection to stripe payment page.  Depending on the package,  user selected price items will be retrieved from stripe Api.
    14. payment_success  - when a payment is successful, user will be redirected to this view by stripe
    15. payment_cancel - when a payment is canceled from stripe payment page, user will be redirected to this view by stripe
    16. payment_packages - for saved ads which are not paid, will have a “Pay Now” link. Once clicked on this link user will be taken to this view where they can select the ad package depending on rent ad or sale item and pay for it in order to make the Ad live
    17. view_my_ads - view list of live ads published by logged in user. 
    18. view_my_saved_ads - view list of non live (saved ads without payment) ads published by logged in user. 
    19. my_ad_more_details - more details of selected live ad, published by logged in user
    20. my_saved_ad_more_details - more details of non-live ad (saved ads without payment) published by logged in user
    21. send_message  - send email to seller
```

---

Following  **configurable parameters** were added to **settings.py**
  
Following variables were configured for email send functionality: 
```    
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = (this was configured using environment variable )
    EMAIL_HOST_PASSWORD = (this was configured using environment variable )
    DEFAULT_FROM_EMAIL = (this was configured using environment variable )
```

Added following configureable parameters to configure image save path:
```
    MEDIA_URL = "/Media/"
    MEDIA_PATH = "Media"
```
Added following configureable parameters to display currency & its symbol:
```    
    CURRENCY = 'AUD'
    CURRENCY_SYMBOL =‘$'
```
Added following configureable parameters to keep no of Ads per page:
```
    NO_OF_ADS_PER_PAGE =9
```
Added following configureable parameters to keep Stripe payment function:
```    
    STRIPE_PUBLISHABLE_API_KEY =  (this was configured using environment variable )
    STRIPE_SECRET_API_KEY =  (this was configured using environment variable )
    PAYMENT_SUCCESS_URL ='http://127.0.0.1:8000/payment_success?session_id={CHECKOUT_SESSION_ID}'
    PAYMENT_CANCEL_URL ='http://127.0.0.1:8000/payment_cancel'
```
Added following configureable parameter to keep Google Map key:
```
    GOOGLE_MAP_KEY =  (this was configured using environment variable )
```

---

**_NOTE:_**

In order to implement filter functionality for getting the ad items from suburbs within  25 kilometres of a given location, I had to use sqlite3 math extension to get acos, cos, sin, radians of given longitudes and latitudes. Sqlite3 was built with extension loading disabled. So I had to install sqlite3 via Homebrew and then build Python from scratch with the appropriate sqlite3 library linked.

Following commands were run in order to enable above functionality:

```
    brew install sqlite3
    brew install xz
    brew install openssl
    brew install gdbm
    brew install pyenv
```

PYTHON_CONFIGURE_OPTS="--enable-loadable-sqlite-extensions --enable-optimizations --with-openssl=/usr/bin/openssl" LDFLAGS="-L/usr/local/Cellar/sqlite/3.32.1/lib -L/usr/local/opt/zlib/lib" CPPFLAGS="-I/usr/local/Cellar/sqlite/3.32.1/include -I/usr/local/opt/zlib/include" pyenv install 3.8.2

Reference : https://stackoverflow.com/questions/57977481/how-to-use-enable-load-extension-from-sqlite3

Also I had to download following extension-functions.c file for Sqlite web  (https://www.sqlite.org/contrib/download/extension-functions.c?get=25) and compile it using following command before using it in the python code

gcc -g -fPIC -dynamiclib extension-functions.c -o math

---


