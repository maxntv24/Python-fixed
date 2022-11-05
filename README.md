# ctf-game

### Installation
```bash
docker compose up
```

### Cách để code có hiệu lực trong Docker

1. Trong file `src/main.py` đổi dòng code `app.run(HOST, PORT)` thành `app.run(HOST, PORT, debug=True)` để server có thể autoreload khi thay đổi code
2. Sau khi docker-compose up, cứ để web chạy bình thường
3. Sửa code trực tiếp trong thư mục src
