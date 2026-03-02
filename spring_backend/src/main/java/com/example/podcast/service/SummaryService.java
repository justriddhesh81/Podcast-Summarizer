package com.example.podcast.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;

@Service
public class SummaryService {

    @Value("${python.service.url}")
    private String pythonServiceUrl;

    public String getSummary(String videoId) {
        RestTemplate restTemplate = new RestTemplate();
        String url = pythonServiceUrl + "/summarize/" + videoId;

        ResponseEntity<String> response =
                restTemplate.getForEntity(url, String.class);

        return response.getBody();
    }
}