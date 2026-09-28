package com.maruthesh.spring.Service;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.http.MediaType;
import com.maruthesh.spring.DTOs.AskResponse;
import com.maruthesh.spring.DTOs.QuestionRequest;

@Service 
public class RagService {
    private final RestClient restClient;
    public RagService() {
    this.restClient = RestClient.builder()
            .baseUrl("http://localhost:8000")
            .requestInterceptor((request, body, execution) -> {

                System.out.println("METHOD: " + request.getMethod());
                System.out.println("URL: " + request.getURI());
                System.out.println("HEADERS: " + request.getHeaders());
                System.out.println("BODY: " + new String(body));

                return execution.execute(request, body);
            })
            .build();
}
    public AskResponse getAnswer(String question) {
    QuestionRequest request = new QuestionRequest();
    request.setQuestion(question);

    System.out.println("Sending body:");
    System.out.println(question);

    return restClient.post()
            .uri("/ask")
            .header("Content-Type", "application/json")
            .body(request)
            .retrieve()
            .body(AskResponse.class);
    }
    
}
