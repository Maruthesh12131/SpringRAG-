package com.maruthesh.spring.Controller;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.maruthesh.spring.DTOs.AskResponse;
import com.maruthesh.spring.DTOs.QuestionRequest;
import com.maruthesh.spring.Service.RagService;

@CrossOrigin(origins = "http://54.253.130.88:5173")
@RestController 
public class HealthController {

    private final RagService ragService;

    public HealthController(RagService ragService){
        this.ragService = ragService;
    }

    @GetMapping ("api/health")
    public String health() {
        return "RAG application is running";
    }

    @PostMapping("api/ask")
    public AskResponse askQuestion(@RequestBody QuestionRequest request) {
        return ragService.getAnswer(request.getQuestion());
    }   
}

