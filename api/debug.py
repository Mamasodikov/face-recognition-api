from http.server import BaseHTTPRequestHandler
import json
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Simple GET handler for debugging."""
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            
            response = "🔍 Debug Info:\n"
            response += f"Path: {self.path}\n"
            response += f"Headers: {dict(self.headers)}\n"
            response += f"Bot Token Set: {'Yes' if os.environ.get('TELEGRAM_BOT_TOKEN') else 'No'}\n"
            response += "✅ Handler is working!\n"
            
            self.wfile.write(response.encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())
    
    def do_POST(self):
        """Simple POST handler for debugging."""
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write("POST OK".encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())
