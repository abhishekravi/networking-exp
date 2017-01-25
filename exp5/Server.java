import java.net.InetSocketAddress;

import com.sun.net.httpserver.HttpServer;

public class Server {

	/**
	 * main method that starts the http server
	 * @param args command line arguments
	 * @throws Exception
	 */
	public static void main(String[] args) throws Exception {
		if (checkArgs(args)) {
			try {
				int port = Integer.parseInt(args[1]);
				//int port = 54685;
				String addr = args[3];
				//String addr = "ec2-52-4-98-110.compute-1.amazonaws.com";
				HttpServer server = HttpServer.create();
				server.bind((new InetSocketAddress(port)),1);
				server.createContext("/", new ReqHandler(addr));
				server.setExecutor(null); // creates a default executor
				server.start();
			} catch (Exception e) {
				System.out.println("terminated due to exception:");
				e.printStackTrace();
			}
		} else {
			System.out
					.println("Invalid arguments. expected: -p <port> -o <origin>");
		}
	}

	/**
	 * method to check if the input arguments are valid
	 * @param args arguments
	 * @return boolean
	 */
	private static boolean checkArgs(String[] args) {
		boolean ret = true;
		if (args.length != 4 || !args[0].equals("-p") || !args[2].equals("-o")) {
			ret = false;
		}
		return ret;
	}
}
