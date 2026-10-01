import socket
import uvicorn


def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "<PC-IP>"


if __name__ == "__main__":
    ip = local_ip()
    print("\nEnglishCoach Mobile v0.2")
    print("PC:      http://127.0.0.1:8000")
    print(f"Mobile:  http://{ip}:8000")
    print("※ PC와 휴대폰을 같은 Wi-Fi에 연결하세요.")
    print("※ Windows 방화벽이 물으면 Python의 개인 네트워크 접근을 허용하세요.\n")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
