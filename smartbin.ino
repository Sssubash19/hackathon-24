#include <WiFi.h>
#include <HTTPClient.h>

// WiFi credentials
const char* ssid = "Your_SSID";
const char* password = "Your_PASSWORD";

// Server URL
const char* serverUrl = "http://your-server.com/api/bin-data";

// Ultrasonic sensor pins
const int trigPin = 5;
const int echoPin = 18;

// Variables
long duration;
float distance;

void setup() {
  Serial.begin(115200);
  
  // Setup sensor pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi!");
}

void loop() {
  // Measure distance
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2; // Convert to cm
  
  // Send data to server if connected
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    String jsonData = "{\"bin_id\": 1, \"level\": " + String(distance) + "}";
    int httpResponseCode = http.POST(jsonData);
    
    if (httpResponseCode > 0) {
      Serial.println("Data sent successfully!");
    } else {
      Serial.println("Failed to send data.");
    }
    http.end();
  }
  
  delay(60000); // Send data every 60 seconds
}
