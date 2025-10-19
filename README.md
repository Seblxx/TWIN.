Here’s the simply 4 step guide to running my project!

#0 Install Python (if you dont already have it)

#1 Create a python environment
python -m venv .venv
.venv\Scripts\Activate.ps1

#2 Install all the dependencies
pip install flask flask-cors pandas numpy requests yfinance statsmodel

#3 run the backend
python app.py

$4 run the frontend
Open a NEW terminal and paste this command: python -m http.server 5500

VISIT localhost:5500 and you’re free to use my app!
