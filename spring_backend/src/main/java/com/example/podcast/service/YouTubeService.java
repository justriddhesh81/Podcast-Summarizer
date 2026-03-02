package com.example.podcast.service;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.client.RestTemplate;
import org.json.JSONObject;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
@Service
public class YouTubeService {

    @Value("${youtube.api.key}")
    private String apiKey;

    public String searchVideo(String query) throws Exception {
        String url = "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=1&q="
                + URLEncoder.encode(query, StandardCharsets.UTF_8)
                + "&key=" + apiKey;

        RestTemplate restTemplate = new RestTemplate();
        String response = restTemplate.getForObject(url, String.class);

        JSONObject json = new JSONObject(response);
        return json.getJSONArray("items")
                .getJSONObject(0)
                .getJSONObject("id")
                .getString("videoId");
    }
}