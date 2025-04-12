# Online3DBinPacking

## Cài đặt môi trường

### 1. Cài đặt môi trường ảo (Virtual Environment)
Trước tiên, hãy chắc chắn rằng bạn đã cài đặt môi trường ảo cho dự án này:

```bash
python -m venv env
```

### 2. Cài đặt các thư viện yêu cầu
Kích hoạt môi trường ảo và cài đặt các thư viện yêu cầu (nếu có):

Trên Windows:

```bash
.\env\Scripts\activate
```  

Trên Linux/macOS:
```bash
source env/bin/activate
```

### 3. Chạy trong VSCode
Khi chạy các script Python trong VSCode, bạn cần cấu hình PYTHONPATH để VSCode có thể nhận diện được thư mục src. Để làm điều này, bạn cần thiết lập PYTHONPATH trong terminal của VSCode như sau:

Mở terminal trong VSCode.

Trước khi chạy bất kỳ script nào, thêm đường dẫn của thư mục gốc vào PYTHONPATH bằng lệnh sau:

Windows (PowerShell):
```bash
$env:PYTHONPATH="path\to\your\project"
```  
Đảm bảo thay đổi "path\to\your\project" thành đường dẫn thư mục gốc của dự án trên máy của bạn.

Sau đó, bạn có thể chạy các script Python hoặc run trong vscode như bình thường:

