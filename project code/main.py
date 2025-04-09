from flask import Flask, render_template_string, send_from_directory
import os
import webbrowser

#Configure flask
app = Flask(__name__)

#Configure routes for webpages and other static files
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<page>.html')
def other_html_pages(page):
    return send_from_directory('frontend', f"{page}.html")

@app.route('/<filename>')
def serve_static_file(filename):
    return send_from_directory('frontend', filename)

@app.route('/assets/<path:filename>')
def serve_asset_file(filename):
    return send_from_directory('frontend/assets', filename)

if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)