import java.io.DataInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.ConnectException;
import java.net.Socket;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Client {

	private static int defaultPort = 27993;
	private static String preMsg = "cs5700spring2015";
	private static String SPACE = " ";
	private static String LINEFEED = "\n";
	private static boolean DATAOK = true;
	private static String host = "";
	private static int port = defaultPort;
	private static String neuID = "";

	/**
	 * main method.
	 * 
	 * @param arg
	 */
	public static void main(String arg[]) {

		Socket socket;
		handleInput(arg);
		if (DATAOK) {
			try {
				String response = "";
				String dataToSend = "";
				String key = "";
				byte[] data = new byte[256];
				socket = new Socket(host, port);
				// ssl connection
				/*
				 * try { SSLSocketFactory f = (SSLSocketFactory)
				 * SSLSocketFactory.getDefault(); SSLSocket sslSocket =
				 * (SSLSocket) f.createSocket(host,27994);
				 * System.out.println("ssl port:" + sslSocket.getLocalPort());
				 * sslSocket.startHandshake(); } catch(Exception e) {
				 * e.printStackTrace(); System.out.println(e.getMessage()); }
				 */
				DataInputStream inputStream = new DataInputStream(
						socket.getInputStream());
				OutputStream outputStream = socket.getOutputStream();
				outputStream
						.write((preMsg + SPACE + "HELLO" + SPACE + neuID + LINEFEED)
								.getBytes("US-ASCII"));
				while (!response.contains("BYE")) {
					dataToSend = "";
					inputStream.read(data);
					if (data == null)
						throw new Error(
								"Ouput from the server is null. Terminating Program.");
					response = new String(data, "US-ASCII");
					Client.validateOutput(response);
					if (preMsg.equals(response.substring(0, preMsg.length()))) {
						if (response.contains("BYE")) {
							key = processBye(response);
							break;
						}
						if (response.contains("STATUS")) {
							dataToSend = processExpression(response.substring(
									24, response.indexOf(LINEFEED)).trim());
							outputStream.write(dataToSend.getBytes("US-ASCII"));
						}
					} else {
						System.out.println("message invalid");
						break;
					}
				}
				System.out.println("key:" + key);
				inputStream.close();
				outputStream.close();
				socket.close();
			} catch (ConnectException e) {
				System.out
						.println("connection exception, please check connection and data");
			} catch (IOException ioe) {
				System.out
						.println("io exception, please check connection and data");
			}
		} else {
			System.out
					.println("expected input <-p port> <-s> [hostname] [NEU ID]");
		}

	}

	/**
	 * Method to handle input.
	 * 
	 * @param neuID
	 * @param host
	 * @param port
	 * @param arg
	 * @param ssl
	 */
	public static void handleInput(String[] arg) {
		try {
			if (arg.length > 0) {
				if (arg[0].equals("-p")) {
					handlePostInput(arg);
				} else if (arg.length == 2 && !arg[0].equals("-p")) {
					handleOtherInput(arg);
				} else {
					DATAOK = false;
				}
			} else {
				DATAOK = false;
			}
		} catch (Exception e) {
			DATAOK = false;
		}
	}

	private static void handleOtherInput(String[] arg) {
		host = arg[0];
		port = defaultPort;
		neuID = arg[1];
	}

	private static void handlePostInput(String[] arg) {
		if (arg.length == 4) {
			port = Integer.parseInt(arg[1]);
			host = arg[2];
			neuID = arg[3];
		} else {
			DATAOK = false;
		}
	}

	/**
	 * method to process the expression.
	 * 
	 * @param expression
	 *            this contains the expression to be evaluated
	 * @return the response to be sent
	 */
	private static String processExpression(String expression) {
		int operand1 = 0;
		int operand2 = 0;
		String response = "";
		String[] operands;
		if (expression.contains("+")) {
			operands = expression.split("\\+");
			operand1 = Integer.parseInt(operands[0].trim());
			operand2 = Integer.parseInt(operands[1].trim());
			response = getResponse("add", operand1, operand2);
		} else if (expression.contains("-")) {
			operands = expression.split("\\-");
			operand1 = Integer.parseInt(operands[0].trim());
			operand2 = Integer.parseInt(operands[1].trim());
			response = getResponse("sub", operand1, operand2);
		} else if (expression.contains("*")) {
			operands = expression.split("\\*");
			operand1 = Integer.parseInt(operands[0].trim());
			operand2 = Integer.parseInt(operands[1].trim());
			response = getResponse("mul", operand1, operand2);
		} else if (expression.contains("/")) {
			operands = expression.split("\\/");
			operand1 = Integer.parseInt(operands[0].trim());
			operand2 = Integer.parseInt(operands[1].trim());
			response = getResponse("div", operand1, operand2);
		}
		return response;
	}

	/**
	 * this method is to extract the key.
	 * 
	 * @param msg
	 *            incoming message
	 * @return key
	 */
	private static String processBye(String msg) {
		String key = msg.substring(17, msg.indexOf("BYE\n")).trim();
		return key;
	}

	/**
	 * this is where the operation is executed.
	 * 
	 * @param operation
	 *            operation to perform
	 * @param operand1
	 *            operand1
	 * @param operand2
	 *            operand2
	 * @return solution expression to be sent
	 */
	public static String getResponse(String operation, int operand1,
			int operand2) {
		int answer = 0;
		String response = "";
		if (operation.equals("add")) {
			answer = operand1 + operand2;
		}
		if (operation.equals("sub")) {
			answer = operand1 - operand2;
		}
		if (operation.equals("mul")) {
			answer = operand1 * operand2;
		}
		if (operation.equals("div")) {
			answer = Math.round(operand1 / operand2);
		}
		response = preMsg + SPACE + answer + LINEFEED;
		return response;
	}

	/*
	 * @method:validateOutput validates the output pattern. Throws an error if
	 * the pattern fails to match.
	 */

	public static void validateOutput(String data) {
		Pattern pattern1 = Pattern
				.compile("^cs5700spring2015(\\s)STATUS(\\s)(\\d+)(\\s)[\\+|\\-\\*\\/](\\s)(\\d+)\n(.*)");
		Pattern pattern2 = Pattern
				.compile("^cs5700spring2015(\\s)(.*)(\\s)BYE\n(.*)");

		Matcher matcher1 = pattern1.matcher(data);
		Matcher matcher2 = pattern2.matcher(data);
		if (matcher1.find() || matcher2.find()) {
			return;
		} else {
			throw new Error("Pattern Match error. Terminating program Client.");
		}
	}
}
