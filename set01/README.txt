Project 1: Simple Client

REQUIREMENT: Implementing a client program which communicates with a server using sockets. The server asks your program to solve hundreds of simple mathematical expressions. If the program successfully solves all of the expressions, then the server will return a secret flag that is unique for each student id.

APPROACH: In order to achieve the above requirement we decided to use java sockets api.

We have one java class Client.java which accomplishes the following in the respective methods.

Method main

We pass the input to a input handler to make sure the input parameters are proper, then we use the server socket api to create a connection with the server by passing in the port id and the url.
If the connection is established we use the OutputStream and the DataInputStream api to write and read data respectively.
Once connection is established the data DataInputStream reads the data into a byte buffer of size 256. This data is then converted from the ASCII format into a string for further processing.
Before processing the data we use regular expressions (pattern matching) on the data to make sure that the data received is as per the protocol standards mentioned in the program.
If the data is per conforms to the acceptable standards, we enter a while loop which continues processing messages from the server until the message BYE is encountered.
The data is split into further components based on the messages received in the response. 
If the status message contains the message STATUS, then the data part of the response is separated using the line feed as a terminator and sent to the method processExpression() for further processing. Anything after the line feed is ignored.
If the status message contains the message BYE then the data part of the response is separated using the line feed as a terminator and send to the method processBye for further processing. Anything after the line feed is ignored.
Once the output from the methods processExpression is received, the main method writes the response back to the server and reads the next incoming message from the server. This continues until the message contains BYE in it.

Method processExpression
In this method the data part of the response is further split on the basis of an empty space to get three components.
First components is a number, seconds is a mathematical operand which could be +, - , * or /. The last one is a number.
The mathematical operation is then performed on the numbers based on the type of the mathematical operand by invoking the getResponse method and the response is sent back to the main method.

Challenges faced.
The main challenges we faced in this program was converting the response in the ASCII format. It was confusing at first, we tried to convert the message into hex format to send to the server. However after further investigation we used ASCII encoding and decoding on the messages to solve this problem.
Other than that, we tried to implement the ssl implementation, we got till the step of getting the client certificate .pem file from the server using $openssl s_client -host cs5700sp15.ccs.neu.edu -port 27994. Added it to the key stored but were unable to cacerts appropriately to make the connection.


Testing:
We first created the regex for both the pattern the one with STATUS protocol and one with BYE protocol. We test various strings of data to see if it confirmed to the regex and then proceeded with the rest of the program.
