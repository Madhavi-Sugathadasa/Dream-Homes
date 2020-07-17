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
