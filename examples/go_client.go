package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// Request structures matching the Python microservice
type AnalyzeRequest struct {
	Title    string   `json:"title"`
	Abstract string   `json:"abstract"`
	Field    string   `json:"field"`
	Authors  []string `json:"authors,omitempty"`
	Keywords []string `json:"keywords,omitempty"`
}

type TopicRequest struct {
	Topic     string `json:"topic"`
	Field     string `json:"field"`
	MaxPapers int    `json:"max_papers,omitempty"`
}

// Response structures
type ResearchGap struct {
	GapDescription   string  `json:"gap_description"`
	ConfidenceScore  float64 `json:"confidence_score"`
	GapType         string  `json:"gap_type"`
	PotentialImpact string  `json:"potential_impact"`
}

type Hypothesis struct {
	Hypothesis       string   `json:"hypothesis"`
	Rationale       string   `json:"rationale"`
	FeasibilityScore float64  `json:"feasibility_score"`
	RequiredMethods []string `json:"required_methods"`
}

type AnalyzeResponse struct {
	KeyFindings        []string      `json:"key_findings"`
	Gaps              []ResearchGap `json:"gaps"`
	SuggestedHypotheses []Hypothesis  `json:"suggested_hypotheses"`
	Limitations       []string      `json:"limitations"`
	MethodologyGaps   []string      `json:"methodology_gaps"`
	FutureDirections  []string      `json:"future_directions"`
	ProcessingTime    float64       `json:"processing_time"`
}

type TopicAnalysisResult struct {
	PaperTitle string        `json:"paper_title"`
	Authors    []string      `json:"authors"`
	Abstract   string        `json:"abstract"`
	Gaps       []ResearchGap `json:"gaps"`
	URL        string        `json:"url"`
}

type TopicResponse struct {
	Topic                    string                 `json:"topic"`
	PapersAnalyzed          int                    `json:"papers_analyzed"`
	CommonGaps              []ResearchGap          `json:"common_gaps"`
	IndividualResults       []TopicAnalysisResult  `json:"individual_results"`
	SuggestedResearchDirections []string            `json:"suggested_research_directions"`
	ProcessingTime          float64                `json:"processing_time"`
}

type HealthResponse struct {
	Status    string `json:"status"`
	Version   string `json:"version"`
	Timestamp string `json:"timestamp"`
}

// AIGapFinderClient is a client for the AI Gap Finder microservice
type AIGapFinderClient struct {
	baseURL    string
	httpClient *http.Client
}

// NewAIGapFinderClient creates a new client instance
func NewAIGapFinderClient(baseURL string) *AIGapFinderClient {
	return &AIGapFinderClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 60 * time.Second,
		},
	}
}

// AnalyzeAbstract analyzes a single research abstract
func (c *AIGapFinderClient) AnalyzeAbstract(req AnalyzeRequest) (*AnalyzeResponse, error) {
	jsonData, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("error marshaling request: %w", err)
	}

	url := c.baseURL + "/analyze"
	resp, err := c.httpClient.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("error making request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	var result AnalyzeResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("error unmarshaling response: %w", err)
	}

	return &result, nil
}

// AnalyzeTopic analyzes multiple papers on a topic
func (c *AIGapFinderClient) AnalyzeTopic(req TopicRequest) (*TopicResponse, error) {
	jsonData, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("error marshaling request: %w", err)
	}

	url := c.baseURL + "/topic"
	resp, err := c.httpClient.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("error making request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	var result TopicResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("error unmarshaling response: %w", err)
	}

	return &result, nil
}

// HealthCheck checks if the microservice is healthy
func (c *AIGapFinderClient) HealthCheck() (*HealthResponse, error) {
	url := c.baseURL + "/health"
	resp, err := c.httpClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("error making request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	var result HealthResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("error unmarshaling response: %w", err)
	}

	return &result, nil
}

// Example usage
func main() {
	// Create client
	client := NewAIGapFinderClient("http://localhost:8001")

	// Check health
	health, err := client.HealthCheck()
	if err != nil {
		fmt.Printf("Health check failed: %v\n", err)
		return
	}
	fmt.Printf("Service status: %s\n", health.Status)

	// Analyze an abstract
	analyzeReq := AnalyzeRequest{
		Title:    "Deep Learning Applications in Medical Imaging",
		Abstract: "This study explores the use of convolutional neural networks for medical image analysis, focusing on diagnostic accuracy improvements. We trained models on radiological datasets and evaluated performance across multiple metrics.",
		Field:    "medicine",
		Authors:  []string{"Dr. Jane Smith", "Dr. John Doe"},
	}

	result, err := client.AnalyzeAbstract(analyzeReq)
	if err != nil {
		fmt.Printf("Analysis failed: %v\n", err)
		return
	}

	fmt.Printf("Analysis completed in %.2f seconds\n", result.ProcessingTime)
	fmt.Printf("Found %d research gaps:\n", len(result.Gaps))
	for i, gap := range result.Gaps {
		fmt.Printf("  %d. %s (Confidence: %.2f)\n", i+1, gap.GapDescription, gap.ConfidenceScore)
	}

	// Analyze a topic
	topicReq := TopicRequest{
		Topic:     "quantum computing in cryptography",
		Field:     "computer_science",
		MaxPapers: 5,
	}

	topicResult, err := client.AnalyzeTopic(topicReq)
	if err != nil {
		fmt.Printf("Topic analysis failed: %v\n", err)
		return
	}

	fmt.Printf("\nTopic analysis for '%s' completed in %.2f seconds\n", topicResult.Topic, topicResult.ProcessingTime)
	fmt.Printf("Analyzed %d papers\n", topicResult.PapersAnalyzed)
	fmt.Printf("Found %d common gaps:\n", len(topicResult.CommonGaps))
	for i, gap := range topicResult.CommonGaps {
		fmt.Printf("  %d. %s (Type: %s)\n", i+1, gap.GapDescription, gap.GapType)
	}
}
