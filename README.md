# AI Voice-Activated Pizza Ordering System

A full-stack, voice-driven pizza ordering platform built with **Python**, **Google Gemini**, **LangChain**, **React**, **Firebase Realtime Database**, and **ElevenLabs TTS**.  
The system enables customers to place orders entirely through natural conversation, while a React frontend provides a real-time dashboard of incoming orders.

---

## Features

### Conversational AI Ordering (Backend)
- Fully voice-controlled ordering using **SpeechRecognition**, **Google Gemini 2.5**, and **ElevenLabs TTS**
- LangChain agent using **structured tool-calling** to guide users through:
  - Name collection  
  - Phone number validation  
  - Pick-up vs. delivery  
  - Pickup location or delivery address  
  - Itemized order processing  
- Intelligent natural-language order parsing with modification handling  
- Automated total price calculation and receipt generation  
- Robust error handling and fallback logic for speech and tool calls  

### Firebase Integration
- Uses **Firebase Realtime Database** to store:
  - Customer details  
  - Delivery/pickup method  
  - Itemized order details  
  - Timestamps  
  - Total price  
- Ensures normalized, structured order receipts  

### React Frontend Dashboard
- Real-time sales queue that listens to Firebase updates using `onValue`  
- Renders item-level entries including images, prices, names, and metadata  
- Clean, responsive UI for sales and operations teams  
- Custom components such as `SalesQueue` and `Entry`  

---

## Tech Stack

### Backend
- Python  
- LangChain  
- Google Gemini 2.5  
- ElevenLabs Text-to-Speech  
- Google SpeechRecognition  
- Firebase Admin SDK  

### Frontend
- React  
- JavaScript  
- Firebase Web SDK  
- CSS  

---

## Project Structure
```bash
backend/
│── main.py
│── requirements.txt
│── firebase_key.json
│── utils/
│── menu/
frontend/
│── src/
│ ├── components/
│ │ ├── SalesQueue.jsx
│ │ ├── Entry.jsx
│ ├── Firebase.jsx
│ ├── App.jsx
│── public/images/
│── package.json
```
---

## How It Works

### Backend Flow
1. Agent calls tools sequentially:
   - `get_name`  
   - `get_phone_number`  
   - `get_pickordel_method`  
   - `get_pickup_location` or `get_delivery_address`  
   - `get_order_details`  
   - `get_total_price`  
2. LLM creates a typed `finalReceipt` object  
3. Receipt is saved to Firebase with timestamp  
4. Frontend streams updates instantly  

### Frontend Flow
- Connects to Firebase Realtime Database  
- Subscribes to `/orders` path  
- Flattens itemized order data into display-ready entries  
- Displays each item with:
  - Image
  - Order ID
  - Customer name
  - Phone number
  - Quantity & price  
  - Pickup/delivery data  

---

## Installation

### Backend Setup
```bash
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
npm run dev
```
