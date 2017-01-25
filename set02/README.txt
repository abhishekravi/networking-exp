Project 2: Web Crawler
Aim: Implementation of a web crawler (sometimes known as a robot, a spider, or a screen scraper) is a piece of software that automatically gathers and traverses documents on the web.
In this case we would be traversing the site FakeBook with the Login Page available at the below url.
http://cs5700sp15.ccs.neu.edu/accounts/login/?next=/fakebook/


High Level Approach

We used the below approach to complete the programs.
Following is the hight level approach. 
1. We use the url given above to get to the login page of fake book via sockets and an   HTTP GET call. 
2. Once we get the HTML via a successful GET call we extract its parameters using buildHTTPRequest method to create the next request.
namely the HTTP header inputs ie Cookie:We add the cookies received from the response namely the csrftoken and the sessionid.
3. Along with the Cookie header we add the headers Host, From, User-Agent , Connection: keep-alive, Content-Type and Content-Length to build the next request header.
4. We then add the data to the body of the Http request. The data mainly includes username, password , csrfmiddlewaretoken and next fields.
with this data we make the POST call to login into to the server.
5. Once a successful login is done we parse the href links on the all the web page recursively and store them into different Collections. 
6. These links are use to make the concurrent GET calls. In order that no GET call maybe repeated twice we make use of different Collections ie. visited, toVisit and current.
7. These keep a tract of the links we have visited so that they are not repeated, the links which we need to traverse and the once that are currently getting executed.
8. For each of these we make a GET call using the buildHTTPRequest as mentioned from Step 1 to 3. 
9. The status codes mentioned below are also appropriately handled. In case an a STATUS 500 message is received the crawler re-tries the request for the URL until the request is successful. Similarly in case of 301 and 302 it does a redirect and for STATUS 403 and STATUS 404 the response is ignored and next traversal begins for the other urls.  
6. Along with the href the Jsoup parser for the html body keeps a track of the h2 elements  to discover any secret flags. IF a secret flag is received its printed out.
7. The moment 5 secret flags are received the program breaks from the continuous loop and terminates.

200: STATUS 0K
301:PERMANENT MOVED
302: MOVED TEMPORARILY
403: FORBIDDEN
404: NOT FOUND
500: INTERNAL SERVER ERROR.

Libraries Used.
java Sockets are used for making sockets connections for making socket connection.
Jsoup for parsing the HTML data.

CHALLENGES: 
1.The first challenge was to finalize upon a library. That took some time. Along with the approach as to the fact that the Jsoup should only parse data and not make any calls.

2. Logging into the server took a day. We had things in place but unfortunately we were trying to log in from the eclipse.

3. Setting up the header fields, going through the headers, trying and checking each request using tools like POSTMAN helped.

4. The first call on login was a redirect, this took time to figure out.
5. Creating a new socket on internal server error too required analysis.



