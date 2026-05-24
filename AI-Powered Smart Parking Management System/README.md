# Wisteria Parking: AI-Powered Smart Parking System

A beautiful, high-performance web-based parking management solution featuring real-time license plate recognition (ANPR), predictive analytics, and a dynamic theme engine.

## Requirements

The system requires Python 3.x and the following libraries:

- `streamlit`
- `opencv-python-headless`
- `easyocr`
- `numpy`
- `scikit-learn`
- `pillow`
- `sqlite3`

Install all dependencies using pip:

```bash
pip install streamlit opencv-python-headless easyocr numpy scikit-learn pillow
```

## How to Run

### 1. Initialize the Database
```bash
python3 init_db.py
```

### 2. (Optional) Generate Dummy Data
```bash
python3 generate_dummy_data.py
```

### 3. Launch the Application
```bash
streamlit run app.py
```

## Key Features
- **Dynamic Themes:** Toggle between **Wisteria Bloom (Light)** and **Midnight Bloom (Dark)**.
- **Enhanced OCR:** AI-powered plate recognition optimized with image processing and alphanumeric allowlists to prevent character confusion.
- **IPCam Integration:** Direct stream support from LAN or RTSP links.
- **Made by Rafay:** Personalized branding and professional UI design.
- **Advanced AI Analytics:** Peak demand prediction and real-time violation monitoring.

## Credits
**Made by Rafay**
