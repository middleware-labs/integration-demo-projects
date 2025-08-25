package com.example.controller;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;

@RestController
public class LogGeneratorController {

    private static final Logger logger = LogManager.getLogger(LogGeneratorController.class);

    @GetMapping("/")
    public Map<String, String> health() {
        logger.info("Health check endpoint accessed");
        Map<String, String> response = new HashMap<>();
        response.put("status", "healthy");
        response.put("service", "json-log-reproduction-service");
        return response;
    }

    @GetMapping("/generate-logs")
    public Map<String, String> generateLogs(@RequestParam(defaultValue = "10") int count) {
        logger.info("Starting log generation for {} entries", count);
        
        for (int i = 0; i < count; i++) {
            generateRandomLog(i);
        }
        
        logger.info("Completed log generation for {} entries", count);
        
        Map<String, String> response = new HashMap<>();
        response.put("message", "Generated " + count + " log entries");
        response.put("status", "success");
        return response;
    }

    @GetMapping("/api-simulation")
    public Map<String, String> simulateApiCall() {
        String sellerId = "A" + ThreadLocalRandom.current().nextInt(100000, 999999) + "Z" + ThreadLocalRandom.current().nextInt(10, 99) + "Y";
        String actionType = getRandomActionType();
        String amazonChannel = getRandomAmazonChannel();
        int tokenBlockCount = ThreadLocalRandom.current().nextInt(1, 50);
        
        // Simulate the exact log format from the user's example
        logger.warn("token blocked SpApiClient.CacheTokenKey(amazonChannel={}, actionType={}, sellerId={}), count {}", 
                   amazonChannel, actionType, sellerId, tokenBlockCount);
                   
        logger.info("API simulation completed for seller {} on channel {}", sellerId, amazonChannel);
        
        Map<String, String> response = new HashMap<>();
        response.put("sellerId", sellerId);
        response.put("actionType", actionType);
        response.put("amazonChannel", amazonChannel);
        response.put("tokenBlockCount", String.valueOf(tokenBlockCount));
        return response;
    }

    @GetMapping("/error-simulation")
    public Map<String, String> simulateError() {
        try {
            // Simulate an error scenario
            throw new RuntimeException("Simulated database connection timeout");
        } catch (Exception e) {
            logger.error("Database operation failed", e);
            
            Map<String, String> response = new HashMap<>();
            response.put("error", "Database connection timeout");
            response.put("status", "error");
            return response;
        }
    }

    private void generateRandomLog(int index) {
        int logType = ThreadLocalRandom.current().nextInt(1, 5);
        
        switch (logType) {
            case 1:
                logger.info("Processing request #{} for user session {}", index, generateSessionId());
                break;
            case 2:
                logger.warn("Rate limit approaching for API key: {} ({}% of limit used)", 
                           generateApiKey(), ThreadLocalRandom.current().nextInt(70, 95));
                break;
            case 3:
                logger.debug("Cache hit for key: {} in {} ms", 
                            generateCacheKey(), ThreadLocalRandom.current().nextInt(1, 50));
                break;
            case 4:
                logger.error("Failed to process order {} due to payment validation error", 
                            generateOrderId());
                break;
        }
    }

    private String getRandomActionType() {
        String[] actionTypes = {"getCatalogItem", "getOrder", "updateInventory", "getListingOffers", "submitFeed"};
        return actionTypes[ThreadLocalRandom.current().nextInt(actionTypes.length)];
    }

    private String getRandomAmazonChannel() {
        String[] channels = {"AMAZON_US", "AMAZON_UK", "AMAZON_DE", "AMAZON_FR", "AMAZON_IT", "AMAZON_ES"};
        return channels[ThreadLocalRandom.current().nextInt(channels.length)];
    }

    private String generateSessionId() {
        return "session_" + ThreadLocalRandom.current().nextInt(100000, 999999);
    }

    private String generateApiKey() {
        return "ak_" + ThreadLocalRandom.current().nextInt(1000000, 9999999);
    }

    private String generateCacheKey() {
        return "cache:" + ThreadLocalRandom.current().nextInt(1000, 9999);
    }

    private String generateOrderId() {
        return "ord_" + ThreadLocalRandom.current().nextInt(1000000, 9999999);
    }
} 