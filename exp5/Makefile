# define a makefile variable for the java compiler
#
JCC = javac

# (the default one in this case)

default: ReqHandler.class Server.class
	@chmod +x deployCDN
	@chmod +x runCDN
	@chmod +x stopCDN
	@chmod +x httpserver
	@chmod +x dnsserver
	@chmod +x performanceReader

# this target entry builds the Server class
Server.class: Server.java
	@$(JCC) Server.java
# this target entry builds the ReqHandler class
ReqHandler.class: ReqHandler.java
	@$(JCC) ReqHandler.java


