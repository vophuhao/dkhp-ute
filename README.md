# HCMUTE - Công cụ đăng ký học phần

Tool tự động đăng ký môn học HCMUTE với tính năng retry tự động.

## Tính năng
- ✅ Tự động thử lại cho đến khi thành công
- ✅ Đăng ký nhiều môn cùng lúc
- ✅ Giao diện web thân thiện
- ✅ Hiển thị kết quả real-time

## Deploy lên Render

1. Tạo tài khoản tại [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect với GitHub repo hoặc upload code
4. Cấu hình:
   - **Name**: hcmute-registration-tool
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free
5. Click **"Create Web Service"**

Website sẽ được deploy tại: `https://your-app-name.onrender.com`

## Chạy local

```bash
python app.py
```

Mở trình duyệt: http://localhost:10000
