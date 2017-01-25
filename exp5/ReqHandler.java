import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

public class ReqHandler implements HttpHandler {

	// holds the origin address
	String addr;
	// this will hold the case paths
	private Map<String, Object> cache = new HashMap<String, Object>();
	// this will holds the frequency of pages requested
	private Map<String, Integer> frequency = new HashMap<String, Integer>();

	/**
	 * constructor method.
	 * 
	 * @param addr
	 */
	public ReqHandler(String addr) {
		this.addr = addr;
	}

	/**
	 * method which handles the incoming request.
	 */
	@Override
	public void handle(HttpExchange arg) throws IOException {
		byte[] bytearray = this.getContent(arg.getRequestURI().toString());
		OutputStream os = arg.getResponseBody();
		arg.sendResponseHeaders(200, bytearray.length);
		os.write(bytearray, 0, bytearray.length);
		os.close();

	}

	/**
	 * method to fetch requested content
	 * 
	 * @param path
	 *            request path
	 * @return content
	 * @throws IOException
	 */
	public byte[] getContent(String path) throws IOException {
		byte[] content;
		if (this.cache.containsKey(path)) {
			try {
				File file = new File(String.valueOf(this.cache.get(path)));
				content = new byte[(int) file.length()];
				FileInputStream fis = new FileInputStream(file);
				BufferedInputStream bis = new BufferedInputStream(fis);
				bis.read(content, 0, content.length);
				bis.close();
				// updating frequency
				this.frequency.put(path, this.frequency.get(path) + 1);
			} catch (FileNotFoundException e) {
				this.frequency.remove(path);
				this.cache.remove(path);
				content = this.downloadFile(path);
			}
		} else {
			content = this.downloadFile(path);
		}
		return content;
	}

	/**
	 * method to remove least frequent path
	 */
	private void removeLeastFrequent(String currDirPath) {
		String path = this.getLeastFrequentKey();
		this.frequency.remove(path);
		this.cache.remove(path);
		this.deleteContent(path, currDirPath);
	}

	/**
	 * method to delete cache content
	 * 
	 * @param path
	 *            path
	 * @param currDirPath
	 *            current dir path
	 */
	private void deleteContent(String path, String currDirPath) {
		File f = new File(currDirPath + path);
		String dirPath = f.getAbsoluteFile().getParentFile().getAbsolutePath();
		File d = new File(dirPath);
		try {
			this.delete(d);
		} catch (IOException e) {
			System.out.println("nothing to delete");
		}
	}

	/**
	 * method to delete all files in a dir
	 * 
	 * @param f
	 *            dir to delete
	 * @throws IOException
	 */
	void delete(File f) throws IOException {
		for (File c : f.listFiles())
			if (!f.isDirectory())
				delete(c);
		if (!f.delete())
			throw new FileNotFoundException("Failed to delete file: " + f);
	}

	/**
	 * method to get the least frequent path
	 * 
	 * @return
	 */
	private String getLeastFrequentKey() {
		String key = "";
		List<Integer> freqs = new ArrayList<Integer>();
		freqs.addAll(this.frequency.values());
		Collections.sort(freqs);
		for (String k : this.frequency.keySet()) {
			if (freqs.get(0) == this.frequency.get(k)) {
				key = k;
			}
		}
		return key;
	}

	/**
	 * method to download the file
	 * 
	 * @param path
	 *            path
	 * @return file content
	 */
	private byte[] downloadFile(String path) {
		String url = "http://" + this.addr + ":8080" + path;
		StringBuffer response = new StringBuffer();
		String currDirPath = System.getProperty("user.dir") + "/cache";
		File t = new File(System.getProperty("user.dir"));
		try {
			URL addr = new URL(url);
			HttpURLConnection con = (HttpURLConnection) addr.openConnection();
			con.setRequestMethod("GET");
			BufferedReader in = new BufferedReader(new InputStreamReader(
					con.getInputStream()));
			String inputLine;

			while ((inputLine = in.readLine()) != null) {
				response.append(inputLine);
			}
			in.close();
			File f = new File(currDirPath + path);
			String dirPath = f.getAbsoluteFile().getParentFile()
					.getAbsolutePath();
			File d = new File(dirPath);
			d.mkdirs();
			FileOutputStream out = new FileOutputStream(f);
			out.write(response.toString().getBytes());
			out.close();
			this.cache.put(path, currDirPath + path);
			this.frequency.put(path, 1);

		} catch (IOException e) {
			System.out.println("failed writing file");
			//if cache is not empty and space left is 100kb then free space
			if (!this.cache.isEmpty() && t.getUsableSpace() < 102400)
				this.removeLeastFrequent(currDirPath);
		}
		return response.toString().getBytes();
	}
}
