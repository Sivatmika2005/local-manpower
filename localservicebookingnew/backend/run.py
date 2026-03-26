#!/usr/bin/env python3
"""
Run script for Local Service Booking Backend
"""

import os
import sys
from app import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Starting Local Service Booking Backend on port {port}")
    print(f"📊 Health check: http://localhost:{port}/api/health")
    print("Press Ctrl+C to stop the server")

    try:
        app.run(debug=True, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)