package com.example.podcast.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import com.example.podcast.service.YouTubeService;
import com.example.podcast.service.SummaryService;

@RestController
@RequestMapping("/api")
@CrossOrigin
public class PodcastController {

    @Autowired
    private YouTubeService youTubeService;

    @Autowired
    private SummaryService summaryService;

    @GetMapping("/search")
    public String searchAndSummarize(@RequestParam String query) throws Exception {

        String videoId = youTubeService.searchVideo(query);
        return summaryService.getSummary(videoId);
    }
}