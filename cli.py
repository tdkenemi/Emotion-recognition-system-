import argparse
import uvicorn
import os
import sys

def start_server(port, host):
    print(f"Khoi dong EmotionAI Server tai http://{host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)

def main():
    parser = argparse.ArgumentParser(description="EmotionAI CLI - Hệ thống phân tích cảm xúc")
    subparsers = parser.add_subparsers(dest="command", help="Các lệnh khả dụng")
    
    # Command: start
    start_parser = subparsers.add_parser("start", help="Khởi động Web Server")
    start_parser.add_argument("--port", type=int, default=8000, help="Cổng chạy server (mặc định: 8000)")
    start_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host chạy server")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_server(args.port, args.host)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
