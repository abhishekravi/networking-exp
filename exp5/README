Experiment 5 : Roll Your Own CDN milestone
------------------------------------------

------------------------------------
The HTTP server was created in java.
------------------------------------
A simple program that takes in a http request and returns the content requested. The inputs for this program are the port number and the origin server address.
The program first checks if the file is available locally in the chache, if yes then return the content from there, if not then ask the origin server for the file content. When we get the file from the server, we update the cache by writing the file locally as well.
Each time we retrieve the file from the cache, we update the cache frequency by incrementing it by 1.

Everytime we write a file into the cache, we keep checking the amount of freespace available. When the amount reaches to 100kb , we remove the file with the lowest frequency

-------------------------------------
The DNS server was built using python
-------------------------------------
The DNS server has a udp socket to handle all the requests. The incoming query is first deconstructed to get the query name. The source ip is then be sent to the CDN to get the best replica ip for this source ip. Once the ip is fetched it is then reconstructed into the dns answer format which is then sent back to the client.

---------------
The CDN Program
---------------
We have small performance measuring programs at the replicas. These will be started along with the http servers. We have a path resolver program on the dns server side, which is called each time a dns request is received. the dns server internally calls the pathfinder program which again calls the programs at the servers to get the performance values from each server.

We use active measures to get the best replica ip address. We choose the best ip based on the latency(we used scamper for this), time to connect(we just created a tcp socket and recorded the time taken to establish the connection) and the geographical location(we calculated the distance by getting the latitude and longitude of the source ip using http://freegeoip.net/json/)

When ever a client requests a resolution, this is stored along with the best replica chosen in the cache(we write it into a file "paths.txt"). This file will be read each time the server stats up. We have put up a limit of 50 hits, for this to be updated. After a client asks for a resolution, 50 times, we refresh that ip's replica by calling the servers again. 

This ensures that we do not have to keep calling the servers everytime to resolve the address and the address will be refreshed after a while if there is any change in their performance

scripts to run
--------------
The DNS server can be run using ./dnsserver -p <port> -n <name>
The HTTP server can be run using ./httpserver -p <port> -o <origin>
scripts to deploy, run or stop the servers ./[deploy|run|stop]CDN -p <port> -o <origin> -n <name> -u <username> -i <keyfile>

---------------------------------------------
What could have been improved with more time:
---------------------------------------------
At the CDN part we can perhaps have a dynamic pinging mechanism that would keep updating the best replica address in a file every 1 second(some small interval). This would probably make the resolution much quicker. But we would have to come up with a mechanism to ensure that the file is not read and written at the same time.

currently we have a very simple form of caching at the web servers. This could be upgraded to make it more robust, and ensure we are chaching only the most requested data. maybe even compression so that we can store more at chache(would lead to more overhead to compress and decompress...is this faster that getting the file from origin???)
