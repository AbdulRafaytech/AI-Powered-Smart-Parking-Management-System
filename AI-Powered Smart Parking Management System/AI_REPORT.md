# AI-Powered Smart Parking Management System Report

## Overview
This project transforms a traditional parking lot into a high-intelligence facility using a suite of seven Deep Learning and Statistical AI models. The system is designed for high accuracy, real-time response, and operational efficiency.

## Implemented AI Models & Architectures

### 1. Two-Stage CNN ANPR (Automatic Number Plate Recognition)
- **Architecture:** Implements a sophisticated two-stage pipeline for maximum recognition accuracy.
  - **Stage 1 (Detection):** Uses the **CRAFT** (Convolutional Character Region Awareness) model to identify and localize the specific bounding box of the license plate within the frame.
  - **Stage 2 (Recognition):** The localized plate is cropped, upscaled, and enhanced using **CLAHE** (Contrast Limited Adaptive Histogram Equalization). Recognition is then performed using a **CRNN** (Convolutional Recurrent Neural Network) with an LSTM-based sequence decoder.
- **Benefits:** By focusing only on the cropped plate region, the model minimizes background noise and character confusion, delivering professional-grade accuracy.

### 2. Intelligent Parking Space Recommendation AI
- **Description:** A logic-driven AI that assigns slots based on real-time availability and vehicle classification (Normal, Disabled, VIP, Bike).
- **Benefits:** Ensures optimal space allocation and prioritized access.

### 3. Automated Billing & AI Time Tracking
- **Description:** Automatically calculates parking duration and fees upon vehicle exit by cross-referencing Entry/Exit timestamps recorded by the ANPR system.
- **Benefits:** Removes human error and speeds up throughput.

### 4. Overstay Detection AI
- **Description:** Monitors active sessions and flags vehicles exceeding the allowed duration threshold.
- **Benefits:** Identifies abandoned vehicles and improves lot turnover.

### 5. Statistical Peak Hour Prediction AI
- **Description:** Uses historical data analysis and statistical modeling (frequency distribution) to forecast high-demand periods.
- **Benefits:** Enables predictive staffing and dynamic facility management.

### 6. Computer Vision Fraud Detection (Simulation)
- **Description:** Simulates the detection of parking violations (e.g., parking in no-parking zones or unauthorized VIP slot usage).
- **Benefits:** Provides a blueprint for integrating real-world sensor/camera data for compliance monitoring.

### 7. Integrated Smart Parking System
- **Description:** A unified, web-based control center (built with Streamlit) that centralizes all AI outputs, live IPCam monitoring, and security protocols.

## Technical Stack
- **Interface:** Streamlit (Dynamic Theme Engine: Wisteria/Midnight Bloom)
- **Computer Vision:** OpenCV & Two-Stage Deep Learning Pipeline (CRAFT + CRNN)
- **Database:** SQLite3
- **Data Processing:** NumPy & Scikit-learn
- **Branding:** Made by Rafay

## Conclusion
The transition to a Two-Stage CNN architecture significantly enhances the system's ability to operate in real-world conditions, providing reliable license plate recognition and intelligent facility management.
