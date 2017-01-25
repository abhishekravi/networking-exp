import java.io.DataInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

public class Crawler {

	private static String root = "cs5700sp15.ccs.neu.edu";
	private static int port = 80;
	private static String initPath = "/accounts/login/?next=/fakebook/";
	private static String LINEFEED = "\n";
	
	//Various HTTP code handled
	private static String STATUS_200_OK = "OK";
	private static String STATUS_301_PERMANENTLY_MOVED = "PERMANENTLY_MOVED";
	private static String STATUS_302_FOUND = "302_FOUND";
	private static String STATUS_403_FORBIDDEN = "403_FORBIDDEN";
	private static String STATUS_404_NOT_FOUND = "404_NOT_FOUND";
	private static String STATUS_500_INTERNAL_SERVER_ERROR = "500_INTERNAL_SERVER_ERROR";

	//Types of HTTP requests
	private static enum types {
		GET, POST
	};

	private static String userAgent = "Crawler1.0";
	private static String protocol = "HTTP/1.1";
	private static String session = "";
	private static String token = "";
	private static Socket socket;
	private static DataInputStream inputStream;
	private static OutputStream outputStream;
	private static List<String> keys = new ArrayList<String>();
	private static Set<String> visited = new HashSet<String>();
	private static Set<String> toVisit = new HashSet<String>();
	private static List<String> current = new ArrayList<String>();

	/**
	 * main method to execute crawler.
	 * @param args
	 * this will contain user name and password
	 */
	public static void main(String[] args) {
		String response;
		String userid = "";
		String password = "";
		if (args.length == 2) {
			userid = args[0];
			password = args[1];
			try {
				socket = new Socket(root, port);
				inputStream = new DataInputStream(socket.getInputStream());
				outputStream = socket.getOutputStream();
				response = loginPage(userid, password);
				responseParser(response, "/");
				while (keys.size() < 5) {
					for (String link : current) {
						if (otherPage(link))
							break;
					}
					current.clear();
					current.addAll(toVisit);
					toVisit.clear();
					if (current.size() == 0) {
						break;
					}
				}
				inputStream.close();
				outputStream.close();
				socket.close();
			} catch (Exception e) {
				System.out.println("Program failed because of:" + e.getMessage()+ ". please retry");
				e.printStackTrace();
			}
		} else {
			System.out.println("expected input [username] [password]");
		}

	}


	/**
	 * method login to the website.
	 * 
	 * @param password
	 * password
	 * @param userid
	 * userid
	 * @return response page - home page
	 * @throws UnsupportedEncodingException
	 * @throws IOException
	 */
	private static String loginPage(String userid, String password)
			throws UnsupportedEncodingException, IOException {
		String response = "";
		String status = "";
		visited.add(initPath);
		String request = buildHTTPRequest(initPath, types.GET.toString(), null);
		while (!status.equals(STATUS_200_OK)) {
			response = readWrtite(request);
			status = checkResponseFormat(response);
		}
		getCookies(response);
		request = buildHTTPRequest(initPath, types.POST.toString(),
				getData(getHtml(response), userid, password));
		status = "";
		while (!status.equals(STATUS_200_OK)) {
			response = readWrtite(request);
			status = checkResponseFormat(response);
			if (status.equals(STATUS_302_FOUND)) {
				getCookies(response);
				response = redirect(getRedirectURL(response));
				status = checkResponseFormat(response);
			}
		}
		return response;
	}

	/**
	 * method to fetch other pages.
	 * @param url
	 * url to visit
	 * @return
	 * true, if all flags are fetched
	 * @throws UnknownHostException
	 * @throws IOException
	 */
	private static boolean otherPage(String url) throws UnknownHostException,
			IOException {
		String response = "";
		String request = "";
		String status = "";
		visited.add(url);
		while (!status.equals(STATUS_200_OK)) {
			request = buildHTTPRequest(url, types.GET.toString(), null);
			response = readWrtite(request);
			status = checkResponseFormat(response);
			if (status.equals(STATUS_500_INTERNAL_SERVER_ERROR)) {
				response = retry(request);
				status = checkResponseFormat(response);
			}
			if (status.equals(STATUS_302_FOUND) || status.equals(STATUS_301_PERMANENTLY_MOVED)) {
				response = redirect(getRedirectURL(response));
				status = checkResponseFormat(response);
			}
			if (status.equals(STATUS_403_FORBIDDEN)  
					|| status.equalsIgnoreCase(STATUS_404_NOT_FOUND)) {
				return false;
			}
		}
		return responseParser(response, url);
	}

	/**
	 * method which will retry the request till we get a response.
	 * @param request
	 * request to retry
	 * @return
	 * response
	 * @throws UnknownHostException
	 * @throws IOException
	 */
	private static String retry(String request) throws UnknownHostException,
			IOException {
		String response = "";
		String status = STATUS_500_INTERNAL_SERVER_ERROR;
		while (status.equals(STATUS_500_INTERNAL_SERVER_ERROR)) {
			socket = new Socket(root, port);
			inputStream = new DataInputStream(socket.getInputStream());
			outputStream = socket.getOutputStream();
			response = readWrtite(request);
			status = checkResponseFormat(response);
		}
		return response;
	}

	/**
	 * method which check the response to see if it has proper HTTP header 
	 * and set status accordingly.
	 * @param response
	 * response from server
	 * @return
	 * status
	 */
	private static String checkResponseFormat(String response) {
		String status = "";
		String line = Arrays.asList(response.split("\n")).get(0);
		if (line.contains(protocol)) {
			String httpStatus = line.substring(line.indexOf(protocol));
			status = checkResponse(Integer.parseInt(httpStatus.substring(9, 12)));
		} else {
			status = STATUS_500_INTERNAL_SERVER_ERROR;
		}
		return status;
	}

	/**
	 * method to help with page redirection, 302 or 301 HTTP status code.
	 * @param url
	 * url to redirect to.
	 * @return
	 * response
	 * @throws IOException
	 */
	private static String redirect(String url) throws IOException {
		String status = STATUS_302_FOUND;
		String request = "";
		String response = "";
		while(status.equals(STATUS_302_FOUND) || status.equals(STATUS_301_PERMANENTLY_MOVED)) {
			visited.add(url);
			request = buildHTTPRequest(url,
				types.GET.toString(), null);
			response = readWrtite(request);
			status = checkResponseFormat(response);
			getCookies(response);
			if (status.equals(STATUS_500_INTERNAL_SERVER_ERROR)) {
				response = retry(request);
			}
		}
		return response;
	}

	/**
	 * this method just writes a request and fetches the response.
	 * @param request
	 * request to be sent
	 * @return
	 * response
	 * @throws IOException
	 */
	private static String readWrtite(String request) throws IOException {
		byte[] data = new byte[4048];
		outputStream.write(request.getBytes("UTF-8"));
		inputStream.read(data);
		return new String(data, "UTF-8").trim();
	}

	/**
	 * to get data for login.
	 * 
	 * @param httpBody
	 *            body from response
	 * @param password
	 * password for login
	 * @param userid
	 * user id for login
	 * @return used data to be sent
	 */
	private static String getData(String httpBody, String userid,
			String password) {
		StringBuffer data = new StringBuffer();
		String next = "";
		String token = "";
		Elements elements;
		Document document = Jsoup.parse(httpBody);
		elements = document.select("input[name=next]");
		next = elements.get(0).attr("value");
		elements = document.select("input[name=csrfmiddlewaretoken]");
		token = elements.get(0).attr("value");
		data.append("username=").append(userid).append("&password=")
				.append(password).append("&csrfmiddlewaretoken=").append(token)
				.append("&next=").append(next);

		return data.toString();
	}

	/**
	 * method to get the redirecting url.
	 * 
	 * @param header
	 *            http header
	 * @return url
	 */
	private static String getRedirectURL(String header) {
		String url = "";
		for (String line : header.split("\n")) {
			if (line.contains("Location:")) {
				url = line.substring((root.length() + line.indexOf(root)))
						.trim();
			}
		}
		return url;
	}

	/**
	 * method which checks http code.
	 * 
	 * @param code
	 *            code
	 * @return status
	 */
	private static String checkResponse(int code) {
		String status = STATUS_200_OK;
		switch (code) {
		case 200:
			break;
		case 301:
			status = STATUS_301_PERMANENTLY_MOVED;
			break;
		case 302:
			status = STATUS_302_FOUND;
			break;
		case 403:
			status = STATUS_403_FORBIDDEN;
			break;
		case 404:
			status = STATUS_404_NOT_FOUND;
			break;
		case 500:
			status = STATUS_500_INTERNAL_SERVER_ERROR;
			break;
		default:
			status = "unknown";
		}
		return status;
	}

	/**
	 * method to parse the response for urls and keys.
	 * @param response
	 * response to be parsed
	 * @param currUrl
	 * url visited
	 * @return
	 * returns tru if all keys are fetched
	 */
	private static boolean responseParser(String response, String currUrl) {
		visited.add(currUrl);
		String html = getHtml(response);
		getCookies(response);
		Document document = Jsoup.parse(html);
		Elements eKeys = document.select("h2[class=secret_flag]");
		for (Element e : eKeys) {
			System.out.println(e.text().substring(e.text().indexOf(" ") + 1));
			keys.add(e.text().substring(e.text().indexOf(" ") + 1));
			if (keys.size() == 5)
				return true;
		}
		Elements alinks = document.select("a[href]");
		for (Element e : alinks) {
			if (!visited.contains(e.attr("href"))
					&& e.attr("href").contains("/fakebook/")
					&& !current.contains(e.attr("href"))) {
				toVisit.add(e.attr("href"));
			}
		}
		return false;
	}

	/**
	 * method to get cookies, session and token
	 * 
	 * @param response
	 *            response
	 */
	private static void getCookies(String response) {
		List<String> lines = Arrays.asList(response.split("\n"));
		for (String line : lines) {
			if (line.contains("Set-Cookie")) {
				if (line.contains("session")) {
					session = line.split(" ")[1].split("=")[1].replace(";", "");
				}
				if (line.contains("csrf")) {
					token = line.split(" ")[1].split("=")[1].replace(";", "");
				}
			}
		}
	}

	/**
	 * method to get html part of data
	 * 
	 * @param response
	 *            response
	 * @return html body
	 */
	private static String getHtml(String response) {
		return response.substring(response.indexOf("<html"));
	}

	/**
	 * this method builds the http message to be sent to server
	 * 
	 * @param path
	 *            path
	 * @param type
	 *            type, post or get
	 * @param data
	 *            data for post
	 * @return http message
	 */
	private static String buildHTTPRequest(String path, String type, String data) {
		StringBuffer sb = new StringBuffer();
		sb.append(type).append(" ").append(path).append(" ").append(protocol)
				.append(LINEFEED);
		sb.append("Host: cs5700sp15.ccs.neu.edu").append(LINEFEED);
		sb.append("From: ").append("neu").append(LINEFEED);
		sb.append("User-Agent: ").append(userAgent).append(LINEFEED);
		sb.append("Connection: keep-alive").append(LINEFEED);
		if (null != session && !session.isEmpty())
			sb.append("Cookie: sessionid=").append(session)
					.append("  csrftoken=").append(token).append(LINEFEED);
		if (type.equals("POST")) {
			sb.append("Content-Type: application/x-www-form-urlencoded")
					.append(LINEFEED);
			sb.append("Content-Length: ").append(data.length())
					.append(LINEFEED);
			sb.append(LINEFEED);
			sb.append(data);
		}
		sb.append(LINEFEED).append(LINEFEED);
		return sb.toString();
	}
}
